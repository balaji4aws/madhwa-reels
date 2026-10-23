#!/usr/bin/env python3
"""Reusable cut-boundary tool, shared across all source videos.

Given a rough start/end time (in source seconds) and the source video + its
VTT captions, this module proposes a *snapped* boundary for each end of the
window:

  1. It runs `ffmpeg ... -af silencedetect` on a short audio window around the
     rough timestamp to find a real pause in speech near it.
  2. It snaps to the pause closest to the rough timestamp (if one was found).
  3. It cross-checks the (possibly snapped) time against the VTT cue
     intervals using the same `inside_cue` logic that `check_reel.py` already
     relies on for its odd-cut check, so a "clean" result here and a PASS from
     `check_reel.py` later mean the same thing.
  4. It reports a structured, explicit confidence flag per boundary:
       - "clean"                  — pause found AND lands at a cue boundary.
       - "snapped-low-confidence" — boundary looks OK but one signal is
                                     missing/ambiguous (no clear pause, or a
                                     pause was found but not close to a cue
                                     edge). Needs a quick human glance.
       - "review-manually"        — still inside a cue with no nearby pause.
                                     This is the pattern `check_reel.py`'s
                                     docstring already says it reliably
                                     catches; always read the caption text at
                                     this timestamp before cutting here.

IMPORTANT: exactly like `check_reel.py`, `silencedetect` is only ever used to
CHOOSE a candidate snap point. It is never the final correctness signal —
these recordings carry a constant background drone (tanpura/shruti) that
makes raw loudness unreliable, so the only thing that can certify a boundary
is whether it lands at a caption cue edge, not inside a cue. This module
never silently reports "clean" without having actually checked both signals.

Usable as a library:
    from clip_cutter import load_cues, inside_cue, snap_boundary, build_report

Usable as a CLI:
    python3 clip_cutter.py --video <source.mp4> --vtt <source.en.vtt> \\
        --start 1131.0 --end 1168.5 [--window 4.0] [--silence-db -30] \\
        [--silence-min-dur 0.25] [--json report.json]
"""
import argparse
import json
import os
import re
import subprocess
import sys

CUE_RE = re.compile(
    r"(\d\d):(\d\d):(\d\d)\.(\d+)\s*-->\s*(\d\d):(\d\d):(\d\d)\.(\d+)")
SILENCE_START_RE = re.compile(r"silence_start:\s*([-\d.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([-\d.]+)")

DEFAULT_WINDOW = 4.0          # seconds either side of the rough time to scan
DEFAULT_SILENCE_DB = -30      # dBFS threshold, deliberately conservative
DEFAULT_SILENCE_MIN_DUR = 0.25  # minimum silence duration to count as a pause
INSIDE_CUE_PAD = 0.25          # matches check_reel.py's pad constant


def load_cues(vtt_path):
    """Parse a VTT into a list of (start_sec, end_sec) cue intervals.

    This is the canonical implementation — `check_reel.py` imports it instead
    of keeping its own copy, so the two tools can never drift apart on how a
    cue boundary is defined.
    """
    cues = []
    with open(vtt_path) as f:
        for ln in f:
            m = CUE_RE.match(ln)
            if m:
                a = (int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
                     + int(m[4]) / 1000)
                b = (int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7])
                     + int(m[8]) / 1000)
                if b > a:
                    cues.append((a, b))
    return cues


def inside_cue(t, cues, pad=INSIDE_CUE_PAD):
    """True if t falls strictly inside a cue (not within pad of its edges),
    i.e. speech is still mid-flow there -> likely odd cut."""
    for a, b in cues:
        if a + pad < t < b - pad:
            return True
    return False


def nearest_cue_text(t, vtt_path, pad=INSIDE_CUE_PAD):
    """Best-effort text of the cue nearest to t, for a human-readable report.
    Re-reads the VTT to pair each interval with its text (load_cues only
    keeps timings)."""
    best = None
    best_dist = None
    with open(vtt_path) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        m = CUE_RE.match(lines[i])
        if m:
            a = (int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
                 + int(m[4]) / 1000)
            b = (int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7])
                 + int(m[8]) / 1000)
            # collect the text lines until the next blank line
            text_lines = []
            j = i + 1
            while j < len(lines) and lines[j].strip():
                text_lines.append(lines[j].strip())
                j += 1
            text = " ".join(text_lines).strip()
            if text and b > a:
                dist = 0.0 if a - pad <= t <= b + pad else min(abs(t - a), abs(t - b))
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best = text
            i = j
        else:
            i += 1
    return best or ""


def find_candidate_pause(video_path, center_time, window=DEFAULT_WINDOW,
                          db=DEFAULT_SILENCE_DB,
                          min_dur=DEFAULT_SILENCE_MIN_DUR):
    """Run ffmpeg silencedetect on a short audio window around center_time.

    Returns a list of (pause_start, pause_end) tuples in *source* seconds,
    sorted by closeness of the pause midpoint to center_time. Empty list if
    no pause was detected in the window.
    """
    seek = max(0.0, center_time - window)
    dur = 2 * window
    cmd = [
        "ffmpeg", "-nostdin", "-ss", str(seek), "-t", str(dur),
        "-i", video_path,
        "-af", f"silencedetect=noise={db}dB:d={min_dur}",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    stderr = r.stderr

    starts = [float(x) for x in SILENCE_START_RE.findall(stderr)]
    ends = [float(x) for x in SILENCE_END_RE.findall(stderr)]
    # silencedetect reports times relative to the (seeked) input stream.
    pauses = []
    for idx, s_rel in enumerate(starts):
        e_rel = ends[idx] if idx < len(ends) else dur
        pauses.append((seek + s_rel, seek + e_rel))

    pauses.sort(key=lambda p: abs((p[0] + p[1]) / 2 - center_time))
    return pauses


def snap_boundary(video_path, cues, rough_time, vtt_path,
                   window=DEFAULT_WINDOW, db=DEFAULT_SILENCE_DB,
                   min_dur=DEFAULT_SILENCE_MIN_DUR, label=""):
    """Propose a snapped boundary near rough_time and report confidence.

    Returns a dict (JSON-able) with the requested/snapped times, whether a
    pause was found, whether the result lands inside a cue, and an explicit
    confidence flag. Never silently claims "clean" without checking both the
    silence signal and the caption-boundary signal.
    """
    pauses = find_candidate_pause(video_path, rough_time, window, db, min_dur)

    pause_found = len(pauses) > 0
    if pause_found:
        p_start, p_end = pauses[0]
        snapped = (p_start + p_end) / 2
        pause_gap_sec = round(p_end - p_start, 3)
        pause_distance = round(abs(snapped - rough_time), 3)
    else:
        snapped = rough_time
        pause_gap_sec = None
        pause_distance = None

    is_inside = inside_cue(snapped, cues)
    cue_text = nearest_cue_text(snapped, vtt_path)

    # Confidence rule (deliberately conservative — see module docstring).
    if is_inside:
        # Still mid-sentence even after trying to snap: the one failure mode
        # check_reel.py already says it reliably catches.
        confidence = "review-manually"
    elif pause_found and pause_distance is not None and pause_distance <= window:
        # A real pause was found and the result is clear of any cue body.
        # Treat a pause very far from the rough time (unlikely given the
        # window bound, kept as an explicit guard) as low-confidence instead.
        confidence = "clean"
    else:
        # Either no clear pause was found (we fell back to the rough time but
        # it happens to land on a cue boundary), or ambiguous otherwise.
        confidence = "snapped-low-confidence"

    return {
        "label": label,
        "requested": round(rough_time, 3),
        "snapped": round(snapped, 3),
        "pause_found": pause_found,
        "pause_gap_sec": pause_gap_sec,
        "pause_distance_sec": pause_distance,
        "inside_cue": is_inside,
        "nearest_cue_text": cue_text,
        "confidence": confidence,
    }


def build_report(video, vtt, windows, window=DEFAULT_WINDOW,
                  db=DEFAULT_SILENCE_DB, min_dur=DEFAULT_SILENCE_MIN_DUR):
    """Run snap_boundary for the start and end of every (label, start, end)
    window. Returns one JSON-able report dict.

    `windows` is a list of (label, start, end) tuples, e.g.
    [("reel06", 1130.0, 1169.0)].
    """
    cues = load_cues(vtt)
    boundaries = []
    for label, start, end in windows:
        boundaries.append(snap_boundary(
            video, cues, start, vtt, window, db, min_dur,
            label=f"{label}_start"))
        boundaries.append(snap_boundary(
            video, cues, end, vtt, window, db, min_dur,
            label=f"{label}_end"))
    return {"video": video, "vtt": vtt, "boundaries": boundaries}


def print_report(report):
    for b in report["boundaries"]:
        flag = b["confidence"].upper()
        print(f"[{flag}] {b['label']}: requested={b['requested']}s -> "
              f"snapped={b['snapped']}s "
              f"(pause_found={b['pause_found']}, "
              f"inside_cue={b['inside_cue']})")
        if b["nearest_cue_text"]:
            print(f"         nearest cue text: \"{b['nearest_cue_text']}\"")
        if b["confidence"] != "clean":
            print("         -> human review recommended before cutting here")


def main():
    ap = argparse.ArgumentParser(
        description="Snap a rough cut boundary to a real speech pause and "
                    "verify it against VTT cue boundaries.")
    ap.add_argument("--video", required=True, help="source video path")
    ap.add_argument("--vtt", required=True, help="source .en.vtt path")
    ap.add_argument("--start", type=float, required=True,
                     help="rough clip start, source seconds")
    ap.add_argument("--end", type=float, required=True,
                     help="rough clip end, source seconds")
    ap.add_argument("--label", default="clip",
                     help="label prefix for the two boundaries (default: clip)")
    ap.add_argument("--window", type=float, default=DEFAULT_WINDOW,
                     help="seconds either side of the rough time to scan "
                          "for a pause (default: %(default)s)")
    ap.add_argument("--silence-db", type=float, default=DEFAULT_SILENCE_DB,
                     help="silencedetect noise threshold in dB "
                          "(default: %(default)s)")
    ap.add_argument("--silence-min-dur", type=float,
                     default=DEFAULT_SILENCE_MIN_DUR,
                     help="minimum silence duration to count as a pause, "
                          "seconds (default: %(default)s)")
    ap.add_argument("--json", help="optional path to write the JSON report")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print(f"ERROR: video not found: {args.video}", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(args.vtt):
        print(f"ERROR: vtt not found: {args.vtt}", file=sys.stderr)
        sys.exit(2)

    report = build_report(
        args.video, args.vtt,
        [(args.label, args.start, args.end)],
        window=args.window, db=args.silence_db, min_dur=args.silence_min_dur)

    print(f"\n=== CUT BOUNDARY REPORT: {os.path.basename(args.video)} ===")
    print_report(report)
    print("=== end report (advisory only — review any non-'clean' flag) ===")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nWrote JSON report to {args.json}")


if __name__ == "__main__":
    main()

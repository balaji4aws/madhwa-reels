#!/usr/bin/env python3
"""Shared cut-transition fade helper, used across all source videos.

Context (see docs/CHANGELOG.md's "abrupt cuts" entries): reels 03/04 had
tight, frame-accurate cuts with no transition at all, and the channel owner
flagged them as abrupt. A follow-up build (05/06) widened the SILENCE MARGIN
at each cut boundary (snapping further into the surrounding pause) -- that
fix verified cleanly via silencedetect + VTT sentence-boundary checks, but
the user watched the result and said it was STILL abrupt. Root cause (per
direct conversation, not re-diagnosed here): the margin controls WHERE the
cut lands, not HOW the cut transitions -- a hard jump-cut feel (instant
amplitude edge, instant visual start/stop) persists even when the boundary
itself sits in genuine silence.

This module is the fix for the TRANSITION, layered ON TOP of (not instead
of) correct silence-margin boundary placement:
  - a short fade-IN from black + audio fade-in at the very start of the raw
    cut clip
  - a short fade-OUT to black + audio fade-out at the very end

Chosen technique: fade-to/from-BLACK (ffmpeg `fade=t=in/out`), not an
alpha/crossfade trick -- this machine's ffmpeg has no drawtext but DOES
support the plain `fade` video filter (it's a pixel-level dissolve, not a
text/font feature), and fading through black is the simplest, most robust
visual treatment that reads as an intentional edit rather than a hiccup.
Matching `afade` on audio so the sound level ramps instead of hard-cutting.

FADE_DURATION = 0.2s (200ms), chosen and verified by:
  1. Prototyping on an existing raw clip (clip03_dharmadevi-name-meaning.mp4)
     and inspecting the actual rendered first/last frames directly -- 200ms
     is clearly visible as a deliberate fade (first frame is solid black,
     the frame just before the true end is already visibly dimming), not
     imperceptibly short.
  2. It's short enough not to eat meaningfully into the already-tight
     silence-margin boundaries from the 05/06 session (margins there ranged
     ~0.4-1.2s; a 0.2s fade fits inside that margin on every one of the 4
     existing boundaries without encroaching on spoken content).
  3. Applied consistently to all 6 clips in this task (the 2 rebuilt + 4
     new) for a uniform house feel -- not re-tuned per clip.

This MUST be applied to the RAW cut clip, BEFORE overlay compositing
(title/subtitle/watermark PNGs) -- see apply_fade()'s docstring for why.

Usable as a library:
    from fade_clip import apply_fade, DEFAULT_FADE_DURATION

Usable as a CLI (handy for prototyping/inspection):
    python3 fade_clip.py --in clip03_dharmadevi-name-meaning.mp4 \\
        --out /tmp/clip03_faded.mp4 [--duration 0.2]
"""
import argparse
import subprocess
import sys

DEFAULT_FADE_DURATION = 0.2  # seconds; see module docstring for reasoning


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def apply_fade(src_path, out_path, duration=DEFAULT_FADE_DURATION):
    """Apply a video fade-in/out (to/from black) and matching audio
    fade-in/out to the RAW cut clip at src_path, writing a new file at
    out_path. Re-encodes (fades are a pixel/sample-level effect, can't be
    done with `-c copy`).

    IMPORTANT: this must run on the raw clip BEFORE any overlay compositing
    (title card / subtitle / watermark PNGs). If it ran after compositing,
    fading the full frame to black would also fade out an overlay that
    might still need to be visible (or fade one in at a different rate than
    the background), and if it ran only on a sub-layer, the fade would be
    inconsistent across the frame. Running it first means every later
    overlay step composites onto an already-fade-corrected background, so
    the finished, fully composited clip fades as one unit.

    Returns out_path on success; raises RuntimeError on ffmpeg failure.
    """
    dur = probe_duration(src_path)
    if dur <= 2 * duration:
        raise ValueError(
            f"clip duration ({dur:.2f}s) too short for a {duration}s "
            f"fade on both ends -- would overlap in the middle.")
    fade_out_start = round(dur - duration, 3)

    cmd = [
        "ffmpeg", "-y", "-nostdin", "-i", src_path,
        "-vf", f"fade=t=in:st=0:d={duration},"
               f"fade=t=out:st={fade_out_start}:d={duration}",
        "-af", f"afade=t=in:st=0:d={duration},"
               f"afade=t=out:st={fade_out_start}:d={duration}",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-crf", "16", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg fade failed on {src_path}:\n{r.stderr[-2000:]}")
    return out_path


def main():
    ap = argparse.ArgumentParser(
        description="Apply a short fade-in/out (video to/from black + "
                    "matching audio afade) to a raw cut clip, as the fix "
                    "for jump-cut-feeling boundaries.")
    ap.add_argument("--in", dest="src", required=True, help="raw clip path")
    ap.add_argument("--out", dest="dst", required=True, help="output path")
    ap.add_argument("--duration", type=float, default=DEFAULT_FADE_DURATION,
                     help="fade duration in seconds (default: %(default)s)")
    args = ap.parse_args()
    try:
        apply_fade(args.src, args.dst, args.duration)
    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {args.dst}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build Reel 02 (slug: venkatachala-ep06) -- "Why the Chakra & Conch?"

Source: "Glory of Venkatachala | Ep - 06 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri
Satyatmateertha Shripadangalavaru" (Sri Uttaradi Math Adhyatmavani), full
discourse 2887.4s (~48.1 min) -- NOT trimmed at download time, per house rule.

Moment: a "did you know" teaching on why the Lord carries the Sudarshana
chakra and conch -- per the Aditya Purana / Venkatesa Mahatma, the chakra's
radiance (bright as crores of suns) dispels not just outer darkness but the
darkness of ignorance within, and the conch doesn't just make sound -- it
gives knowledge of the truth, being the Lord's own form. Self-contained
hook+payoff, two parallel "not just X, but Y" statements that need to land
together for the symmetry (and the payoff) to read -- see cut-length note
below.

Cut boundaries verified with tools/clip_cutter.py (see cut_report_02.json) +
manual review (both boundaries read by hand against the VTT text + a direct
ffmpeg silencedetect pass -- see docs/CHANGELOG.md for the full writeup):
  start = 616.661 (source): flagged review-manually (lands inside the coarse
          run-on cue "one by one. As", 613.04-617.59s). Confirmed by direct
          silencedetect (genuine ~0.6s pause at 616.31-616.92s) and by
          reading the cue's word order: the pause sits right after "...the
          Supreme Soul has described all the weapons one by one." and
          before "As indicated in the Aditya Purana..." begins the next
          sentence -- a real sentence break, same cue-display-lag pattern
          already documented for venkatachala-ep01. Kept clip_cutter.py's
          snap as-is.
  end   = 671.407 (source): CLEAN per clip_cutter.py on the second pass (an
          earlier rough guess of 667.5 snapped mid-clause -- "...the conch
          was the [pause] form of the Lord" -- confirmed bad by a direct
          silencedetect check, so the window was widened and re-run against
          671.38, landing on the real pause between "...the form of the
          Lord." and "In addition, in the chakra...").
Clip duration: 54.8s -- over the 20-45s default band and even the 15-30s
Gen-Z range, but within STYLE.md's 15-60s acceptable range. The chakra
teaching and the conch teaching are one continuous parallel-structure
passage ("not just a chakra that dispels outer darkness, but... the inner
darkness of ignorance" / "the conch was not just for making sound... [it]
was giving knowledge of the truth"); trimming either half would break the
parallel and leave one payoff dangling, the same trade-off already made for
venkatachala-ep01's reels 06/07 (32s clips kept whole over the 15-30s ideal
for the same reason).

This source is 4K (3840x2160) -- scaled down to 1920x1080 BEFORE calling the
shared crop_reframe_filter() (which assumes a 1920-wide input), so crop_x
stays directly comparable to previous sources' derivations.

Title card uses a per-slug override (title_compact.py), NOT the shared
overlays_lib.render_title() -- see build_reel01.py's docstring for the full
reasoning (this speaker has near-zero headroom above his hairline/tilak
mark; shrunk/repositioned for this source only, per explicit user
direction 2026-10-23, shared default untouched).

Uses the shared crop_reframe_filter() from venkatachala-ep01's overlays_lib.py
(imported via sys.path) and tools/reel_numbering.py to assign the reel number.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.join("..", "..", "tools"))
from overlays_lib import render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import next_reel_number, reel_dir, format_reel_number  # noqa: E402

from title_compact import render_title_compact  # noqa: E402

SLUG = "venkatachala-ep06"
CLIP = "clip02_chakra-conch-meaning.mp4"
WM = "../../assets/watermark.png"
TOPIC = "chakra-conch-meaning"

# crop_x=573 derived + verified for THIS source/speaker (see
# docs/CHANGELOG.md) -- same speaker/framing as reel01, re-verified on a
# frame from this clip's own time range before reuse within this slug (NOT
# reused across a different source video).
CROP_X = 573

# Subtitles: spell-checked, clip-relative seconds (clip starts at source
# 616.661s). Auto-caption's "Venkatesa" standardized to "Venkateshwara"
# (the channel's existing canonical spelling, see tools/sanskrit_terms.py)
# except inside the quoted title "Venkatesa Mahatma" is not quoted verbatim
# here -- paraphrased as "the Lord" per STYLE.md's spell-check rule
# (prefer clean readable form over raw auto-caption spelling). Lines kept
# short.
subs = [
    ("As told in the Aditya Purana,", 0.5, 4.3),
    ("the Lord carries the Sudarshana wheel", 4.5, 10.9),
    ("to destroy the darkness of ignorance.", 11.0, 15.3),
    ("It blazes bright as crores of suns \u2014", 15.4, 21.6),
    ("not just dispelling outer darkness,", 21.7, 29.0),
    ("but the darkness within us.", 29.1, 33.1),
    ("And the conch wasn't just for sound \u2014", 33.2, 38.8),
    ("the Aditya Purana says it gives", 38.9, 46.9),
    ("knowledge of truth, the Lord's own form.", 47.0, 54.8),
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    # Compact per-slug title (see title_compact.py) -- the shared
    # overlays_lib.render_title() band collides with this speaker's
    # forehead/tilak mark on this source; not a shared-code change.
    tp = render_title_compact(outdir, "Why the", "Chakra & Conch?")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    # PINNED to the live reel number (04). Numbers are never reused, so
    # next_reel_number() would now return a new number (2026-10-23).
    num = 4
    num_str = format_reel_number(num)
    out_dir = reel_dir(SLUG)
    out_name = f"{SLUG}_{num_str}_{TOPIC}.mp4"
    out_path = os.path.join(out_dir, out_name)

    inputs = ["-i", CLIP, "-i", tp]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    fc = (
        "[0:v]scale=1920:1080[scaled];" +
        crop_reframe_filter(src_label="scaled", crop_x=CROP_X) +
        "[reframed][1:v]overlay=0:0[v0];"
    )
    prev = "v0"
    for i, (_, s, e) in enumerate(sub_paths):
        inp = i + 2
        out = f"vs{i}"
        fc += f"[{prev}][{inp}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out
    wm_idx = 2 + len(sub_paths)
    fc += f"[{prev}][{wm_idx}:v]overlay=0:0[vout]"

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc, "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "30", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED\n", r.stderr[-2000:])
        return False, None
    print("Built", out_path, f"({dur:.1f}s source clip)")
    return True, out_path


if __name__ == "__main__":
    build()

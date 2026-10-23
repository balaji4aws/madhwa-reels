#!/usr/bin/env python3
"""Rebuild Reel 01 (four names) SHORTER, for the Gen-Z/Instagram 15-30s target.

Old reel01 (clip_raw.mp4, source 134.1-153.6s, 19.6s) is replaced with a
tighter cut that starts and ends on clean word boundaries (verified against
source.en.vtt word-level timestamps, see docs/CHANGELOG.md's 2026-10-23
entry):

  start = 136.48  ("Shatananda tells Janaka Maharaja..." -- the word "Shatananda"
                    itself begins here; the previous sentence ends cleanly
                    before this point, confirmed via word-level VTT tags)
  end   = 152.88   (right after "...Kali Yuga, Venkatachala." finishes at
                    152.672s and before the next sentence's "The reason..."
                    begins at 152.879s)

Clip: clip01_names_v2.mp4, 16.4s duration. The four-names content is now
conveyed via single-line subtitles (see names_subs below), not the old
multi-line build-up band -- see docs/CHANGELOG.md's crop/subtitle restyle
entry for why.
"""
import subprocess
from overlays_lib import render_title, render_sub, crop_reframe_filter

CLIP = "clip01_names_v2.mp4"
WM = "../../assets/watermark.png"
OUT = "../../reels/venkatachala-ep01_01_four-names.mp4"

# Subtitles rewritten for the 16.4s clip (clip-relative seconds).
# Content: "Shatananda tells Janaka Maharaja the four names of Venkatachala
# in the four ages. In the Krita Yuga, he was called Vrishabachala, in the
# Treta Yuga, Anjanachala, in the Dwapara Yuga, Seshachala, and in the Kali
# Yuga, Venkatachala."
subs = [
    ("Shatananda tells Janaka Maharaja", 0.2, 3.4),
    ("the four names of Venkatachala", 3.4, 6.1),
    ("across the four Yugas (ages).", 6.1, 7.1),
]

# NOTE on the style change in this rebuild: the old reel 01 showed all four
# Yuga/name pairs as a multi-line band that grew one row at a time
# ("build-up list"). Per the user's explicit preference ("I always like a
# single-line subtitle style rather than build-up list that grows too
# big"), that band is replaced with four single-line render_sub cues below
# -- same four-names content, same clip-relative reveal timing the old
# band used (NAME_REVEAL_T 7.6/9.8/11.5/13.4), just one line on screen at a
# time, in the same style/position as every other reel's subtitles.
names_subs = [
    ("Krita Yuga \u2014 Vrishabhachala", 7.6, 9.8),
    ("Treta Yuga \u2014 Anjanachala", 9.8, 11.5),
    ("Dwapara Yuga \u2014 Seshachala", 11.5, 13.4),
    ("Kali Yuga \u2014 Venkatachala", 13.4, 16.2),
]

if __name__ == "__main__":
    render_title(".", "The 4 Names of", "Venkatachala")
    all_subs = subs + names_subs
    sub_paths = [(render_sub(".", i, t), s, e) for i, (t, s, e) in enumerate(all_subs, 1)]

    # inputs: 0 clip, 1 title, 2..(1+len(all_subs)) subs, last wm
    inputs = ["-i", CLIP, "-i", "ov_title.png"]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    fc = (
        crop_reframe_filter() +
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
        "-movflags", "+faststart", OUT,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED\n", r.stderr[-1500:])
    else:
        print("Built", OUT)

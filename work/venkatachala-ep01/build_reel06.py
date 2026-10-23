#!/usr/bin/env python3
"""Build Reel 06 — "The sinner who was purified" (Madhava / Kapila Tirtha).

Short-form (Gen-Z/Instagram target 15-30s) reel. Cut boundaries were produced
by tools/clip_cutter.py (see cut_report_06.json) and then manually verified /
adjusted against source.en.vtt per docs/STYLE.md's "Cut placement" rule,
since both boundaries came back `review-manually`. See docs/CHANGELOG.md
for the full reasoning.

Clip source seconds used for the final cut (NOT the raw tool snap):
  start = 1135.05  (small lead-in before the cue "Earlier, a Brahmin named
                     Madhava..." begins at 1135.35 -- confirmed continuous
                     speech right after, no silence found at 1134.5-1136.5)
  end   = 1167.72  (the tool's own snap; re-verified: it lands on the real
                     ~0.97s pause right after "...making a pilgrimage" and
                     before the following "in this Kali Yuga, the work of..."
                     clause -- a genuine mid-cue pause the coarse run-on VTT
                     cue just doesn't expose as a formal boundary)
Clip duration: 32.67s (trim at a sentence boundary close to the 15-30s target,
slightly over because the payoff line needs to land whole).
"""
import os
import subprocess
from overlays_lib import render_title, render_sub, crop_reframe_filter

CLIP = "clip06_sinner-purified.mp4"
WM = "../../assets/watermark.png"
OUT = "../../reels/venkatachala-ep01_06_sinner-purified.mp4"

# Subtitles: spell-checked / cleaned from source.en.vtt, clip-relative seconds
# (clip starts at source 1135.05s). Lines kept short (4-7 words).
subs = [
    ("A Brahmin named Madhava", 0.3, 3.2),
    ("once committed great sins", 3.2, 6.9),
    ("and lost his Brahminhood.", 6.9, 9.4),
    ("But after this pilgrimage", 9.6, 13.0),
    ("to Venkatachala, offering prayers", 13.0, 16.6),
    ("to his ancestors at Kapila Tirtha,", 16.6, 20.5),
    ("Venkatachala is said to have", 29.2, 31.0),
    ("washed away all his sins.", 31.0, 32.6),
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    tp = render_title(outdir, "The sinner who was", "purified")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    inputs = ["-i", CLIP, "-i", tp]
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
        print("FAILED\n", r.stderr[-2000:])
        return False
    print("Built", OUT, f"({dur:.1f}s source clip)")
    return True


if __name__ == "__main__":
    build()

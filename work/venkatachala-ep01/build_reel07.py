#!/usr/bin/env python3
"""Build Reel 07 — "Lose your ego" (closing moral + dedication shloka).

Short-form (Gen-Z/Instagram target 15-30s) reel. Cut boundaries were produced
by tools/clip_cutter.py (see cut_report_07.json). The start flagged
`review-manually` and was manually re-verified against source.en.vtt and a
direct silencedetect pass per docs/STYLE.md's "Cut placement" rule; the
end came back `clean` and was used as-is. See docs/CHANGELOG.md for the
full reasoning.

Clip source seconds used for the final cut (the tool's own snap, both ends):
  start = 1251.157  (tool snap; review-manually flag was a false positive —
                      it lands inside the VTT's displayed cue for "Therefore,
                      it is called Venkatachala." (1250.149-1252.95), but the
                      actual spoken words of that sentence finish ~1250.15s;
                      the cue's trailing display window overruns the real
                      speech, same run-on-cue slop already documented for
                      reel06's end boundary. A direct silencedetect sweep at
                      -18/-20/-25/-30dB confirms the real gap is the quiet
                      stretch 1250.93-1251.39s, which the tool snapped to
                      the midpoint of (1251.157) -- a genuine inter-sentence
                      pause, clear of speech)
  end   = 1283.527  (tool's own "clean" snap; kept as-is, no adjustment)
Clip duration: 32.4s (slightly over the 15-30s Gen-Z target, same as reel06 --
  the closing shloka needs to land whole for the payoff to work).
"""
import os
import subprocess
from overlays_lib import render_title, render_sub, crop_reframe_filter

CLIP = "clip07_lose-your-ego.mp4"
WM = "../../assets/watermark.png"
OUT = "../../reels/venkatachala-ep01_07_lose-your-ego.mp4"

# Subtitles: spell-checked / cleaned from source.en.vtt, clip-relative seconds
# (clip starts at source 1251.157s). Lines kept short (4-7 words). The VTT has
# an ASR gap between "become" (9.48s) and "pure" (18.12s) -- speech continues
# there (confirmed by silencedetect, not one long silence) but the auto-
# caption has no English text for it, so no subtitle is shown in that window,
# same pattern as reel06's untranscribed stretch.
subs = [
    ("We should make such", 1.6, 4.1),
    ("a special approach -", 4.1, 5.7),
    ("lose all our sins,", 5.7, 7.9),
    ("abandon our ego,", 7.9, 9.3),
    ("and become pure", 9.3, 17.8),
    ("by rendering special service", 18.0, 19.8),
    ("to the Supreme Lord,", 19.8, 20.5),
    ("the Supreme Lord of the Wind,", 20.5, 21.6),
    ("with all our dedication.", 21.6, 24.5),
    ("The message from these four names:", 24.6, 28.4),
    ("Haraye Namah,", 28.4, 29.3),
    ("Shri Krishna Arpanamastu.", 29.3, 32.3),
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    tp = render_title(outdir, "Lose Your", "Ego")

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

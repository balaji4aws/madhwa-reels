#!/usr/bin/env python3
"""Build Reel 02 (slug: utsarjana-upakarma) -- "What is Utsarjana & Upakarma?"

Source: "ಏನಿದು ಉತ್ಸರ್ಜನ ಉಪಾಕರ್ಮ? / What is Utsarjana & Upakarma?"
(Sri Uttaradi Math Adhyatmavani). Full source downloaded (1698.9s / 28.3 min
-- NOT trimmed at download time, per house rule).

Cut boundaries verified by hand with ffmpeg silencedetect (tools/clip_cutter.py
flagged both review-manually on this source's coarse run-on VTT cues, same
known pattern as venkatachala-ep01 -- see docs/CHANGELOG.md):
  start = 20.2   (source 20.2s): clean 2.38s pause (17.3-20.23s absolute)
                  right after the opening Sanskrit invocation, before the
                  English narration begins.
  end   = 87.8   (source 87.8s): clean 2.38s pause (85.55-87.93s absolute)
                  right after "...the foundation of our Sanatan Dharma is
                  the Vedas" completes, before the next sentence begins.
Clip duration: 67.6s (slightly over the 60s Short soft-limit -- the "let
go / accept -> Vedas as foundation" thought doesn't resolve cleanly any
shorter without cutting mid-argument; check_reel.py WARNs, doesn't FAIL,
on >60s, consistent with how this project already treats the limit).

Uses the shared crop_reframe_filter() from venkatachala-ep01's overlays_lib.py
(imported via sys.path -- see note below) and tools/reel_numbering.py to
assign the reel number instead of hardcoding it.
"""
import os
import sys
import subprocess

# Reuse the shared overlay renderer + fixed crop function from the
# venkatachala-ep01 work folder (it's genuinely source-agnostic -- takes no
# slug-specific state) rather than duplicating it for this new slug.
sys.path.insert(0, os.path.join("..", "venkatachala-ep01"))
from overlays_lib import render_title, render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import next_reel_number, reel_dir, format_reel_number  # noqa: E402

SLUG = "utsarjana-upakarma"
CLIP = "clip02_let-go-accept.mp4"
WM = "../../assets/watermark.png"
TOPIC = "let-go-accept"

# Subtitles: spell-checked, clip-relative seconds (clip starts at source
# 20.2s). "Utsanjana" in the raw auto-caption corrected to "Utsarjana"
# (matches the source video's own title spelling). Lines kept short.
subs = [
    ("A festival in the month of Shravan \u2014", 0.3, 4.5),
    ("the Janivara festival.", 4.5, 6.8),
    ("What is Utsarjana and Upakarma?", 6.8, 9.5),
    ("Utsarjana means to let go,", 9.6, 13.0),
    ("Upakarma means to accept.", 30.2, 33.0),
    ("But let go of what,", 44.6, 46.8),
    ("and accept what?", 46.8, 48.8),
    ("Let go of the old Vedas,", 50.5, 53.5),
    ("and take up the Vedas anew.", 53.5, 56.5),
    ("The Vedas are the very source", 62.0, 64.5),
    ("and foundation of Sanatana Dharma.", 64.5, 66.9),
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    tp = render_title(outdir, "What is", "Utsarjana & Upakarma?")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    # Auto-incrementing reel number for this slug -- never hardcoded.
    num = next_reel_number(SLUG)
    num_str = format_reel_number(num)
    out_dir = reel_dir(SLUG)
    out_name = f"{SLUG}_{num_str}_{TOPIC}.mp4"
    out_path = os.path.join(out_dir, out_name)

    inputs = ["-i", CLIP, "-i", tp]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    # crop_x=488 verified against this source's own frames (speaker's face
    # center sits at x~920 on the 1920-wide source; 920 - 864//2 = 488) --
    # see docs/CHANGELOG.md. Do NOT reuse this number for a different
    # source video without re-deriving it.
    fc = (
        crop_reframe_filter(crop_x=488) +
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

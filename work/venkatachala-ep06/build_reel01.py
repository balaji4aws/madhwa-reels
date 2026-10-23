#!/usr/bin/env python3
"""Build Reel 01 (slug: venkatachala-ep06) -- "No friend like a mother"

Source: "Glory of Venkatachala | Ep - 06 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri
Satyatmateertha Shripadangalavaru" (Sri Uttaradi Math Adhyatmavani), full
discourse 2887.4s (~48.1 min) -- NOT trimmed at download time, per house rule.

Moment: Dharmadevi (Dharani Devi in disguise) wakes Padmavati and quotes the
verse "Nachamatrasamam Mitram Putrinam Asthi Nandini" ("there is no friend
like a mother for one's children"), then the speaker generalises it into a
teaching about parents and children exchanging love and trust. Self-contained
hook ("there is no friend like a mother") + payoff (the generalised lesson),
no dependency on earlier/later material in the discourse.

Cut boundaries verified with tools/clip_cutter.py (see cut_report_01.json) +
manual review (both boundaries landed clean/plausible on direct silencedetect
checks, cross-read against the VTT text -- see docs/CHANGELOG.md for the
full writeup):
  start = 300.973 (source): CLEAN per clip_cutter.py -- pause right after
          "...Srinivas went outside," before "Dharani Devi came directly to
          Padmavati's room..." begins the new scene.
  end   = 345.088 (source): flagged review-manually (lands inside a coarse
          run-on VTT cue "children should be the same as for parents. There
          is", 340.72-345.43s) -- confirmed by direct ffmpeg silencedetect
          (genuine ~1.07s pause at 344.55-345.62s) and by reading the cue's
          own word order: the pause sits right after "...for parents." and
          before "There is love, of course..." -- a real sentence break the
          coarse cue grouping doesn't expose as a formal boundary. Same
          false-positive pattern already documented for venkatachala-ep01's
          reels 06/07. Kept clip_cutter.py's snap as-is.
Clip duration: 44.2s -- within the 20-45s default target band.

This source is 4K (3840x2160), unlike venkatachala-ep01/utsarjana-upakarma
(1920x1080) -- scaled down to 1920x1080 BEFORE calling the shared
crop_reframe_filter() (which assumes a 1920-wide input), so crop_x stays
directly comparable to previous sources' derivations.

Title card uses a per-slug override (title_compact.py), NOT the shared
overlays_lib.render_title(): this speaker sits with near-zero headroom
above his hairline/tilak mark, so the shared title band (tuned for
venkatachala-ep01's framing) collided with his forehead. Per explicit user
direction (2026-10-23), the title was shrunk/repositioned for this source
only -- the shared default in overlays_lib.py is untouched, so
venkatachala-ep01's reels are unaffected. Verified against a real rendered
frame before use -- see docs/CHANGELOG.md.

Uses the shared crop_reframe_filter() from venkatachala-ep01's overlays_lib.py
(imported via sys.path, same pattern as utsarjana-upakarma/build_reel02.py)
and tools/reel_numbering.py to assign the reel number instead of hardcoding it.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.join("..", "venkatachala-ep01"))
from overlays_lib import render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import next_reel_number, reel_dir, format_reel_number  # noqa: E402

from title_compact import render_title_compact  # noqa: E402

SLUG = "venkatachala-ep06"
CLIP = "clip01_no-friend-like-mother.mp4"
WM = "../../assets/watermark.png"
TOPIC = "no-friend-like-mother"

# crop_x=573 derived + verified for THIS source/speaker (see
# docs/CHANGELOG.md) -- NOT reused from any other slug. Source is 4K, so the
# filter chain scales 3840x2160 -> 1920x1080 first; crop_x is in that
# 1920-wide coordinate space, matching how it was measured on the probe frame.
CROP_X = 573

# Subtitles: spell-checked, clip-relative seconds (clip starts at source
# 300.973s). "Nachamatrasamam Mitram Putrinam Nandini" is a direct Sanskrit
# quote transcribed as heard (not a channel proper noun to standardize --
# see check_reel.py's slug-specific allowlist note). Lines kept short.
subs = [
    ("Dharmadevi came to Padmavati's room", 0.3, 4.0),
    ("and gently woke her up.", 4.3, 8.4),
    ("\u201cDo not hide anything,\u201d", 8.6, 13.8),
    ("Nachamatrasamam Mitram Putrinam Nandini \u2014", 13.9, 18.8),
    ("there is no friend like a mother.", 19.0, 23.8),
    ("Whatever is on your mind,", 24.0, 27.3),
    ("say it without hesitation.", 27.5, 31.0),
    ("This is a great message from the Purana:", 31.2, 35.8),
    ("the love of parents for children", 36.0, 39.7),
    ("should be matched with love in return.", 39.9, 44.1),
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
    tp = render_title_compact(outdir, "There's No Friend", "Like a Mother")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    num = next_reel_number(SLUG)
    num_str = format_reel_number(num)
    out_dir = reel_dir(SLUG)
    out_name = f"{SLUG}_{num_str}_{TOPIC}.mp4"
    out_path = os.path.join(out_dir, out_name)

    inputs = ["-i", CLIP, "-i", tp]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    # Scale 4K source down to 1920x1080 BEFORE the shared crop filter (which
    # assumes a 1920-wide input) -- see module docstring.
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

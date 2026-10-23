#!/usr/bin/env python3
"""Build Reel 01 (slug: venkatachala-ep07) -- "God does all the work"

Source: "Glory of Venkatachala | Ep - 07 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri
Satyatmateertha Shripadangalavaru" (Sri Uttaradi Math Adhyatmavani), full
discourse 3474.5s (~57.9 min), https://www.youtube.com/watch?v=9IDCabMthdQ
-- downloaded in FULL (never trimmed at download time, per house rule),
duration verified against the published ~3475s before use.

Moment (source 87.9-112.5s, 24.6s): a self-contained "did you know"
teaching that opens the talk -- everything good that comes to a living
being (praise, fame, success, even basic humanity) is God's doing and
God's mercy, not the being's own achievement. Hook ("who really gets the
credit for your success?") + payoff (it is all God's grace, shown by how
the Lord himself honours Bakula). Short, punchy, Gen-Z-paced (24.6s, in
the 15-30s band) -- one hook, one payoff, no multi-part list. Stands alone:
the surrounding narrative isn't needed to grasp the teaching.

Cut boundaries (source seconds; clip starts at 87.9s):
  start = 87.9. tools/clip_cutter.py (cut_report_cand1.json) reported this
          boundary CLEAN (snapped 87.936s, inside_cue=False) -- a genuine
          pause sits just before the first word "God" (karaoke word-tag
          88.559s), ~0.66s of lead-in before speech starts.
  end   = 112.5. clip_cutter.py also reported CLEAN here (snapped 113.435s,
          inside_cue=False). Manually confirmed against the VTT word-tags:
          the payoff sentence's last word "him." is spoken at 112.396s and
          the clip ends at 112.5s, just after it -- BEFORE "Immediately,"
          (112.56s), which begins a new, unrelated scene beat. No mid-word
          truncation.

This source is 4K (3840x2160) -- scaled to 1920x1080 BEFORE the shared
crop_reframe_filter() (which assumes 1920-wide input), keeping crop_x
directly comparable to previous sources' derivations.

crop_x=523 was FRESHLY DERIVED for THIS source (NOT reused from ep06's 573
-- the task required a fresh derivation and the two differ): grid-overlay
on a 1920-scaled probe frame put the speaker's face-center at x~955, so
crop_x = 955 - 864//2 = 523. Verified by rendering the crop against three
real probe frames (10%/50%/90% of the talk) before use -- speaker centred,
no off-centre artifact. See work/build-notes.md.

Title card uses the per-slug compact override (title_compact.py) -- this
speaker has the SAME near-zero-headroom-above-the-tilak problem as ep06
(confirmed proactively: compositing the shared render_title() band over a
real crop_x=523 frame collided with the tilak), so the compact title is
built for this slug too. The shared overlays_lib.render_title() default is
NOT changed.

FADE (the "abrupt cuts" fix, applied to ALL 6 clips in this task): a 0.2s
video fade-to/from-black + matching audio afade, applied to the FINAL
COMPOSITED frame ([vout], after title/subtitle/watermark overlays) so the
whole frame fades as one unit -- NOT to the raw clip before compositing
(which would leave the title/watermark at full opacity over a black
background; see venkatachala-ep06/build_reel03.py and work/build-notes.md
for that overlay-desync bug and why the fade goes at the end of the chain).
This is a brand-new build, but the jump-cut-feel check still applies: the
finished clip's first/last ~1-2s were inspected directly before declaring
it done.

Uses the shared crop_reframe_filter() from venkatachala-ep01's
overlays_lib.py and tools/reel_numbering.py for the reel number.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.join("..", "..", "tools"))
from overlays_lib import render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import reel_dir, format_reel_number  # noqa: E402

from title_compact import render_title_compact  # noqa: E402

SLUG = "venkatachala-ep07"
CLIP = "clip01_god-does-all-work.mp4"
WM = "../../assets/watermark.png"
TOPIC = "god-does-all-work"
CROP_X = 523
FADE_DURATION = 0.2
# Number 01 was assigned by tools/reel_numbering.py's next_reel_number()
# on this slug's FIRST build (fresh slug -> started at 01, per the
# no-hardcoded-start rule). It is PINNED here afterwards so re-running this
# script to tweak a subtitle doesn't re-increment to 05/06 (reels 01-04
# already exist on disk). See work/build-notes.md.
REEL_NUM = 1

# Subtitles: spell-checked, PARAPHRASED (not a verbatim VTT quote -- the
# source captions are YouTube's machine paraphrase of Kannada speech, per
# STYLE.md's transcript-honesty rule), single line each, clip-relative
# seconds (clip starts at source 87.9s). Proper nouns: "Bakula" is a plain
# dictionary word; no new/uncertain Sanskrit spelling is introduced here.
subs = [
    ("God does all the work.", 0.7, 3.6),
    ("Praise, fame, success, money \u2014", 3.9, 8.4),
    ("everything the living being receives", 8.5, 12.3),
    ("is the mercy of God.", 12.4, 15.0),
    ("Even our very humanity", 15.5, 18.0),
    ("is a gift the Supreme Lord gives.", 18.1, 21.2),
    ("He honors us, and blesses us \u2014", 21.3, 23.4),
    ("the credit was never ours.", 23.5, 24.6),
]

TITLE_LEAD = "Who Really Gets"
TITLE_MAIN = "the Credit?"


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    tp = render_title_compact(outdir, TITLE_LEAD, TITLE_MAIN)
    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e)
                 for i, (t, s, e) in enumerate(subs, 1)]

    num_str = format_reel_number(REEL_NUM)
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
    fc += f"[{prev}][{wm_idx}:v]overlay=0:0[vcomposited];"
    # Fade applied to the FULLY COMPOSITED frame so title/subtitle/watermark
    # fade together with the background as one unit (see module docstring).
    fade_out_start = round(dur - FADE_DURATION, 3)
    fc += (
        f"[vcomposited]fade=t=in:st=0:d={FADE_DURATION},"
        f"fade=t=out:st={fade_out_start}:d={FADE_DURATION}[vout]"
    )

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc, "-map", "[vout]", "-map", "0:a",
        "-af", f"afade=t=in:st=0:d={FADE_DURATION},"
               f"afade=t=out:st={fade_out_start}:d={FADE_DURATION}",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "30", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED\n", r.stderr[-2000:])
        return False, None
    print("Built", out_path, f"({dur:.1f}s)")
    return True, out_path


if __name__ == "__main__":
    build()

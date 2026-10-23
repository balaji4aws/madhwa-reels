#!/usr/bin/env python3
"""Build Reel 04 (slug: venkatachala-ep07) -- closing moral: offer humbly

Source: "Glory of Venkatachala | Ep - 07" by Sri Satyatmateertha
Shripadangalavaru (Sri Uttaradi Math Adhyatmavani), full discourse
3474.5s, https://www.youtube.com/watch?v=9IDCabMthdQ. See build_reel01.py
for the shared crop_x/title/fade rationale.

Moment (source 3272.0-3326.3s, 54.3s): the discourse's CLOSING MORAL plus
its traditional Sanskrit dedication -- exactly the "short summary line +
dedication shloka" recurring candidate category STYLE.md says to look for
near the end of a talk. The teaching: what greater blessing do we need
than the Lord taking us toward liberation? And how to live it -- when you
host or give, do not arrogantly say "Take it"; humbly say "I have done
only this much, to the extent you wished." It closes on the dedication
"Haraye Namah, Shri Krishna Arpanamastu" (offering the act to God). Hook
(what more could we ask for?) + payoff (give humbly, dedicate it to God).
Self-contained; 54.3s -- over the 20-45s default band but within STYLE.md's
15-60s acceptable range, kept whole so the moral and its dedication both
land (same complete-thought trade-off as ep06 reel06).

Cut boundaries (clip starts at source 3272.3s):
  start = 3272.3. clip_cutter.py (cut_report_cand4.json) flagged
          REVIEW-MANUALLY. Resolved by hand against the VTT word-tags: the
          preceding fragment "...taking us to salvation and saying," has no
          clean standalone subject (the cues before it, 54:09-54:30, carry
          no transcribed text), so the clip deliberately OPENS on the
          quoted line itself -- "What greater blessing do we need than
          this?" -- whose first word "What" begins at word-tag 3272.48s. A
          short gap sits at ~3272.49-3272.60s right at that word onset; the
          clip starts at 3272.3s, ~0.18s before "What", so speech is not
          clipped mid-word. (An earlier pass started at 3272.0s, which
          began mid-word inside "...salvation and saying" -- caught by the
          odd-cut check + a direct word-tag read, and corrected here.)
  end   = 3326.3. clip_cutter.py flagged REVIEW-MANUALLY. Resolved by hand:
          the dedication "...Shri Krishna Arpanamastu" cue runs to 3326.79s
          and a direct silencedetect pass found a pause at ~3325.65-3326.10s
          as it tails off; the clip ends at 3326.3s, i.e. right at the end
          of the dedication line and BEFORE the long "Rama Rama Rama..."
          chant that follows (a repeated devotional refrain with no
          teaching content, deliberately not included). No mid-word
          truncation of the dedication.

TRANSLITERATION NOTE (GUARDRAILS: never guess a Sanskrit proper noun):
the auto-caption renders the opening dedication word as "Hare Namah". The
channel's confirmed, already-standardised spelling for this traditional
closing phrase is "Haraye Namah" (tools/sanskrit_terms.py). "Hare" reads
as the same known phrase rendered loosely by the auto-captioner, so the
subtitle uses the CONFIRMED shared spelling "Haraye Namah" -- this is
using an already-confirmed term from the shared list, NOT inventing a new
spelling. "Arpanamastu" is likewise already confirmed in sanskrit_terms.py.
No new or uncertain proper noun is introduced by this reel.

crop_x=523 (freshly derived, see build_reel01.py). Per-slug compact title.
0.2s fade on the final composited frame + matching audio afade.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.join("..", "venkatachala-ep01"))
from overlays_lib import render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import reel_dir, format_reel_number  # noqa: E402

from title_compact import render_title_compact  # noqa: E402

SLUG = "venkatachala-ep07"
CLIP = "clip04_credit-grace-not-self.mp4"
WM = "../../assets/watermark.png"
TOPIC = "give-humbly-dedicate-to-god"
CROP_X = 523
FADE_DURATION = 0.2
# Number 04 assigned by next_reel_number() on the first build; PINNED
# afterwards to prevent re-increment on rebuild (see build_reel01.py).
REEL_NUM = 4

# Subtitles: spell-checked, PARAPHRASED, single line, clip-relative seconds
# (clip starts at source 3272.3s). "Haraye Namah" and "Arpanamastu" are the
# CONFIRMED shared spellings (tools/sanskrit_terms.py), used in place of the
# auto-caption's loose "Hare Namah" rather than guessing a new spelling.
subs = [
    ("What greater blessing do we need", 0.5, 4.2),
    ("than the Lord leading us to liberation?", 4.3, 9.2),
    ("We are all blessed. This is how it should be.", 9.3, 14.7),
    ("The Lord is always present in your home.", 16.2, 20.7),
    ("So when you give, never say proudly:", 23.7, 28.2),
    ("\u201cTake it.\u201d", 28.3, 30.7),
    ("Say humbly instead:", 31.2, 34.2),
    ("\u201cI have done only this much,", 34.3, 38.2),
    ("to the extent that you wished.\u201d", 38.3, 42.7),
    ("Haraye Namah \u2014 Shri Krishna Arpanamastu.", 45.7, 54.0),
]

TITLE_LEAD = "Give Humbly,"
TITLE_MAIN = "Offer It to God"


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

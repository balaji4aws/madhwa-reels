#!/usr/bin/env python3
"""Build Reel 02 (slug: venkatachala-ep07) -- "The God who got down to walk"

Source: "Glory of Venkatachala | Ep - 07" by Sri Satyatmateertha
Shripadangalavaru (Sri Uttaradi Math Adhyatmavani), full discourse
3474.5s, https://www.youtube.com/watch?v=9IDCabMthdQ (downloaded in full,
duration verified). See build_reel01.py for the shared crop_x/title/fade
rationale that applies to all four ep07 reels.

Moment (source 1055.2-1081.9s, 26.7s): when the Supreme Lord hears that
Brahma is coming, He gets down from His own swan chariot and walks to
meet him; Brahma prostrates, the Lord raises him up and embraces him, and
they stand in silence for "two muhurtas" (the discourse glosses this as a
long, wordless embrace). Hook (God Himself steps down to greet His
devotee) + payoff (the wordless embrace / silence -- devotion beyond
words). Self-contained; a tight 26.7s Gen-Z-paced moment (15-30s band).

Cut boundaries (clip starts at source 1055.2s):
  start = 1055.2. clip_cutter.py (cut_report_cand2.json) flagged this
          REVIEW-MANUALLY (coarse run-on cue). Resolved by hand against the
          VTT word-tags: the prior sentence ("...Bhumi.") closes and the
          new sentence "When he heard the news..." begins at word-tag
          1055.265s. The clip starts at 1055.2s, i.e. right at that
          sentence start -- a clean caption-boundary cut; the speaker runs
          on from the previous clause here without an audible breath (a
          documented pattern on these sources: the sentence boundary is
          real even when no silence gap aligns with it), so placement is
          certified by the caption boundary, not by a silence gap, exactly
          as STYLE.md/clip_cutter.py prescribe.
  end   = 1081.9. clip_cutter.py flagged REVIEW-MANUALLY. Resolved by hand:
          the payoff line "...nine minutes of silence." ends at word-tag
          1081.27s, and a direct silencedetect pass found a genuine
          ~0.46s pause at 1081.63-1082.09s right after it, before the next
          (and noticeably garbled) "Lord Brahma is looking at the face of
          Lord Brahma" line -- which is both a new beat AND an auto-caption
          glitch, so it is deliberately excluded. Clip end 1081.9s sits
          inside that post-sentence pause.

crop_x=523 (freshly derived for this source, see build_reel01.py).
Per-slug compact title (title_compact.py). 0.2s fade on the final
composited frame + matching audio afade (see build_reel01.py docstring).
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
CLIP = "clip02_brahma-walks-to-god.mp4"
WM = "../../assets/watermark.png"
TOPIC = "god-steps-down-for-devotee"
CROP_X = 523
FADE_DURATION = 0.2
# Number 02 assigned by next_reel_number() on the first build; PINNED
# afterwards to prevent re-increment on rebuild (see build_reel01.py).
REEL_NUM = 2

# Subtitles: spell-checked, PARAPHRASED, single line, clip-relative seconds
# (clip starts at source 1055.2s). "Brahma" is a plain dictionary word;
# "muhurtas" is paraphrased away in favour of the discourse's own gloss
# ("a long, wordless silence") so no uncertain transliteration is burned
# in. No new/uncertain Sanskrit proper noun introduced here.
subs = [
    ("The Lord heard His devotee was coming.", 0.6, 4.3),
    ("He stepped down from His own chariot", 4.4, 8.0),
    ("and walked out to meet him.", 8.1, 11.0),
    ("Brahma bowed low before Him \u2014", 13.5, 17.5),
    ("the Lord raised him up", 17.6, 20.0),
    ("and embraced him tightly.", 20.1, 22.8),
    ("They stood in a long, wordless silence.", 23.0, 26.7),
]

TITLE_LEAD = "God Steps Down"
TITLE_MAIN = "for His Devotee"


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

#!/usr/bin/env python3
"""Build Reel 03 (slug: venkatachala-ep07) -- "Vishwakarma's humility"

Source: "Glory of Venkatachala | Ep - 07" by Sri Satyatmateertha
Shripadangalavaru (Sri Uttaradi Math Adhyatmavani), full discourse
3474.5s, https://www.youtube.com/watch?v=9IDCabMthdQ. See build_reel01.py
for the shared crop_x/title/fade rationale.

Moment (source 1306.6-1356.2s, 49.6s): Indra snaps at Vishwakarma, "Remove
him from my work!" Instead of defending himself, Vishwakarma answers with
pure humility: a great deity though he is, he says he has no merit before
them, that even an ordinary person's raised eyebrow is enough to make him
look at himself, and that if something is wrong with him he should simply
correct himself and walk the right path. The Lord then accepts this and
sends him off to build the wedding assembly. Hook (a famous craftsman-god
publicly accused) + payoff (he responds with self-correction, not
defensiveness). Self-contained; 49.6s -- over the 20-45s default band but
inside STYLE.md's 15-60s acceptable range, kept whole because the humility
arc (accusation -> humble reply -> the Lord's acceptance) needs both ends
to land, the same complete-thought trade-off already accepted for ep06
reel06 (55.2s).

Cut boundaries (clip starts at source 1306.6s):
  start = 1306.6. clip_cutter.py (cut_report_cand3.json) flagged
          REVIEW-MANUALLY. Resolved by hand: the hook sentence "Indra said,
          'Remove him from my work.'" begins at word-tag 1306.943s; the
          clip starts at 1306.6s, ~0.34s before it, at the sentence
          boundary (the prior cue "...a little angry with Vishwakarma" has
          already closed). Clean sentence-start cut.
  end   = 1356.2. clip_cutter.py flagged REVIEW-MANUALLY (snapped 1355.267s).
          Resolved by hand: the Lord's closing line "...go and build the
          assembly right now." ends at word-tag 1355.909s, and a direct
          silencedetect pass found a pause at ~1355.04-1355.57s and again
          after the line; clip end 1356.2s sits just past the full
          sentence, before the next (unrelated) "Indra immediately made him
          build the assembly" narration. No mid-word truncation.

crop_x=523 (freshly derived, see build_reel01.py). Per-slug compact title.
0.2s fade on the final composited frame + matching audio afade.
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
CLIP = "clip03_vishwakarma-humility.mp4"
WM = "../../assets/watermark.png"
TOPIC = "vishwakarma-humility"
CROP_X = 523
FADE_DURATION = 0.2
# Number 03 assigned by next_reel_number() on the first build; PINNED
# afterwards to prevent re-increment on rebuild (see build_reel01.py).
REEL_NUM = 3

# Subtitles: spell-checked, PARAPHRASED, single line, clip-relative seconds
# (clip starts at source 1306.6s). Proper nouns used: "Indra" (plain
# dictionary word) and "Vishwakarma" (standard, single-spelling Sanskrit
# proper noun, now in tools/sanskrit_terms.py). No uncertain/invented
# spelling burned in.
subs = [
    ("\u201cRemove him from my work!\u201d", 0.6, 3.6),
    ("Indra snapped at Vishwakarma.", 3.7, 7.0),
    ("But Vishwakarma did not defend himself.", 8.0, 12.5),
    ("\u201cWhat did I do wrong?", 12.6, 15.5),
    ("There is no reason to be so angry with me.", 15.6, 20.5),
    ("I have no merit before you.", 22.0, 26.0),
    ("Even an ordinary man's raised eyebrow", 26.1, 30.5),
    ("is enough to make me look at myself.", 30.6, 35.0),
    ("I should simply correct myself,", 36.0, 40.0),
    ("and walk the right path.\u201d", 40.1, 43.5),
    ("And the Lord blessed his humility.", 45.0, 49.6),
]

TITLE_LEAD = "Accused in Public,"
TITLE_MAIN = "He Chose Humility"


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

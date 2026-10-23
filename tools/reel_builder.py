#!/usr/bin/env python3
"""Shared, data-driven reel builder.

Replaces copy-pasting a build_reelNN.py per reel. Each source keeps ONE spec
file, work/<slug>/reels.json, describing every reel cut from it (cut points,
title, subtitles, caption text). This script turns a spec entry into a
finished reel, following docs/STYLE.md + docs/WORKFLOW.md:

  1. cut the raw clip from sources/<slug>/source.mp4 (re-encoded, frame-accurate)
  2. reframe to 1080x1920 with tools/overlays_lib.crop_reframe_filter(crop_x)
  3. compact title card at the top (clears speakers with no headroom)
  4. single-line spell-checked subtitles at SUB_Y (tools/overlays_lib.render_sub)
  5. watermark assets/watermark.png (channel URL + brand icon)
  6. 0.2s fade in/out on the FINAL composited picture + matching audio afade
  7. write reels/<slug>/<slug>_NN_<topic>.mp4 + .caption.txt
  8. write work/<slug>/subs_NN.json (for check_reel.py) and report the
     finished file's real leading/trailing quiet (the "abrupt ending" check)

Run with the Pillow-enabled interpreter, from the project folder:
    /Users/venkyb/envs/bie-work/bin/python3 tools/reel_builder.py <slug> [NN ...]
(no NN = build every reel in the spec).

reels.json shape:
{
  "slug": "...", "crop_x": 548,
  "source_title": "...", "source_url": "...",
  "reels": [
    {"num": 7, "topic": "kebab-topic", "start": 1946.25, "end": 1969.90,
     "title_lead": "A Prayer for", "title_main": "Steady Devotion",
     "subs": [["text", start_s, end_s], ...],      # clip-relative seconds
     "caption": {"title": "...", "description": "...", "hashtags": "..."}}
  ]
}
Reel numbers are assigned ONCE (tools/reel_numbering.next_reel_number) when a
reel is added to the spec, then stay fixed there -- never renumbered.
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from overlays_lib import (render_sub, crop_reframe_filter, _font, _wrap,  # noqa: E402
                          FONT_BOLD, W, H, ACCENT, WHITE)
from reel_numbering import reel_dir, format_reel_number  # noqa: E402

FADE = 0.2            # owner-confirmed cut fade (docs/STYLE.md, "Cut placement")
MAX_LEN = 60.0        # strict rule: every reel must be UNDER 60s
WATERMARK = os.path.join(ROOT, "assets", "watermark.png")
FONT_GEO_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"


def render_title_compact(outdir, lead, main):
    """Compact title band hugging the top edge (band_top=8, 26/34px Georgia
    Bold). Same verified geometry as ep06/ep07's title_compact.py -- these
    speakers sit with near-zero headroom, so the default band hits the tilak."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_lead, f_main = ImageFont.truetype(FONT_GEO_BOLD, 26), ImageFont.truetype(FONT_GEO_BOLD, 34)
    band_top, line_h = 8, 38
    d.rounded_rectangle([70, band_top, W - 70, band_top + 20 + 2 * line_h],
                        radius=16, fill=(0, 0, 0, 135))
    for text, fnt, y, fill in ((lead, f_lead, band_top + 10, WHITE),
                               (main, f_main, band_top + 10 + line_h, ACCENT)):
        bb = d.textbbox((0, 0), text, font=fnt)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x + 2, y + 2), text, font=fnt, fill=(0, 0, 0, 190))
        d.text((x, y), text, font=fnt, fill=fill)
    path = os.path.join(outdir, "ov_title.png")
    img.save(path)
    return path


def sub_line_count(text):
    d = ImageDraw.Draw(Image.new("RGBA", (W, 200)))
    return len(_wrap(text, _font(FONT_BOLD, 46), d, W - 150))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1500:])
    return r


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", path]).stdout
    return float(out.strip())


def edge_quiet(path, dur):
    """Real quiet at the head and tail of the FINISHED file (silencedetect on
    the delivered reel, not the source -- see STYLE.md verification #4)."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          "silencedetect=noise=-30dB:d=0.1", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if len(se) < len(ss):
        se.append(dur)
    head = next((e for s, e in zip(ss, se) if s <= 0.05), 0.0)
    tail = next((dur - s for s, e in zip(ss, se) if e >= dur - 0.05), 0.0)
    return head, tail


def write_caption(path, cap):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"TITLE\n{cap['title']}\n\nDESCRIPTION\n{cap['description']}\n\n"
                f"HASHTAGS\n{cap['hashtags']}\n")


def build(spec, reel):
    slug = spec["slug"]
    work = os.path.join(ROOT, "work", slug)
    src = os.path.join(ROOT, "sources", slug, "source.mp4")
    nn = format_reel_number(reel["num"])
    length = reel["end"] - reel["start"]
    if length >= MAX_LEN:
        raise ValueError(f"{nn}: cut is {length:.1f}s -- must be under {MAX_LEN:.0f}s")
    for text, s, e in reel["subs"]:
        if sub_line_count(text) > 1:
            raise ValueError(f"{nn}: subtitle wraps to 2 lines, shorten it: {text!r}")
        if not (0 <= s < e <= length + 0.01):
            raise ValueError(f"{nn}: subtitle timing {s}-{e} outside clip 0-{length:.2f}: {text!r}")

    # 1. raw clip (re-encode for a frame-accurate cut)
    clip = os.path.join(work, f"clip{nn}_{reel['topic']}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{reel['start']:.3f}", "-i", src,
         "-t", f"{length:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", clip])
    dur = duration(clip)

    # 2-5. overlays, rendered into a per-reel folder so reels never share PNGs
    ov = os.path.join(work, f"ov_{nn}")
    os.makedirs(ov, exist_ok=True)
    title = render_title_compact(ov, reel["title_lead"], reel["title_main"])
    subs = [(render_sub(ov, i, t), s, e) for i, (t, s, e) in enumerate(reel["subs"], 1)]

    inputs = ["-i", clip, "-i", title]
    for p, _, _ in subs:
        inputs += ["-i", p]
    inputs += ["-i", WATERMARK]
    fc = ("[0:v]scale=1920:1080[scaled];"
          + crop_reframe_filter(src_label="scaled", crop_x=spec["crop_x"])
          + "[reframed][1:v]overlay=0:0[v0];")
    prev = "v0"
    for i, (_, s, e) in enumerate(subs):
        fc += f"[{prev}][{i + 2}:v]overlay=0:0:enable='between(t,{s},{e})'[vs{i}];"
        prev = f"vs{i}"
    fc += f"[{prev}][{len(subs) + 2}:v]overlay=0:0[vc];"
    # 6. fade on the FINAL composited frame, so title/subs/watermark fade together
    fo = round(dur - FADE, 3)
    fc += f"[vc]fade=t=in:st=0:d={FADE},fade=t=out:st={fo}:d={FADE}[vout]"

    out_dir = reel_dir(slug)
    name = f"{slug}_{nn}_{reel['topic']}"
    out = os.path.join(out_dir, name + ".mp4")
    run(["ffmpeg", "-y", "-v", "error"] + inputs + [
        "-filter_complex", fc, "-map", "[vout]", "-map", "0:a",
        "-af", f"afade=t=in:st=0:d={FADE},afade=t=out:st={fo}:d={FADE}",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
        "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])

    # 7-8. sidecar + subtitle text for check_reel.py
    write_caption(os.path.join(out_dir, name + ".caption.txt"), reel["caption"])
    with open(os.path.join(work, f"subs_{nn}.json"), "w", encoding="utf-8") as f:
        json.dump([t for t, _, _ in reel["subs"]], f, ensure_ascii=False, indent=2)
    final = duration(out)
    head, tail = edge_quiet(out, final)
    print(f"Built {name}.mp4  {final:.1f}s  quiet: head {head:.2f}s / tail {tail:.2f}s")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    with open(os.path.join(ROOT, "work", slug, "reels.json"), encoding="utf-8") as f:
        spec = json.load(f)
    want = {int(n) for n in sys.argv[2:]}
    for reel in spec["reels"]:
        if not want or reel["num"] in want:
            build(spec, reel)


if __name__ == "__main__":
    main()

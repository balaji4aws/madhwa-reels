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
                          render_sub_bilingual, bilingual_fits,
                          FONT_BOLD, W, H, ACCENT, WHITE)
from kannada_check import check as kannada_check  # noqa: E402
from reel_numbering import reel_dir, format_reel_number  # noqa: E402
from glitch_scan import scan as glitch_scan  # noqa: E402

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
    # subs entries: [english, start, end] or [english, start, end, kannada]
    subs_in = [(t[0], t[1], t[2], t[3] if len(t) > 3 else "") for t in reel["subs"]]
    bilingual = any(kn for _, _, _, kn in subs_in)
    for text, s, e, kn in subs_in:
        if bilingual:
            ok_kn, ok_en = bilingual_fits(kn, text)
            if not ok_kn:
                raise ValueError(f"{nn}: Kannada subtitle too long for one line: {kn!r}")
            if not ok_en:
                raise ValueError(f"{nn}: English subtitle too long for one line: {text!r}")
        elif sub_line_count(text) > 1:
            raise ValueError(f"{nn}: subtitle wraps to 2 lines, shorten it: {text!r}")
        if not (0 <= s < e <= length + 0.01):
            raise ValueError(f"{nn}: subtitle timing {s}-{e} outside clip 0-{length:.2f}: {text!r}")
    kn_review = []
    if bilingual:
        kn_lines = [kn for _, _, _, kn in subs_in]
        if not all(kn_lines):
            raise ValueError(f"{nn}: bilingual reel but some subtitles have no Kannada line")
        kn_errors, kn_review = kannada_check(
            kn_lines, os.path.join(ROOT, "sources", slug, "source.kn.vtt"))
        if kn_errors:
            raise ValueError(f"{nn}: Kannada orthography errors: " + "; ".join(kn_errors))

    # 0. glitch scan of the SOURCE range (added 2026-10-23: ep06 reel 10 went
    #    live with a 1.6s "Missing File" card that was in the source video).
    #    Every flagged range must be covered by a "hold_frames" entry
    #    ([[src_start, src_end], ...]) or the build stops.
    holds = reel.get("hold_frames", [])
    flagged, _ = glitch_scan(src, reel["start"], reel["end"])
    uncovered = [(a, b) for a, b in flagged
                 if not any(h0 <= a + 0.01 and b - 0.01 <= h1 for h0, h1 in holds)]
    if uncovered:
        raise ValueError(f"{nn}: source has glitch frames at "
                         + ", ".join(f"{a:.2f}-{b:.2f}s" for a, b in uncovered)
                         + " -- pick a different cut, or cover them with hold_frames")

    # 1. raw clip (re-encode for a frame-accurate cut)
    clip = os.path.join(work, f"clip{nn}_{reel['topic']}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{reel['start']:.3f}", "-i", src,
         "-t", f"{length:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", clip])
    dur = duration(clip)

    # 1b. cover glitch ranges: hold the last good frame over them (audio keeps
    #     playing underneath, so no words are lost).
    for i, (h0, h1) in enumerate(holds):
        a, b = h0 - reel["start"], h1 - reel["start"]
        still = os.path.join(work, f"hold{nn}_{i}.png")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(a - 0.08, 0):.3f}", "-i", clip,
             "-frames:v", "1", still])
        patched = clip + ".patched.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", clip, "-loop", "1", "-i", still,
             "-filter_complex",
             f"[0:v][1:v]overlay=0:0:shortest=1:enable='between(t,{a:.3f},{b:.3f})'[v]",
             "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "fast",
             "-crf", "16", "-c:a", "copy", patched])
        os.replace(patched, clip)
        os.remove(still)

    # 2-5. overlays, rendered into a per-reel folder so reels never share PNGs
    ov = os.path.join(work, f"ov_{nn}")
    os.makedirs(ov, exist_ok=True)
    title = render_title_compact(ov, reel["title_lead"], reel["title_main"])
    if bilingual:
        subs = [(render_sub_bilingual(ov, i, kn, t)[0], s, e)
                for i, (t, s, e, kn) in enumerate(subs_in, 1)]
    else:
        subs = [(render_sub(ov, i, t), s, e) for i, (t, s, e, _) in enumerate(subs_in, 1)]

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
        json.dump([t for t, _, _, _ in subs_in], f, ensure_ascii=False, indent=2)
    if bilingual:
        with open(os.path.join(work, f"subs_kn_{nn}.json"), "w", encoding="utf-8") as f:
            json.dump([kn for _, _, _, kn in subs_in], f, ensure_ascii=False, indent=2)
    final = duration(out)
    head, tail = edge_quiet(out, final)
    # 9. glitch scan of the FINISHED reel, every frame at 5fps (not a spot
    #    check). Held frames are frozen on purpose, so they are excluded.
    held = [(h0 - reel["start"], h1 - reel["start"]) for h0, h1 in holds]
    bad, _ = glitch_scan(out)
    bad = [(a, b) for a, b in bad
           if not any(h0 - 0.3 <= a and b <= h1 + 0.3 for h0, h1 in held)]
    if bad:
        raise RuntimeError(f"{nn}: finished reel has glitch frames at "
                           + ", ".join(f"{a:.2f}-{b:.2f}s" for a, b in bad)
                           + f" -- NOT ready to upload: {out}")
    print(f"Built {name}.mp4  {final:.1f}s  quiet: head {head:.2f}s / tail {tail:.2f}s"
          f"  glitch scan: clean{' (holds: ' + str(len(holds)) + ')' if holds else ''}")
    if bilingual:
        print("  Kannada orthography: PASS"
              + (f"; review (not in source captions): {kn_review}" if kn_review
                 else "; all words found in source captions"))
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

#!/usr/bin/env python3
"""Per-slug title override for venkatachala-ep07 ONLY.

Same situation as venkatachala-ep06 (see that slug's title_compact.py):
venkatachala-ep01/overlays_lib.py's render_title() places its title band
tuned for THAT source's speaker, who sits with clearance above the head.
This source's speaker (Sri Satyatmateertha Shripadangalavaru, "Glory of
Venkatachala Ep-07", Hubli recording) sits with near-zero headroom above
the hairline/tilak mark -- confirmed on a real probe frame during this
build (the default band collides directly with the tilak, verified by
compositing render_title()'s band over a crop_x=523 frame of this source
and looking at it). crop_h already equals the full source height, so
crop_y=0 is the only option -- there is nothing above the head to crop
into instead, exactly like ep06.

Per the standing per-slug-override approach already approved for ep06
(2026-10-23): shrink/reposition the title for THIS source only, as a
per-slug override -- do NOT change the shared default in overlays_lib.py.
This keeps venkatachala-ep01's reels (different speaker/framing, out of
scope) unaffected.

Geometry: identical to ep06's verified title_compact (band_top=8, fonts
26px lead / 34px main, line_h=38) -- the two speakers share the same
studio/camera framing and the same near-zero-headroom problem, so the
geometry that cleared ep06's tilak also clears this one. Re-verified
against a real rendered frame of THIS source before use (see
work/build-notes.md / the title_collision check).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ACCENT = (245, 166, 35, 255)   # saffron #F5A623, same as overlays_lib.py
WHITE = (255, 255, 255, 255)
FONT_GEO_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

BAND_TOP = 8
LINE_H = 38


def _font(size):
    return ImageFont.truetype(FONT_GEO_BOLD, size)


def _center(draw, text, fnt, y, fill, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2 - bbox[0]
    if shadow:
        draw.text((x + 2, y + 2), text, font=fnt, fill=(0, 0, 0, 190))
    draw.text((x, y), text, font=fnt, fill=fill)
    return tw


def render_title_compact(outdir, lead, main):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_lead = _font(26)
    f_main = _font(34)
    band_h = 20 + 2 * LINE_H
    d.rounded_rectangle([70, BAND_TOP, W - 70, BAND_TOP + band_h],
                         radius=16, fill=(0, 0, 0, 135))
    y = BAND_TOP + 10
    _center(d, lead, f_lead, y, WHITE)
    y += LINE_H
    _center(d, main, f_main, y, ACCENT)
    path = os.path.join(outdir, "ov_title.png")
    img.save(path)
    return path

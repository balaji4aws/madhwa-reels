#!/usr/bin/env python3
"""Per-slug title override for venkatachala-ep06 ONLY.

venkatachala-ep01/overlays_lib.py's render_title() hardcodes band_top=160
and 46/60px fonts -- tuned so there's clearance above THAT source's
speaker's head. This source's speaker sits much closer to the top of frame
(near-zero headroom above the hairline/tilak mark in the original footage
-- confirmed on a real probe frame, see docs/CHANGELOG.md), so the shared
band collides with his forehead every time. There is no crop_y value that
fixes this (crop_h already equals the full source height, so crop_y=0 is
the only option -- there's nothing above the head to crop into instead).

Per explicit user direction (2026-10-23): shrink/reposition the title for
THIS source only, as a per-slug override -- do NOT change the shared
default in overlays_lib.py, so venkatachala-ep01's reels (already built,
out of scope for this task) stay unaffected.

New geometry, verified against a real rendered frame before use (see
title_test_composite.png / docs/CHANGELOG.md): band_top=8 (tucked right at
the top edge, above the hairline), fonts shrunk to 26px (lead) / 34px
(main), line_h=38. This clears the tilak mark with visible margin and
stays legible and within the top safe zone -- no other STYLE.md rule
(subtitle SUB_Y, watermark y, crop_x/crop_w/crop_h) is touched.
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

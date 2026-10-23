#!/usr/bin/env python3
"""Reusable overlay renderer for Madhwa reels.

ffmpeg here has no drawtext, so we draw every text element as a transparent PNG
and composite with ffmpeg `overlay`. This module renders, for one reel:
  - a title card PNG (top)
  - one subtitle PNG per caption cue (slightly above bottom, safe zone)

Call build_reel_overlays(outdir, title_lead, title_main, subs) where
`subs` is a list of (text, start, end) in clip-seconds.

Returns a dict describing produced files + their timings so the caller can wire
the ffmpeg overlay chain.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ACCENT = (245, 166, 35, 255)   # saffron #F5A623
WHITE = (255, 255, 255, 255)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_GEO_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

# Safe-zone anchors (IG/YouTube cover bottom ~15% + right edge)
SUB_Y = 1560          # spoken-word subtitles sit here (above platform UI).
                      # Moved down from 1460 (2026-10, user feedback): with
                      # the crop filling to y~1350 and a blurred margin
                      # below it, 1460 sat right at that seam with barely
                      # any breathing room. 1560 gives clear separation
                      # from the video/margin seam while staying above the
                      # bottom ~280px platform-UI zone and the @handle
                      # watermark below it.


def crop_reframe_filter(src_label="0:v", crop_w=864, crop_h=1080,
                         crop_x=None, crop_y=0, fill_mode="mirror_blur"):
    """Return an ffmpeg filter_complex fragment reframing a 1920x1080
    horizontal source into a 1080x1920 vertical frame by CROPPING a vertical
    slice centered on the speaker, instead of blur-filling the whole frame.

    IMPORTANT -- crop_x has NO safe default and MUST be passed explicitly,
    re-derived per source video. It depends on where THIS speaker sits in
    THIS camera's framing, which varies source to source (confirmed: a
    value tuned for one speaker/source, reused unchanged for a different
    speaker/source, produced a visibly off-center crop -- see CHANGELOG.md
    2026-10 entry). Before calling this for a new source: extract a frame,
    overlay a grid (e.g. `ffmpeg -vf drawgrid=w=100:h=100:t=1:c=yellow@0.5`),
    find the speaker's face-center x-coordinate, then
    crop_x = face_center_x - crop_w // 2. Verify by rendering the crop
    against a real frame and looking at it before using it in a build.

    FIXED 2026-10 (see CHANGELOG.md): the first version of this function
    scaled the crop to 1080x1920 with INDEPENDENT x/y factors
    (`scale=1080:1920` on a 1080x1080 crop = 1x horizontal, 1.78x vertical
    stretch). That distorted faces badly and, combined with the square
    crop already filling most of its own frame, rendered as an extreme,
    uncomfortable close-up once verified against real frames -- confirmed
    by reproducing the exact filter and looking at the output directly, not
    assumed from the code alone.

    Correct behavior: the crop is scaled UNIFORMLY (same factor on both
    axes, preserving the crop's own aspect ratio -- here 1:1, so no
    distortion), to `crop_w` wide = 1080px. A 1080x1080 crop scaled
    uniformly to 1080 wide stays 1080 tall, landing SHORT of the 1920
    canvas height by 840px. That leftover 840px (420 top + 420 bottom) is
    filled with a blurred, scaled mirror of the FULL original 1920x1080
    frame (not the crop) -- this is the leftover-margin fallback the task
    brief explicitly approved ("scaled mirror is also fine"), now actually
    implemented rather than silently never triggered.

    Output label: `[reframed]`. Caller continues the overlay chain from
    there (title/sub/watermark overlays stay structurally unchanged).
    """
    if crop_x is None:
        raise ValueError(
            "crop_x is required and has no safe default -- it must be "
            "re-derived per source video (see this function's docstring). "
            "Extract a frame, find the speaker's face-center x, and pass "
            "crop_x = face_center_x - crop_w // 2."
        )
    if fill_mode != "mirror_blur":
        raise ValueError(f"Unsupported fill_mode: {fill_mode!r}")

    # Sharp crop, scaled UNIFORMLY (aspect-ratio preserved) to crop_w wide.
    sharp_h = round(1080 * crop_h / crop_w)  # height after uniform scale
    margin_total = 1920 - sharp_h
    if margin_total <= 0:
        # Crop already tall enough (or taller) once scaled -- no margin
        # needed, sharp video fills (or overflows; caller should pick
        # crop_h so this doesn't happen) the whole frame on its own.
        return (
            f"[{src_label}]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},"
            f"scale=1080:-2,crop=1080:1920[reframed];"
        )

    # Margin placed entirely at the BOTTOM (overlay y=0), not split
    # top/bottom. Verified against real probe frames: putting the sharp
    # crop at the very top maximizes headroom above the speaker's head
    # (matches the reference reels' framing) and pushes the blurred-margin
    # strip down into the chest/robe area, which reads naturally rather
    # than as an obvious seam. A centered split wasted some margin above
    # the head where it isn't needed.
    return (
        # background: blurred mirror of the FULL frame, scaled/cropped to
        # fill 1080x1920 (same technique the old approach used for its
        # whole background, now demoted to margin-filler only).
        f"[{src_label}]split=2[reframe_sharp_src][reframe_bg_src];"
        "[reframe_bg_src]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=20:2,eq=brightness=-0.25[reframe_bg];"
        # sharp: the actual crop, scaled uniformly, no distortion.
        f"[reframe_sharp_src]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},"
        f"scale=1080:-2[reframe_sharp];"
        # composite: sharp crop pinned to the top; blurred background
        # shows through in the remaining bottom margin only.
        f"[reframe_bg][reframe_sharp]overlay=0:0[reframed];"
    )


def _font(path, size):
    return ImageFont.truetype(path, size)


def _center(draw, text, fnt, y, fill, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2 - bbox[0]
    if shadow:
        draw.text((x + 3, y + 3), text, font=fnt, fill=(0, 0, 0, 190))
    draw.text((x, y), text, font=fnt, fill=fill)
    return tw


def _band(draw, x0, y0, x1, y1, r, fill):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)


def _wrap(text, fnt, draw, max_w):
    """Wrap text to fit max_w pixels, return list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_title(outdir, lead, main):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Sizes reduced TWICE now (2026-10): 64/82px -> 54/70px -> 46/60px.
    # Even at 54/70 the title band still touched the speaker's hairline on
    # some sources (user feedback, screenshot-verified) -- 46/60 shrinks it
    # further, and the band's start moved UP from y=230 to y=160 so there's
    # real clearance above the head, not just a smaller font in the same
    # low position. Re-verify against a real frame whenever this changes.
    f_lead = _font(FONT_GEO_BOLD, 46)
    f_main = _font(FONT_GEO_BOLD, 60)
    line_h = 66  # shrunk to match the smaller font (was 78, then 92)
    band_top = 160  # was 230 -- moved up for more clearance above the head
    # wrap main word(s) if long
    main_lines = _wrap(main, f_main, d, W - 180)
    n = 1 + len(main_lines)
    band_h = 50 + n * line_h
    _band(d, 55, band_top, W - 55, band_top + band_h, 28, (0, 0, 0, 125))
    y = band_top + 24
    _center(d, lead, f_lead, y, WHITE)
    y += line_h
    for ml in main_lines:
        _center(d, ml, f_main, y, ACCENT)
        y += line_h
    path = os.path.join(outdir, "ov_title.png")
    img.save(path)
    return path


def render_sub(outdir, idx, text):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = _font(FONT_BOLD, 46)
    lines = _wrap(text, fnt, d, W - 150)
    line_h = 60
    total_h = len(lines) * line_h
    # pill behind all lines
    widest = max((d.textbbox((0, 0), ln, font=fnt)[2] for ln in lines), default=0)
    pad_x, pad_y = 34, 18
    x0 = (W - widest) // 2 - pad_x
    x1 = (W + widest) // 2 + pad_x
    top = SUB_Y - pad_y
    _band(d, x0, top, x1, top + total_h + pad_y, 22, (0, 0, 0, 155))
    y = SUB_Y
    for ln in lines:
        _center(d, ln, fnt, y, WHITE)
        y += line_h
    path = os.path.join(outdir, f"ov_sub_{idx:02d}.png")
    img.save(path)
    return path


# --- Bilingual subtitles (owner direction 2026-10-23: Kannada + English) ---
# Kannada on top (larger, the speaker's own words), English below (smaller),
# each in its OWN pill with a clear gap between them, so they never look
# crammed. Kannada needs complex text shaping (raqm/HarfBuzz) or conjuncts
# like ನ್ನ / ಕ್ತಿ / ಶ್ರೀ break apart -- Pillow here has raqm (checked 2026-10-23).
FONT_KN_BOLD = "/System/Library/Fonts/NotoSansKannada.ttc"
FONT_KN_BOLD_INDEX = 6        # "Noto Sans Kannada" Bold face in the .ttc
KN_SIZE, EN_SIZE = 44, 36
KN_TOP = 1452                 # top of the Kannada pill
PILL_GAP = 26                 # clear space between the two pills
PAD_X, PAD_Y = 30, 14
MAX_TEXT_W = W - 150


def kn_font(size=KN_SIZE):
    return ImageFont.truetype(FONT_KN_BOLD, size, index=FONT_KN_BOLD_INDEX,
                              layout_engine=ImageFont.Layout.RAQM)


# English uses Noto Sans Bold, the SAME type family as Noto Sans Kannada, so
# the two subtitle lines match (owner rule 2026-10-23: English and Kannada in
# the same/related font family). Noto Sans (Latin) isn't shipped with macOS,
# so the official OFL variable font lives in assets/fonts/ (licence beside it).
FONT_EN_NOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                            "assets", "fonts", "NotoSans-Variable.ttf")


def en_font(size=EN_SIZE):
    f = ImageFont.truetype(FONT_EN_NOTO, size, layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_name("Bold")
    return f


# --- Single-line English title (owner rule 2026-10-23) ---
TITLE_SIZE, TITLE_MIN_SIZE = 38, 32   # readable but not big; shrink only if needed
TITLE_TOP = 8                         # hugs the top edge (speakers have no headroom)


def render_title_line(outdir, lead, main):
    """One line, Noto Sans Bold: `lead` in white, `main` in saffron, inside a
    slim dark band at the top. Shrinks from 38px down to 32px to fit; raises
    if it still doesn't fit (shorten the title)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lead = lead.strip()
    gap = " " if lead else ""
    for size in range(TITLE_SIZE, TITLE_MIN_SIZE - 1, -1):
        fnt = en_font(size)
        if d.textlength(lead + gap + main, font=fnt) <= W - 180:
            break
    else:
        raise ValueError(f"title too long for one line: {lead + gap + main!r}")
    full = lead + gap + main
    bb = d.textbbox((0, 0), full, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = (W - tw) // 2
    _band(d, x0 - 30, TITLE_TOP, x0 + tw + 30, TITLE_TOP + th + 26, 16, (0, 0, 0, 140))
    y = TITLE_TOP + 13 - bb[1]
    x = x0 - bb[0]
    lead_w = d.textlength(lead + gap, font=fnt)
    for dx, dy, col_lead, col_main in ((2, 2, (0, 0, 0, 190), (0, 0, 0, 190)),
                                       (0, 0, WHITE, ACCENT)):
        if lead:
            d.text((x + dx, y + dy), lead + gap, font=fnt, fill=col_lead)
        d.text((x + lead_w + dx, y + dy), main, font=fnt, fill=col_main)
    path = os.path.join(outdir, "ov_title.png")
    img.save(path)
    return path


def _pill_line(d, text, fnt, top):
    """Draw one centred line in its own rounded pill whose top edge is `top`.
    Uses the real ink bbox so Kannada's tall vowel signs and below-base
    conjuncts sit inside the pill. Returns the pill's bottom y."""
    bb = d.textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (W - tw) // 2 - bb[0]
    y = top + PAD_Y - bb[1]
    bottom = top + th + 2 * PAD_Y
    _band(d, (W - tw) // 2 - PAD_X, top, (W + tw) // 2 + PAD_X, bottom, 22, (0, 0, 0, 160))
    d.text((x + 2, y + 2), text, font=fnt, fill=(0, 0, 0, 190))
    d.text((x, y), text, font=fnt, fill=WHITE)
    return bottom


def bilingual_fits(kn, en):
    """True if both lines fit on ONE line each (no wrapping allowed)."""
    d = ImageDraw.Draw(Image.new("RGBA", (W, 200)))
    ok_kn = (not kn) or d.textlength(kn, font=kn_font()) <= MAX_TEXT_W
    ok_en = (not en) or d.textlength(en, font=en_font()) <= MAX_TEXT_W
    return ok_kn, ok_en


def render_sub_bilingual(outdir, idx, kn, en):
    """Kannada line in one pill, English line in a second pill below it.
    Returns (png_path, english_pill_bottom_y)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = KN_TOP
    if kn:
        y = _pill_line(d, kn, kn_font(), y) + PILL_GAP
    bottom = _pill_line(d, en, en_font(), y) if en else y
    path = os.path.join(outdir, f"ov_sub_{idx:02d}.png")
    img.save(path)
    return path, bottom

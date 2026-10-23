#!/usr/bin/env python3
"""Render the Madhwa16 channel watermark as a transparent PNG (1080x1920 canvas,
   text placed in a corner). ffmpeg here has no drawtext, so we overlay this PNG."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ACCENT = (245, 166, 35, 255)   # saffron
WHITE = (255, 255, 255, 235)

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

handle = "@madhwa16"
fnt = ImageFont.truetype(FONT_BOLD, 40)

# bottom-center, just above the lower safe area, semi-transparent
bbox = d.textbbox((0, 0), handle, font=fnt)
tw = bbox[2] - bbox[0]
x = (W - tw) // 2 - bbox[0]
y = 1700  # Re-checked 2026-10 against the new crop-based reframe (was 1840):
          # at the tighter crop the source's own baked-in bottom banner/
          # platform-handle strip now falls around y~1790-1920, so the
          # watermark moved up to clear it and stay legible.
# soft shadow for legibility over any background
d.text((x + 2, y + 2), handle, font=fnt, fill=(0, 0, 0, 150))
d.text((x, y), handle, font=fnt, fill=WHITE)

img.save("watermark.png")
print("watermark.png written")

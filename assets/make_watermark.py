#!/usr/bin/env python3
"""Render the Madhwa16 channel watermark as a transparent PNG (1080x1920 canvas,
   icon + channel URL, placed bottom-center above the lower safe area).
   ffmpeg here has no drawtext, so we overlay this PNG.

   WATERMARK CONTENT (updated 2026-10-23, per channel-owner request):
   - Text is the FULL channel URL "https://www.youtube.com/@madhwa16"
     (changed from the bare handle "@madhwa16" — the owner wants the full
     clickable-looking URL so viewers know exactly where to find the channel).
   - A small brand icon (assets/channels4_profile.jpg, the channel's profile
     image) sits to the LEFT of the URL text.

   IMPORTANT — VISUAL VERIFICATION REQUIRED ON FIRST REAL USE:
   The full URL is a much longer, wider string than the old "@madhwa16"
   handle. The font size (URL_FONT_PX), icon size (ICON_PX), gap, and the
   whole icon+text block's width MUST be verified against a real rendered
   1080-wide frame before shipping a reel with this watermark:
     - the block must stay centered and NOT run into the right-edge safe zone,
     - it must stay legible at the bottom-center position (y=WM_Y), above the
       platform-UI zone (~bottom 280px) and the source's own baked-in banner
       (~y1790-1920 under the current crop),
     - the icon and text must be vertically centered against each other.
   Treat the sizes below as a STARTING POINT to tune on first use (the way
   crop_x and SUB_Y are tuned per the house style), not as final constants.
   After regenerating, overlay this PNG on an actual reel frame and look at it.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
ACCENT = (245, 166, 35, 255)   # saffron
WHITE = (255, 255, 255, 235)

# Noto Sans Bold -- same family as the title and subtitles (owner 2026-10-23:
# "not Arial"). Official OFL font kept in assets/fonts/.
FONT_BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSans-Variable.ttf")

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(HERE, "channels4_profile.jpg")

# --- Tunable layout (verify visually on first real use — see module docstring) ---
URL_TEXT = "https://www.youtube.com/@madhwa16"
URL_FONT_PX = 30   # smaller than the old 40px handle, because the URL is far
                   # wider; tune against a real 1080-wide frame.
ICON_PX = 48       # rendered size of the square brand icon (source is 160x160).
ICON_TEXT_GAP = 14 # horizontal gap between the icon and the URL text.
WM_Y = 1700        # vertical baseline band, same as the prior handle watermark:
                   # clears the source's baked-in bottom banner/handle strip
                   # (~y1790-1920 under the current crop) and the platform-UI
                   # zone, stays legible. Re-verify if the crop geometry changes.

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
fnt = ImageFont.truetype(FONT_BOLD, URL_FONT_PX)
fnt.set_variation_by_name("Bold")

# Measure the URL text.
bbox = d.textbbox((0, 0), URL_TEXT, font=fnt)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]

# Load + resize the brand icon (round it slightly / keep square — kept square
# here; circular-mask it on a future pass if the owner prefers the round look).
icon = None
if os.path.exists(ICON_PATH):
    icon = Image.open(ICON_PATH).convert("RGBA").resize((ICON_PX, ICON_PX))
else:
    print(f"WARNING: brand icon not found at {ICON_PATH} — rendering URL text only.")

# Total block width = icon + gap + text (or just text if icon missing).
block_w = tw + (ICON_PX + ICON_TEXT_GAP if icon else 0)
block_x = (W - block_w) // 2
# Vertically center the icon against the text's visual center at WM_Y.
text_x = block_x + (ICON_PX + ICON_TEXT_GAP if icon else 0)
text_y = WM_Y
if icon:
    icon_y = text_y + (th - ICON_PX) // 2  # center icon on the text's height
    img.alpha_composite(icon, (block_x, icon_y))

# soft shadow for legibility over any background
d.text((text_x + 2, text_y + 2), URL_TEXT, font=fnt, fill=(0, 0, 0, 150), anchor="la")
d.text((text_x, text_y), URL_TEXT, font=fnt, fill=WHITE, anchor="la")

out = os.path.join(HERE, "watermark.png")
img.save(out)
print(f"watermark.png written ({out})")
print("REMINDER: verify this against a real rendered reel frame before shipping "
      "— the full URL is wide; check it stays centered, legible, and clear of "
      "the right-edge safe zone (see module docstring).")

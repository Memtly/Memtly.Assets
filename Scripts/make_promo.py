#!/usr/bin/env python3
"""
make_promo.py — Composite a desktop + mobile screenshot into a single promo image.

Usage:
    python3 make_promo.py <desktop_image> <mobile_image> [output_path]

Examples:
    python3 make_promo.py desktop.png mobile.png promo.png
    python3 make_promo.py https://raw.githubusercontent.com/.../Desktop/Light/Gallery_Default.png \
                          https://raw.githubusercontent.com/.../Mobile/Light/Gallery_Default.png \
                          Screenshots/Community/promo.png

Accepts local file paths or http(s) URLs for the two input images.
"""

import sys
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

W, H = 1790, 800
BG_COLOR = (243, 244, 247)     # neutral light gray
BORDER_COLOR = (210, 213, 219) # thin sharp border, no shadow
ACCENT_COLOR = (37, 99, 235)   # brand blue accent line

DESKTOP_WIDTH = 1400
DESKTOP_RADIUS = 3             # sharp, near-square corners

MOBILE_WIDTH = 390
MOBILE_RADIUS = 3              # no chrome/bezel — just the screenshot

MARGIN = 20       # outer margin
GUTTER = 10        # space between the two images

def load_image(source: str) -> Image.Image:
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source) as resp:
            data = resp.read()
        return Image.open(BytesIO(data)).convert("RGBA")
    return Image.open(source).convert("RGBA")


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def bordered_paste(canvas, img, pos, radius):
    """Paste img onto canvas at pos with a thin sharp border, no shadow."""
    x, y = pos
    w, h = img.size
    canvas.paste(img, (x, y), rounded_mask(img.size, radius))
    bd = ImageDraw.Draw(canvas)
    bd.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=radius, outline=BORDER_COLOR, width=1)


def make_promo(desktop_src: str, mobile_src: str, output_path: str):
    canvas = Image.new("RGBA", (W, H), BG_COLOR + (255,))

    # Desktop screenshot
    desktop = load_image(desktop_src)
    desktop_h = int(desktop.height * (DESKTOP_WIDTH / desktop.width))
    desktop = desktop.resize((DESKTOP_WIDTH, desktop_h), Image.LANCZOS)

    # Mobile screenshot — cap its height to roughly match the desktop image
    # so the pair reads as one balanced row, not two mismatched blocks.
    mobile_raw = load_image(mobile_src)
    mobile_h = min(desktop_h, int(mobile_raw.height * (MOBILE_WIDTH / mobile_raw.width)))
    mobile_w = int(MOBILE_WIDTH * (mobile_h / (mobile_raw.height * (MOBILE_WIDTH / mobile_raw.width))))
    mobile = mobile_raw.resize(
        (int(mobile_raw.width * (mobile_h / mobile_raw.height)), mobile_h), Image.LANCZOS
    )
    if mobile.width > MOBILE_WIDTH:
        mobile = mobile.crop((0, 0, MOBILE_WIDTH, mobile_h))

    total_w = DESKTOP_WIDTH + GUTTER + mobile.width
    start_x = (W - total_w) // 2
    row_h = max(desktop_h, mobile.height)
    start_y = (H - row_h) // 2

    dx, dy = start_x, start_y + (row_h - desktop_h) // 2
    mx, my = start_x + DESKTOP_WIDTH + GUTTER, start_y + (row_h - mobile.height) // 2

    bordered_paste(canvas, desktop, (dx, dy), DESKTOP_RADIUS)
    bordered_paste(canvas, mobile, (mx, my), MOBILE_RADIUS)

    # Thin accent line beneath both images ties them together as one unit
    line_y = start_y + row_h + 24
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([start_x, line_y, start_x + total_w, line_y + 3], fill=ACCENT_COLOR)

    canvas.convert("RGB").save(output_path, quality=95)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    desktop_src = sys.argv[1]
    mobile_src = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "promo.png"
    make_promo(desktop_src, mobile_src, output_path)
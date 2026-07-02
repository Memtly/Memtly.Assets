#!/usr/bin/env python3
"""
make_promo.py — Composite two or more screenshots side-by-side into a single promo image.

All images are scaled to a common height so they line up neatly, placed left to
right in the order given, and surrounded by a border equal to the gap between
images. You specify the input images and the desired output width; the output
height is calculated automatically to fit everything.

Usage:
    python3 make_promo.py <image1> <image2> [<image3> ...] [options]

Options:
    -o, --output PATH     Output file path (default: promo.png)
    -w, --width INT       Total output width in pixels (default: 1790)
    -g, --gap INT         Gap between images, and border around the whole
                           composite (default: 20)
    -r, --radius INT      Corner radius applied to each image (default: 3)
    --bg-color HEX        Background color, e.g. "f3f4f7" (default: f3f4f7)
    --border-color HEX    Per-image border color, e.g. "d2d5db" (default: d2d5db)

Examples:
    python3 make_promo.py mobile.png desktop.png promo.png -w 1790

    python3 make_promo.py Mobile/Light/Gallery_Default.png \
                          Tablet/Light/Gallery_Default.png \
                          Desktop/Light/Gallery_Default.png \
                          -o Screenshots/Community/Promo_Light.png -w 2200 -g 16

Accepts local file paths or http(s) URLs for any input image.
"""

import argparse
import sys
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw


def load_image(source: str) -> Image.Image:
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source) as resp:
            data = resp.read()
        return Image.open(BytesIO(data)).convert("RGBA")
    return Image.open(source).convert("RGBA")


def hex_color(s: str):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def bordered_paste(canvas, img, pos, radius, border_color):
    """Paste img onto canvas at pos with a thin sharp border, no shadow."""
    x, y = pos
    w, h = img.size
    canvas.paste(img, (x, y), rounded_mask(img.size, radius))
    bd = ImageDraw.Draw(canvas)
    bd.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=radius, outline=border_color, width=1)


def make_promo(
    sources,
    output_path,
    out_width,
    gap,
    radius,
    bg_color,
    border_color,
):
    if len(sources) < 2:
        raise ValueError("Need at least 2 input images")

    images = [load_image(s) for s in sources]
    aspect_ratios = [img.width / img.height for img in images]

    n = len(images)
    margin = gap  # border around the composite matches the gap between images

    # Solve for the common height H such that:
    #   sum(ar_i * H) + (n-1)*gap + 2*margin == out_width
    available_width = out_width - (n - 1) * gap - 2 * margin
    if available_width <= 0:
        raise ValueError("Output width is too small for the given gap/margin")

    row_h = int(available_width / sum(aspect_ratios))
    if row_h <= 0:
        raise ValueError("Computed row height is <= 0; increase --width")

    resized = []
    for img, ar in zip(images, aspect_ratios):
        w = round(ar * row_h)
        resized.append(img.resize((w, row_h), Image.LANCZOS))

    # Recompute actual total width from rounded per-image widths so the
    # layout is pixel-exact (avoids drift from rounding each width).
    total_content_w = sum(im.width for im in resized) + (n - 1) * gap
    out_w = total_content_w + 2 * margin
    out_h = row_h + 2 * margin

    canvas = Image.new("RGBA", (out_w, out_h), bg_color + (255,))

    x = margin
    y = margin
    for im in resized:
        bordered_paste(canvas, im, (x, y), radius, border_color)
        x += im.width + gap

    canvas.convert("RGB").save(output_path, quality=95)
    print(f"Saved {output_path} ({out_w}x{out_h}, row height {row_h}px)")


def parse_args():
    p = argparse.ArgumentParser(
        description="Composite two or more screenshots side-by-side into a single promo image.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("images", nargs="+", help="Input images (paths or URLs), left to right")
    p.add_argument("-o", "--output", default="promo.png", help="Output file path")
    p.add_argument("-w", "--width", type=int, default=1790, help="Total output width in pixels")
    p.add_argument("-g", "--gap", type=int, default=20, help="Gap between images / border width")
    p.add_argument("-r", "--radius", type=int, default=3, help="Corner radius per image")
    p.add_argument("--bg-color", default="f3f4f7", help="Background color (hex)")
    p.add_argument("--border-color", default="d2d5db", help="Per-image border color (hex)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # If the last positional arg looks like an output path (not an existing file
    # or URL) and no -o was explicitly used, keep backward-compatible behavior
    # of treating a trailing plain filename as the output.
    images = args.images
    output = args.output
    if output == "promo.png" and len(images) >= 3:
        last = images[-1]
        looks_like_output = (
            not last.startswith("http://")
            and not last.startswith("https://")
            and not __import__("os").path.exists(last)
        )
        if looks_like_output:
            output = images.pop()

    if len(images) < 2:
        print("Error: need at least 2 input images.\n", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

    try:
        make_promo(
            sources=images,
            output_path=output,
            out_width=args.width,
            gap=args.gap,
            radius=args.radius,
            bg_color=hex_color(args.bg_color),
            border_color=hex_color(args.border_color),
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
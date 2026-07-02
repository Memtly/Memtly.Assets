#!/usr/bin/env python3
"""
generate_all_promos.py — Run make_promo.py for all default/inverted, light/dark promo combos.

Usage:
    python3 generate_all_promos.py [options]

Options:
    -w, --width INT       Total output width in pixels (default: 1920)
    -g, --gap INT         Gap between images, and border around the whole
                           composite (default: 50)
    -r, --radius INT      Corner radius applied to each image (default: 3)
    --bg-color HEX        Background color, e.g. "f3f4f7" (default: f3f4f7)
    --border-color HEX    Per-image border color, e.g. "d2d5db" (default: d2d5db)

Examples:
    python3 generate_all_promos.py
    python3 generate_all_promos.py -w 2200 -g 40
    python3 generate_all_promos.py -w 2200 -g 40 -r 8 --bg-color 111111 --border-color 333333
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MAKE_PROMO = SCRIPT_DIR / "make_promo.py"

BASE = "Screenshots/Community"

# Each job is (images, output). images is a list of 2 or more paths, in
# left-to-right order — add or remove entries freely.
JOBS = [
    (
        [
            f"{BASE}/Desktop/Light/Gallery_Default.png",
            f"{BASE}/Mobile/Light/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Light_Default.png",
    ),
    (
        [
            f"{BASE}/Desktop/Dark/Gallery_Default.png",
            f"{BASE}/Mobile/Dark/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Dark_Default.png",
    ),
    (
        [
            f"{BASE}/Mobile/Light/Gallery_Default.png",
            f"{BASE}/Desktop/Light/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Light_Inverted.png",
    ),
    (
        [
            f"{BASE}/Mobile/Dark/Gallery_Default.png",
            f"{BASE}/Desktop/Dark/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Dark_Inverted.png",
    ),
    (
        [
            f"{BASE}/Desktop/Light/Gallery_Default.png",
            f"{BASE}/Tablet/Light/Gallery_Default.png",
            f"{BASE}/Mobile/Light/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Light_All.png",
    ),
    (
        [
            f"{BASE}/Desktop/Dark/Gallery_Default.png",
            f"{BASE}/Tablet/Dark/Gallery_Default.png",
            f"{BASE}/Mobile/Dark/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Dark_All.png",
    ),
    (
        [
            f"{BASE}/Mobile/Light/Gallery_Default.png",
            f"{BASE}/Tablet/Light/Gallery_Default.png",
            f"{BASE}/Desktop/Light/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Light_All_Inverted.png",
    ),
    (
        [
            f"{BASE}/Mobile/Dark/Gallery_Default.png",
            f"{BASE}/Tablet/Dark/Gallery_Default.png",
            f"{BASE}/Desktop/Dark/Gallery_Default.png",
        ],
        f"{BASE}/Promos/Dark_All_Inverted.png",
    ),
]


def parse_args():
    p = argparse.ArgumentParser(
        description="Run make_promo.py for all default/inverted, light/dark combos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-w", "--width", type=int, default=1920, help="Total output width in pixels (default: 1920)")
    p.add_argument("-g", "--gap", type=int, default=50, help="Gap between images / border width (default: 50)")
    p.add_argument("-r", "--radius", type=int, default=3, help="Corner radius per image (default: 3)")
    p.add_argument("--bg-color", default="f3f4f7", help="Background color, hex (default: f3f4f7)")
    p.add_argument("--border-color", default="d2d5db", help="Per-image border color, hex (default: d2d5db)")
    return p.parse_args()


def main():
    args = parse_args()
    print(
        f"Using width={args.width} gap={args.gap} radius={args.radius} "
        f"bg-color={args.bg_color} border-color={args.border_color}\n"
    )

    for images, output in JOBS:
        if len(images) < 2:
            print(f"Skipping {output}: fewer than 2 images configured")
            continue

        cmd = [
            sys.executable,
            str(MAKE_PROMO),
            *images,
            "-o", output,
            "-w", str(args.width),
            "-g", str(args.gap),
            "-r", str(args.radius),
            "--bg-color", args.bg_color,
            "--border-color", args.border_color,
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"\nmake_promo.py failed on: {output}")
            sys.exit(result.returncode)

    print("\nAll promo images generated successfully.")


if __name__ == "__main__":
    main()
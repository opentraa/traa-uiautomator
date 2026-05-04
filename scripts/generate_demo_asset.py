from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: generate_demo_asset.py <output-path> <text>")
        return 1

    output = Path(sys.argv[1])
    text = sys.argv[2]
    output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (600, 180), color="white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 590, 170), outline="black", width=2)
    draw.text((40, 70), text, fill="black")
    image.save(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

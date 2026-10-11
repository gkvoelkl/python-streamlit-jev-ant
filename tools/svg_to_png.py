"""Turns the hand-drawn diagrams in tutorial/bilder into PNGs for the document.

    uv run python tools/svg_to_png.py                # all of them
    uv run python tools/svg_to_png.py koordinaten    # just one

The English versions in tutorial/bilder/en are rendered along with the German
ones; "koordinaten" renders both.

The rendering is QuickLook, which is macOS and the one renderer here that draws
colour emoji. It always writes a square with the picture in the top left, so
the empty part is cut away afterwards.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

BILDER = Path(__file__).resolve().parent.parent / "tutorial" / "bilder"
SCALE = 3


def render(svg: Path) -> None:
    text = svg.read_text(encoding="utf-8")
    width, height = (
        int(float(n)) for n in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups()
    )

    with tempfile.TemporaryDirectory() as work:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(width * SCALE), "-o", work, str(svg)],
            check=True,
            capture_output=True,
        )
        square = Image.open(Path(work) / f"{svg.name}.png")
        factor = square.width / width
        out = svg.with_suffix(".png")
        picture = square.crop((0, 0, square.width, round(height * factor)))
        picture.save(out)

        # QuickLook does not place the drawing exactly where the viewBox says,
        # so anything close to the bottom edge is cut off — silently, which
        # cost me one diagram's last box. Leave the last lines empty.
        background = picture.getpixel((4, 4))
        drawn = [
            y
            for y in range(picture.height)
            if any(picture.getpixel((x, y)) != background for x in range(0, picture.width, 7))
        ]
        air = picture.height - (max(drawn) if drawn else 0)
        if air < 20:
            print(f"   ! {out.name}: only {air} px below the last thing drawn — "
                  f"something is probably cut off, give the SVG more height")

        print(f"{out.name} — {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    wanted = sys.argv[1:]
    for svg in sorted([*BILDER.glob("*.svg"), *BILDER.glob("en/*.svg")]):
        if not wanted or svg.stem in wanted:
            render(svg)

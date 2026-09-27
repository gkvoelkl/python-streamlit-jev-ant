"""Turns the hand-drawn diagrams in tutorial/bilder into PNGs for the document.

    uv run python tools/svg_to_png.py                # all of them
    uv run python tools/svg_to_png.py koordinaten    # just one

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
        square.crop((0, 0, square.width, round(height * factor))).save(out)
        print(f"{out.name} — {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    wanted = sys.argv[1:]
    for svg in sorted(BILDER.glob("*.svg")):
        if not wanted or svg.stem in wanted:
            render(svg)

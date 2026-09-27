"""Makes a picture of the running game for the tutorial.

    uv run python tools/board_image.py tutorial/bilder/das-spiel.png \
        --order "Fan out and search, and carry what you find straight home." \
        --rounds 10

It drives the real `app.py` through Streamlit's own test harness, so the board
in the picture is the board the program draws — not a mock-up that will quietly
go out of date. The SVG comes back out of the rendered page, and macOS turns it
into a PNG with QuickLook, which is the one renderer here that draws colour
emoji.

    --dice   plays with the dice instead of the model: no key, no requests, no
             cost. Good for pictures where the labels do not matter.
    --app    a different program to photograph, for the pictures a chapter
             needs of its own step: `--app steps/01_board.py`. Anything the
             chosen program has no buttons for is skipped.

Without `--dice` it spends real requests — eight per round.

macOS only, because of `qlmanage`. It is a tool for making the tutorial, not
part of the game.
"""

import argparse
import base64
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def rendered_svg(order: str, rounds: int, dice: bool, program: str = "app.py") -> str:
    """Plays the game and returns the board as it stands afterwards."""
    os.chdir(ROOT)
    app = AppTest.from_file(str(ROOT / program), default_timeout=120)
    app.run()

    # An early step has no buttons to press and nothing to play; its board is
    # what it draws on the first run.
    if not app.button:
        return svg_of(app)

    if dice and app.toggle:
        app.toggle[0].set_value(True).run()
    elif not dice:
        if not (os.getenv("TYPESAFE_API_KEY") or "").strip():
            sys.exit("No TYPESAFE_API_KEY — either set one or pass --dice.")
        # An early step has no queen to speak for, so there is no field and
        # nothing to say.
        if app.text_input:
            app.text_input[0].set_value(order).run()
            next(b for b in app.button if b.label == "Say").click().run()

    def press(label: str) -> bool:
        button = next((b for b in app.button if b.label == label), None)
        if button is None:
            return False
        button.click().run()
        return True

    for _ in range(max(1, rounds // 5)):
        # Whatever this step calls playing a round.
        if not press("Five rounds"):
            for _ in range(5):
                if not (press("Next round") or press("Ask Jev for a step")):
                    break

    # A picture is of the round that happened last, and a round in which every
    # answer was thrown away is eight grey dashes — true, but not what the
    # front of a tutorial should show. So play on, one round at a time, until
    # most of the colony has something to say.
    if not dice and "ants" in app.session_state:
        for _ in range(8):
            speaking = sum(ant["said"] is not None for ant in app.session_state.ants)
            if speaking >= len(app.session_state.ants) * 0.6:
                break
            press("Next round")

    if "ants" in app.session_state:
        print(f"round {app.session_state.round}, {app.session_state.stores} stored, "
              f"{app.session_state.requests} requests, "
              f"{sum(a['said'] is not None for a in app.session_state.ants)} of "
              f"{len(app.session_state.ants)} ants with a label")

    return svg_of(app)


def svg_of(app: AppTest) -> str:
    """The board out of the rendered page.

    `st.image` hands the SVG to the page as a data URI; this is the same string
    the browser draws.
    """
    source = next(e for e in app.main if type(e).__name__ == "Image").value[0]
    return base64.b64decode(re.sub(r"^data:image/svg\+xml;base64,", "", source)).decode()


def to_png(svg: str, out: Path, scale: int = 3) -> None:
    """SVG to PNG through QuickLook, cropped back to the board.

    `qlmanage` always writes into a square, with the picture in the top left
    corner, so the empty part below it is cut away afterwards.
    """
    width, height = (int(n) for n in re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())

    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "board.svg"
        source.write_text(svg, encoding="utf-8")
        subprocess.run(
            ["qlmanage", "-t", "-s", str(width * scale), "-o", work, str(source)],
            check=True,
            capture_output=True,
        )
        square = Image.open(Path(work) / "board.svg.png")
        factor = square.width / width
        board = square.crop((0, 0, square.width, round(height * factor)))
        out.parent.mkdir(parents=True, exist_ok=True)
        board.save(out)

    print(f"{out.relative_to(ROOT)} — {board.width} x {board.height}")


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description=__doc__)
    parse.add_argument("out", type=Path)
    parse.add_argument("--order", default="Fan out and search, and carry what you find home.")
    parse.add_argument("--rounds", type=int, default=10)
    parse.add_argument("--dice", action="store_true")
    parse.add_argument("--scale", type=int, default=3)
    parse.add_argument("--app", default="app.py")
    where = parse.parse_args()

    to_png(
        rendered_svg(where.order, where.rounds, where.dice, where.app),
        where.out if where.out.is_absolute() else ROOT / where.out,
        where.scale,
    )

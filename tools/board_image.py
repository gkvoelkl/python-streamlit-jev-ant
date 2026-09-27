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
    --crop   a detail instead of the whole board, in cells: `--crop 7,3,10,9`
             is ten by nine cells starting at (7, 3). For close-ups of the
             nest, where a picture of the whole board says nothing.

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

    # Whatever this step calls playing a round. `--rounds 0` means none at
    # all, which is how a picture of the starting position is taken.
    played = 0
    while played < rounds:
        if rounds - played >= 5 and press("Five rounds"):
            played += 5
        elif press("Next round") or press("Ask Jev for a step"):
            played += 1
        else:
            break

    # A picture is of the round that happened last, and a round in which every
    # answer was thrown away is eight grey dashes — true, but not what the
    # front of a tutorial should show. So play on, one round at a time, until
    # most of the colony has something to say.
    # Only from the step that draws labels on; before that there is nothing to
    # wait for.
    labelled = "ants" in app.session_state and "said" in app.session_state.ants[0]
    if not dice and labelled:
        for _ in range(8):
            speaking = sum(ant["said"] is not None for ant in app.session_state.ants)
            if speaking >= len(app.session_state.ants) * 0.6:
                break
            press("Next round")

    # Reported out of whatever this step happens to keep — an early one has
    # no stores and no requests to count.
    kept = app.session_state
    told = [f"round {kept.round}"] if "round" in kept else []
    for key, label in (("stores", "stored"), ("requests", "requests")):
        if key in kept:
            told.append(f"{kept[key]} {label}")
    if labelled:
        told.append(
            f"{sum(a['said'] is not None for a in kept.ants)} of "
            f"{len(kept.ants)} ants with a label"
        )
    print(", ".join(told) or "nothing to play")

    return svg_of(app)


def svg_of(app: AppTest) -> str:
    """The board out of the rendered page.

    `st.image` hands the SVG to the page as a data URI; this is the same string
    the browser draws.
    """
    source = next(e for e in app.main if type(e).__name__ == "Image").value[0]
    return base64.b64decode(re.sub(r"^data:image/svg\+xml;base64,", "", source)).decode()


def to_png(svg: str, out: Path, scale: int = 3, crop: str | None = None) -> None:
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

        if crop:
            # In cells, because that is how the board is talked about
            # everywhere else. CELL is 28 in the game.
            x, y, w, h = (int(n) for n in crop.split(","))
            cell = 28 * factor
            board = board.crop(
                (round(x * cell), round(y * cell), round((x + w) * cell), round((y + h) * cell))
            )

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
    parse.add_argument("--crop", help="x,y,w,h in cells")
    where = parse.parse_args()

    to_png(
        rendered_svg(where.order, where.rounds, where.dice, where.app),
        where.out if where.out.is_absolute() else ROOT / where.out,
        where.scale,
        where.crop,
    )

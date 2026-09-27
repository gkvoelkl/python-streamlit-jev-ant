"""Jev Ants — an ant colony that asks TypeSafe Jev what to do next.

Step 1: the board. A grid and nothing else, so that the one thing this step is
about — getting a picture on the page at all — has nothing to hide behind.

    uv run streamlit run app.py
"""

import streamlit as st

# The board in cells, and one cell in pixels. These are the numbers of level 1
# in the Bevy version of this game, so both play the same board.
COLUMNS = 24
ROWS = 16
CELL = 28

# Positions are counted from the top left, x to the right and y *downwards*,
# because that is how SVG counts and a second coordinate system in a program
# this size earns nothing. It costs one thing, later: north is y - 1.

DARK = "#2b2b33"
LIGHT = "#33333d"

st.set_page_config(page_title="Jev Ants", layout="wide")


def board() -> str:
    """The board as a single SVG.

    The chequerboard is a `pattern`: two squares described once and repeated by
    the browser, rather than 384 rectangles written out by hand. What that
    buys is not speed but reading — from the next step on, every element in
    this SVG is something that actually means something, and the floor is one
    line.
    """
    width = COLUMNS * CELL
    height = ROWS * CELL

    return f"""
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The board">
  <defs>
    <pattern id="chequer" width="{2 * CELL}" height="{2 * CELL}"
             patternUnits="userSpaceOnUse">
      <rect width="{2 * CELL}" height="{2 * CELL}" fill="{DARK}"/>
      <rect width="{CELL}" height="{CELL}" fill="{LIGHT}"/>
      <rect x="{CELL}" y="{CELL}" width="{CELL}" height="{CELL}" fill="{LIGHT}"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#chequer)"/>
</svg>
"""


st.title("Jev Ants")
st.caption(f"Step 1 — the board, {COLUMNS} by {ROWS}. Nothing lives on it yet.")

# `st.image` and not `st.html`, which is the obvious thing to reach for and
# silently draws nothing: it runs the string through a sanitiser that keeps
# HTML and throws SVG away, so the page ends up with an empty block and no
# error anywhere. `st.image` takes SVG as a string and is meant for exactly
# this. (`st.components.v1.html` would work too, but it wraps the board in an
# iframe of a height we would then have to keep in step with the board.)
st.image(board())

"""Jev Ants — an ant colony that asks TypeSafe Jev what to do next.

Step 2: one ant, and it asks. A key, one question per click, and the ant takes
the step the model names. Everything this game is about is already here — the
rest of the tutorial is about what the ant is shown and how it is asked.

    uv run streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient, TypeSafeError

# Reads `.env` into the environment if there is one. No key in the file is not
# an error — the sidebar asks for one instead.
load_dotenv()

COLUMNS = 24
ROWS = 16
CELL = 28

# Positions are counted from the top left, x to the right and y *downwards*,
# because that is how SVG counts and a second coordinate system in a program
# this size earns nothing. It costs one thing, here: north is y - 1.
#
# The eight directions are named rather than numbered, and that is not for
# readability. These names are what Jev is offered and what it answers with —
# "north-east" is a word a model understands, `(1, -1)` is not.
DIRECTIONS = {
    "north": (0, -1),
    "north-east": (1, -1),
    "east": (1, 0),
    "south-east": (1, 1),
    "south": (0, 1),
    "south-west": (-1, 1),
    "west": (-1, 0),
    "north-west": (-1, -1),
}

FLOOR_DARK = "#2b2b33"
FLOOR_LIGHT = "#33333d"
# Ants are dark and so is the floor. A pale disc under each one turns it into a
# game piece that can be found at a glance.
ANT_DISC = "#ded9cb"

# The question the ant is asked. It is a text, not code, and rewording it is
# the actual work in a project like this — so it sits here on its own, where it
# can be changed without reading the program.
STEP_QUESTION = (
    "An ant is standing on a board and has to decide where to go next. "
    "Which way should it go?"
)

st.set_page_config(page_title="Jev Ants", page_icon="🐜", layout="wide")


def api_key() -> str:
    """The key, from the sidebar if the player typed one, else from `.env`.

    The sidebar wins, so a key typed in beats a stale one in the file. What is
    typed lives in `st.session_state` for this session and is written nowhere —
    close the tab and it is gone.
    """
    return st.session_state.get("typed_key", "").strip() or os.getenv(
        "TYPESAFE_API_KEY", ""
    ).strip()


def start() -> None:
    """Puts the ant on the board, once.

    Streamlit runs this whole script again on every interaction, so anything
    that should survive a click lives in `st.session_state`. Setting it only
    when it is missing is what makes a rerun a redraw instead of a restart.
    """
    if "ant" in st.session_state:
        return

    st.session_state.ant = {"x": COLUMNS // 2, "y": ROWS // 2}
    st.session_state.said = None
    st.session_state.failure = None


def free_directions(ant: dict) -> list[str]:
    """The directions this ant could actually take, right now.

    Built from where the ant is, not from a list somewhere: off the board is
    not a direction. What comes back is what the model will be allowed to
    choose from, which is why these are names and not offsets.
    """
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            open_ways.append(name)
    return open_ways


def ask_jev(ant: dict) -> object:
    """One question about this ant, and the answer as it comes back.

    The **criteria** are the directions the ant can actually take, worked out a
    moment ago. They are not a fixed list of eight: an ant at the edge is not
    offered the edge. The model therefore cannot answer something impossible —
    the impossible was never on the menu. That is the whole idea of this game,
    and it is one line.

    The **state** is only what concerns this one ant. A state padded with
    things that do not matter makes the answer worse, and costs money per token
    besides.
    """
    ways = free_directions(ant)

    state = {"the ant is": "standing on open ground"}
    questions = {
        "step": Choice(instructions=STEP_QUESTION, criteria=dict.fromkeys(ways))
    }

    client = TypeSafeClient(api_key=api_key(), timeout=15)
    return client.system_one(state=state, questions=questions)


def take_a_step() -> None:
    """Ask, and move the ant where the answer says."""
    ant = st.session_state.ant

    try:
        answer = ask_jev(ant)
    except TypeSafeError as failed:
        # Everything the SDK can go wrong with comes back as a `TypeSafeError`
        # — a wrong key, a rate limit, a timeout, a refused body. The class
        # name is shown as well, because `TypeSafeAuthenticationError` means
        # something quite different from `TypeSafeRateLimitError`.
        st.session_state.said = None
        st.session_state.failure = f"{type(failed).__name__}: {failed}"
        return

    step = answer.choices["step"]
    dx, dy = DIRECTIONS[step.choice]
    ant["x"] += dx
    ant["y"] += dy

    st.session_state.failure = None
    st.session_state.said = {
        "choice": step.choice,
        "confidence": step.confidence,
        "probabilities": step.probabilities,
        "tokens": answer.usage.input_tokens,
        "model": answer.model,
    }


def cell_disc(x: int, y: int) -> str:
    """A pale round token in a cell, for something to be drawn on top of."""
    return (
        f'  <circle cx="{x * CELL + CELL / 2}" cy="{y * CELL + CELL / 2}" '
        f'r="{CELL * 0.42}" fill="{ANT_DISC}"/>'
    )


def cell_text(x: int, y: int, glyph: str, size: float = 0.7) -> str:
    """One glyph in the middle of one cell.

    `text-anchor` and `dominant-baseline` do the centring, so no caller ever
    has to know how wide a glyph is — and emoji are all different widths.
    """
    return (
        f'  <text x="{x * CELL + CELL / 2}" y="{y * CELL + CELL / 2}" '
        f'font-size="{CELL * size}" text-anchor="middle" '
        f'dominant-baseline="central">{glyph}</text>'
    )


def board() -> str:
    """The board as a single SVG.

    The chequerboard is a `pattern`: two squares described once and repeated by
    the browser, rather than 384 rectangles written out by hand. Everything
    drawn after it means something.
    """
    width = COLUMNS * CELL
    height = ROWS * CELL
    ant = st.session_state.ant

    return f"""
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The board">
  <defs>
    <pattern id="chequer" width="{2 * CELL}" height="{2 * CELL}"
             patternUnits="userSpaceOnUse">
      <rect width="{2 * CELL}" height="{2 * CELL}" fill="{FLOOR_DARK}"/>
      <rect width="{CELL}" height="{CELL}" fill="{FLOOR_LIGHT}"/>
      <rect x="{CELL}" y="{CELL}" width="{CELL}" height="{CELL}" fill="{FLOOR_LIGHT}"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#chequer)"/>
{cell_disc(ant["x"], ant["y"])}
{cell_text(ant["x"], ant["y"], "🐜")}
</svg>
"""


start()

st.title("🐜 Jev Ants")
st.caption("Step 2 — one ant, and every step it takes was decided by Jev.")

# `st.image` and not `st.html`, which is the obvious thing to reach for and
# silently draws nothing: it runs the string through a sanitiser that keeps
# HTML and throws SVG away, so the page ends up with an empty block and no
# error anywhere. `st.image` takes SVG as a string and is meant for exactly
# this.
st.image(board())

with st.sidebar:
    st.subheader("TypeSafe key")
    if os.getenv("TYPESAFE_API_KEY"):
        st.caption("Found in `.env`. Nothing to do.")
    else:
        st.text_input(
            "Key",
            key="typed_key",
            type="password",
            placeholder="paste your key",
            label_visibility="collapsed",
        )
        st.caption(
            "Used for this session only and stored nowhere. "
            "Get one at console.typesafe.ai/keys."
        )

# Without a key nothing moves, and there is no mode that would. The game exists
# to show what Jev decides; a board without it is an empty board.
if st.button("Ask Jev for a step", type="primary", disabled=not api_key()):
    with st.spinner("asking…"):
        take_a_step()
    st.rerun()

if not api_key():
    st.info("No key yet — the ant cannot ask anyone, so it does not move.")

if st.session_state.failure:
    st.error(st.session_state.failure)

if st.session_state.said:
    said = st.session_state.said

    chosen, sure, tokens = st.columns(3)
    chosen.metric("Chosen", said["choice"])
    sure.metric("Confidence", f"{said['confidence']:.2f}")
    tokens.metric("Input tokens", said["tokens"])

    # Every option with what the model thought of it. This is the picture worth
    # looking at: a clear answer is one tall bar, an ant with no reason to
    # prefer anything is eight similar ones.
    st.bar_chart(
        {"probability": dict(sorted(said["probabilities"].items()))},
        horizontal=True,
        height=260,
    )

    st.caption(
        f"Model {said['model']}. Confidence is not the highest probability — it is "
        "how far the answer sits from pure chance, scaled by how many options "
        "there were."
    )

"""Jev Ants — an ant colony that asks TypeSafe Jev what to do next.

Step 3: a colony. Eight ants instead of one, a board that comes from a file,
and all eight asked at the same time. Nobody stands on anybody, and the answers
are checked again when they are carried out.

    uv run streamlit run app.py
"""

import asyncio
import json
import os

import streamlit as st
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice

# Reads `.env` into the environment if there is one. No key in the file is not
# an error — the sidebar asks for one instead.
load_dotenv()

# One cell in pixels. Everything else about the board comes from the level.
CELL = 28

LEVEL_FILE = "level1.json"

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
NEST_FILL = "#3a3a2a"
NEST_EDGE = "#c8b24a"

# The question the ant is asked. It is a text, not code, and rewording it is
# the actual work in a project like this — so it sits here on its own, where it
# can be changed without reading the program.
STEP_QUESTION = (
    "An ant of a colony is standing on a board and has to decide where to go "
    "next. Which way should it go?"
)

st.set_page_config(page_title="Jev Ants", page_icon="🐜", layout="wide")


def load_level() -> dict:
    """The level as it is on disk.

    A level is data, not code: board size, where the nest sits, where the fruit
    lies, how many ants there are and how many fruits win. A second level is a
    second file, not a second version of the program.
    """
    with open(LEVEL_FILE, encoding="utf-8") as file:
        return json.load(file)


def api_key() -> str:
    """The key, from the sidebar if the player typed one, else from `.env`.

    The sidebar wins, so a key typed in beats a stale one in the file. What is
    typed lives in `st.session_state` for this session and is written nowhere —
    close the tab and it is gone.
    """
    return st.session_state.get("typed_key", "").strip() or os.getenv(
        "TYPESAFE_API_KEY", ""
    ).strip()


def start(level: dict) -> None:
    """Puts the colony on the board, once.

    Streamlit runs this whole script again on every interaction, so anything
    that should survive a click lives in `st.session_state`. Setting it only
    when it is missing is what makes a rerun a redraw instead of a restart.

    The ants start in the nest because that is where the game begins: a colony
    at home, waiting for a reason to leave.
    """
    if "ants" in st.session_state:
        return

    nest = level["nest"]
    st.session_state.ants = [
        {"x": nest["x"] + i % nest["size"], "y": nest["y"] + i // nest["size"]}
        for i in range(level["ants"])
    ]
    st.session_state.fruit = [tuple(cell) for cell in level["fruit"]]
    st.session_state.round = 0
    st.session_state.said = []
    st.session_state.failure = None


def taken_cells() -> set[tuple[int, int]]:
    """Every cell something is standing on.

    Ants and fruit in one set, because for the question this answers — may an
    ant step here — they are the same thing. An ant walks around a fruit, not
    over it.
    """
    return {(ant["x"], ant["y"]) for ant in st.session_state.ants} | set(
        st.session_state.fruit
    )


def free_directions(level: dict, ant: dict, taken: set[tuple[int, int]]) -> list[str]:
    """The directions this ant could actually take, right now.

    Built from where the ant is, not from a list somewhere: off the board is
    not a direction, and neither is a cell somebody is already on. What comes
    back is what the model is allowed to choose from, which is why these are
    names and not offsets.
    """
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        on_board = 0 <= x < level["columns"] and 0 <= y < level["rows"]
        if on_board and (x, y) not in taken:
            open_ways.append(name)
    return open_ways


def question_for(level: dict, ant: dict, taken: set[tuple[int, int]]) -> tuple[dict, dict]:
    """The state and the question for one ant: everything a request needs.

    The **criteria** are the directions this ant can actually take. They are
    not a fixed list of eight: an ant at the edge is not offered the edge, an
    ant with a neighbour in the way is not offered that neighbour. The model
    therefore cannot answer something impossible — the impossible was never on
    the menu.

    The **state** is only what concerns this one ant. A state padded with
    things that do not matter makes the answer worse, and costs money per token
    besides.
    """
    ways = free_directions(level, ant, taken)
    state = {"the ant is": "standing on open ground"}
    choice = Choice(instructions=STEP_QUESTION, criteria=dict.fromkeys(ways))
    return state, {"step": choice}


async def ask_everyone(payloads: list[tuple[dict, dict]], key: str) -> list[object]:
    """One request per ant, all of them at once.

    This is the one place in the program where async earns its keep. Eight
    requests of about half a second each are four seconds in a row and well
    under one side by side — and a round that takes four seconds is a game
    nobody watches.

    `return_exceptions=True` because one ant's bad luck is not the colony's: a
    failed request comes back as the exception itself and is dealt with where
    the answers are read.
    """
    async with AsyncTypeSafeClient(api_key=key, timeout=20) as client:
        return await asyncio.gather(
            *(client.system_one(state=state, questions=q) for state, q in payloads),
            return_exceptions=True,
        )


def next_round(level: dict) -> None:
    """One round: ask every ant, then do what came back.

    Asked first, all at once, and acted on afterwards. That means every answer
    was decided against the same board — so two ants can pick the same empty
    cell, and the check when the step is taken is what keeps them apart. An
    answer is a wish, not a move.
    """
    taken = taken_cells()
    payloads = [question_for(level, ant, taken) for ant in st.session_state.ants]
    answers = asyncio.run(ask_everyone(payloads, api_key()))

    st.session_state.said = []
    st.session_state.failure = None

    for ant, answer in zip(st.session_state.ants, answers):
        if isinstance(answer, BaseException):
            st.session_state.failure = f"{type(answer).__name__}: {answer}"
            st.session_state.said.append(None)
            continue

        step = answer.choices["step"]
        st.session_state.said.append((step.choice, step.confidence))

        dx, dy = DIRECTIONS[step.choice]
        target = (ant["x"] + dx, ant["y"] + dy)
        # Checked again here, because the board has moved on since the question
        # was asked.
        if target not in taken:
            taken.discard((ant["x"], ant["y"]))
            ant["x"], ant["y"] = target
            taken.add(target)

    st.session_state.round += 1


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


def board(level: dict) -> str:
    """The whole board as a single SVG.

    The chequerboard is a `pattern`: two squares described once and repeated by
    the browser, rather than 384 rectangles written out by hand. Everything
    drawn after it means something — the nest, the fruit, the ants.
    """
    width = level["columns"] * CELL
    height = level["rows"] * CELL
    nest = level["nest"]

    # The nest is floor like any other cell, so it gets an outline rather than
    # a solid block: a wall is the one thing it must not look like.
    nest_svg = (
        f'  <rect x="{nest["x"] * CELL}" y="{nest["y"] * CELL}" '
        f'width="{nest["size"] * CELL}" height="{nest["size"] * CELL}" '
        f'fill="{NEST_FILL}" stroke="{NEST_EDGE}" stroke-width="2"/>'
    )
    fruit_svg = "\n".join(cell_text(x, y, "🍎") for x, y in st.session_state.fruit)
    ants_svg = "\n".join(
        cell_disc(ant["x"], ant["y"]) + "\n" + cell_text(ant["x"], ant["y"], "🐜")
        for ant in st.session_state.ants
    )

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
{nest_svg}
{fruit_svg}
{ants_svg}
</svg>
"""


level = load_level()
start(level)

st.title("🐜 Jev Ants")
st.caption(f"Step 3 — {level['name']}. {level['briefing']}")

# `st.image` and not `st.html`, which is the obvious thing to reach for and
# silently draws nothing: it runs the string through a sanitiser that keeps
# HTML and throws SVG away, so the page ends up with an empty block and no
# error anywhere. `st.image` takes SVG as a string and is meant for exactly
# this.
st.image(board(level))

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

st.write(
    f"Round **{st.session_state.round}** · "
    f"**{len(st.session_state.ants)}** ants · "
    f"**{len(st.session_state.fruit)}** fruits on the board"
)

# Without a key nothing moves, and there is no mode that would. The game exists
# to show what Jev decides; a board without it is an empty board.
one, five, over = st.columns([1, 1, 5])
if one.button("Next round", type="primary", disabled=not api_key()):
    with st.spinner("eight ants are asking…"):
        next_round(level)
    st.rerun()

if five.button("Five rounds", disabled=not api_key()):
    with st.spinner("asking…"):
        for _ in range(5):
            next_round(level)
    st.rerun()

if over.button("Start over"):
    st.session_state.clear()
    st.rerun()

if not api_key():
    st.info("No key yet — the colony cannot ask anyone, so nothing moves.")

if st.session_state.failure:
    st.error(st.session_state.failure)

if st.session_state.said:
    # What each ant was told this round. It is a list for now; in a later step
    # it moves onto the board itself, where it belongs.
    st.caption(
        " · ".join(
            f"{number}: {choice} {confidence:.2f}" if choice else f"{number}: —"
            for number, said in enumerate(st.session_state.said, start=1)
            for choice, confidence in [said or (None, 0)]
        )
    )

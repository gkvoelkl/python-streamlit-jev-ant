"""Jev Ants — an ant colony that asks TypeSafe Jev what to do next.

Step 5: eyes. The ant is told what lies around it, and the options it is given
say where they would lead. Under both sits a floor: an answer that is barely
better than a coin toss is thrown away and counted, and the ant does nothing
that round.

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

# How far an ant sees, in cells. Small on purpose: an ant that saw the whole
# board would need nobody to tell it anything.
VISION_RADIUS = 3

# --- The trail home ------------------------------------------------------
#
# A searching ant marks the ground behind it, and the mark is weaker the
# further it has come from the nest. The strongest mark wins on a cell, so the
# peak of the whole field is the nest itself — and walking uphill is walking
# home. This is the one thing in the game an ant knows that it cannot see.
#
# The numbers are the ones the Bevy version measured its way to.

# What a searching ant leaves on the cell it just left, before the decay below.
SCENT_DEPOSIT = 1.0

# What is left of that with every step since the ant was last in the nest.
SCENT_STEP_DECAY = 0.88

# Rounds for a trail to fade to half. Evaporation is not decoration: it is how
# the colony forgets a way that leads nowhere any more.
SCENT_HALF_LIFE = 12.0

# Below this a cell counts as unscented, so old trails stop being offered.
SCENT_THRESHOLD = 0.05

# Answers below this are thrown away and the ant does nothing that round. The
# number is measured, not guessed — it comes from the Bevy version of this
# game. Mind what `confidence` means: how far the answer sits from pure chance,
# scaled by the number of options, not the highest probability.
MIN_CONFIDENCE = 0.22

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
SCENT_TINT = "#4f8f5c"
NEST_FILL = "#3a3a2a"
NEST_EDGE = "#c8b24a"

# The question the ant is asked. It is a text, not code, and rewording it is
# the actual work in a project like this — so it sits here on its own, where it
# can be changed without reading the program.
STEP_QUESTION = (
    "An ant of the colony has to decide which way to go next. The colony lives "
    "on fruit. An ant with empty hands searches: it walks towards any fruit it "
    "can see, and where it sees none it keeps going into open ground, away from "
    "the nest and away from the other ants, because ground another ant is "
    "already walking has nothing left on it. An ant carrying a fruit takes it "
    "to the nest. Which way should this ant go now?"
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
        {
            "x": nest["x"] + i % nest["size"],
            "y": nest["y"] + i // nest["size"],
            # One fruit at a time, and which fruit it is never matters — so a
            # flag, not an identity.
            "carrying": False,
            # Steps since this ant was last in the nest. It decides how much
            # scent it leaves: the further from home, the fainter the mark.
            "since_nest": 0,
        }
        for i in range(level["ants"])
    ]
    st.session_state.fruit = [tuple(cell) for cell in level["fruit"]]
    # How strongly each cell smells of the colony. Sparse on purpose — most
    # of the board never carries a trail, and the cells that do are few.
    st.session_state.scent = {}
    st.session_state.round = 0
    st.session_state.stores = 0
    st.session_state.requests = 0
    st.session_state.tokens = 0
    st.session_state.discarded = []
    st.session_state.said = []


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


def in_nest(level: dict, x: int, y: int) -> bool:
    """Is this cell part of the nest?"""
    nest = level["nest"]
    return (
        nest["x"] <= x < nest["x"] + nest["size"]
        and nest["y"] <= y < nest["y"] + nest["size"]
    )


def fruit_beside(ant: dict) -> tuple[int, int] | None:
    """The first fruit on one of the eight neighbouring cells, if there is one.

    Beside and not underneath: an ant never stands on a fruit, so picking one
    up is something that happens from the next cell over.
    """
    for dx, dy in DIRECTIONS.values():
        cell = (ant["x"] + dx, ant["y"] + dy)
        if cell in st.session_state.fruit:
            return cell
    return None


def pick_up_and_deliver(level: dict, ant: dict) -> None:
    """What follows from where the ant now stands.

    Neither of these is a decision the ant makes — they are consequences of
    walking. That matters for the bill: the model is asked where an ant should
    *go*, and picking up and putting down stay consequences. A question whose
    answer is the same nearly every time is a request paid for and thrown away.
    """
    if ant["carrying"]:
        if in_nest(level, ant["x"], ant["y"]):
            ant["carrying"] = False
            st.session_state.stores += 1
        return

    fruit = fruit_beside(ant)
    if fruit is not None:
        st.session_state.fruit.remove(fruit)
        ant["carrying"] = True


def steps_away(dx: int, dy: int) -> int:
    """How many steps apart two cells are when moving diagonally counts as one.

    A diagonal step covers as much ground as a straight one here, so the
    distance is the larger of the two offsets, not their sum.
    """
    return max(abs(dx), abs(dy))


def direction_of(dx: int, dy: int) -> str | None:
    """Which of the eight directions roughly points at an offset."""
    step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
    for name, offset in DIRECTIONS.items():
        if offset == step:
            return name
    return None


def phrase(dx: int, dy: int) -> str:
    """"2 cells to the north-east" — how far and which way, in words.

    Relative and never absolute. The ant is told what lies around it, not where
    it stands on a grid it cannot see, because a coordinate is a fact it has no
    way of using.
    """
    away = steps_away(dx, dy)
    return f"{away} cell{'' if away == 1 else 's'} to the {direction_of(dx, dy)}"


def nearest_nest_cell(level: dict, ant: dict) -> tuple[int, int]:
    """The corner or edge of the nest closest to this ant."""
    nest = level["nest"]
    return (
        min(max(ant["x"], nest["x"]), nest["x"] + nest["size"] - 1),
        min(max(ant["y"], nest["y"]), nest["y"] + nest["size"] - 1),
    )


def vision(level: dict, ant: dict) -> list[str]:
    """What this ant can see, as sentences.

    Fruit and other ants within `VISION_RADIUS`, and — only for an ant that is
    carrying something — the nest, at any distance. Real ants find their way
    home by counting their own steps, and this port has no pheromone trails to
    do the job instead; without it a loaded ant would be as lost as a random
    one.

    Only when carrying, and that is not a detail. Told where home is, an ant
    with empty hands walks there: the question says the colony brings fruit to
    the nest, so the nest is the thing in the state that sounds like an
    instruction. The first version of this function mentioned it always, and
    the whole colony sat at home for twenty-two rounds without touching a
    single fruit. What is in the state *is* the behaviour.
    """
    seen = []

    for x, y in st.session_state.fruit:
        dx, dy = x - ant["x"], y - ant["y"]
        if steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"a fruit, {phrase(dx, dy)}")

    for other in st.session_state.ants:
        dx, dy = other["x"] - ant["x"], other["y"] - ant["y"]
        if other is not ant and steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"another ant, {phrase(dx, dy)}")

    # The nest only when it is actually in sight. Before the trail existed it
    # was named from anywhere, which was a shortcut with a note attached: real
    # ants do not know where home is, they follow what the colony left on the
    # ground. Now they can, so the shortcut goes.
    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        if 0 < near <= VISION_RADIUS:
            seen.append(f"the nest, {phrase(nx - ant['x'], ny - ant['y'])}")

        # And the trail, which is the whole point: a sense, not a sight.
        way = uphill(ant)
        if way:
            seen.append(
                f"a {describe_scent(way[1])} smell of the colony, "
                f"1 cell to the {way[0]}"
            )

    return seen


def options(level: dict, ant: dict, taken: set[tuple[int, int]]) -> dict[str, str | None]:
    """What this ant may choose from, and what lies that way.

    The keys are the directions that are actually open — `free_directions` from
    step 3. The values say what the ant would be heading towards, and they are
    written fresh every round out of what it sees. A direction with nothing
    interesting in it gets no description, and that is honest: there is nothing
    to say about it.

    This is the whole idea in one dictionary. The model is not trusted to avoid
    impossible answers; it is never shown one.
    """
    ways = free_directions(level, ant, taken)
    towards: dict[str, str] = {}

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        home = direction_of(nx - ant["x"], ny - ant["y"])
        if home and 0 < near <= VISION_RADIUS:
            towards[home] = f"towards the nest, {phrase(nx - ant['x'], ny - ant['y'])}"

        # Uphill, for an ant that cannot see the nest from here. It is offered
        # as what it is — a smell that grows stronger, not a route.
        way = uphill(ant)
        if way and way[0] not in towards:
            towards[way[0]] = f"the smell of the colony gets {describe_scent(way[1])}er"
    else:
        visible = [
            (steps_away(x - ant["x"], y - ant["y"]), x, y)
            for x, y in st.session_state.fruit
            if steps_away(x - ant["x"], y - ant["y"]) <= VISION_RADIUS
        ]
        for _, x, y in sorted(visible):
            way = direction_of(x - ant["x"], y - ant["y"])
            if way:
                towards.setdefault(
                    way, f"towards a fruit, {phrase(x - ant['x'], y - ant['y'])}"
                )

    return {way: towards.get(way) for way in ways}


def describe_scent(strength: float) -> str:
    """How a trail is put to an ant: a word, never a number.

    A number would promise a precision the field does not have, and the model
    reads words better than it reads 0.41.
    """
    if strength >= 0.7:
        return "strong"
    return "clear" if strength >= 0.3 else "faint"


def lay_scent(level: dict, ant: dict) -> None:
    """What a searching ant leaves behind on the cell it stands on.

    Only a **searching** ant marks the ground, and the mark is weaker the
    further it has come from the nest. That is what gives the field a shape:
    its peak is the nest, so uphill is homeward.

    The strongest mark wins; they do not add up. Adding looks right and is
    wrong — a hundred faint traces out in the open would then outweigh one
    strong mark near the nest, and the slope would point away from home.
    Traffic still counts, only differently: a path walked again is marked
    again and so outlives evaporation.
    """
    if in_nest(level, ant["x"], ant["y"]):
        ant["since_nest"] = 0
    else:
        ant["since_nest"] += 1

    if ant["carrying"]:
        return

    cell = (ant["x"], ant["y"])
    amount = SCENT_DEPOSIT * SCENT_STEP_DECAY ** ant["since_nest"]
    st.session_state.scent[cell] = max(st.session_state.scent.get(cell, 0.0), amount)


def evaporate() -> None:
    """One round of time passing. What falls under the threshold is dropped."""
    factor = 0.5 ** (1 / SCENT_HALF_LIFE)
    st.session_state.scent = {
        cell: strength * factor
        for cell, strength in st.session_state.scent.items()
        if strength * factor >= SCENT_THRESHOLD
    }


def uphill(ant: dict) -> tuple[str, float] | None:
    """The neighbouring cell that smells strongest, if it beats this one.

    Standing on the peak gives `None`, and that is not a failure: the peak is
    at the nest, and an ant standing there has arrived.
    """
    here = st.session_state.scent.get((ant["x"], ant["y"]), 0.0)
    best = None
    for name, (dx, dy) in DIRECTIONS.items():
        strength = st.session_state.scent.get((ant["x"] + dx, ant["y"] + dy), 0.0)
        if strength >= SCENT_THRESHOLD and strength > here:
            if best is None or strength > best[1]:
                best = (name, strength)
    return best


def question_for(level: dict, ant: dict, taken: set[tuple[int, int]]) -> tuple[dict, dict]:
    """The state and the question for one ant: everything a request needs.

    The **criteria** come from `options`: the directions this ant can take, each
    with what lies that way. Not a fixed list of eight — an ant at the edge is
    not offered the edge — so the model cannot answer something impossible.

    The **state** now includes what the ant sees, which is the change this step
    is about.

    The **state** is only what concerns this one ant. A state padded with
    things that do not matter makes the answer worse, and costs money per token
    besides.
    """
    state = {
        "the ant is carrying": "a fruit" if ant["carrying"] else "nothing",
        "the ant is": "in the nest"
        if in_nest(level, ant["x"], ant["y"])
        else "out on the board",
        "the ant can see": vision(level, ant) or ["nothing at all"],
    }
    choice = Choice(instructions=STEP_QUESTION, criteria=options(level, ant, taken))
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


def accepted(answer: object, offered: dict[str, str | None]) -> str | None:
    """The direction to act on, or `None` with a reason written down.

    Three ways an answer is refused, and all three are counted rather than
    quietly patched over:

    * the request failed — `asyncio.gather` handed back the exception itself;
    * the answer names something that was never offered;
    * the answer is barely better than a coin toss.

    There is no fallback. A refused answer means this ant does nothing this
    round, and it will be asked again in the next one. A colony that kept
    working on rules whenever the model faltered would hide exactly what this
    game is built to show.
    """
    if isinstance(answer, BaseException):
        st.session_state.discarded.append(type(answer).__name__)
        return None

    step = answer.choices["step"]
    st.session_state.tokens += answer.usage.input_tokens

    if step.choice not in offered:
        st.session_state.discarded.append(f"{step.choice} was never offered")
        return None

    if step.confidence < MIN_CONFIDENCE:
        st.session_state.discarded.append(f"{step.choice} at {step.confidence:.2f}")
        return None

    return step.choice


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

    st.session_state.requests += len(payloads)
    st.session_state.said = []

    for ant, (_, question), answer in zip(st.session_state.ants, payloads, answers):
        way = accepted(answer, question["step"].criteria)
        st.session_state.said.append(
            (way, answer.choices["step"].confidence) if way is not None else None
        )

        if way is None:
            before = set(st.session_state.fruit)
            pick_up_and_deliver(level, ant)
            taken -= before - set(st.session_state.fruit)
            continue

        dx, dy = DIRECTIONS[way]
        target = (ant["x"] + dx, ant["y"] + dy)
        # Checked again here, because the board has moved on since the question
        # was asked.
        if target not in taken:
            taken.discard((ant["x"], ant["y"]))
            ant["x"], ant["y"] = target
            taken.add(target)

        # After the step, not before: a fruit picked up here is gone from
        # `taken` for everybody who moves after this ant.
        before = set(st.session_state.fruit)
        pick_up_and_deliver(level, ant)
        taken -= before - set(st.session_state.fruit)

        # Marked after the step, so the trail records where the ant went.
        lay_scent(level, ant)

    evaporate()
    st.session_state.round += 1


def cell_disc(x: int, y: int) -> str:
    """A pale round token in a cell, for something to be drawn on top of."""
    return (
        f'  <circle cx="{x * CELL + CELL / 2}" cy="{y * CELL + CELL / 2}" '
        f'r="{CELL * 0.42}" fill="{ANT_DISC}"/>'
    )


def cell_text(x: int, y: int, glyph: str, size: float = 0.7, lift: float = 0.0) -> str:
    """One glyph in a cell: middle by default, `lift` cells higher if asked.

    `text-anchor` and `dominant-baseline` do the centring, so no caller ever
    has to know how wide a glyph is — and emoji are all different widths.
    """
    return (
        f'  <text x="{x * CELL + CELL / 2}" y="{(y - lift) * CELL + CELL / 2}" '
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
    # The trail, tinted into the floor. It is ground, not an object, so it is
    # drawn under everything and never brighter than the ants.
    scent_svg = "\n".join(
        f'  <rect x="{x * CELL}" y="{y * CELL}" width="{CELL}" height="{CELL}" '
        f'fill="{SCENT_TINT}" fill-opacity="{min(0.55, strength * 0.55):.2f}"/>'
        for (x, y), strength in st.session_state.scent.items()
    )

    nest_svg = (
        f'  <rect x="{nest["x"] * CELL}" y="{nest["y"] * CELL}" '
        f'width="{nest["size"] * CELL}" height="{nest["size"] * CELL}" '
        f'fill="{NEST_FILL}" stroke="{NEST_EDGE}" stroke-width="2"/>'
    )
    fruit_svg = "\n".join(cell_text(x, y, "🍎") for x, y in st.session_state.fruit)
    # A carried fruit is drawn small and high in the cell, so that a loaded ant
    # can be told from an empty one across the board.
    ants_svg = "\n".join(
        cell_disc(ant["x"], ant["y"])
        + "\n"
        + cell_text(ant["x"], ant["y"], "🐜")
        + (
            "\n" + cell_text(ant["x"], ant["y"], "🍎", size=0.45, lift=0.3)
            if ant["carrying"]
            else ""
        )
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
{scent_svg}
{nest_svg}
{fruit_svg}
{ants_svg}
</svg>
"""


level = load_level()
start(level)

st.title("🐜 Jev Ants")
st.caption(f"Step 5 — {level['name']}. {level['briefing']}")

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

won = st.session_state.stores >= level["target"]
carried = sum(ant["carrying"] for ant in st.session_state.ants)

st.write(
    f"Round **{st.session_state.round}** · "
    f"**{st.session_state.stores}** of {level['target']} stored · "
    f"**{carried}** carried · "
    f"**{len(st.session_state.fruit)}** on the board · "
    f"**{st.session_state.requests}** decisions from Jev, "
    f"**{len(st.session_state.discarded)}** discarded"
)

if won:
    st.success(
        f"The stores are full — {level['target']} fruits home in "
        f"{st.session_state.round} rounds."
    )

# Without a key nothing moves, and there is no mode that would. The game exists
# to show what Jev decides; a board without it is an empty board.
one, five, over = st.columns([1, 1, 5])
ready = bool(api_key()) and not won

if one.button("Next round", type="primary", disabled=not ready):
    with st.spinner("eight ants are asking…"):
        next_round(level)
    st.rerun()

if five.button("Five rounds", disabled=not ready):
    with st.spinner("asking…"):
        for _ in range(5):
            if st.session_state.stores >= level["target"]:
                break
            next_round(level)
    st.rerun()

if over.button("Start over"):
    st.session_state.clear()
    st.rerun()

if not api_key():
    st.info("No key yet — the colony cannot ask anyone, so nothing moves.")

if st.session_state.discarded:
    with st.expander(f"{len(st.session_state.discarded)} answers thrown away"):
        # Worth reading rather than hiding. Most of them are not a weak model
        # but a badly put question, and this is where you notice.
        for reason in st.session_state.discarded[-12:]:
            st.write(f"· {reason}")

if st.session_state.said:
    # What each ant was told this round. It is a list for now; in step 7 it
    # moves onto the board itself, where it belongs.
    st.caption(
        " · ".join(
            f"{number}: {said[0]} {said[1]:.2f}" if said else f"{number}: —"
            for number, said in enumerate(st.session_state.said, start=1)
        )
    )

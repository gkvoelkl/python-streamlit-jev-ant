# Step 3 — The ant colony

*[Deutsche Fassung](../de/03-die-kolonie.md) · Translated from the German original.*

![Several worker ants in colourful helmets stand spread out on the glowing
board between fruit and the nest, each with a speech bubble full of question
marks; from each a glowing line leads to a large golden “Jev” above the
board](../bilder/schritt-3-titel.png)

*They all ask at once, and they all ask the same model.*

**Goal:** Eight ants instead of one, the board read from a file, and a way
asked of the decision model for all eight at the same time.

![The board of step 3: eight ants have left the nest and are spreading out,
the eight fruits lying between them](../bilder/schritt-3-kolonie.png)

*After five rounds. The fruit lies around, but nobody can do anything with it
yet — that is chapter 4.*

The approach from chapter 2 stays unchanged. What is new is the question of
how to steer eight ants without a round taking four seconds.

## The level as a file

In the first level the ants' task is to bring as much of their food (fruit) as
they can into the nest.

`level1.json`:

```json
{
  "name": "Fruit for the stores",
  "briefing": "Eight ants, fruit scattered about, nothing in the way. Get five of them home.",

  "columns": 24,
  "rows": 16,

  "nest": { "x": 10, "y": 6, "size": 4 },
  "ants": 8,

  "fruit": [
    [3, 13], [5, 3], [18, 12], [20, 4],
    [2, 7], [21, 8], [12, 1], [14, 14]
  ],

  "target": 5
}
```

This description of the level is kept in a file that the Python program reads
at the start. That makes it possible to extend the game with any number of
levels.

`COLUMNS` and `ROWS` disappear from the program, because they come from the
level file. That way levels can differ in size.

```python
def load_level() -> dict:
    with open(LEVEL_FILE, encoding="utf-8") as file:
        return json.load(file)
```

## Eight ants in the nest

![Close-up of the nest: eight ants sit in two rows of four in the square with
the yellow border](../bilder/bau-start.png)

*The starting line-up: `i % size` and `i // size` spread the eight over the
first rows.*

```python
    nest = level["nest"]
    st.session_state.ants = [
        {"x": nest["x"] + i % nest["size"], "y": nest["y"] + i // nest["size"]}
        for i in range(level["ants"])
    ]
    st.session_state.fruit = [tuple(cell) for cell in level["fruit"]]
    st.session_state.round = 0
```

`i % size` and `i // size` spread the eight over the first rows of the nest.
That they start there is not a whim of placement: the colony is at home and
waiting for a reason to do something.

## Which square is already taken?

```python
def taken_cells() -> set[tuple[int, int]]:
    return {(ant["x"], ant["y"]) for ant in st.session_state.ants} | set(
        st.session_state.fruit
    )
```

The program keeps in the **set taken** which squares (cells) already hold an
ant or a fruit.

Ants and fruit go into **one** set, because for this question they answer the
same thing:

May anyone step here? Is the square free?

`free_directions` gets the **set taken** added to its check:

```python
def free_directions(level: dict, ant: dict, taken: set[tuple[int, int]]) -> list[str]:
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        on_board = 0 <= x < level["columns"] and 0 <= y < level["rows"]
        if on_board and (x, y) not in taken:
            open_ways.append(name)
    return open_ways
```

With that, the options the decision model gets are one step closer to
reality: no edge, and no square that already holds an ant or a fruit.

## Eight requests at once

This is where `async` pays off.

```python
async def ask_everyone(payloads, key) -> list[object]:
    async with AsyncTypeSafeClient(api_key=key, timeout=20) as client:
        return await asyncio.gather(
            *(client.system_one(state=state, questions=q) for state, q in payloads),
            return_exceptions=True,
        )
```

Eight requests, one per ant, one after the other at half a second each, add up
to four seconds. Sent off at the same time (asynchronously), these requests
bring all the answers back much faster.

Measured: **about 0.6 seconds for a complete round.**

`return_exceptions=True` makes sure that one ant's bad luck is not the
colony's: a failed request comes back as an exception object instead of
dragging the other seven down with it.

It is called from the ordinary, synchronous Streamlit flow with
`asyncio.run(...)`.

## The round

```python
def next_round(level: dict) -> None:
    taken = taken_cells()
    payloads = [question_for(level, ant, taken) for ant in st.session_state.ants]
    answers = asyncio.run(ask_everyone(payloads, api_key()))

    for ant, answer in zip(st.session_state.ants, answers):
        ...
        dx, dy = DIRECTIONS[step.choice]
        target = (ant["x"] + dx, ant["y"] + dy)
        if target not in taken:
            taken.discard((ant["x"], ant["y"]))
            ant["x"], ant["y"] = target
            taken.add(target)

    st.session_state.round += 1
```

![How a round runs: first a picture of the board, then one question for each of
the eight ants, all requests at the same time through asyncio.gather, then the
answers carried out one after the other with a check whether the target square
is still free](../bilder/en/runde.png)

First **all** ask, then all act. That has a consequence that is easy to
overlook: every answer is decided on the basis of **the same** board.

If two happen to choose the same square, the check `if target not in taken`
catches it when the moves are carried out.

> An answer is a wish, not yet a move.

## Drawing

The nest gets an **outline** instead of a fill:

```python
    nest_svg = (
        f'  <rect x="{nest["x"] * CELL}" y="{nest["y"] * CELL}" '
        f'width="{nest["size"] * CELL}" height="{nest["size"] * CELL}" '
        f'fill="{NEST_FILL}" stroke="{NEST_EDGE}" stroke-width="2"/>'
    )
```

![The same close-up after three rounds: two ants are still in the nest, six
are out and standing on the ground around it](../bilder/bau-durchlaessig.png)

*Three rounds later. You can see why the nest is an outline and not a fill:
the ants walk through it and beyond. A solid block would look like an
obstacle.*

Emojis are well suited for drawing the game pieces. The fruits are 🍎 and the
ants are 🐜. The ants also get a light background, so that they are easier to
spot on the board.

```python
    fruit_svg = "\n".join(cell_text(x, y, "🍎") for x, y in st.session_state.fruit)
    ants_svg = "\n".join(
        cell_disc(ant["x"], ant["y"]) + "\n" + cell_text(ant["x"], ant["y"], "🐜")
        for ant in st.session_state.ants
    )
```

With emojis as game pieces you save yourself extra image files.

## Try it

* Press “Next round”: the colony comes out of the nest. The answers are shown
  below — my first round was `north 0.39 · north 0.68 · north 0.67 ·
  north 0.37 · west 0.26 · south 0.30 · south 0.32 · east 0.29`.
* Four of eight wanted to go north. At this confidence that is not a plan but
  a slight lean of the model when nothing steers it.
* Press “Five rounds” and look at the clock — eight ants times five rounds are
  forty requests in a few seconds.
* Change `"ants"` in `level1.json` to 20 and reload. Nothing happens, because
  `start()` only sets up the colony when there is none. That is what “Start
  over” is for — and with twenty ants in the nest you will see how tight it
  gets.

---

*This tutorial was created by Gerhard Völkl using Claude Code (Anthropic). It is meant to help you learn more about what happens when ants ask a decision model. Suggestions for improvement are welcome at gkvoelkl@nelson-games.de.*

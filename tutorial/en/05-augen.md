# Step 5 — Seeing

*[Deutsche Fassung](../de/05-augen.md) · Translated from the German original.*

![The worker ant in the white helmet now wears round glasses and points at a
glowing pear; around her a bright circle on the board, outside it darkness and
fog, in the distance the nest and a green
trail](../bilder/schritt-5-titel.png)

*As far as she sees, so far the choice reaches.*

**Goal:** The ant sees what is going on around it, plus a threshold below which
an answer is thrown away.

![The board of step 5 after twelve rounds: the ants spread out, two carrying a
fruit, the ground around the nest green from the scent
trail](../bilder/schritt-5-sehen.png)

*Twelve rounds, three fruits in the stores. The green is the trail — it is
made further down in this chapter.*

Up to here the decision model has more or less guessed, because there was
nothing in the state from which anything could be concluded. That changes now
— and the colony starts to work.

## Distance and direction in words

```python
def steps_away(dx: int, dy: int) -> int:
    return max(abs(dx), abs(dy))


def direction_of(dx: int, dy: int) -> str | None:
    step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
    for name, offset in DIRECTIONS.items():
        if offset == step:
            return name
    return None


def phrase(dx: int, dy: int) -> str:
    away = steps_away(dx, dy)
    return f"{away} cell{'' if away == 1 else 's'} to the {direction_of(dx, dy)}"
```

`steps_away` measures in steps, not as the crow flies: a diagonal step gets as
far as a straight one, so the larger of the two distances counts.

`phrase` makes sentences like `2 cells to the north-east`. Always **relative,
never absolute.**

The ant learns what lies around it — not where on the board it stands. A
coordinate would be a piece of data it can do nothing with.

## The field of vision

```python
VISION_RADIUS = 3


def vision(level: dict, ant: dict) -> list[str]:
    seen = []

    for x, y in st.session_state.fruit:
        dx, dy = x - ant["x"], y - ant["y"]
        if steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"a fruit, {phrase(dx, dy)}")

    for other in st.session_state.ants:
        dx, dy = other["x"] - ant["x"], other["y"] - ant["y"]
        if other is not ant and steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"another ant, {phrase(dx, dy)}")

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        if 0 < near <= VISION_RADIUS:
            seen.append(f"the nest, {phrase(nx - ant['x'], ny - ant['y'])}")

        ...  # and the trail, further down

    return seen
```

The ant sees three squares in every direction, and that is not much — on
purpose. Later (chapter 6) the queen overlooks the whole board and the single
ant does not. That difference is what makes the queen's orders valuable later.

![The field of vision: a window of seven by seven squares around the ant; a
fruit three squares away lies inside it, one four squares away no
longer does](../bilder/en/sichtweite.png)

The nest is named when it is within sight, and only to an ant that is carrying
something. Further down this is complemented by what real ants really have: a
scent trail.

And in the state:

```python
        "the ant can see": vision(level, ant) or ["nothing at all"],
```

## The options say something now

Until now the options for the answer were a list of names. Now every direction
gets a description — when there is something to describe:

```python
def options(level: dict, ant: dict, taken: set[tuple[int, int]]) -> dict[str, str | None]:
    ways = free_directions(level, ant, taken)
    towards: dict[str, str] = {}

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        home = direction_of(nx - ant["x"], ny - ant["y"])
        if home and 0 < near <= VISION_RADIUS:
            towards[home] = f"towards the nest, {phrase(nx - ant['x'], ny - ant['y'])}"

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
                towards.setdefault(way, f"towards a fruit, {phrase(...)}")

    return {way: towards.get(way) for way in ways}
```

The **keys** are the open directions, as they have been since chapter 2. The
**values** say where going that way would lead, and they are made anew every
round from what this ant sees. A direction in which nothing interesting lies
gets no description — that is honest, there is nothing to say about it.

Remember `dict.fromkeys(ways)` from chapter 2: there was `None` everywhere. Now
there are sentences. Nothing about the type has changed.

### A real example

This was recorded from a running game, round 5. The ant sees a fruit and a
colleague:

```json
"the ant can see": [
  "a fruit, 3 cells to the north-west",
  "another ant, 2 cells to the south-west"
]
```

And this is what it gets to choose from:

```json
{
  "north":      null,
  "north-east": null,
  "east":       null,
  "south-east": null,
  "south":      null,
  "south-west": null,
  "west":       null,
  "north-west": "towards a fruit, 3 cells to the north-west"
}
```

Eight directions, one of them labelled. The other seven stand there without a
comment, because there is nothing to say about them — and that is exactly the
information: there is only one reason, and it points north-west.

The same ant two rounds later, now with a fruit on its back:

```json
"the ant can see": ["a clear smell of the colony, 1 cell to the south-east"]
```

```json
{ "south-east": "the smell of the colony gets clearer", ... }
```

## A threshold

```python
MIN_CONFIDENCE = 0.22


def accepted(answer: object, offered: dict[str, str | None]) -> str | None:
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
```

Three ways to reject an answer — and all three are **counted**, not quietly
glossed over. An expandable section below the board shows them with the
reason.

Expanded, it looks like this — six lines from a real run:

```
· north-east at 0.18
· north-west at 0.18
· north-east at 0.16
· north at 0.15
· north-east at 0.13
· north at 0.17
```

All just below the threshold, and all pointing north. That is not chance but
the same slight preference of the model that pushed half the colony to the top
edge in chapter 4. When nothing speaks for one direction, it comes through —
and the threshold catches it.

`MIN_CONFIDENCE = 0.22` is measured, not guessed. It is lower than you might
expect, and that is because of what confidence measures: the distance from pure
chance, normalised by the number of options. With eight options, 0.22 is
already a recognisable preference.

![The confidence scale from 0 to 1 with the threshold at 0.22 and the
conversion: with eight options this corresponds to a highest probability of
0.32](../bilder/en/schwelle.png)

The second check — `step.choice not in offered` — is the safeguard against the
case where the model names something that was never offered. For me it has
never fired; that is exactly the point of the whole construction. But you
check rather than trust.

A rejected answer means: this ant does nothing this round and is asked again
next round.

## The trail home

Up to here an ant with a fruit only knows where its nest is when the nest is in
sight — that is, within three squares out of 384. That is not enough.

Real ants do not only use their eyes, they use a **scent trail**: they leave a
trail behind, and the way back is the direction in which it gets stronger.

```python
# What a searching ant leaves on the cell it just left, before the decay below.
SCENT_DEPOSIT = 1.0

# What is left of that with every step since the ant was last in the nest.
SCENT_STEP_DECAY = 0.88

# Rounds for a trail to fade to half. Evaporation is not decoration: it is how
# the colony forgets a way that leads nowhere any more.
SCENT_HALF_LIFE = 12.0

# Below this a cell counts as unscented, so old trails stop being offered.
SCENT_THRESHOLD = 0.05
```

### Laid while searching, not while carrying

```python
def lay_scent(level: dict, ant: dict) -> None:
    if in_nest(level, ant["x"], ant["y"]):
        ant["since_nest"] = 0
    else:
        ant["since_nest"] += 1

    if ant["carrying"]:
        return

    cell = (ant["x"], ant["y"])
    amount = SCENT_DEPOSIT * SCENT_STEP_DECAY ** ant["since_nest"]
    st.session_state.scent[cell] = max(st.session_state.scent.get(cell, 0.0), amount)
```

![Close-up of the nest after eighteen rounds: the ground all around is
coloured green, most strongly close to the nest; one ant is just bringing in a
fruit](../bilder/spur-nahaufnahme.png)

*The colony's roads. The closer to the nest, the stronger the scent — which is
why uphill leads home.*

Only a **searching** ant marks the ground, and the mark is the weaker the
further it is from the nest. That gives the field a shape: the highest value is
in the nest. **Uphill is homeward.**

For this every ant counts its own steps since the nest — `since_nest`. The
program resets it as soon as the ant is back inside.

### The strongest deposit wins, they do not add up

`max(...)` is better than `+=`. If the deposits were added up, a hundred weak
trails far out would beat a strong one at the nest. Traffic still counts, just
differently: a path walked often is marked anew often and so survives
evaporation.

### Evaporation

```python
def evaporate() -> None:
    factor = 0.5 ** (1 / SCENT_HALF_LIFE)
    st.session_state.scent = {
        cell: strength * factor
        for cell, strength in st.session_state.scent.items()
        if strength * factor >= SCENT_THRESHOLD
    }
```

This is not cosmetics but the colony's memory: this is how it forgets a path
that no longer leads anywhere. And because everything below the threshold
drops out, the dictionary stays small — on a 24 × 16 board it is rarely more
than eighty squares.

### Uphill

```python
def uphill(ant: dict) -> tuple[str, float] | None:
    here = st.session_state.scent.get((ant["x"], ant["y"]), 0.0)
    best = None
    for name, (dx, dy) in DIRECTIONS.items():
        strength = st.session_state.scent.get((ant["x"] + dx, ant["y"] + dy), 0.0)
        if strength >= SCENT_THRESHOLD and strength > here:
            if best is None or strength > best[1]:
                best = (name, strength)
    return best
```

On the summit there is nothing further up, and `uphill` returns `None`. That is
not a failure: the summit is the nest, and whoever stands there has arrived.

### As a sentence, not as a number

```python
def describe_scent(strength: float) -> str:
    if strength >= 0.7:
        return "strong"
    return "clear" if strength >= 0.3 else "faint"
```

The state then says:

```
a clear smell of the colony, 1 cell to the north-west
```

A number like 0.41 would promise a precision the field does not have, and the
model reads words better anyway. The same reasoning as for the field of
vision: what is said is what the ant *notices*, not what is in memory.

### What it brings

Three versions, the same order, two runs each:

| | Rounds to five fruits |
|---|---|
| **Trail** | 16 · 17 |
| Shortcut (nest visible from everywhere) | 18 · 16 |
| neither trail nor shortcut | 2 of 5 after 40 rounds — not made |

The trail is **as good as perfect information**. It catches up exactly what the
shortcut simply gave away — only this time the colony earns it itself, square
by square.

And the third line shows that something really happens here: without either,
the colony does not reach the goal.

## The question says more now

The text has changed along with it:

> An ant of the colony has to decide which way to go next. The colony lives on
> fruit. An ant with empty hands searches: it walks towards any fruit it can
> see, and where it sees none it keeps going into open ground, away from the
> nest and away from the other ants, because ground another ant is already
> walking has nothing left on it. An ant carrying a fruit takes it to the nest.
> Which way should this ant go now?

Before, it only said what the colony does as a whole. Now it says what an ant
with empty hands is to do.

## Try it

* Watch a single ant when a fruit comes into its field of vision.

* Expand the discarded answers. Who discards — the ants in the crowd or the
  ones out in the open?

* Set `VISION_RADIUS` to 1. The colony gets much worse, and the number of
  discards goes up.

* Set `VISION_RADIUS` to 8. Does it get better? And what happens to the token
  count?

* Set `MIN_CONFIDENCE` to 0.0: now every answer is accepted, even the guessed
  ones. Does the colony get faster or slower?

* Take the sentence about fanning out out of `STEP_QUESTION` and start again.
  It is worth having seen this once yourself.

* Watch the board turn green: the trail grows most where many ants walk, and
  the brightest spot is in the nest.

* Set `SCENT_HALF_LIFE` to 2 rounds. The trail evaporates before anyone can use
  it — and the colony is as helpless as in the third line of the table above.

* In `lay_scent`, swap the `max(...)` for `+=`. The deposits then add up, the
  summit moves out of the nest to where there is the most traffic — and the
  carriers walk in the wrong direction. That is the most instructive mistake you
  can build into this program.

---

*This tutorial was created by Gerhard Völkl using Claude Code (Anthropic). It is meant to help you learn more about what happens when ants ask a decision model. Suggestions for improvement are welcome at gkvoelkl@nelson-games.de.*

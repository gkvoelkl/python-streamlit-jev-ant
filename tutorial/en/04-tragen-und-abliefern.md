# Step 4 — Carrying and delivering

*[Deutsche Fassung](../de/04-tragen-und-abliefern.md) · Translated from the German original.*

![A worker ant in a white helmet hauls a large red apple across the board and
walks away from the nest, which lies just behind her; next to her a lit board
shows “0/5”](../bilder/schritt-4-titel.png)

*She can carry now. She cannot see yet.*

**Goal:** An ant that passes a fruit picks it up. If it gets into the nest with
it, the fruit goes into the stores. As soon as five fruits are in the nest, the
level is won.

![The board of step 4 after 25 rounds: several ants stand at the top edge, one
of them carrying a fruit, two sit in the nest, the fruit lies
untouched](../bilder/schritt-4-tragen.png)

*Twenty-five rounds, not a single piece in the stores. Why that is comes
further down — and it is more revealing than it looks.*

With this the game is complete — there is a goal, a way to it and an end. The
decision model decides every step, but the ants cannot see and nobody tells
them anything. They stumble into fruit and into the nest.

The next two chapters work on that.

## An ant carries something

In `start()` every ant gets one more field:

```python
        {
            "x": nest["x"] + i % nest["size"],
            "y": nest["y"] + i // nest["size"],
            "carrying": False,
        }
```

An ant carries at most one fruit, and which one it is never matters. So the
truth value `carrying` is enough — an identity would be a piece of data nobody
ever reads.

Plus the stores counter, how many fruits are already in the nest:

```python
    st.session_state.stores = 0
```

## Where is the nest? Where is fruit?

```python
def in_nest(level: dict, x: int, y: int) -> bool:
    nest = level["nest"]
    return (
        nest["x"] <= x < nest["x"] + nest["size"]
        and nest["y"] <= y < nest["y"] + nest["size"]
    )


def fruit_beside(ant: dict) -> tuple[int, int] | None:
    for dx, dy in DIRECTIONS.values():
        cell = (ant["x"] + dx, ant["y"] + dy)
        if cell in st.session_state.fruit:
            return cell
    return None
```

**Beside, not underneath.** An ant never stands on a fruit — `taken_cells()`
has prevented that since step 3. So a fruit is always picked up from a
neighbouring square. That is why `fruit_beside` goes through the eight
directions, the same ones as for walking.

## What a step leads to

```python
def pick_up_and_deliver(level: dict, ant: dict) -> None:
    if ant["carrying"]:
        if in_nest(level, ant["x"], ant["y"]):
            ant["carrying"] = False
            st.session_state.stores += 1
        return

    fruit = fruit_beside(ant)
    if fruit is not None:
        st.session_state.fruit.remove(fruit)
        ant["carrying"] = True
```

There is a design decision in here that saves money later, so it is spelled
out in full:

**Picking up and delivering are not decisions but consequences.** The model
only decides where the ant goes. If a fruit is beside it afterwards, it takes
it; if it stands in the nest with a fruit, it puts it down.

You could build it differently and ask the model: “Do you want to pick up this
fruit?” But that question practically always has the same answer — and every
question costs a request, that is, time and money. Asking only pays where the
answer is open.

## A subtlety in the round

In `next_round` the step now ends like this:

```python
        # After the step, not before: a fruit picked up here is gone from
        # `taken` for everybody who moves after this ant.
        before = set(st.session_state.fruit)
        pick_up_and_deliver(level, ant)
        taken -= before - set(st.session_state.fruit)
```

When an ant picks up a fruit, the fruit disappears from the board — and the
square it lay on is free. The ants still to move in the same round need to
know that, or they will step around an obstacle that is no longer there.

The line takes out of `taken` exactly the squares this pick-up emptied. Note
also that `pick_up_and_deliver` is called **after** walking, not before: what
counts is where the ant stands now.

A side effect that matters later: if an ant's request fails, the loop moves on
with `continue` — and so skips `pick_up_and_deliver` as well. In that round
this ant does not even pick up a fruit it is standing next to. An ant that
merely **could** not walk because the target square was taken, on the other
hand, does pick up. In chapter 5, where the discarded answers become a subject
of their own, this is straightened out.

## The fruit on its back

`cell_text` gets two more parameters:

```python
def cell_text(x: int, y: int, glyph: str, size: float = 0.7, lift: float = 0.0) -> str:
    return (
        f'  <text x="{x * CELL + CELL / 2}" y="{(y - lift) * CELL + CELL / 2}" '
        f'font-size="{CELL * size}" text-anchor="middle" '
        f'dominant-baseline="central">{glyph}</text>'
    )
```

And in `board()` a carrying ant gets a small fruit above it:

```python
    ants_svg = "\n".join(
        cell_text(ant["x"], ant["y"], "🐜")
        + (
            "\n" + cell_text(ant["x"], ant["y"], "🍎", size=0.45, lift=0.3)
            if ant["carrying"]
            else ""
        )
        for ant in st.session_state.ants
    )
```

Smaller and higher, so that loaded ants can be told from empty ones across the
whole board. This is exactly where SVG pays off: “a little higher” is
`y - 0.3`, not a CSS puzzle.

![Close-up: two ants side by side below the nest, the right one carrying a
small fruit on its back](../bilder/ameise-mit-frucht.png)

*Empty on the left, loaded on the right, above them the yellow edge of the
nest. The difference has to be visible across the whole board, not just in the
close-up.*

## Stores and victory

```python
won = st.session_state.stores >= level["target"]
carried = sum(ant["carrying"] for ant in st.session_state.ants)

st.write(
    f"Round **{st.session_state.round}** · "
    f"**{st.session_state.stores}** of {level['target']} stored · "
    f"**{carried}** being carried · "
    f"**{len(st.session_state.fruit)}** left on the board"
)

if won:
    st.success(...)
```

Both buttons are switched off as soon as the game is won:

```python
ready = bool(api_key()) and not won

if one.button("Next round", type="primary", disabled=not ready):
    ...

if five.button("Five rounds", disabled=not ready):
    for _ in range(5):
        if st.session_state.stores >= level["target"]:
            break
        next_round(level)
```

## Why it is so slow going

A fruit is quickly picked up — eight ants cover a lot of ground, and they only
have to end up next to one. Finding the way back to the nest is the problem.
The nest is 16 of 384 squares, and an ant that does not know where it is finds
it only by chance.

Watching, though, something else comes out that I had not expected. After
twenty-five rounds the colony stood like this:

```
Ant 1: (17,  0)           Ant 5: (14,  0)
Ant 2: ( 6,  0) carrying  Ant 6: (11, 10)
Ant 3: (21,  0)           Ant 7: (18,  0)
Ant 4: (22,  0)           Ant 8: (13, 10)
```

**Six of eight are stuck to the top edge.** `y = 0`, spread right across the
board.

That is not wandering about, that is a direction. Remember the first round from
chapter 3: four of eight ants chose `north`, all with low confidence. When
nothing tells one direction from another, the model still has a slight
preference — and eight ants all following the same slight preference end up
together at the wall after twenty-five rounds.

Neither a bug in the program nor one in the model. It is the honest answer to a
question without clues. The state does not say where the nest is, it does not
say where fruit is, and there is no field of vision at all yet. The question is
asked anyway — eight times a round, and paid for as well.

Remember the picture for comparison. **In chapter 5 the ants learn to see**,
and there wandering turns into a way home; in chapter 6 the queen gets a
voice, and then the model's slight preference is no longer the strongest thing
in the state.

## Try it

* Press “Five rounds” a few times. Soon most ants are carrying a fruit, and
  there is hardly anything in the stores.

* Look closely at a loaded ant: the fruit sits small above it.

* As a test, set the nest in `level1.json` to `"size": 10` and press “Start
  over”. With a huge nest the game is suddenly easy. That is not a balancing
  tip but the confirmation of where the problem lies: in finding home.

* Look at the state that is sent now — it has gained two lines (`carrying`,
  `in the nest`). Each of them was a decision. What is missing is everything
  the ant *sees*.

# Appendix A — The way across the river

*[Deutsche Fassung](../de/09-anhang-die-planke.md) · Translated from the German original.*

![Queeny, seen from behind, points across the glowing board at an L-shaped dark
blue river; on the near bank three worker ants stand with a long plank, beyond
the river a pile of red apples lies in the
corner](../bilder/anhang-a-titel.png)

*The fruit lies on the other side of the river. The queen knows how to get
across.*

**Goal:** Three new things come into the game:

* **water** that no ant can cross,
* a **plank** that an ant can pick up,
* and a **crossing** that appears where it has put the plank down.

Everything else has stayed unchanged.

The level is the second level of the game.

You will find the finished program at `anhang/app_mit_planke.py`, and the level
next to it as `anhang/level-planke.json`:

```sh
uv run streamlit run anhang/app_mit_planke.py
```

## The second level

![The plank level at the start: the fruit in the north-west corner, in front
of it an L-shaped river, in the middle the nest with eight ants, far to the
south-east the small brown plank](../bilder/planke-start.png)

The task is not in the carrying but in the **recognising**.

No ant knows that there is fruit behind the river. None knows that a plank
would help.

And none sees both — three squares of sight, and the two things lie half a
board's width apart.

Only you see the whole picture, and one sentence is all it takes.

From `anhang/level-planke.json`, shortened by the name, the briefing and where
the fruit lies:

```json
{
  "columns": 30,
  "rows": 20,
  "nest": { "x": 13, "y": 8, "size": 4 },
  "water": [[7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6],
            [6, 6], [5, 6], [4, 6], [3, 6], [2, 6], [1, 6], [0, 6]],
  "plank": [22, 15],
  "target": 5
}
```

The river is one square wide everywhere. That is enough, because nobody wades.

## A hand instead of a switch

Until now the ant's attribute `carrying` was a truth value — carrying a fruit,
yes or no.

Now there are two things to carry, so it becomes a string:

```python
            # What this ant has hold of: nothing, "a fruit" or "the plank".
            # A word rather than a flag, because there are two things now and
            # because this is what goes into the state as it stands.
            "holding": None,
```

That pays off, because the value goes into the state unchanged:

```python
        "the ant is carrying": ant["holding"] or "nothing",
```

`"a fruit"` becomes `"the plank"`, and the question understands that without
further ado.

## Water is taken, the crossing is not

```python
def taken_cells() -> set[tuple[int, int]]:
    blocked = {(ant["x"], ant["y"]) for ant in st.session_state.ants}
    blocked |= set(st.session_state.fruit)
    blocked |= st.session_state.water - {st.session_state.bridge}
    if st.session_state.plank:
        blocked.add(st.session_state.plank)
    return blocked
```

A single line makes the river impassable, and the set difference
`- {st.session_state.bridge}` makes exactly one square of it walkable again.
Because `free_directions` builds on this set, it takes effect everywhere at
once: no neighbouring square in the water is offered, the square with the
plank is.

Introducing an obstacle costs one line in this program. That is no accident
but the harvest of step 3: everything that means “something is already here”
gathers in one place.

## The one option that is not a direction

```python
TAKE_PLANK = "take the plank"
```

In `options()`:

```python
    plank = st.session_state.plank
    if plank and not ant["holding"] and steps_away(plank[0] - ant["x"], plank[1] - ant["y"]) == 1:
        extra[TAKE_PLANK] = "pick up the plank lying beside this ant"
```

At the end it joins the directions:

```python
    return {way: towards.get(way) for way in ways} | extra
```

The rule is the same as for all other options: it exists only when it is
possible. An ant with its hands full is never offered it, and neither is one
far away.

**Why is picking up a decision and putting down not?** In chapter 4 both were a
consequence, and the reasoning was: a question whose answer is almost always
the same is a request paid for and thrown away.

With the plank it is half different. An ant on its way to a fruit should not
pick up a plank in passing — here the answer is open, so it is asked. On the
other hand, an ant arriving at the water with the plank has exactly one
sensible option, so it is not asked:

```python
    if ant["holding"] == "the plank":
        water = water_beside(ant)
        if water is not None:
            ant["holding"] = None
            st.session_state.bridge = water
        return
```

> The Rust version picks the square more carefully: `nearest_crossing` only
> takes water with at least two walkable neighbours, so that the plank is not
> laid into nowhere. Here the river is one square wide everywhere, so every
> water square meets that condition, and the check can be left out.

## Three exceptions, all for the same reason

While building this I fell into the same pit three times. It is worth writing
down, because it is the same one as in chapter 5.

**First: the plank has to be visible from further away than anything else.**

```python
PLANK_VISIBLE_FROM = 8
```

With the usual three squares of sight the level did not work. Over thirty
rounds not a single ant walked to the plank — none could know it was there. The
Rust version has the same constant with the same value. A plank is a big thing
lying about in the open.

**Second: whoever carries the plank must not learn where the nest is.**

In the first attempt every ant with its hands full was told where the nest
was. So the carrier dutifully took the plank home and walked in circles with
it for thirty rounds. Now every load learns only its own destination:

```python
    if ant["holding"] == "a fruit":
        ...  # the nest
    elif ant["holding"] == "the plank":
        ...  # the nearest water
```

**Third: the crossing has to be visible from everywhere.**

Otherwise the plank is laid — and afterwards nobody finds the spot again.
Measured: eighty rounds, one fruit. Now the crossing is named to every ant, no
matter how far away it stands, as a landmark like the nest:

```python
                f"the crossing over the water, {phrase(bx - ant['x'], by - ant['y'])}"
```

Three times the same lesson, and it is the most important one of this
tutorial:

> What is in the state is the behaviour. What is not in it does not exist for
> the ant — no matter how obvious it looks on the screen.

## What comes of it

The sentence I played with:

> The fruit is all in the far north-west, behind a river you cannot wade. A
> plank lies in the south-east: whoever sees it, fetch it, carry it west to the
> river and lay it down there. Everyone else go north-west, cross where the
> plank lies, and carry fruit back to the nest.

![The board after 25 rounds: the plank lies in the river as a brown crossing,
several ants are across, one is already carrying a
fruit](../bilder/planke-bruecke.png)

The course of events, measured: the plank is picked up around round 6 to 10,
carried north-west — one of those answers with **0.96** confidence — and put
down between round 20 and 30. After that the colony streams across the one
square.

**With that the puzzle is solved**, and by one sentence. No ant could have
worked it out.

## Where this appendix reaches its limit

And then it gets slow going. Four full runs, in the order I did them:

| | Bridge down | Stores | Cost |
|---|---|---|---|
| crossing visible only from three squares | round 30 | 1 of 5 after 80 rounds | $0.016 |
| crossing as a landmark | round 25 | 1 of 5 after 70 rounds | $0.015 |
| plus the scent trail, half-life 12 | round 25 | **0** of 5 after 60 rounds | $0.013 |
| half-life 30 | round 30 | **0** of 5 after 60 rounds | $0.012 |

One fruit, then none. The puzzle is solved, the carrying away is not — and
with the scent trail it even gets worse.

That can be explained and, honestly, was to be expected. On the first board the
trail is as good as perfect information (chapter 5). Here the way home is three
times as long and leads through **one** square — and a trail that nobody
refreshes, because nobody happens to walk the same way, has faded before the
carrier is back.

So my first guess was the half-life. It is now in the level instead of in the
code:

```json
  "scent_half_life": 30
```

It brought **nothing** — line four of the table. The setting has stayed anyway,
because the reasoning behind it is sound: how long a trail has to last depends
on how far the colony walks. It just was not the problem here.

The reason is not a weakness of the model but the way this port is built:
**every single step is a question of its own.** An ant that is to fetch fruit
and come back over one particular square needs twenty decisions in a row for
it, each without any memory of the previous one. On top of that, eight ants
squeeze through a single square.

That is exactly why the Rust version has **intents instead of single steps**:
there you ask once “fetch the fruit in the north-west”, and the ant works on it
for several seconds. That is the point from chapter 8 where carrying on pays
off — and this appendix is the proof that it is not theoretical.

## Try it

* First give an order that mentions neither river nor plank, say “Search for
  fruit and bring it home”, and play twenty rounds. The colony finds the river,
  and that is where it ends.
* Switch on the dice and let it run for a hundred rounds. Does it ever pick up
  the plank? And if so, does it put it down somewhere sensible?
* Say only “Fetch the plank in the south-east”. Is it fetched? And where is it
  carried to?
* Set `PLANK_VISIBLE_FROM` back to 3 and play again.
* Move the plank closer to the river in `level-planke.json`. How much easier
  does the level get?
* Add a second water square, so that the river is two squares wide in one
  place. What happens if the plank is laid there? (And now you know what the
  Rust version has `nearest_crossing` for.)
* Watch the board after the bridge is down: where does it turn green? The trail
  shows which way the colony really takes — and how quickly it fades again when
  nobody uses it.

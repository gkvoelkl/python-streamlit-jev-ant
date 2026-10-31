# Step 7 — Insights

*[Deutsche Fassung](../de/07-zusehen.md) · Translated from the German original.*

![Queeny, seen from behind over her shoulder, looks across the glowing board at
four worker ants in colourful helmets; above each floats an arrow in a coloured
sign — green, yellow, green, red — and at the edge of the board two dollar
signs glow](../bilder/schritt-7-titel.png)

*Now you see what every ant is up to.*

**Goal:**

* Above every ant stands what the decision model decided for it and how sure
  it was — shown in three colours.
* Below the board stands what the colony has achieved so far and what it has
  cost.

![The board of step 7 after six rounds of “Go east”: eight ants east of the
nest, above each a green label like “E 0.99” or “E 0.86”; on the far right a
label slides over the ant above it](../bilder/schritt-7-einblicke.png)

*Six rounds after “Go east”: eight times east, eight times green.*

## Every ant remembers what it was told

In `start()` every ant gets a new attribute:

```python
            "said": None,
```

And in `next_round`, right after `accepted(...)`:

```python
        ant["said"] = (
            (way, answer.choices["step"].confidence) if way is not None else None
        )
```

`None` means: this ant did nothing this round. Either no answer came, or the
answer was thrown away.

## Three colours and a dash

```python
SURE = [(0.85, "#7fd18b"), (0.60, "#e3c45c"), (0.0, "#e08074")]
UNSURE = "#8b8b93"
```

```python
def colour_of(confidence: float) -> str:
    """Which of the three bands a confidence falls into."""
    for floor, colour in SURE:
        if confidence >= floor:
            return colour
    return UNSURE
```

* **Green** (from 0.85): the model had a reason.
* **Yellow** (from 0.60): a slight leaning.
* **Red** (below 0.60): the answer cleared the threshold of 0.22, but the model
  is basically guessing.
* **Grey**: the ant did nothing.

Red reaches all the way down, to 0.0. But no answer that appears on the board
gets lower than 0.22 — everything below was already thrown away in
`accepted()` and turns grey.

The directions are abbreviated:

```python
SHORT = {
    "north": "N",
    "north-east": "NE",
    "east": "E",
    "south-east": "SE",
    "south": "S",
    "south-west": "SW",
    "west": "W",
    "north-west": "NW",
}
```

Written out, a label would be wider than the three squares around the ant, and
the board would turn into a wall of text.

```python
def label(ant: dict) -> str:
    if ant["said"] is None:
        text, colour = "—", UNSURE
    else:
        way, confidence = ant["said"]
        text, colour = f"{SHORT[way]} {confidence:.2f}", colour_of(confidence)

    return (
        f'  <text x="{ant["x"] * CELL + CELL / 2}" y="{ant["y"] * CELL - CELL * 0.15}" '
        f'font-size="{CELL * 0.38}" font-family="system-ui, sans-serif" '
        f'fill="{colour}" text-anchor="middle">{text}</text>'
    )
```

The grey dash for an idle ant matters more than it looks. A board on which
half the labels are grey says something about the **question**, not about the
ants. Drawing nothing at all would hide exactly that.

The labels are drawn **last**, so that an ant never lies on top of a label —
the labels are, after all, the reason you look at the board. And they only
appear once the colony is awake; before that there is nothing to label:

```python
    labels_svg = "\n".join(
        label(ant) for ant in st.session_state.ants if st.session_state.awake
    )
```

Below the board, one line explains what the colours mean:

```python
if st.session_state.awake:
    st.caption(
        "Above each ant: what Jev chose and how sure it was. "
        ":green[green from 0.85] · :orange[yellow from 0.60] · "
        ":red[red down to 0.22] · grey means the ant did nothing this round."
    )
```

## What it costs

```python
USD_PER_MILLION_TOKENS = 0.042
```

```python
cost = st.session_state.tokens * USD_PER_MILLION_TOKENS / 1_000_000
asked = st.session_state.requests
thrown = len(st.session_state.discarded)
```

`accepted()` has been counting the input tokens since step 6. Now their price
is shown as well.

```python
colony, meter = st.columns(2)
colony.write(
    f"Round **{st.session_state.round}** · "
    f"**{st.session_state.stores}** of {level['target']} stored · "
    f"**{carried}** carried · "
    f"**{len(st.session_state.fruit)}** on the board"
)
meter.write(
    f"**{asked}** decisions from Jev, **{thrown}** discarded"
    + (f" (**{thrown / asked:.0%}**)" if asked else "")
    + f" · {st.session_state.tokens:,} tokens · **\\${cost:.4f}**"
)
```

The colony on the left, the meter on the right. The order is deliberate: the
stores are the game, the cost is only what you measure it with.

From a real run: 88 decisions in eleven rounds, 53 thrown away, 48,100 tokens,
**0.0020 dollars**. So a round with eight ants costs about 0.0002 dollars, a
whole game half a cent to a cent (measured in chapter 8). That is a number
worth knowing before you start asking every second.

## Tip: dollar signs are LaTeX

The first version wrote `**${cost:.4f}**` — and the screen did not show the
number in bold, but typeset as a formula. Streamlit's Markdown reads a pair of
dollar signs as a mathematical formula.

The fix is `\\$` in the Python string, that is, an escaped dollar sign in the
Markdown.

## What you see now

The difference the labels make visible is the same as in chapter 6. Only now
you see it directly instead of working it out from a percentage.

After “Fan out and search, keep away from each other” the board shows almost
nothing but grey dashes.

After “Go east. Every one of you, east, until you find fruit — then bring it
home.” it looks like the picture above: eight labels, all green, all `E`,
between 0.86 and 0.99. The order is unambiguous, and so are the answers.

It does not stay that way for long. In another run with the same order, next
to four green `E` there was a red `SE 0.36`. It belonged to an ant whose way
east was blocked just then, and which therefore had to choose something else.
The order says nothing about what is right instead — and that is exactly what
the colour shows.

So you read in the picture what used to be a statistic: **a clear order makes
sure ants.** Whether it also makes them clever is another matter — in chapter 6
this very colony marched into a corner as one with an equally clear order.

## Try it

* Give an unambiguous order (“Go west”) and a vague one (“Do something
  useful”) and compare the colours on the board.
* Count the grey dashes per round. That is the discard rate, just without the
  percentages.
* Watch a single ant over several rounds. If it sees a fruit, its label turns
  green before it gets there.
* Let the cost run along and extrapolate: what does a board with 50 ants and
  200 rounds cost?

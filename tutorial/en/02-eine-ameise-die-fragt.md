# Step 2 — One ant asks the decision model

*[Deutsche Fassung](../de/02-eine-ameise-die-fragt.md) · Translated from the German original.*

![A worker ant in a white hard hat and with a radio stands alone on the glowing
board, above her a speech bubble with a question mark; of the arrows around
her, one glows golden and carries the label
“Jev”](../bilder/schritt-2-titel.png)

*She asks, and the model shows her the way.*

**Goal:** One ant stands on the board. You press a button, and the ant goes
where the **decision model** tells it to — in this tutorial **TypeSafe Jev**.

![The board of step 2 with the one ant, standing on the square the model sent
it to](../bilder/schritt-2-ameise.png)

*One ant, and every step it has taken came from the decision model.*

## The API key

For requests to TypeSafe Jev you need a personal **API key**. You get it from
the web page [console.typesafe.ai/keys](https://console.typesafe.ai/keys).

Either you write this key **into the file `.env`**.

```
TYPESAFE_API_KEY=your-key
```

**Or into the sidebar** of the running application. That is the way for
everyone who later uses the game directly on the web: everybody brings their
own key.

![The sidebar with the heading “TypeSafe key”, an empty password field with the
hint “paste your key” and the eye that makes it visible, below it the note that
the key is stored nowhere](../bilder/schluessel-seitenleiste.png)

*The field appears only when there is no key in `.env` — otherwise the sidebar
just shows “Found in .env”. The eye on the right makes what was pasted visible,
which after a botched paste is the only way to see the mistake without spending
a request on it.*

```python
import os
from dotenv import load_dotenv

load_dotenv()


def api_key() -> str:
    return st.session_state.get("typed_key", "").strip() or os.getenv(
        "TYPESAFE_API_KEY", ""
    ).strip()
```

What was typed takes precedence over the file `.env` — otherwise you could not
override a stale key there.

> **It works without a key, too.** Since Ollama 0.35 a locally running model
> answers the same requests: no cost, no network, and not one line of code
> different — just three lines in `.env`. How that works is in **appendix B**.
> If you would rather work through the tutorial that way, set it up there and
> come back here; everything else stays the same.

## The ant

```python
def start() -> None:
    if "ant" in st.session_state:
        return

    st.session_state.ant = {"x": COLUMNS // 2, "y": ROWS // 2}
    st.session_state.said = None
    st.session_state.failure = None
```

**Streamlit runs the whole script again on every interaction.** Every click:
the file runs through again from top to bottom, and everything held in
ordinary variables is gone.

Whatever is to survive a click must go into `st.session_state` — and may only
be written **when it is not there yet**.

That is exactly what this does:

`if "ant" in st.session_state: return`

It turns a rerun into a redraw instead of a restart.

## The eight directions

```python
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
```

y counts downwards (chapter 1), so north is `(0, -1)`.

![The eight directions around an ant, each with its name and its offset; north
is (0, −1) because y counts downwards](../bilder/en/richtungen.png)

That the directions have **names** and are not numbered is a matter of
readability and of communication. The ant queen, the player, can say: “All ants
move north.” Coordinates would be no help here.

Beyond that, these names are what the decision model is offered to choose from
and what it gives back. `"north-east"` is a word a language model understands;
`(1, -1)` is not.

## What this ant can do right now

```python
def free_directions(ant: dict) -> list[str]:
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            open_ways.append(name)
    return open_ways
```

![On the left an ant in the middle of the board with eight arrows, on the right
the same ant at the top edge with only five arrows; three directions are
crossed out because there are no squares there](../bilder/en/optionen.png)

*Exactly the green arrows become `criteria`. What is crossed out, the model
never gets to see.*

This function works out which neighbouring squares of the ant are free and so
come into question for the next step. On top of that it checks whether the edge
of the board has been reached.

## The question

```python
STEP_QUESTION = (
    "An ant is standing on a board and has to decide where to go next. "
    "Which way should it go?"
)
```

This is the basic question that comes up at every step of the ant.

## The request to the decision model

```python
from typesafe_sdk import Choice, TypeSafeClient, TypeSafeError


def ask_jev(ant: dict) -> object:
    ways = free_directions(ant)

    state = {"the ant is": "standing on open ground"}
    questions = {
        "step": Choice(instructions=STEP_QUESTION, criteria=dict.fromkeys(ways))
    }

    client = TypeSafeClient(api_key=api_key(), timeout=15)
    return client.system_one(state=state, questions=questions)
```

A question to the decision model always consists of:

* **state**: the basis for the model's decision. In this example the ant's
  current situation.

* **question**: the question the model is to answer.

What is special about a decision model is that it does not answer with text
like chat models do; instead you prescribe the data type of the answer.

**Choice** prescribes a selection, the **criteria**, from which the model picks
one. For the ant these are the directions it can go in.

### The options are made at runtime

```python
criteria=dict.fromkeys(ways)
```

`ways` comes from the function `free_directions`. It is **not a fixed list of
eight directions** but what is possible for the ant right now. An ant at the
edge is not offered the edge.

`dict.fromkeys(ways)` contains `{"north": None, "east": None, …}`. The values
are descriptions that can be given to the options.

### The **state** is as small as possible

```python
state = {"the ant is": "standing on open ground"}
```

One entry. That is not laziness: a **state** padded with things that do not
matter makes the answer **worse** — and costs money per word. Every line added
in the next chapters has to justify itself.

### One client, synchronous

The SDK offers `TypeSafeClient` and `AsyncTypeSafeClient`. The synchronous one
is enough here: Streamlit works through a script from top to bottom, and a
request that is waited for fits that exactly. The asynchronous one pays off
from chapter 3 on, when eight ants ask at the same time.

## Taking the step

```python
def take_a_step() -> None:
    ant = st.session_state.ant

    try:
        answer = ask_jev(ant)
    except TypeSafeError as failed:
        st.session_state.said = None
        st.session_state.failure = f"{type(failed).__name__}: {failed}"
        return

    step = answer.choices["step"]
    dx, dy = DIRECTIONS[step.choice]
    ant["x"] += dx
    ant["y"] += dy
    ...
```

`answer.choices["step"]` — the key is the same one the question was asked
under. Inside: `choice`, `confidence` and `probabilities`.

Every error the SDK knows is derived from `TypeSafeError`: wrong key, limit
exceeded, timeout. The class name goes into the message too, because
`TypeSafeAuthenticationError` means something quite different from
`TypeSafeRateLimitError`.

If the request fails, the ant stays where it is.

## Showing the answer as well

```python
    chosen, sure, tokens = st.columns(3)
    chosen.metric("Chosen", said["choice"])
    sure.metric("Confidence", f"{said['confidence']:.2f}")
    tokens.metric("Input tokens", said["tokens"])

    st.bar_chart(
        {"probability": dict(sorted(said["probabilities"].items()))},
        horizontal=True, height=260,
    )
```

The model's answers can also be seen in a bar chart. A clear answer is a tall
bar.

## An answer from the decision model

An answer to a real request:

| | |
|---|---|
| Model | `jev-1.13.0` |
| Chosen | `north` |
| Confidence | **0.33** |
| Input tokens | 356 |

### What confidence really measures

The value **confidence** says how the probability is spread over the options:
if it all lies on one, it is 1. The more evenly it is spread, the smaller it
gets, down to 0 for a completely even spread.

That is a fine but important difference from “how sure is the model that the
answer is **right**”. The value says nothing about that. It only measures how
clearly one option stands out. A model can be very sure and still be wrong —
then the confidence is high and the answer is wrong.

### Confidence in detail

TypeSafe's documentation gives the calculation for three options:
`(3 × highest probability − 1) ÷ 2`. Generalised, with *n* options:

> **confidence = (n × highest probability − 1) ÷ (n − 1)**

Checked against the answer above — eight options, the highest at 0.37:
`(8 × 0.37 − 1) ÷ 7 = 0.28`. The model reported 0.29; the rest is rounding,
because the probabilities come with two decimal places.

![The eight probabilities of a real answer as bars, with the line for pure
chance at 0.125 and the confidence calculated from
them](../bilder/en/konfidenz.png)

The divisor `n − 1` is the reason why confidence must **not** be confused with
the highest probability: it takes the number of options out of the
calculation. 0.37 is three times chance with eight options, but with two
options it is less than half. That is exactly what this game needs, because the
number of options changes here with every step.

0.33 looks low at first glance, but it is actually right.

Ask yourself what the ant knows:

It is standing somewhere, and nothing else. It sees no goal (a fruit, say),
because there is none. Nobody has told it anything. Under these circumstances
one direction is as good as another — and the model says so by answering with
a confidence of 0.33.

A high confidence would be the **worse** result here: a model that is sure
without having a reason.

### When may you follow an answer?

TypeSafe recommends three levels: **below 0.5** the model is genuinely unsure
and you should not guess; **0.5 to 0.9** means carry on, but with care; only
**above 0.9** may something risky happen. Which level applies depends on what a
wrong decision does.

This game sets the threshold in chapter 5 at **0.22** — well below that. That
is not a contradiction but the same reasoning: what an ant does with a wrong
step is one wrong step. It costs a round and can be corrected in the next one.
For a bank transfer or a cancellation, 0.9 would be too low.

These 0.33 are the number the rest of the tutorial wants to improve. Chapter 5
lets the ant see more, chapter 6 gives the queen a voice. Both should raise
the value.

## Try it

* Press several times. The answer wavers — at 0.33 confidence that is not a
  malfunction, it is the message.
* Walk the ant into a corner. There it has only three options left, and the
  chart has only three bars left too. That is the options made at runtime, in
  pictures.
* Change `STEP_QUESTION` to “Which way should it go? It is looking for food in
  the north.” and look at the confidence.

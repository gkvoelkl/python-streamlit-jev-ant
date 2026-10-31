# Step 8 — What is the decision model worth?

*[Deutsche Fassung](../de/08-was-bringt-das-modell.md) · Translated from the German original.*

![Queeny, seen from behind, holds a glowing dice in her hand; to her left
worker ants with apples stand about the board in disorder, a second dice
floating above them; to her right worker ants in white helmets walk in a line
along a glowing green trail, a green arrow above most of
them](../bilder/schritt-8-titel.png)

*Random moves (the dice) compared with the decision model — the same ants, the
same paths.*

**Goal:**

* A switch that replaces the decision model with a dice.
* The same colony, the same board, the same options — only nobody decides any
  more; chance does.

![The board after 40 rounds with the dice: the ants scattered across the whole
board, four of them carrying a fruit, none of it in the nest; around the nest
the ground is faintly green from the trail](../bilder/schritt-8-wuerfel.png)

*Forty rounds of chance: four fruits on the way, none in the stores.*

Throughout the tutorial a model has decided, and it looked good.

“Looked good” is not an objective statement, not a measurement. This chapter
builds the yardstick against which the model can be measured.

## A dice that gets the same options

```python
def decide_with_dice(level: dict, taken: set[tuple[int, int]]) -> list[str | None]:
    ways = []
    for ant in st.session_state.ants:
        open_ways = free_directions(level, ant, taken)
        ant["said"] = None
        ways.append(random.choice(open_ways) if open_ways else None)
    return ways
```

What matters is `free_directions`. That is **the same** function from which
`options()` builds the choice for the decision model.

The dice gets as its input what the model would have been shown — only without
the descriptions, because it cannot read them.

So the difference is the choosing itself, not what there is to choose from.

`ant["said"] = None` makes sure that no label from an earlier round is left
standing above an ant.

## One line decides

```python
def next_round(level: dict) -> None:
    taken = taken_cells()
    decide = decide_with_dice if st.session_state.dice else decide_with_jev

    for ant, way in zip(st.session_state.ants, decide(level, taken)):
        ...
```

Every round gets a list of directions and carries them out — with the same
check when moving as since chapter 3, because a dice can send two ants to the
same square too.

## The switch

```python
    st.session_state.dice = st.toggle(
        "A dice instead of Jev",
        value=st.session_state.dice,
        help=(
            "Draws blindly from the same options the model would have been "
            "given. Nothing is asked and nothing is paid. It is a yardstick, "
            "not a fallback."
        ),
    )
    if st.session_state.dice:
        st.caption("Nobody is being asked. Watch how long five fruits take now.")
```

When the switch is on, two locks fall away:

```python
ready = (st.session_state.dice or (bool(api_key()) and st.session_state.awake)) and not won
```

With the dice you need neither a key nor an order — nobody is asked, after
all. That is exactly what makes it usable as a yardstick.

## Two hundred runs without Streamlit

In the game itself you can see the difference. Measuring it there is awkward:
every round is a click, and a run with the dice takes hundreds of them.

`tutorial/baseline.py` plays the dice rules without Streamlit and without
drawing — two hundred runs in a second:

```sh
python3 tutorial/baseline.py
```

```
200 of 200 runs brought five fruits home
median    240 rounds
mean      248 rounds
range     75 to 603
middle 80% 146 to 361
```

Your numbers will look a little different; the dice is a dice, after all. But
over two hundred runs the median stays somewhere around 240.

## The result

For the model, three runs with the same order, “Fan out and search, and carry
what you find straight home.”:

| Run | Rounds | Requests | discarded | Cost |
|---|---|---|---|---|
| 1 | 59 | 472 | 222 (47 %) | $0.0100 |
| 2 | 23 | 184 | 68 (37 %) | $0.0040 |
| 3 | 26 | 208 | 74 (36 %) | $0.0045 |

| | Rounds to five fruits |
|---|---|
| Dice (median of 200 runs) | **240** |
| Decision model (Jev), median of 3 runs | **26** |

The model is about **nine times** faster. A whole game costs between half a
cent and a cent.

The first run shows how much spread there is with the decision model too: more
than twice as long as the other two, and almost every second answer was thrown
away. It was still faster than the fastest dice run (75 rounds).

Where does the big gap come from?

Not from picking up: a fruit right next to an ant is picked up in both
colonies without anyone deciding (`pick_up_and_deliver` from chapter 4).

A small part comes from the model heading for a fruit it sees three squares
away. The dice walks past it.

But the big part comes on the **way home**. A carrying ant follows the scent
trail uphill and arrives. A dice would have to hit the 16 squares of the nest
among 384 squares by wandering about. You can see it in the picture above:
four ants are carrying a fruit, none finds its way home.

And now comes the subtlety that makes this comparison sharp: **the dice colony
lays the same trail.** `lay_scent` hangs on walking, not on deciding, so its
board smells just the same — the picture shows that too. It just cannot read
the trail, because for that someone would have to choose something from what
is on offer.

So the trail is not what makes the difference. It is only the information —
and the difference is that one side can make use of it and the other cannot.

Remember the general part of this: the benefit was not where the decision
looked difficult, but where there was **information** that chance cannot make
use of.

## Limitations

**The numbers are not measured on equal terms.** 240 is an average (median)
of two hundred runs, the 26 for the decision model a median of three, because
each of them costs several hundred requests.

The runs spread from 23 to 59 rounds. Before you take a number for the model
seriously, you should do more runs — and also try out how much difference
another order makes.

**The claim lies elsewhere.** What the rule cannot do: respond to “Leave the
fruit in the north alone”. Or to “Stay together”. Or to a sentence you have
only just thought of. That is what the text field from chapter 6 is for, and
that is what the whole thing is built for.

## Try it

* Switch on, “Five rounds” a few dozen times. It costs nothing, and it takes a
  while. That is exactly the message.
* Switch off, “Start over”, say a good sentence and count the rounds.
* Open `tutorial/baseline.py` and build in the rule that is missing above:
  fruit in sight → go there; carrying → go home. How many rounds does it need?
* Set `RUNS` to 20 and run it twice. The medians will differ — with this much
  spread, twenty runs say little. That is the most important lesson about
  measuring in this tutorial.

---

# Done

Eight steps, one game. What stands there now:

* a board in SVG that draws a level from a JSON file
* **options that are made anew every round from the situation of each single
  ant** — the model never gets to see anything impossible
* eight parallel requests per round in a little over half a second
* a colony that finds fruit, carries it and brings it home
* a threshold below which answers are thrown away and counted instead of
  hidden, and no falling back on rules underneath
* a text field into which you type a sentence that each of the eight ants
  reads for itself
* the display that shows whether it helped
* and a yardstick against which all of it can be measured

## Where it could go next

* **A second level** is already included: `level2.json`. Nothing more than a
  second file was needed; you play it by changing one line in `app.py`:

  ```python
  LEVEL_FILE = "level2.json"
  ```

  ![Level 2 at the start: the nest with eight ants at the bottom right, all
  eight fruits far up on the left, an empty board in
  between](../bilder/level-2.png)

  The nest is in the south-east, all the fruit in the north-west — 13 to 17
  squares away, with a vision range of three. With a vague order the colony
  searches an empty board. With “The fruit lies far to the north-west, go
  there” it has a direction. The rules are the same as in the first level, only
  without the chance of getting lucky by wandering about.

* **An obstacle.** The Rust version has a level with a river and a plank that
  two ants have to carry together — coordination without agreement is the most
  interesting part of the whole thing. Appendix A shows how far this can be
  rebuilt here.
* **Intents instead of single steps.** Instead of asking “which direction?”
  every round, ask once “fetch the fruit in the north-east” and let the ant
  work on it for several rounds. That saves most of the requests.
* **Refining the question.** The most rewarding point and the cheapest:
  turning the knobs on `STEP_QUESTION` costs not one line of code and changes
  the behaviour of the whole colony. One of the exercises in chapter 5 shows
  it: take out the sentence about fanning out, and the colony behaves
  differently.

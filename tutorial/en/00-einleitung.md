# When ants ask a decision model

*[Deutsche Fassung](../de/00-einleitung.md) · Translated from the German original.*

![Queeny, the queen with a crown, stands in the colony's control room, with four
worker ants in hard hats and with tools to her left and
right](../bilder/queeny-und-arbeiterinnen.png)

*Queeny and her workers.*

## Trying out a decision model with Python, playfully

A decision model is a new kind of AI model: it makes quick assessments and
decisions that programs can build into their flow.

The example in this tutorial is an ant colony that you watch in the browser.
The decision model steers every single ant according to the instructions of the
queen, who is you. The ants are to bring fruit into the nest or get past
obstacles.

![The finished game: eight ants on the board, above each one what the model
chose and how sure it was — green for high, red for narrow
confidence](../bilder/das-spiel.png)

*This is what it looks like at the end of step 7. Above every ant stands what
the model chose and how sure it was — and the green squares are the scent
trail the colony leaves while searching. It is strongest at the nest, and
uphill is homeward.*

No clicking, no keys, no joystick. You type “Fetch the fruit from the north”,
and every ant decides for itself what that means for it. The decision is made
by a **decision model**, in this tutorial **TypeSafe Jev**.

A decision model is not a chat model. It does not answer questions in prose,
it makes **typed decisions with calibrated confidence** — exactly what a
program can build into its flow. For TypeSafe Jev you need three addresses:

| | |
|---|---|
| The website | [typesafe.ai](https://typesafe.ai) |
| The documentation | [docs.typesafe.ai](https://docs.typesafe.ai/introduction) |
| The key | [console.typesafe.ai/keys](https://console.typesafe.ai/keys) |

![The TypeSafe console after signing in: on the left the navigation with
Playground, Usage, API Keys, Billing and Documentation, on the right examples
of the question types Noul and Choice](../bilder/typesafe-website.png)

*The console at [console.typesafe.ai](https://console.typesafe.ai). You get the
key you need from step 2 on under **API Keys** on the left; under **Usage** you
will later see what the tutorial cost. At the top right of the picture are
already the two question types this is going to be about:* `noul` *for a
yes/no with a probability and* `choice` *for a selection — the second is the
one every ant asks.*

Every ant asks the decision model one question per round, and the answer is
exactly one of the options this one ant really has at that moment.

The program builds the options **at runtime** from what the ant sees. If no
fruit is in sight, there is no option “fetch the fruit”.

**A local alternative: Ollama with decision models.** Since version 0.35
Ollama offers the endpoint `/v1/systemone`, with the same questions, options,
probabilities and the same confidence as Jev. The model then runs on your own
machine, without a key and without a cost per request. The library from this
tutorial talks to Ollama unchanged; three entries in `.env` are enough. How
that works and how fast it is, is in appendix B.

The market moves fast. For the tutorial this holds: what a decision model is
and how to ask it stays the same, no matter who it comes from.

## What you need

* **Python 3.12 or newer.**
* **[uv](https://docs.astral.sh/uv/)** as the package manager. It works with
  `pip` too; where it makes a difference, both are given.
* **A TypeSafe key** from
  [console.typesafe.ai/keys](https://console.typesafe.ai/keys). It is needed
  **from step 2 on**: the model is the subject, so it comes early and stays.
  Only step 1 runs without one.
* A text editor and a browser.

Cost: one request is about 350 to 600 input tokens, and a million of them cost
0.042 dollars. A complete game — eight ants, twenty to sixty rounds — comes to
**half a cent to a cent**. A few cents will probably be enough to work through
the whole tutorial.

## The eight steps of the tutorial

After **every** step you have a program that runs. You always see something
new on the screen.

| Step | What runs afterwards |
|---|---|
| 1 | The board — a grid in the browser |
| 2 | **One ant that asks the model** — one click, one request, one step |
| 3 | The colony — eight ants with eight parallel requests |
| 4 | Carrying and delivering — bringing fruit home, winning |
| 5 | Eyes — field of vision, better options, a threshold |
| 6 | The queen — your sentence |
| 7 | Insights — what every ant chose, and what it costs |
| 8 | What is the decision model worth? — the comparison with a dice |

**From step 2 on the model decides**, and everything after that is about what
it gets to see.

First the ant is blind and alone; then there are eight; then they have a task;
then they can see; then a queen who tells them something.

## How to get the code

Every step is a state of its own in the repository:

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
git checkout step-1        # the state after step 1
uv run streamlit run app.py
```

The same eight states are also in `steps/` as single files, if that is easier
for you:

```sh
uv run streamlit run steps/01_board.py
```

Start them from the root directory — `level1.json` and `.env` are looked for
where you start the program.

But you can just as well start with an empty file and type the programs
yourself. That is what the tutorial is written for.

---

*This tutorial was created by Gerhard Völkl using Claude Code (Anthropic). It is meant to help you learn more about what happens when ants ask a decision model. Suggestions for improvement are welcome at gkvoelkl@nelson-games.de.*

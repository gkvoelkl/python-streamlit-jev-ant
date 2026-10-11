# Jev Ants — Streamlit

An ant colony where every ant asks [TypeSafe Jev](https://docs.typesafe.ai/introduction)
what to do next. You are the queen, and your only control is a sentence.

A small Python port of [rust-bevy-jev-ants](https://github.com/gkvoelkl/rust-bevy-jev-ants),
built in eight steps — each one a program that runs, and from step 2 on every
step the ants take was decided by the model. The tags `step-1` … `step-8` are
those eight states, and `steps/` holds the same files to copy from.

## Run it

```sh
uv run streamlit run app.py
```

`uv` reads `pyproject.toml`, makes the environment and starts the app in one go.
Without uv, `pip install -r requirements.txt` and then `streamlit run app.py`
does the same thing with unpinned versions.

From step 2 on you need a TypeSafe key from
[console.typesafe.ai](https://console.typesafe.ai/keys), either in `.env` as
`TYPESAFE_API_KEY` or typed into the sidebar.

Nothing here talks to the API through a proxy: Streamlit runs the request on the
server, so the browser never calls the API itself and there is no CORS to work
around.

## The tutorial

`Ameisen-die-fragen.docx` builds the whole thing in eight steps, in German. It
is generated from the chapters in `tutorial/`, which are the source — edit
those, not the Word file:

```sh
npm install docx
node tools/build_tutorial.js
```

`tutorial/baseline.py` belongs to it: it plays the game without Streamlit to
measure what random walking achieves, which is the number step 6 is compared
against.

## Layout

```
app.py              the game, one file
level1.json         the board, the nest, the fruit, what wins
steps/              app.py as it stood after each step, generated from the tags
tutorial/           the German chapters the Word document is built from
tools/              the two generators
```

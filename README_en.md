# Jev Ants — Streamlit

*[Deutsche Fassung](README_de.md)*

An ant colony where every ant asks a decision model —
[TypeSafe Jev](https://docs.typesafe.ai/introduction) — what to do next. You are
the queen, and your only way to intervene is to type orders in natural
language.

This is a Python port of [rust-bevy-jev-ants](https://github.com/gkvoelkl/rust-bevy-jev-ants).
It comes with a tutorial in eight steps that describes how the program is
built.

The GitHub tags `step-1` … `step-8` hold the program as it stands after each
step of the tutorial. The directory `steps/` holds the same files side by side.

## Run it

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

From step 2 of the tutorial on you need a TypeSafe key from
[console.typesafe.ai](https://console.typesafe.ai/keys), either in `.env` as
`TYPESAFE_API_KEY` or typed into the sidebar.

Nothing here talks to the API through a proxy: Streamlit runs the request on the
server, so the browser never calls the API itself and there is no CORS to work
around.

### Without the cloud

Ollama 0.35 and later serve decision models locally on `/v1/systemone`, in the
same format as TypeSafe. Three lines in `.env` and the app runs without a key
and without cost per request:

```
TYPESAFE_API_KEY=ollama
TYPESAFE_BASE_URL=http://localhost:11434
TYPESAFE_DEFAULT_MODEL=nimble
```

Appendix B of the tutorial has the measurements.

## The tutorial

The tutorial builds the game in eight steps. It was written in German and is
fully translated into English.

- **Website:** [gkvoelkl.github.io/python-streamlit-jev-ant/en/](https://gkvoelkl.github.io/python-streamlit-jev-ant/en/)
- **Markdown:** [tutorial/en/README.md](tutorial/en/README.md) · German original in [tutorial/de/](tutorial/de/README.md)

The chapters in `tutorial/de/` and `tutorial/en/` are the source. Two things
are generated from them — edit the chapters, not these:

```sh
uv run --only-group docs mkdocs serve     # the bilingual website, locally
npm install docx && node tools/build_tutorial.js   # the German Word document
```

A GitHub Actions workflow builds the website and publishes it on GitHub Pages
on every push to `main` that touches the tutorial.

`tutorial/baseline.py` belongs to it: it plays the game without Streamlit to
measure what random walking achieves, which is the number step 8 is compared
against.

## Layout

```
app.py              the game, one file
level1.json         the board, the nest, the fruit, what wins
steps/              app.py as it stood after each step, generated from the tags
tutorial/de/        the German chapters — the original
tutorial/en/        the English translation, every chapter
tutorial/bilder/    pictures and diagrams; English diagrams in bilder/en/
tools/              the generators for the Word document, the PNGs and the website
mkdocs.yml          the website
```

## Licence

MIT, see [LICENSE](LICENSE).

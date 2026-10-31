# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

A deliberately small Streamlit port of
[`rust-bevy-jev-ants`](https://github.com/gkvoelkl/rust-bevy-jev-ants): level 1 only,
no click-an-ant dialog. Every ant asks TypeSafe Jev what to do next; the player, as the
queen, steers the colony with one sentence.

The original repo is the reference for *what the game is*. Its `internals/ANTS.md` is the
binding spec there and worth reading before changing a rule here — but this port is
allowed to be simpler, and simpler is the point.

## Language

**The project is English** — code, identifiers, comments, UI text, README (with a German
copy in `README_de.md` and a bilingual start page in `README.md`), commit
messages.

**The tutorial is German, with a complete English translation beside it.** The German
chapters in `tutorial/de/` are the original; `tutorial/en/` holds translations under the
same file names, every chapter and both appendices. A change to a German chapter is
carried over to its translation in the same commit. Diagrams with text get an English copy in `tutorial/bilder/en/`. Comments in
the code should carry the reasoning a reader will need in the chapters: say *why*, not
just *what*.

Two things are generated from the chapters and never edited by hand: the German Word
document (`tools/build_tutorial.js`, from `tutorial/de/` only) and the bilingual website
(MkDocs with `mkdocs-static-i18n`, `mkdocs.yml`, published on GitHub Pages by
`.github/workflows/docs.yml`). A German chapter links to its translation in a line of its
own, `*[English version](../en/<name>.md)*`; the Word build drops that line, and
`tools/mkdocs_hooks.py` rewrites cross-language links for the website.

## The eight steps

Each step ends in a program that runs. The tags `step-1` … `step-8` are those states, and
`steps/` holds the same files to copy from (generated from the tags at the end, so there
is one source of truth in practice).

1. The board — a grid as SVG
2. One ant, and it asks — the key, one request per click, the ant moves
3. The colony — level from JSON, eight ants, eight parallel requests
4. Carrying and delivering — pick up, bring home, stores, win
5. Eyes — vision, options with descriptions, the confidence floor, discards
6. The queen — a text field, and a colony that sleeps until the first order
7. Seeing it — action and confidence per ant, a line with stores, cost, discards
8. What is the model worth? — a dice in the model's place, as a yardstick

The model arrives in step 2 on purpose: it is what the tutorial is about, and
everything after it is about what the model is shown and how it is asked. The
dice is a measuring stick at the end, never a fallback.

**Stop after every step** so the change can be tested by hand before the next one starts.

**The tutorial grows with the code.** Every step gets its chapter in `tutorial/de/` as
German Markdown, written in the same turn as the step, not reconstructed at the end. The
Word document is generated from those chapters when it is wanted. Code listings in a
chapter must match the code word for word — the app's interface is English, so the
listings are too, and only the prose around them is German.

## Rules carried over from the Bevy version

These are what make the demo a demo. Do not simplify them away.

1. **Options are built at runtime from what the one ant can see**, never hardcoded. An ant
   with nothing in sight is not offered `fetch_north_east`. This is the type-safety
   argument and the core of the whole thing.
2. **Intents, not single steps.** Jev is asked what the ant should do, and the answer is
   carried out over more than one round where that makes sense.
3. **No fallback.** When a request fails or the answer is rejected, that ant does nothing
   this round. The dice of step 8 runs only when it is switched on by hand, and then the
   model is not asked at all — a colony that fell back to it would hide what the model
   does.
4. **The colony sleeps until the queen's first order**, and no request goes out before it.
5. **Confidence floor 0.22**, measured in the Bevy version. Note what `confidence` is: the
   distance from pure chance normalised by the number of options, not the top
   probability — which is the right measure when the options are built at runtime.
6. **The key belongs to the player**: `.env` or a password field in the sidebar, held for
   the run, never written down, with the call count and cost on screen.

## Things already learned here

* **`st.html` silently drops SVG.** It sanitises with an HTML profile, so the block
  renders empty with no error anywhere. Use `st.image`, which takes an SVG string.
  `st.components.v1.html` works too but wraps the board in an iframe whose height would
  have to be kept in step with the board.
* **No CORS problem, unlike the Bevy web build.** Streamlit calls the API from the server,
  so the browser never calls it and no proxy is needed. The Worker and the `Origin`
  business in the Rust repo have no counterpart here.
* **Coordinates count from the top left, y downwards**, the way SVG does. One coordinate
  system in a program this size. The price: north is `y - 1`.
* **The same wire format runs locally.** Ollama 0.35 serves `/v1/systemone` with
  the same questions, criteria, probabilities and confidence — its own
  announcement says it is based on TypeSafe's Jev API. The SDK speaks to it
  unchanged: `TYPESAFE_BASE_URL=http://localhost:11434` (no `/v1`, the SDK
  appends it) and `TYPESAFE_DEFAULT_MODEL=nimble`. Appendix B has the
  measurements (M4, 32 GB, Ollama 0.40.13, 2026-10-31): nimble plays as well as
  the cloud (19–23 rounds) but a round of eight takes 11–18 s against 0.6,
  because eight different prompts queue on one GPU. Ollama caches identical
  prompts (4 ms), so measure only with requests that differ — the old "163 ms"
  was the cache. kev and strands-decider never leave the nest: their
  confidence there stays under the 0.22 floor, which was measured for Jev.
* `typesafe-sdk` is the official Python client — `AsyncTypeSafeClient`, `Choice`,
  `client.system_one(state=…, questions=…)`, answers at
  `response.choices["step"].choice / .probabilities / .confidence`, and `response.usage`.
  `~/Desktop/git/python-jev` has a working example.

## Commands

```sh
uv run streamlit run app.py          # the app
uv add <package>                     # dependencies live in pyproject.toml
uv run --only-group docs mkdocs serve   # the bilingual website, locally
node tools/build_tutorial.js         # the German Word document
uv run python tools/svg_to_png.py    # diagrams, German and English, to PNG
uv export --no-hashes --no-dev --no-emit-project -o /dev/null   # requirements.txt is
                                     # hand-written and unpinned on purpose, for readers
```

`uv.lock` is what Streamlit Community Cloud installs from — it reads that before
`requirements.txt`.

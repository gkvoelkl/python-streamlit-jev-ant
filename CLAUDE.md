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

**The project is English** — code, identifiers, comments, UI text, README, commit
messages.

**The tutorial is German.** It is a Word document, written later, describing how to build
this in eight steps. So comments in the code should carry the reasoning a German reader
will need translated into the doc: say *why*, not just *what*.

## The eight steps

Each step ends in a program that runs. The tags `step-1` … `step-8` are those states, and
`steps/` holds the same files to copy from (generated from the tags at the end, so there
is one source of truth in practice).

1. The board — a grid as SVG
2. Colony and fruit — level 1 from JSON, drawn
3. One round — a button, ants move, no two on a cell
4. Carry and deliver — pick up, bring to the nest, stores, win at five
5. The first request — `typesafe-sdk`, the key, one answer shown
6. Jev decides — vision, options built at runtime, one `Choice` per ant
7. The queen — a text field, and a colony that sleeps until the first order
8. Seeing it — action and confidence per ant, a line with stores, requests, cost,
   discarded answers

**Stop after every step** so the change can be tested by hand before the next one starts.

**The tutorial grows with the code.** Every step gets its chapter in `tutorial/` as
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
   this round. The random movement of steps 3 and 4 is *replaced* in step 6, not kept
   underneath — a colony that worked without the model would hide what the model does.
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
* `typesafe-sdk` is the official Python client — `AsyncTypeSafeClient`, `Choice`,
  `client.system_one(state=…, questions=…)`, answers at
  `response.choices["step"].choice / .probabilities / .confidence`, and `response.usage`.
  `~/Desktop/git/python-jev` has a working example.

## Commands

```sh
uv run streamlit run app.py          # the app
uv add <package>                     # dependencies live in pyproject.toml
uv export --no-hashes --no-dev --no-emit-project -o /dev/null   # requirements.txt is
                                     # hand-written and unpinned on purpose, for readers
```

`uv.lock` is what Streamlit Community Cloud installs from — it reads that before
`requirements.txt`.

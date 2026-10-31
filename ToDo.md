# ToDo

What is still open, as of 2026-10-31.

## Revising the German chapters

- [ ] 0 — Introduction (vendor table dropped in 865e1f4, not yet revised in full)
- [x] 1 — The board
- [ ] 2 — One ant, and it asks
- [ ] 3 — The colony
- [ ] 4 — Carrying and delivering (revised once with the second level, check again)
- [ ] 5 — Eyes
- [ ] 6 — The queen (in progress, uncommitted)
- [x] 7 — Seeing it
- [x] 8 — What is the model worth?
- [ ] A — The plank (revised in 0b46a65, further edits uncommitted)
- [ ] B — Without the cloud

Typos in the uncommitted appendix A edits:

- "auf der der anderen Seite des Flusses" — double "der"
- "wo sie die Planke abgelegt" — missing "hat"

## Pictures

- [ ] `queeny_and_worker.JPG` (untracked, repo root) — decide where it goes,
      convert to PNG under `tutorial/bilder/`, or delete it
- [ ] `queen_queeny.JPG` in the repo root — same question

## English translation

Chapter 1 is translated, the rest links to the German chapters.

- [ ] 0 — Introduction
- [ ] 2 — One ant, and it asks
- [ ] 3 — The colony
- [ ] 4 — Carrying and delivering
- [ ] 5 — Eyes
- [ ] 6 — The queen
- [ ] 7 — Seeing it
- [ ] 8 — What is the model worth?
- [ ] A — The plank
- [ ] B — Without the cloud

Each translated chapter gets the `*[English version](../en/<name>.md)*` line in its
German original and an entry in `tutorial/en/README.md`.

Diagrams with text that still need an English copy in `tutorial/bilder/en/`
(then `uv run python tools/svg_to_png.py`):

- [ ] `konfidenz.svg`
- [ ] `optionen.svg`
- [ ] `richtungen.svg`
- [ ] `runde.svg`
- [ ] `schwelle.svg`
- [ ] `sichtweite.svg`

## At the end

- [ ] Check every code listing against the code, word for word
- [ ] Regenerate `steps/` from the tags `step-1` … `step-8` if the code changed
- [ ] Build the Word document (`node tools/build_tutorial.js`) and read it through
- [ ] Build the website locally (`uv run --only-group docs mkdocs serve`) and check
      the cross-language links

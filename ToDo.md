# ToDo

What is still open, as of 2026-10-31.

## Tutorial

- [x] German chapters revised (0–8, A, B)
- [x] Chapter 0 without the leftover table sentence, chapter 2 with 0.33 and
      0.29 told apart as two different answers
- [x] Authorship note at the end of every page, German and English
- [x] English translation of every chapter and both appendices, with the
      `*[English version]*` line in each German chapter
- [x] English copies of the diagrams in `tutorial/bilder/en/`
      (`python3 tools/translate_svg.py && uv run python tools/svg_to_png.py`)
- [ ] Read the English chapters through once more as a native reader would

## Pictures

- [x] `queeny_and_worker.JPG` deleted — the same picture is
      `tutorial/bilder/queeny-und-arbeiterinnen.png`
- [ ] `queen_queeny.JPG` in the repo root — the app's sidebar loads it, so it
      stays unless the app is changed

## Like python-streamlit-neural-earth-field

- [x] MIT licence (`LICENSE`) and the badge in `README.md`
- [x] `CITATION.cff` — add `version` and `date-released` with the release
- [ ] A GitHub remote, push, and the GitHub Pages website live
- [ ] Release `v1.0`, topics on GitHub, social preview with Queeny
- [ ] The app on Streamlit Community Cloud, with the badge and an
      “App online” link in the READMEs

## At the end

- [ ] Check every code listing against the code, word for word
- [ ] Regenerate `steps/` from the tags `step-1` … `step-8` if the code changed
- [ ] Build the Word document (`node tools/build_tutorial.js`) and read it through
- [ ] Build the website locally (`uv run --only-group docs mkdocs serve`) and check
      the cross-language links

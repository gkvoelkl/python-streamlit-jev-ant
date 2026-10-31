# Tutorial: When ants ask a decision model

*[Deutsche Fassung](../de/README.md) · The tutorial was written in German; all chapters and both appendices are translated.*

An ant colony in the browser, built in eight steps with Python and Streamlit.
Every ant asks a decision model what to do next – in this tutorial TypeSafe
Jev. You are the queen, and your only control is a sentence.

After every step there is a program that runs, and from step 2 on every step an
ant takes comes from the model.

## Getting started

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

From step 2 on you need a key from
[console.typesafe.ai/keys](https://console.typesafe.ai/keys) – or Ollama on
your own machine, see appendix B.

The app and the code are in English, so the listings in the German chapters
read the same as here.

## Contents

[Introduction](00-einleitung.md)

1. [The board](01-das-brett.md)
2. [One ant asks the decision model](02-eine-ameise-die-fragt.md)
3. [The ant colony](03-die-kolonie.md)
4. [Carrying and delivering](04-tragen-und-abliefern.md)
5. [Seeing](05-augen.md)
6. [The queen](06-die-koenigin.md)
7. [Insights](07-zusehen.md)
8. [What is the decision model worth?](08-was-bringt-das-modell.md)

**Appendix**

- A · [The way across the river](09-anhang-die-planke.md)
- B · [The same game without the cloud](10-anhang-b-ohne-cloud.md)

---

*This tutorial was created by Gerhard Völkl using Claude Code (Anthropic). It is meant to help you learn more about what happens when ants ask a decision model. Suggestions for improvement are welcome at gkvoelkl@nelson-games.de.*

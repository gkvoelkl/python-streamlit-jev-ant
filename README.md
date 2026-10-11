<p align="center">
  <img src="./tutorial/bilder/queeny-und-arbeiterinnen.png" alt="Queeny, the ant queen with a crown, in the colony's control room, with four worker ants in hard hats on either side." width="640">
</p>

<h1 align="center">Jev Ants</h1>

<p align="center">
  <b>An ant colony where every ant asks a decision model what to do next.</b><br>
  <b>Eine Ameisen-Kolonie, in der jede Ameise ein Decision-Model fragt, was sie als Nächstes tun soll.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Streamlit-1.64-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit 1.64">
  <img src="https://img.shields.io/badge/Decision%20model-TypeSafe%20Jev%20%7C%20Ollama-6A5ACD" alt="Decision model: TypeSafe Jev | Ollama">
  <a href="https://gkvoelkl.github.io/python-streamlit-jev-ant/"><img src="https://img.shields.io/badge/Tutorial-Deutsch%20%7C%20English-2A86B0" alt="Tutorial: Deutsch | English"></a>
  <a href="https://github.com/gkvoelkl/python-streamlit-jev-ant/actions/workflows/docs.yml"><img src="https://github.com/gkvoelkl/python-streamlit-jev-ant/actions/workflows/docs.yml/badge.svg" alt="Website build"></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-D97757?logo=claude&logoColor=white" alt="Claude Code"></a>
</p>

<p align="center">
  <a href="https://gkvoelkl.github.io/python-streamlit-jev-ant/en/">Tutorial (English)</a> ·
  <a href="https://gkvoelkl.github.io/python-streamlit-jev-ant/">Tutorial (Deutsch)</a> ·
  <a href="README_en.md">README (English)</a> ·
  <a href="README_de.md">README (Deutsch)</a>
</p>

---

## English

You are the queen of an ant colony, and your only way to intervene is to type
an order.

You type “Fetch the fruit from the north”, and every ant decides for itself what
that means for it — by asking a decision model.

A decision model does not answer in prose: it picks a next step from the current
situation and the possible actions.

### What you get

- **A game to try out** — a Streamlit app with eight ants on a board, fruit to
  bring home and a text field for the queen's orders. Above every ant you see
  what the model chose and how sure it was; below the board you see stores,
  requests and cost.
- **A matching tutorial** — in eight steps the tutorial builds the complete
  game: from an empty board to the colony. At the end of every step there is a
  game you can test.

### Getting started

You need Python 3.12 or newer and the tool [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

The app needs a key from [console.typesafe.ai](https://console.typesafe.ai/keys) —
or [Ollama](https://ollama.com) 0.35 or later on your own machine, with no key
and no cost.

- **Tutorial:** [website](https://gkvoelkl.github.io/python-streamlit-jev-ant/en/) · [Markdown](tutorial/en/README.md)
- **Details:** running without the cloud, the tutorial's sources, layout → [README_en.md](README_en.md)

---

<p align="center">
  <img src="./tutorial/bilder/das-spiel.png" alt="The finished game: eight ants on the board, above each one what the model chose and how sure it was." width="820">
  <br><sub><em>The game after step 7 · Das Spiel nach Schritt 7</em></sub>
</p>

---

## Deutsch

Sie sind die Königin einer Ameisen-Kolonie, und Ihre einzige Möglichkeit einzugreifen ist das Eingeben eines Befehls. 

Sie tippen „Holt die Früchte aus dem Norden", und jede Ameise entscheidet für sich, was das für sie bedeutet — indem sie ein Decision-Model fragt. 

Ein Decision-Model antwortet nicht in Prosa: Es wählt einen nächsten Schritt aus der aktuellen Situation und möglichen Aktionen.

### Was Sie bekommen

- **Ein Spiel zum Ausprobieren** — eine Streamlit-App mit acht Ameisen auf
  einem Brett, Früchten zum Heimbringen und einem Textfeld für die Befehle der Königin.
  Über jeder Ameise steht, was das Modell gewählt hat und wie sicher es dabei war,
  unter dem Brett sehen Sie Vorrat, Anfragen und Kosten.
- **Ein passendes Tutorial** — in acht Schritten baut das Tutorial das komplette Spiel auf: vom leeren Brett bis zur Kolonie. Am Ende jedes Schrittes ist ein testbares Spiel vorhanden.

### Loslegen

Sie brauchen Python 3.12 oder neuer und das Werkzeug [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

Die App braucht einen Schlüssel von [console.typesafe.ai](https://console.typesafe.ai/keys) —
oder [Ollama](https://ollama.com) ab Version 0.35 auf dem eigenen Rechner, ohne
Schlüssel und ohne Kosten.

- **Tutorial:** [Website](https://gkvoelkl.github.io/python-streamlit-jev-ant/) · [Markdown](tutorial/de/README.md)
- **Details:** ohne Cloud, die Quellen des Tutorials, Aufbau → [README_de.md](README_de.md)

---

<sub>TypeSafe Jev: [typesafe.ai](https://typesafe.ai) · Port of [rust-bevy-jev-ants](https://github.com/gkvoelkl/rust-bevy-jev-ants)</sub>

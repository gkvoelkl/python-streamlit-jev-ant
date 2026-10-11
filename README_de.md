# Jev Ants — Streamlit

*[English version](README_en.md)*

Eine Ameisen-Kolonie, in der jede Ameise ein Decision-Model —
[TypeSafe Jev](https://docs.typesafe.ai/introduction) — fragt, was sie als
Nächstes tun soll. Sie sind die Königin, und Ihr einziges Steuer ist ein Satz.

Eine kleine Python-Portierung von [rust-bevy-jev-ants](https://github.com/gkvoelkl/rust-bevy-jev-ants),
gebaut in acht Schritten — jeder ein Programm, das läuft, und ab Schritt 2 hat
das Modell jeden Schritt der Ameisen entschieden. Die Tags `step-1` … `step-8`
sind diese acht Stände, und `steps/` enthält dieselben Dateien zum Abschreiben.

## Starten

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

`uv` liest `pyproject.toml`, legt die Umgebung an und startet die App in einem
Zug. Ohne uv tut `pip install -r requirements.txt` und danach
`streamlit run app.py` dasselbe, mit nicht festgelegten Versionen.

Ab Schritt 2 brauchen Sie einen TypeSafe-Schlüssel von
[console.typesafe.ai](https://console.typesafe.ai/keys), entweder in `.env` als
`TYPESAFE_API_KEY` oder in der Seitenleiste eingetippt.

Ein Proxy ist nicht nötig: Streamlit schickt die Anfrage vom Server aus, der
Browser ruft die API nie selbst auf, und es gibt kein CORS-Problem.

### Ohne Cloud

Ollama ab Version 0.35 bietet Decision-Models lokal unter `/v1/systemone` an,
im selben Format wie TypeSafe. Drei Zeilen in `.env`, und die App läuft ohne
Schlüssel und ohne Kosten pro Anfrage:

```
TYPESAFE_API_KEY=ollama
TYPESAFE_BASE_URL=http://localhost:11434
TYPESAFE_DEFAULT_MODEL=nimble
```

Die Messungen dazu stehen in Anhang B des Tutorials.

## Das Tutorial

Das Tutorial baut das Spiel in acht Schritten. Es ist auf Deutsch geschrieben;
Schritt 1 ist ins Englische übersetzt, die übrigen Kapitel folgen.

- **Website:** [gkvoelkl.github.io/python-streamlit-jev-ant](https://gkvoelkl.github.io/python-streamlit-jev-ant/)
- **Markdown:** [tutorial/de/README.md](tutorial/de/README.md) · englische Übersetzung in [tutorial/en/](tutorial/en/README.md)
- **Word:** `Ameisen-die-fragen.docx`

Die Kapitel in `tutorial/de/` und `tutorial/en/` sind die Quelle. Zwei Dinge
werden daraus erzeugt — bearbeiten Sie die Kapitel, nicht diese:

```sh
uv run --only-group docs mkdocs serve     # die zweisprachige Website, lokal
npm install docx && node tools/build_tutorial.js   # das deutsche Word-Dokument
```

Ein GitHub-Actions-Workflow baut die Website und veröffentlicht sie auf GitHub
Pages, sobald ein Push auf `main` das Tutorial ändert.

`tutorial/baseline.py` gehört dazu: Es spielt das Spiel ohne Streamlit und
misst, was zufälliges Laufen erreicht — die Zahl, mit der Schritt 8 verglichen
wird.

## Aufbau

```
app.py              das Spiel, eine Datei
level1.json         das Brett, der Bau, die Früchte, was gewinnt
steps/              app.py nach jedem Schritt, erzeugt aus den Tags
tutorial/de/        die deutschen Kapitel — das Original
tutorial/en/        die englische Übersetzung, bisher Schritt 1
tutorial/bilder/    Bilder und Abbildungen; englische Abbildungen in bilder/en/
tools/              die Generatoren für Word-Dokument, PNGs und Website
mkdocs.yml          die Website
```

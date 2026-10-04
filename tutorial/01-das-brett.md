# Schritt 1 — Das Brett

![Queeny steht im Kontrollraum neben einem großen, leeren, grün leuchtenden
Schachbrett, dessen obere Ecke gerade erst aus einem Lichtblitz
entsteht](bilder/schritt-1-titel.png)

*Bevor eine Ameise loslaufen kann, braucht es ein Brett.*

**Ziel:** Eine Seite im Browser, auf der ein Spielbrett zu sehen ist. Ein Gitter,
24 Felder breit, 16 hoch. Sonst nichts.

![Das Ergebnis von Schritt 1: ein dunkles Schachbrett aus 24 mal 16 Feldern im
Browser, sonst nichts](bilder/schritt-1-brett.png)

*Mehr ist es nicht — und genau das ist der Sinn dieses Schrittes.*


## Wenn Sie ein neues Projekt anlegen

Die Bearbeitung von Python-Projekten erleichtert das Tool **uv** erheblich.
Sie finden es unter [docs.astral.sh/uv](https://docs.astral.sh/uv/); installiert
ist es mit einer Zeile:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```sh
mkdir python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv init --bare --name jev-ants --python 3.12
uv add streamlit typesafe-sdk python-dotenv
```

* `uv init --bare` legt nur eine `pyproject.toml` mit der Beschreibung des
  Projektes an.

*  `uv add` fügt die drei verwendeten Python-Module hinzu und erzeugt `uv.lock` mit den genauen Versionen.

`streamlit` macht es möglich Browser-Oberflächen mit Python zu erstellen.

`typesafe-sdk` ist die Bibliothek, die die Verbindung zum Modell Jev herstellt.

`python-dotenv` liest den API-Schlüssel für Jev aus einer Datei, damit dieser nicht direkt im Programm steht.

## Die erste Seite

Legen Sie `app.py` an:

```python
"""Jev Ants — an ant colony that asks TypeSafe Jev what to do next."""

import streamlit as st

COLUMNS = 24
ROWS = 16
CELL = 28

DARK = "#2b2b33"
LIGHT = "#33333d"

st.set_page_config(page_title="Jev Ants", page_icon="🐜", layout="wide")


def board() -> str:
    width = COLUMNS * CELL
    height = ROWS * CELL

    return f"""
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="chequer" width="{2 * CELL}" height="{2 * CELL}"
             patternUnits="userSpaceOnUse">
      <rect width="{2 * CELL}" height="{2 * CELL}" fill="{DARK}"/>
      <rect width="{CELL}" height="{CELL}" fill="{LIGHT}"/>
      <rect x="{CELL}" y="{CELL}" width="{CELL}" height="{CELL}" fill="{LIGHT}"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#chequer)"/>
</svg>
"""


st.title("🐜 Jev Ants")
st.caption(f"Step 1 — the board, {COLUMNS} by {ROWS}.")
st.image(board())
```

Starten:

```sh
uv run streamlit run app.py
```

Der Browser öffnet sich auf `http://localhost:8501` und zeigt die Spielfläche.

## Warum SVG

Das Spielbrett besteht aus Quadraten und später kommen ein paar Figuren hinzu.
Genau dafür ist SVG (**S**calable **V**ector **G**raphics, skalierbare
Vektorgrafik) besonders geeignet: Aus Linien, Flächen und Texten Bilder im Browser zu zeichnen. SVG ist ein Teil von
HTML, ein Text, der das Bild beschreibt.

Deshalb sind keine zusätzlichen JavaScript-Zeichenbibliotheken und keine
Bilddateien nötig, die das Programm beim Start erst nachladen müsste.

Die Funktion `board()` gibt eine Zeichenkette zurück — mehr ist nicht nötig.

## Warum ein `pattern` und keine Schleife

Das Naheliegende beim Erstellen des Spielfelds wäre eine doppelte Schleife über alle 24 × 16 Felder, die für jedes ein einzelnes Rechteck (in SVG `<rect>`) schreibt. 

Stattdessen verwendet das Programm ein `<pattern>`: Zwei Quadrate werden **einmal** beschrieben, und der Browser wiederholt sie über die ganze Fläche.


## Tipp: `st.image()` und nicht `st.html()` zum Zeichnen in Streamlit verwenden

Um eine Zeichenkette mit SVG auszugeben, wäre `st.html()` das Naheliegende —
SVG ist schließlich ein Teil von HTML. Der Aufruf funktioniert auch und wirft
keinen Fehler, aber auf der Seite ist **nichts** zu sehen.

Der Grund: Streamlit schickt die Zeichenkette durch einen Filter, der HTML
durchlässt und SVG entfernt. Übrig bleibt ein leerer Block. Keine Meldung, kein
Eintrag in der Browserkonsole, nichts.

Richtig ist `st.image()`. Es nimmt SVG als Zeichenkette direkt an und ist genau
dafür gedacht.

## Dark Mode

Ein schwarzes Brett auf weißem Hintergrund passt nicht.

Zwei Zeilen in `.streamlit/config.toml` der Streamlit-Konfigurationsdatei beheben das:

```toml
[theme]
base = "dark"
```

Diese Datei wird nur beim Start gelesen — nach einer Änderung daran also
Streamlit neu starten. `base = "dark"` schaltet die Darstellung auf den Dark
Mode um.

## Koordinaten: y zeigt nach unten

Eine Festlegung, die den Rest des Tutorials begleitet: Positionen werden von
**links oben** gezählt, x nach rechts, y nach **unten**. So rechnet SVG, und
zwei Koordinatensysteme in einem Programm dieser Größe lohnen sich nicht.

Das kostet genau eine Kleinigkeit, gleich im nächsten Kapitel: Norden ist
`y - 1`.

![Das Koordinatensystem: der Nullpunkt liegt links oben, x zählt nach rechts und
y nach unten; die Ameise steht auf (5, 3), darüber liegt Norden mit y minus
1](bilder/koordinaten.png)

*Die Zahlen am Rand sind die Spalten und Zeilen. Die Ameise steht auf (5, 3);
die vier Nachbarfelder zeigen, wie sich das rechnet.*

## Ausprobieren

* Das Brett ist da, dunkel kariert, 672 × 448 Pixel groß.
* Ändern Sie `CELL` auf 40 und laden Sie neu — Streamlit merkt die Änderung
  selbst.
* Tauschen Sie `st.image` versuchsweise gegen `st.html` und sehen Sie sich an,
  wie spurlos das verschwindet. Dann wieder zurück.

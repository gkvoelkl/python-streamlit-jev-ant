# Schritt 1 — Das Brett

**Ziel:** Eine Streamlit-Seite, auf der ein Spielbrett zu sehen ist. Ein Gitter,
24 Felder breit, 16 hoch. Sonst nichts.

Das klingt nach wenig für einen ganzen Schritt. Es ist aber genau deshalb ein
eigener Schritt: Wenn später etwas nicht auf dem Bildschirm erscheint, willst du
wissen, dass es nicht am Zeichnen liegt.

## Das Projekt anlegen

```sh
mkdir python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv init --bare --name jev-ants --python 3.12
uv add streamlit typesafe-sdk python-dotenv
```

`uv init --bare` legt nur eine `pyproject.toml` an und sonst nichts — kein
Beispielprogramm, das du gleich wieder löschst. `uv add` schreibt die drei
Abhängigkeiten hinein und erzeugt `uv.lock` mit den genauen Versionen.

`typesafe-sdk` ist die Bibliothek, mit der ab dem nächsten Kapitel gefragt
wird, `python-dotenv` liest den Schlüssel aus einer Datei. Beide kommen jetzt
schon mit, damit die Umgebung sich nicht mehr ändert.

> **Ohne uv:** Lege eine Datei `requirements.txt` mit den drei Zeilen
> `streamlit`, `typesafe-sdk`, `python-dotenv` an und rufe
> `pip install -r requirements.txt` auf.

## Die Seite

Lege `app.py` an:

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

Der Browser öffnet sich auf `http://localhost:8501` und zeigt ein dunkles
Schachbrett.

## Warum SVG

Das Brett besteht aus Rechtecken und später aus ein paar Zeichen darin. Genau
dafür ist SVG da: Text, den der Browser als Bild zeichnet. Kein Canvas, keine
Zeichenbibliothek, kein Bild, das irgendwo gespeichert werden müsste. Die
Funktion `board()` gibt eine Zeichenkette zurück — mehr ist es nicht.

Die Alternative wären 384 einzelne HTML-Kästchen oder ein Diagramm aus
Matplotlib. Beides geht, beides ist mehr Arbeit, und spätestens wenn über jeder
Ameise ein kleines Etikett stehen soll (Schritt 7), ist SVG das Einfachere:
Dort ist eine Position einfach ein Koordinatenpaar.

## Warum ein `pattern` und keine Schleife

Das Naheliegende wäre eine doppelte Schleife über alle 24 × 16 Felder, die für
jedes ein `<rect>` schreibt. Stattdessen steht dort ein `<pattern>`: Zwei
Quadrate werden **einmal** beschrieben, und der Browser wiederholt sie über die
ganze Fläche.

Das spart nicht nur Zeilen. Es sorgt dafür, dass ab dem nächsten Schritt jedes
einzelne Element im SVG etwas **bedeutet** — der Bau, eine Frucht, eine Ameise.
Der Fußboden ist eine Zeile und steht nicht mehr im Weg.

## Stolperstein: `st.html()` zeichnet nichts

Das Naheliegende für eine Zeichenkette voll SVG wäre `st.html()`. Der Aufruf
funktioniert, wirft keinen Fehler — und auf der Seite ist **nichts** zu sehen.

Der Grund: Streamlit schickt die Zeichenkette durch einen Filter, der HTML
durchlässt und SVG entfernt. Übrig bleibt ein leerer Block. Keine Meldung, kein
Eintrag in der Browserkonsole, nichts.

Richtig ist `st.image()`. Es nimmt SVG als Zeichenkette direkt an und ist genau
dafür gedacht.

> Es gäbe noch `st.components.v1.html()`. Das funktioniert auch, packt das
> Brett aber in einen Iframe, dessen Höhe man von Hand angeben muss — und die
> müsste man dann jedes Mal mitpflegen, wenn das Brett sich ändert.

## Ein dunkles Thema

Ein schwarzes Brett auf weißer Seite sieht aus wie ein Loch im Bildschirm.
Zwei Zeilen in `.streamlit/config.toml` beheben das:

```toml
[theme]
base = "dark"
```

Diese Datei wird nur beim Start gelesen — Streamlit also einmal neu starten.

## Koordinaten: y zeigt nach unten

Eine Festlegung, die den Rest des Tutorials begleitet: Positionen werden von
**links oben** gezählt, x nach rechts, y nach **unten**. So rechnet SVG, und
zwei Koordinatensysteme in einem Programm dieser Größe lohnen sich nicht.

Das kostet genau eine Kleinigkeit, gleich im nächsten Kapitel: Norden ist
`y - 1`.

## Ausprobieren

* Das Brett ist da, dunkel kariert, 672 × 448 Pixel groß.
* Ändere `CELL` auf 40 und lade neu — Streamlit merkt die Änderung selbst.
* Tausche `st.image` versuchsweise gegen `st.html` und sieh dir an, wie
  spurlos das verschwindet. Dann wieder zurück.

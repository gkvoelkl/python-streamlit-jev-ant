# Schritt 3 — Die Ameisen-Kolonie

![Mehrere Arbeiterinnen mit bunten Helmen stehen verteilt auf dem leuchtenden
Brett zwischen Früchten und dem Bau, jede mit einer Sprechblase voller
Fragezeichen; von jeder führt eine leuchtende Linie zu einem großen goldenen
„Jev" über dem Brett](bilder/schritt-3-titel.png)

*Alle fragen auf einmal, und alle fragen dasselbe Modell.*

**Ziel:** Acht Ameisen statt einer, das Spielfeld aus einer Datei lesen und für
alle acht gleichzeitig einen Weg beim Decision-Model erfragen.

![Das Brett von Schritt 3: acht Ameisen haben den Bau verlassen und verteilen
sich, dazwischen liegen die acht Früchte](bilder/schritt-3-kolonie.png)

*Nach fünf Runden. Die Früchte liegen herum, aber noch kann niemand etwas mit
ihnen anfangen — das ist Kapitel 4.*

Die Vorgehensweise aus Kapitel 2 bleibt unverändert. Was dazukommt, ist die Frage, 
wie man acht Ameisen steuert, ohne dass eine Runde vier Sekunden dauert.

## Das Level als Datei

Im ersten Level haben die Ameisen die Aufgabe möglichst ihr Futter (Früchte) in
dem Ameisenbau zu bringen.

`level1.json`:

```json
{
  "name": "Fruit for the stores",
  "briefing": "Eight ants, fruit scattered about, nothing in the way. Get five of them home.",

  "columns": 24,
  "rows": 16,

  "nest": { "x": 10, "y": 6, "size": 4 },
  "ants": 8,

  "fruit": [
    [3, 13], [5, 3], [18, 12], [20, 4],
    [2, 7], [21, 8], [12, 1], [14, 14]
  ],

  "target": 5
}
```

Dies Beschreibung des Levels ist in einer Datei abgelegt, die zu Beginn das Python-Programm liest. Dadurch ist es möglich, das Spiel um beliebig viele
Level zu erweitern.

`COLUMNS` und `ROWS` verschwinden aus dem Programm, da sie aus der Level-Datei kommen. Dadurch können Level unterschiedlich groß sein.

```python
def load_level() -> dict:
    with open(LEVEL_FILE, encoding="utf-8") as file:
        return json.load(file)
```

## Acht Ameisen im Bau

![Ausschnitt um den Bau: acht Ameisen sitzen in zwei Reihen zu vier in dem
gelb umrandeten Quadrat](bilder/bau-start.png)

*Die Startaufstellung: `i % size` und `i // size` verteilen die acht auf die
ersten Reihen.*

```python
    nest = level["nest"]
    st.session_state.ants = [
        {"x": nest["x"] + i % nest["size"], "y": nest["y"] + i // nest["size"]}
        for i in range(level["ants"])
    ]
    st.session_state.fruit = [tuple(cell) for cell in level["fruit"]]
    st.session_state.round = 0
```

`i % size` und `i // size` verteilen die acht auf die ersten Reihen des Baus.
Dass sie dort starten, ist keine Platzierungslaune: Die Kolonie ist zu Hause und
wartet auf einen Grund etwas zu unternehmen.

## Welches Feld ist bereits besetzt?

```python
def taken_cells() -> set[tuple[int, int]]:
    return {(ant["x"], ant["y"]) for ant in st.session_state.ants} | set(
        st.session_state.fruit
    )
```

Das Programm merkt sich in dem **Set taken**, auf welchem Feld (Cell) bereits eine Ameise oder eine Frucht sich befinden.

Ameisen und Früchte in **einer** Menge, weil sie für diese Frage beantwortet: 

Darf hier jemand hintreten? Ist das Feld frei?

`free_directions` bekommt das ****Set taken** zur Prüfung hinzu:

```python
def free_directions(level: dict, ant: dict, taken: set[tuple[int, int]]) -> list[str]:
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        on_board = 0 <= x < level["columns"] and 0 <= y < level["rows"]
        if on_board and (x, y) not in taken:
            open_ways.append(name)
    return open_ways
```

Damit ist die Auswahl, die das Decision-Model bekommt, noch einen Schritt enger an der
Wirklichkeit: kein Rand und kein Feld, auf dem schon eine Ameise oder einen Frucht ist.

## Acht Anfragen auf einmal

An dieser Stelle lohnt sich `async`.

```python
async def ask_everyone(payloads, key) -> list[object]:
    async with AsyncTypeSafeClient(api_key=key, timeout=20) as client:
        return await asyncio.gather(
            *(client.system_one(state=state, questions=q) for state, q in payloads),
            return_exceptions=True,
        )
```

Acht Anfragen, eine je Ameise, nacheinander zu je einer halben Sekunde sind in Summe vier Sekunden. Diese Anfragen gleichzeitg (asynchron) losgeschickt, bringen alle Anworten deutlich schneller.

Gemessen: **rund 0,6 Sekunden für eine komplette Runde.** 

`return_exceptions=True` sorgt dafür, dass das Pech einer Ameise nicht das der
Kolonie ist: Eine gescheiterte Anfrage kommt als Ausnahmeobjekt zurück, statt
die anderen sieben mitzureißen.

Aufgerufen wird das aus dem gewöhnlichen, synchronen Streamlit-Ablauf heraus mit
`asyncio.run(...)`.

## Die Runde

```python
def next_round(level: dict) -> None:
    taken = taken_cells()
    payloads = [question_for(level, ant, taken) for ant in st.session_state.ants]
    answers = asyncio.run(ask_everyone(payloads, api_key()))

    for ant, answer in zip(st.session_state.ants, answers):
        ...
        dx, dy = DIRECTIONS[step.choice]
        target = (ant["x"] + dx, ant["y"] + dy)
        if target not in taken:
            taken.discard((ant["x"], ant["y"]))
            ant["x"], ant["y"] = target
            taken.add(target)

    st.session_state.round += 1
```

![Ablauf einer Runde: erst ein Bild des Bretts, dann für jede der acht Ameisen
eine Frage, alle Anfragen gleichzeitig über asyncio.gather, dann die Antworten
nacheinander ausführen mit der Prüfung, ob das Zielfeld noch frei
ist](bilder/runde.png)

Erst **alle** fragen, dann alle handeln. Das hat eine Folge, die man leicht
übersieht: Jede Antwort wir auf Grundlage **des selben** Spielbretts entschieden 

Wenn zwei zufällig dasselbe Feld wählen, fängt dies die Prüfung `if target not in taken` beim Ausführen ab.

> Eine Antwort ist ein Wunsch, aber noch kein Zug.

## Zeichnen

Der Bau bekommt eine **Umrandung** statt einer Füllung:

```python
    nest_svg = (
        f'  <rect x="{nest["x"] * CELL}" y="{nest["y"] * CELL}" '
        f'width="{nest["size"] * CELL}" height="{nest["size"] * CELL}" '
        f'fill="{NEST_FILL}" stroke="{NEST_EDGE}" stroke-width="2"/>'
    )
```

![Derselbe Ausschnitt nach drei Runden: zwei Ameisen stehen noch im Bau, sechs
sind heraus und stehen ringsum auf dem Boden](bilder/bau-durchlaessig.png)

*Drei Runden später. Man sieht, warum der Bau eine Umrandung und keine Füllung
ist: Die Ameisen laufen hindurch und darüber hinaus. Ein ausgemalter Klotz sähe
aus wie ein Hindernis.*

Zur Darstellung der Spielelemente sind Emojis geeignet. Die Früchte sind 🍎 und die Ameisen sind 🐜. Die Ameisen erhalten zusätzlich einen hellen Hintergrund, damit sie auf dem Spielfeld besser zu erkennen sind.

```python
    fruit_svg = "\n".join(cell_text(x, y, "🍎") for x, y in st.session_state.fruit)
    ants_svg = "\n".join(
        cell_disc(ant["x"], ant["y"]) + "\n" + cell_text(ant["x"], ant["y"], "🐜")
        for ant in st.session_state.ants
    )
```

Durch die Emojis als Spielfiguren spart man sich zusätzliche Bilddateien.

## Ausprobieren

* „Next round" drücken: Die Kolonie kommt aus dem Bau. Die Antworten stehen
  darunter — meine erste Runde war `north 0.39 · north 0.68 · north 0.67 ·
  north 0.37 · west 0.26 · south 0.30 · south 0.32 · east 0.29`.
* Vier von acht wollten nach Norden. Bei dieser Konfidenz ist das kein Plan,
  sondern eine leichte Schlagseite des Modells, wenn nichts es lenkt.
* „Five rounds" drücken und auf die Uhr sehen — acht Ameisen mal fünf Runden
  sind vierzig Anfragen in ein paar Sekunden.
* Ändern Sie in `level1.json` `"ants"` auf 20 und laden Sie neu. Nichts passiert, weil
  `start()` die Kolonie nur aufstellt, wenn keine da ist. Dafür ist „Start
  over" da — und mit zwanzig Ameisen im Bau sehen Sie, wie eng es wird.

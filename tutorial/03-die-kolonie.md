# Schritt 3 — Die Kolonie

**Ziel:** Acht Ameisen statt einer, ein Brett aus einer Datei, und alle acht
werden gleichzeitig gefragt.

Das Prinzip aus Kapitel 2 bleibt unverändert. Was dazukommt, ist die Frage, wie
man acht davon bedient, ohne dass eine Runde vier Sekunden dauert.

## Das Level als Datei

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

**Warum nicht im Code?** Weil es Daten sind und keine Regeln. Ein zweites Level
ist so eine zweite Datei und keine zweite Programmfassung. Und an Zahlen, die in
einer Datei stehen, kann man folgenlos drehen — was Sie am Ende des Kapitels tun
sollten.

`COLUMNS` und `ROWS` verschwinden aus dem Code; die Maße kommen jetzt von hier.

```python
def load_level() -> dict:
    with open(LEVEL_FILE, encoding="utf-8") as file:
        return json.load(file)
```

## Acht Ameisen im Bau

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
wartet auf einen Grund zu gehen. In Kapitel 6 wird daraus etwas Sichtbares.

Die Früchte liegen ab jetzt auf dem Brett, tun aber noch nichts — das ist
Kapitel 4.

## Wo steht schon jemand

```python
def taken_cells() -> set[tuple[int, int]]:
    return {(ant["x"], ant["y"]) for ant in st.session_state.ants} | set(
        st.session_state.fruit
    )
```

Ameisen und Früchte in **einer** Menge, weil sie für die Frage, die diese
Funktion beantwortet, dasselbe sind: Darf hier jemand hintreten? Eine Ameise
geht um eine Frucht herum, nicht darüber.

Eine Menge und keine Liste, weil gleich sehr oft gefragt wird, ob ein bestimmtes
Feld darin vorkommt.

`free_directions` bekommt sie dazu:

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

Damit ist die Auswahl, die das Modell bekommt, noch einen Schritt enger an der
Wirklichkeit: kein Rand, und kein Feld, auf dem schon jemand steht.

## Acht Anfragen auf einmal

Hier lohnt sich `async` — und nur hier.

```python
async def ask_everyone(payloads, key) -> list[object]:
    async with AsyncTypeSafeClient(api_key=key, timeout=20) as client:
        return await asyncio.gather(
            *(client.system_one(state=state, questions=q) for state, q in payloads),
            return_exceptions=True,
        )
```

Acht Anfragen zu je einer halben Sekunde sind nacheinander vier Sekunden und
nebeneinander deutlich unter einer. Gemessen: **rund 0,6 Sekunden für eine
komplette Runde.** Eine Runde, die vier Sekunden dauert, sieht sich niemand an.

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

Erst **alle** fragen, dann alle handeln. Das hat eine Folge, die man leicht
übersieht: Jede Antwort ist gegen **dasselbe** Brett entschieden worden. Zwei
Ameisen können also dasselbe freie Feld wählen.

Deshalb die Prüfung `if target not in taken` beim Ausführen. Merksatz:

> Eine Antwort ist ein Wunsch, kein Zug.

Das gilt über dieses Programm hinaus. Sobald mehrere Anfragen parallel laufen,
ist jede Antwort gegen einen Stand entschieden, der beim Eintreffen schon
veraltet sein kann.

## Zeichnen

Der Bau bekommt eine **Umrandung** statt einer Füllung:

```python
    nest_svg = (
        f'  <rect x="{nest["x"] * CELL}" y="{nest["y"] * CELL}" '
        f'width="{nest["size"] * CELL}" height="{nest["size"] * CELL}" '
        f'fill="{NEST_FILL}" stroke="{NEST_EDGE}" stroke-width="2"/>'
    )
```

Er ist Boden wie jedes andere Feld — Ameisen laufen hindurch. Ein Klotz wäre das
Einzige, wonach er nicht aussehen darf.

Und die Bewohner, Früchte als 🍎, Ameisen als 🐜 auf ihrem hellen Stein:

```python
    fruit_svg = "\n".join(cell_text(x, y, "🍎") for x, y in st.session_state.fruit)
    ants_svg = "\n".join(
        cell_disc(ant["x"], ant["y"]) + "\n" + cell_text(ant["x"], ant["y"], "🐜")
        for ant in st.session_state.ants
    )
```

Emojis als Spielfiguren sind die kürzeste Lösung: keine Bilddateien, keine
Pfade. Der helle Kreis darunter ist nötig, weil eine dunkle Ameise auf dunklem
Boden kaum zu finden ist — und in Kapitel 7 liest sich das Etikett darüber
besser gegen etwas Helles.

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

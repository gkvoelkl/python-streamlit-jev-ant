# Schritt 7 — Einblicke

![Queeny, von hinten über die Schulter gesehen, blickt über das leuchtende Brett
auf vier Arbeiterinnen mit bunten Helmen; über jeder schwebt ein Pfeil in einem
farbigen Schild — grün, gelb, grün, rot —, und am Rand des Bretts leuchten zwei
Dollarzeichen](../bilder/schritt-7-titel.png)

*Jetzt sehen Sie, was jede Ameise vorhat*

**Ziel:**

* Über jeder Ameise steht, was das Decision-Model für sie entschieden hat und wie sicher es war — an den drei Farben zu sehen.
* Unter dem Spiel-Brett steht, was die Kolonie bisher geleistet und gekostet hat.

![Das Brett von Schritt 7 nach sechs Runden „Go east": acht Ameisen östlich des
Baus, über jeder ein grünes Etikett wie „E 0.99" oder „E 0.86"; ganz rechts
schiebt sich ein Etikett über die Ameise darüber](../bilder/schritt-7-einblicke.png)

*Sechs Runden nach „Go east": achtmal Osten, achtmal grün.*


## Jede Ameise merkt sich, was ihr gesagt wurde

In `start()` bekommt jede Ameise ein neues Attribut:

```python
            "said": None,
```

Und in `next_round`, direkt nach `accepted(...)`:

```python
        ant["said"] = (
            (way, answer.choices["step"].confidence) if way is not None else None
        )
```

`None` heißt: Diese Ameise hat in dieser Runde nichts getan. Entweder kam keine
Antwort, oder die Antwort wurde verworfen.

## Drei Farben und ein Strich

```python
SURE = [(0.85, "#7fd18b"), (0.60, "#e3c45c"), (0.0, "#e08074")]
UNSURE = "#8b8b93"
```

```python
def colour_of(confidence: float) -> str:
    """Which of the three bands a confidence falls into."""
    for floor, colour in SURE:
        if confidence >= floor:
            return colour
    return UNSURE
```

* **Grün** (ab 0,85): Das Modell hatte einen Grund.
* **Gelb** (ab 0,60): eine leichte Neigung.
* **Rot** (unter 0,60): Die Antwort hat die Schwelle von 0,22 genommen, aber
  das Modell rät im Grunde.
* **Grau**: Die Ameise hat nichts getan.

Rot reicht bis ganz nach unten, bis 0,0. Tiefer als 0,22 kommt aber keine
Antwort, die auf dem Brett erscheint — alles darunter wurde schon in
`accepted()` verworfen und wird grau.

Die Richtungen werden abgekürzt:

```python
SHORT = {
    "north": "N",
    "north-east": "NE",
    "east": "E",
    "south-east": "SE",
    "south": "S",
    "south-west": "SW",
    "west": "W",
    "north-west": "NW",
}
```

Ausgeschrieben wäre ein Etikett breiter als die drei Felder um die Ameise herum,
und das Brett würde zur Textwand.

```python
def label(ant: dict) -> str:
    if ant["said"] is None:
        text, colour = "—", UNSURE
    else:
        way, confidence = ant["said"]
        text, colour = f"{SHORT[way]} {confidence:.2f}", colour_of(confidence)

    return (
        f'  <text x="{ant["x"] * CELL + CELL / 2}" y="{ant["y"] * CELL - CELL * 0.15}" '
        f'font-size="{CELL * 0.38}" font-family="system-ui, sans-serif" '
        f'fill="{colour}" text-anchor="middle">{text}</text>'
    )
```

Der graue Strich für eine untätige Ameise ist wichtiger, als er aussieht. Ein
Brett, auf dem die Hälfte der Etiketten grau ist, sagt etwas über die **Frage**
aus, nicht über die Ameisen. Gar nichts zu zeichnen würde genau das verstecken.

Gezeichnet werden die Etiketten **zuletzt**, damit nie eine Ameise über einer
Beschriftung liegt — die Etiketten sind schließlich der Grund, warum man aufs
Brett schaut. Und sie erscheinen erst, wenn die Kolonie wach ist; vorher gibt
es nichts zu beschriften:

```python
    labels_svg = "\n".join(
        label(ant) for ant in st.session_state.ants if st.session_state.awake
    )
```

Unter dem Brett erklärt eine Zeile, was die Farben bedeuten:

```python
if st.session_state.awake:
    st.caption(
        "Above each ant: what Jev chose and how sure it was. "
        ":green[green from 0.85] · :orange[yellow from 0.60] · "
        ":red[red down to 0.22] · grey means the ant did nothing this round."
    )
```

## Was es kostet

```python
USD_PER_MILLION_TOKENS = 0.042
```

```python
cost = st.session_state.tokens * USD_PER_MILLION_TOKENS / 1_000_000
asked = st.session_state.requests
thrown = len(st.session_state.discarded)
```

Die Eingabe-Tokens zählt `accepted()` schon seit Schritt 6 mit. Jetzt steht
auch ihr Preis da.

```python
colony, meter = st.columns(2)
colony.write(
    f"Round **{st.session_state.round}** · "
    f"**{st.session_state.stores}** of {level['target']} stored · "
    f"**{carried}** carried · "
    f"**{len(st.session_state.fruit)}** on the board"
)
meter.write(
    f"**{asked}** decisions from Jev, **{thrown}** discarded"
    + (f" (**{thrown / asked:.0%}**)" if asked else "")
    + f" · {st.session_state.tokens:,} tokens · **\\${cost:.4f}**"
)
```

Links die Kolonie, rechts das Messgerät. Die Reihenfolge ist Absicht: Der
Vorrat ist das Spiel, die Kosten sind nur das, womit man es misst.

Aus einem echten Lauf: 88 Entscheidungen, 53 verworfen, 48.100 Token, **0,0020
Dollar**. Ein ganzes Spiel kostet also einen Fünftel-Cent, eine Runde mit acht
Ameisen rund 0,0002 Dollar. Diese Zahl sollte man kennen, bevor man anfängt,
im Sekundentakt nachzufragen.

## Tipp: Dollarzeichen sind LaTeX

Die erste Fassung schrieb `**${cost:.4f}**` — und auf dem Bildschirm stand die
Zahl nicht fett, sondern als Formel gesetzt. Streamlits Markdown liest ein Paar
Dollarzeichen als mathematische Formel.

Die Lösung ist `\\$` im Python-String, also ein escaptes Dollarzeichen im
Markdown.

## Was man jetzt sieht

Der Unterschied, den die Etiketten sichtbar machen, ist derselbe wie in
Kapitel 6. Nur sieht man ihn jetzt direkt, statt ihn aus einer Prozentzahl zu
erschließen.

Nach „Fan out and search, keep away from each other" stehen fast nur graue
Striche auf dem Brett.

Nach „Go east. Every one of you, east, until you find fruit — then bring it
home." sieht es aus wie im Bild oben: acht Etiketten, alle grün, alle `E`,
zwischen 0,86 und 0,99. Der Befehl ist eindeutig, die Antworten sind es auch.

Lange bleibt das nicht so. In einem anderen Lauf mit demselben Befehl stand
neben vier grünen `E` ein rotes `SE 0.36`. Es gehörte zu einer Ameise, der
Osten gerade versperrt war, und die deshalb etwas anderes wählen musste.
Darüber, was stattdessen richtig ist, sagt der Befehl nichts — und genau das
zeigt die Farbe.

So lesen Sie im Bild, was vorher eine Statistik war: **Ein klarer Befehl macht
sichere Ameisen.** Ob er sie auch klug macht, steht auf einem anderen Blatt —
genau diese Kolonie ist in Kapitel 6 mit einem ebenso klaren Befehl geschlossen
in eine Ecke marschiert.


## Ausprobieren

* Geben Sie einen eindeutigen Befehl („Go west") und einen vagen („Do something
  useful") und vergleichen Sie die Farben auf dem Brett.
* Zählen Sie die grauen Striche pro Runde. Das ist die Verwurfsquote, nur ohne
  Prozentrechnung.
* Beobachten Sie eine einzelne Ameise über mehrere Runden. Sieht sie eine
  Frucht, wird ihr Etikett grün, bevor sie dort ankommt.
* Lassen Sie die Kosten mitlaufen und rechnen Sie hoch: Was kostet ein Brett mit
  50 Ameisen und 200 Runden?

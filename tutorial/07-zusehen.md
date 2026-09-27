# Schritt 7 — Zusehen

**Ziel:** Über jeder Ameise steht, was Jev für sie entschieden hat und wie
sicher — in drei Farben. Unter dem Brett steht, was die Kolonie bisher
gekostet hat.

Ein Spiel darüber, was ein Modell entscheidet, muss das Entscheiden zeigen.
Sonst ist es ein Spiel über Ameisen, die laufen.

## Jede Ameise merkt sich, was ihr gesagt wurde

In `start()` bekommt jede Ameise ein Feld dazu:

```python
            "said": None,
```

Und in `next_round`, direkt nach `accepted(...)`:

```python
        ant["said"] = (
            (way, answer.choices["step"].confidence)
            if way is not None and not isinstance(answer, BaseException)
            else None
        )
```

`None` heißt: Diese Ameise hat in dieser Runde nichts getan — keine Antwort
bekommen oder eine, die verworfen wurde.

## Drei Farben und ein Strich

```python
SURE = [(0.85, "#7fd18b"), (0.60, "#e3c45c"), (0.0, "#e08074")]
UNSURE = "#8b8b93"
```

Grün heißt: Das Modell hatte einen Grund. Gelb: eine leichte Neigung. Rot: Es
hat die Schwelle von 0,22 gerade so genommen und rät im Grunde. Grau: Die
Ameise hat nichts getan.

```python
SHORT = {"north": "N", "north-east": "NE", ...}
```

Ausgeschrieben ist ein Etikett breiter als die drei Felder um die Ameise herum,
und das Brett wird zur Textwand.

```python
def label(ant: dict) -> str:
    if ant["said"] is None:
        text, colour = "—", UNSURE
    else:
        way, confidence = ant["said"]
        text, colour = f"{SHORT[way]} {confidence:.2f}", colour_of(confidence)

    return (
        f'  <text x="{ant["x"] * CELL + CELL / 2}" y="{ant["y"] * CELL - CELL * 0.15}" '
        f'font-size="{CELL * 0.38}" fill="{colour}" text-anchor="middle">{text}</text>'
    )
```

Der Strich für eine untätige Ameise ist wichtiger, als er aussieht. Ein Brett,
auf dem die Hälfte der Etiketten grau ist, sagt etwas über die **Frage** aus,
nicht über die Ameisen. Nichts zu zeichnen würde das verstecken.

Gezeichnet werden die Etiketten **zuletzt** — keine Ameise soll je über einer
Beschriftung liegen. Und nur, wenn die Kolonie wach ist; vorher gibt es nichts
zu beschriften.

## Was es kostet

```python
USD_PER_MILLION_TOKENS = 0.042

cost = st.session_state.tokens * USD_PER_MILLION_TOKENS / 1_000_000
```

Die Eingabe-Tokens wurden schon in Schritt 6 in `accepted()` mitgezählt. Jetzt
stehen sie mit ihrem Preis da.

```python
colony, model = st.columns(2)
colony.write(f"Round **{…}** · **{…}** of {…} stored · …")
model.write(f"**{asked}** decisions from Jev, **{thrown}** discarded …")
```

Links die Kolonie, rechts das Messgerät. Die Reihenfolge ist Absicht: Der
Vorrat ist das Spiel, die Kosten sind nur, womit man es misst.

Aus einem echten Lauf: 88 Entscheidungen, 53 verworfen, 48.100 Token, **0,0020
Dollar**. Ein ganzes Spiel kostet einen Fünftel-Cent — eine Runde mit acht
Ameisen rund 0,0002 Dollar. Das ist die Zahl, die man kennen sollte, bevor man
anfängt, im Sekundentakt nachzufragen.

## Stolperstein: Dollarzeichen sind LaTeX

Die erste Fassung schrieb `**${cost:.4f}**` — und auf dem Bildschirm stand die
Zahl in einem Code-Kasten statt fett. Streamlits Markdown liest ein Paar
Dollarzeichen als mathematische Formel.

Lösung: `\\$` im Python-String, also ein escaptes Dollarzeichen im Markdown.

## Was man jetzt sieht

Der Unterschied, den die Etiketten sichtbar machen, ist derselbe wie in
Kapitel 6 — nur sieht man ihn jetzt, statt ihn aus einer Prozentzahl zu
erschließen.

Nach „Fan out and search, keep away from each other": fast nur graue Striche.

Nach „Go east. Every one of you, east, until you find fruit — then bring it
home.":

```
E 0.99   E 0.98   E 0.97   E 0.99   SE 0.36
```

Sieben grüne Etiketten und ein rotes. Der Befehl ist eindeutig, die Antworten
sind es auch — und die einzelne rote gehört zu einer Ameise, der Osten gerade
versperrt war und die deshalb etwas anderes wählen musste.

Damit kannst du im Bild lesen, was vorher eine Statistik war: **Ein klarer
Befehl macht sichere Ameisen.** Ob er sie auch klug macht, steht auf einem
anderen Blatt — genau diese Kolonie ist in Kapitel 6 mit einem ebenso klaren
Befehl geschlossen in eine Ecke marschiert.

## Zwei Dinge, die absichtlich fehlen

**Kein Automatiklauf.** Es wäre leicht, einen Knopf einzubauen, der alle zwei
Sekunden eine Runde spielt. Er würde Geld ausgeben, während niemand hinsieht.
Bei einem Fünftel-Cent pro Spiel ist das kein Drama, aber es ist die falsche
Voreinstellung — und ein vergessener Tab wird teuer, sobald jemand das Brett
vergrößert.

**Etiketten überlappen**, wenn zwei Ameisen nebeneinander stehen. Das ließe
sich mit etwas Mühe lösen (versetzt zeichnen, oder nur das Etikett der
interessantesten Ameise). Für ein Programm dieser Größe ist die Mühe es nicht
wert; man sieht trotzdem, was los ist.

## Ausprobieren

* Gib einen eindeutigen Befehl („Go west") und einen vagen („Do something
  useful") und vergleiche die Farben auf dem Brett.
* Zähle die grauen Striche pro Runde. Das ist die Verwurfsquote, nur ohne
  Prozentrechnung.
* Beobachte eine einzelne Ameise über mehrere Runden. Sieht sie eine Frucht,
  wird ihr Etikett grün, bevor sie dort ankommt.
* Lass die Kosten mitlaufen und rechne hoch: Was kostet ein Brett mit 50
  Ameisen und 200 Runden?

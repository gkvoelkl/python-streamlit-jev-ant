# Schritt 5 — Sehen

*[English version](../en/05-augen.md)*

![Die Arbeiterin mit weißem Helm trägt jetzt eine runde Brille und zeigt auf
eine leuchtende Birne; um sie herum ein heller Kreis auf dem Brett, außerhalb
davon Dunkel und Nebel, in der Ferne der Bau und eine grüne
Spur](../bilder/schritt-5-titel.png)

*So weit sie sieht, so weit reicht die Wahl.*

**Ziel:** Die Ameise sieht, was um sie herum los ist und dazu ein Schwellenwert, unter dem eine Antwort verworfen wird.

![Das Brett von Schritt 5 nach zwölf Runden: die Ameisen verteilt, zwei tragen
eine Frucht, der Boden ist um den Bau herum grün von der Duftspur](../bilder/schritt-5-sehen.png)

*Zwölf Runden, drei Früchte im Vorrat. Das Grün ist die Spur — sie entsteht
weiter unten in diesem Kapitel.*

Bis hierher hat das Decision-Model mehr oder weniger geraten, weil im Zustand (state) nichts stand, woraus sich etwas schließen ließe. Das ändert sich jetzt — und die Kolonie fängt an zu arbeiten.

## Entfernung und Richtung in Worten

```python
def steps_away(dx: int, dy: int) -> int:
    return max(abs(dx), abs(dy))


def direction_of(dx: int, dy: int) -> str | None:
    step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
    for name, offset in DIRECTIONS.items():
        if offset == step:
            return name
    return None


def phrase(dx: int, dy: int) -> str:
    away = steps_away(dx, dy)
    return f"{away} cell{'' if away == 1 else 's'} to the {direction_of(dx, dy)}"
```

`steps_away` misst in Schritten, nicht in Luftlinie: Ein Diagonalschritt bringt
genauso weit wie ein gerader, also zählt der größere der beiden Abstände.

`phrase` erzeugt Sätze wie `2 cells to the north-east`. Immer **Relativ, niemals absolut.** 

Die Ameise erfährt, was um sie herum liegt — nicht, wo sie im Spielfeld steht. Eine Koordinate wäre eine Angabe, mit der sie nichts anfangen kann.

## Das Sichtfeld

```python
VISION_RADIUS = 3


def vision(level: dict, ant: dict) -> list[str]:
    seen = []

    for x, y in st.session_state.fruit:
        dx, dy = x - ant["x"], y - ant["y"]
        if steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"a fruit, {phrase(dx, dy)}")

    for other in st.session_state.ants:
        dx, dy = other["x"] - ant["x"], other["y"] - ant["y"]
        if other is not ant and steps_away(dx, dy) <= VISION_RADIUS:
            seen.append(f"another ant, {phrase(dx, dy)}")

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        if 0 < near <= VISION_RADIUS:
            seen.append(f"the nest, {phrase(nx - ant['x'], ny - ant['y'])}")

        ...  # and the trail, further down

    return seen
```

Die Ameise sieht in jede Richtung drei Felder weit, und das ist nicht viel — mit Absicht. Die Königin überblickt später (Kapitel 6) das ganze Brett und die einzelne Ameise nicht. Dieser Unterschied ist es, der die Kommandos der Königin später wertvoll macht.

![Das Sichtfeld: ein Fenster von sieben mal sieben Feldern um die Ameise, eine
Frucht drei Felder entfernt liegt darin, eine vier Felder entfernte nicht
mehr](../bilder/sichtweite.png)

Der Bau wird genannt, wenn er in Sichtweite ist und nur einer Ameise, die
etwas trägt. Weiter unten wird sie durch das ergänzt, was echte
Ameisen wirklich haben: eine Duftspur.

Und im Zustand:

```python
        "the ant can see": vision(level, ant) or ["nothing at all"],
```

## Die Auswahl sagt jetzt etwas

Bisher war die Auswahl für die Antwort eine Liste von Namen. Jetzt bekommt jede Richtung eine Beschreibung — wenn es etwas zu beschreiben gibt:

```python
def options(level: dict, ant: dict, taken: set[tuple[int, int]]) -> dict[str, str | None]:
    ways = free_directions(level, ant, taken)
    towards: dict[str, str] = {}

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        home = direction_of(nx - ant["x"], ny - ant["y"])
        if home and 0 < near <= VISION_RADIUS:
            towards[home] = f"towards the nest, {phrase(nx - ant['x'], ny - ant['y'])}"

        way = uphill(ant)
        if way and way[0] not in towards:
            towards[way[0]] = f"the smell of the colony gets {describe_scent(way[1])}er"
    else:
        visible = [
            (steps_away(x - ant["x"], y - ant["y"]), x, y)
            for x, y in st.session_state.fruit
            if steps_away(x - ant["x"], y - ant["y"]) <= VISION_RADIUS
        ]
        for _, x, y in sorted(visible):
            way = direction_of(x - ant["x"], y - ant["y"])
            if way:
                towards.setdefault(way, f"towards a fruit, {phrase(...)}")

    return {way: towards.get(way) for way in ways}
```


Die **Schlüssel** sind die offenen Richtungen, wie seit Kapitel 2. Die **Werte**
sagen, wohin es dort ginge, und sie entstehen in jeder Runde neu aus dem, was
diese Ameise sieht. Eine Richtung, in der nichts Interessantes liegt, bekommt
keine Beschreibung — das ist ehrlich, es gibt nichts darüber zu sagen.

Erinnern Sie sich an `dict.fromkeys(ways)` aus Kapitel 2: Dort standen überall
`None`. Jetzt stehen dort Sätze. Am Typ hat sich nichts geändert.

### Ein echtes Beispiel

Das hier ist mitgeschnitten aus einem laufenden Spiel, Runde 5. Die Ameise sieht
eine Frucht und eine Kollegin:

```json
"the ant can see": [
  "a fruit, 3 cells to the north-west",
  "another ant, 2 cells to the south-west"
]
```

Und das bekommt sie zur Auswahl:

```json
{
  "north":      null,
  "north-east": null,
  "east":       null,
  "south-east": null,
  "south":      null,
  "south-west": null,
  "west":       null,
  "north-west": "towards a fruit, 3 cells to the north-west"
}
```

Acht Richtungen, eine davon beschriftet. Die anderen sieben stehen ohne
Kommentar da, weil es über sie nichts zu sagen gibt — und genau das ist die
Information: Es gibt nur einen Grund, und er zeigt nach Nordwesten.

Dieselbe Ameise zwei Runden später, jetzt mit Frucht auf dem Rücken:

```json
"the ant can see": ["a clear smell of the colony, 1 cell to the south-east"]
```

```json
{ "south-east": "the smell of the colony gets clearer", ... }
```

## Eine Schwellwert

```python
MIN_CONFIDENCE = 0.22


def accepted(answer: object, offered: dict[str, str | None]) -> str | None:
    if isinstance(answer, BaseException):
        st.session_state.discarded.append(type(answer).__name__)
        return None

    step = answer.choices["step"]
    st.session_state.tokens += answer.usage.input_tokens

    if step.choice not in offered:
        st.session_state.discarded.append(f"{step.choice} was never offered")
        return None

    if step.confidence < MIN_CONFIDENCE:
        st.session_state.discarded.append(f"{step.choice} at {step.confidence:.2f}")
        return None

    return step.choice
```

Drei Arten, eine Antwort abzulehnen — und alle drei werden **gezählt**, nicht
stillschweigend überspielt. Ein aufklappbarer Bereich unter dem Brett zeigt sie
mit Begründung.

Aufgeklappt sieht das so aus — sechs Zeilen aus einem echten Lauf:

```
· north-east at 0.18
· north-west at 0.18
· north-east at 0.16
· north at 0.15
· north-east at 0.13
· north at 0.17
```

Alle knapp unter der Schwelle, und alle zeigen nach Norden. Das ist kein
Zufall, sondern dieselbe leichte Vorliebe des Modells, die in Kapitel 4 die
halbe Kolonie an den oberen Rand geschoben hat. Wenn nichts für eine Richtung
spricht, kommt sie durch — und die Schwelle fängt sie ab.

`MIN_CONFIDENCE = 0.22` ist gemessen, nicht geraten. Sie ist niedriger, als man vermuten würde, und das liegt daran, was Konfidenz misst: den auf die Zahl der Optionen normierten Abstand zum reinen Zufall. Bei acht Möglichkeiten ist 0,22 bereits ein erkennbarer Vorzug.

![Die Konfidenzskala von 0 bis 1 mit der Schwelle bei 0,22 und der Umrechnung:
bei acht Optionen entspricht das einer höchsten Wahrscheinlichkeit von
0,32](../bilder/schwelle.png)

Die zweite Prüfung — `step.choice not in offered` — ist die Rückversicherung
gegen den Fall, dass das Modell etwas nennt, was nie angeboten wurde. Sie hat
bei mir noch nie ausgelöst; genau das ist der Punkt der ganzen Konstruktion.
Aber man prüft, statt zu vertrauen.

Eine abgelehnte Antwort heißt: Diese Ameise tut in dieser Runde nichts und wird nächste Runde wieder gefragt.

## Die Spur nach Hause

Bis hierher weiß eine Ameise mit Frucht nur dann, wo ihr Ameisenbau liegt, wenn er in Sichtweite ist — also auf drei Feldern von 384. Das reicht nicht. 

Echte Ameisen verwenden nicht nur die Augen, sondern die **Duftspur**: Sie hinterlassen eine Spur, und der Rückweg ist die Richtung, in der sie stärker wird.


```python
# What a searching ant leaves on the cell it just left, before the decay below.
SCENT_DEPOSIT = 1.0

# What is left of that with every step since the ant was last in the nest.
SCENT_STEP_DECAY = 0.88

# Rounds for a trail to fade to half. Evaporation is not decoration: it is how
# the colony forgets a way that leads nowhere any more.
SCENT_HALF_LIFE = 12.0

# Below this a cell counts as unscented, so old trails stop being offered.
SCENT_THRESHOLD = 0.05
```

### Gelegt wird beim Suchen, nicht beim Tragen


```python
def lay_scent(level: dict, ant: dict) -> None:
    if in_nest(level, ant["x"], ant["y"]):
        ant["since_nest"] = 0
    else:
        ant["since_nest"] += 1

    if ant["carrying"]:
        return

    cell = (ant["x"], ant["y"])
    amount = SCENT_DEPOSIT * SCENT_STEP_DECAY ** ant["since_nest"]
    st.session_state.scent[cell] = max(st.session_state.scent.get(cell, 0.0), amount)
```

![Ausschnitt um den Bau nach achtzehn Runden: der Boden ringsum ist grün
gefärbt, am stärksten dicht am Bau, eine Ameise trägt gerade eine Frucht
heran](../bilder/spur-nahaufnahme.png)

*Die Straßen der Kolonie. Je näher am Bau, desto stärker der Duft — deshalb
führt bergauf nach Hause.*

Nur eine **suchende** Ameise markiert den Boden, und die Marke ist umso
schwächer, je weiter sie vom Bau weg ist. Damit hat das Feld eine Form: Der
höchste Wert ist im Bau. **Bergauf ist heimwärts.**

Jede Ameise zählt dafür ihre eigenen Schritte seit dem Bau mit — `since_nest`.
Dies setzt das Programm zurück, sobald sie wieder drinsteht.

### Die stärkste Ablage gewinnt, sie summieren sich nicht

Besser ist `max(...)` statt `+=`. 
Würden sich die Ablagen addiert, dann schlügen hundert schwache Spuren weit draußen eine starke am Bau. Der Verkehr zählt trotzdem, nur
anders: Ein oft begangener Weg wird oft neu markiert und überlebt dadurch das
Verdunsten.

### Verdunsten

```python
def evaporate() -> None:
    factor = 0.5 ** (1 / SCENT_HALF_LIFE)
    st.session_state.scent = {
        cell: strength * factor
        for cell, strength in st.session_state.scent.items()
        if strength * factor >= SCENT_THRESHOLD
    }
```

Das ist keine Kosmetik, sondern das Gedächtnis der Kolonie: So vergisst sie
einen Weg, der nichts mehr bringt. Und weil alles unter der Schwelle wegfällt,
bleibt das Wörterbuch klein — auf einem 24 × 16-Brett sind es selten mehr als
achtzig Felder.

### Bergauf

```python
def uphill(ant: dict) -> tuple[str, float] | None:
    here = st.session_state.scent.get((ant["x"], ant["y"]), 0.0)
    best = None
    for name, (dx, dy) in DIRECTIONS.items():
        strength = st.session_state.scent.get((ant["x"] + dx, ant["y"] + dy), 0.0)
        if strength >= SCENT_THRESHOLD and strength > here:
            if best is None or strength > best[1]:
                best = (name, strength)
    return best
```

Auf dem Gipfel gibt es nichts mehr hinauf, und `uphill` gibt `None` zurück. Das
ist kein Fehlschlag: Der Gipfel ist der Bau, und wer dort steht, ist angekommen.

### Als Satz, nicht als Zahl

```python
def describe_scent(strength: float) -> str:
    if strength >= 0.7:
        return "strong"
    return "clear" if strength >= 0.3 else "faint"
```

Im Zustand steht dann:

```
a clear smell of the colony, 1 cell to the north-west
```

Eine Zahl wie 0,41 würde eine Genauigkeit versprechen, die das Feld nicht hat,
und Wörter liest das Modell ohnehin besser. Dieselbe Überlegung wie beim
Sichtfeld: gesagt wird, was die Ameise *merkt*, nicht, was im Speicher steht.

### Was es bringt

Drei Fassungen, derselbe Befehl, je zwei Läufe:

| | Runden bis fünf Früchte |
|---|---|
| **Spur** | 16 · 17 |
| Abkürzung (Bau von überall sichtbar) | 18 · 16 |
| weder Spur noch Abkürzung | 2 von 5 nach 40 Runden — nicht geschafft |

Die Spur ist **so gut wie perfekte Information**. Sie holt genau das ein, was
die Abkürzung einfach geschenkt hat — nur dass die Kolonie es sich diesmal
selbst erarbeitet, Feld für Feld.

Und die dritte Zeile zeigt, dass hier wirklich etwas passiert: Ohne beides
kommt die Kolonie nicht ins Ziel.

## Die Frage sagt jetzt mehr

Der Text hat sich mitverändert:

> An ant of the colony has to decide which way to go next. The colony lives on
> fruit. An ant with empty hands searches: it walks towards any fruit it can
> see, and where it sees none it keeps going into open ground, away from the
> nest and away from the other ants, because ground another ant is already
> walking has nothing left on it. An ant carrying a fruit takes it to the nest.
> Which way should this ant go now?

Vorher stand dort nur, was die Kolonie im Großen tut. Jetzt steht da, was eine
Ameise mit leeren Händen tun soll.


## Ausprobieren

* Sehen Sie einer einzelnen Ameise zu, wenn eine Frucht in ihr Sichtfeld kommt.

* Klappen Sie die verworfenen Antworten auf. Wer verwirft — die Ameisen im Gedränge
  oder die im Freien?

* Setzen Sie `VISION_RADIUS` auf 1. Die Kolonie wird deutlich schlechter, und die
  Zahl der Verwürfe steigt.

* Setzen Sie `VISION_RADIUS` auf 8. Wird sie besser? Und was passiert mit der
  Tokenzahl?

* Setzen Sie `MIN_CONFIDENCE` auf 0.0: Jetzt wird jede Antwort angenommen, auch die
  geratene. Wird die Kolonie schneller oder langsamer?
  
* Nehmen Sie den Satz über das Ausschwärmen aus `STEP_QUESTION` heraus und
  fangen Sie neu an. Es lohnt sich, das einmal selbst gesehen zu haben.

* Sehen Sie dem Brett beim Grünwerden zu: Die Spur wächst dort am stärksten,
  wo viele Ameisen gehen, und der hellste Fleck liegt im Bau.

* Setzen Sie `SCENT_HALF_LIFE` auf 2 Runden. Die Spur verdunstet, bevor
  jemand sie brauchen kann — und die Kolonie ist wieder so hilflos wie in der
  dritten Zeile der Tabelle oben.

* Tauschen Sie in `lay_scent` das `max(...)` gegen `+=`. Die Ablagen summieren
  sich dann, der Gipfel wandert aus dem Bau heraus dorthin, wo am meisten
  Verkehr ist — und die Trägerinnen laufen in die falsche Richtung. Das ist der
  lehrreichste Fehler, den man in diesem Programm bauen kann.

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

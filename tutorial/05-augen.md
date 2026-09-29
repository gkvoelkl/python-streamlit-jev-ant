# Schritt 5 — Sehen

**Ziel:** Die Ameise sieht, was um sie herum los ist und dazu ein Schwellenwert, unter dem eine Antwort verworfen wird.

Bis hierher hat Jev mehr oder weniger geraten, weil im Zustand (state) nichts stand, woraus sich etwas schließen ließe. Das ändert sich jetzt — und die Kolonie fängt an zu arbeiten.

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
        if (nx, ny) != (ant["x"], ant["y"]):
            seen.append(f"the nest, {phrase(nx - ant['x'], ny - ant['y'])}")

    return seen
```

Die Ameise sieht in jede Richtung drei Felder weit, und das ist nicht viel — mit Absicht. Die Königin überblickt später (Kapitel 6) das ganze Brett und die einzelne Ameise nicht. Dieser Unterschied ist es, der die Kommandos der Königin später wertvoll macht.

Der Bau wird genannt, wenn er in Sichtweite ist, und nur einer Ameise, die
etwas trägt. Eine Zeit lang stand er hier aus **jeder** Entfernung — eine
Abkürzung, die das Problem aus Kapitel 4 löste, aber eine Ameise wissen ließ,
was sie nicht wissen kann. Weiter unten wird sie durch das ersetzt, was echte
Ameisen wirklich haben: eine Spur.

Und im Zustand:

```python
        "the ant can see": vision(level, ant) or ["nothing at all"],
```

## Die Auswahl sagt jetzt etwas

Bisher war die Auswahl eine Liste von Namen. Jetzt bekommt jede Richtung eine
Beschreibung — wenn es etwas zu beschreiben gibt:

```python
def options(level, ant, taken) -> dict[str, str | None]:
    ways = free_directions(level, ant, taken)
    towards = {}

    if ant["carrying"]:
        nx, ny = nearest_nest_cell(level, ant)
        near = steps_away(nx - ant["x"], ny - ant["y"])
        home = direction_of(nx - ant["x"], ny - ant["y"])
        if home and 0 < near <= VISION_RADIUS:
            towards[home] = f"towards the nest, {phrase(nx - ant['x'], ny - ant['y'])}"

        way = uphill(ant)          # die Spur, siehe weiter unten
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

Dieses eine Wörterbuch ist der Kern des Kapitels.

Die **Schlüssel** sind die offenen Richtungen, wie seit Kapitel 2. Die **Werte**
sagen, wohin es dort ginge, und sie entstehen in jeder Runde neu aus dem, was
diese Ameise sieht. Eine Richtung, in der nichts Interessantes liegt, bekommt
keine Beschreibung — das ist ehrlich, es gibt nichts darüber zu sagen.

Erinnern Sie sich an `dict.fromkeys(ways)` aus Kapitel 2: Dort standen überall
`None`. Jetzt stehen dort Sätze. Am Typ hat sich nichts geändert.

## Eine Schwelle

```python
MIN_CONFIDENCE = 0.22


def accepted(answer, offered) -> str | None:
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

`MIN_CONFIDENCE = 0.22` ist gemessen, nicht geraten; die Zahl stammt aus der
Rust-Fassung dieses Spiels. Sie ist niedriger, als man vermuten würde, und das
liegt daran, was Konfidenz misst: den auf die Zahl der Optionen normierten
Abstand zum reinen Zufall. Bei acht Möglichkeiten ist 0,22 bereits ein
erkennbarer Vorzug.

Die zweite Prüfung — `step.choice not in offered` — ist die Rückversicherung
gegen den Fall, dass das Modell etwas nennt, was nie angeboten wurde. Sie hat
bei mir noch nie ausgelöst; genau das ist der Punkt der ganzen Konstruktion.
Aber man prüft, statt zu vertrauen.

**Es gibt weiterhin keinen Rückfall auf Regeln.** Eine abgelehnte Antwort heißt:
Diese Ameise tut in dieser Runde nichts und wird nächste Runde wieder gefragt.

## Die Spur nach Hause

Bis hierher weiß eine Ameise mit Frucht nur dann, wo der Bau liegt, wenn er in
Sichtweite ist — also auf drei Feldern von 384. Das reicht nicht. Echte Ameisen
lösen das nicht mit Augen, sondern mit **Duft**: Sie hinterlassen eine Spur, und
der Rückweg ist die Richtung, in der sie stärker wird.

Genau das kommt jetzt dazu, mit den Zahlen, die die Rust-Fassung dieses Spiels
gemessen hat:

```python
SCENT_DEPOSIT = 1.0        # was eine suchende Ameise hinterlässt
SCENT_STEP_DECAY = 0.88    # ... mal diesem Wert je Schritt seit dem Bau
SCENT_HALF_LIFE = 12.0     # Runden, bis eine Spur auf die Hälfte verblasst
SCENT_THRESHOLD = 0.05     # darunter gilt ein Feld als geruchlos
```

### Gelegt wird beim Suchen, nicht beim Tragen

Das ist die Stelle, an der man es falsch herum bauen kann, und es sieht falsch
herum sogar plausibler aus.

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

Nur eine **suchende** Ameise markiert den Boden, und die Marke ist umso
schwächer, je weiter sie vom Bau weg ist. Damit hat das Feld eine Form: Sein
Gipfel liegt im Bau. **Bergauf ist heimwärts.**

Jede Ameise zählt dafür ihre eigenen Schritte seit dem Bau mit — `since_nest`,
zurückgesetzt, sobald sie wieder drinsteht.

### Die stärkste Ablage gewinnt, sie summieren sich nicht

`max(...)` statt `+=`, und das ist keine Kleinigkeit. Würden sich die Ablagen
addieren, dann schlügen hundert schwache Spuren weit draußen eine starke am Bau
— und die Steigung zeigte vom Bau **weg**. Der Verkehr zählt trotzdem, nur
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

> Ein Wort zur Bescheidenheit dieser Zahlen: Es sind Einzelläufe, und das Brett
> ist klein. Die Rust-Fassung hat auf einem Brett mit 2048 Feldern **+111 %**
> gemessen und auf einem kleinen nur +11 % — dort ist der Bau von einem Viertel
> des Bretts aus zu sehen, und wer ihn sieht, braucht keine Spur. Der
> Mechanismus ist nicht schwach, das Brett ist zu klein, um ihn zu brauchen.

## Die Frage sagt jetzt beides

Der Text hat sich mitverändert:

> An ant of the colony has to decide which way to go next. The colony lives on
> fruit. An ant with empty hands searches: it walks towards any fruit it can
> see, and where it sees none it keeps going into open ground, away from the
> nest and away from the other ants, because ground another ant is already
> walking has nothing left on it. An ant carrying a fruit takes it to the nest.
> Which way should this ant go now?

Vorher stand dort nur, was die Kolonie im Großen tut. Jetzt steht da, was eine
Ameise mit leeren Händen tun soll.

## Der Fehler, der mich das gelehrt hat

Meine erste Fassung nannte den Bau **immer** im Sichtfeld, auch einer Ameise mit
leeren Händen. Technisch lief alles: Anfragen gingen raus, Antworten kamen an,
nichts stürzte ab. Nach 22 Runden stand da:

> Round 22 · **0 of 5 stored** · 0 being carried · 8 left on the board

Null. Alle acht Ameisen saßen zusammengedrängt im Bau.

Die Ursache: Für das Modell war der Bau das einzige Ding im Zustand, das nach
einer Anweisung klang — die Frage sagte ja, dass die Kolonie Früchte dorthin
bringt. Also ging jede Ameise dorthin. Und wer im Bau steht, sieht keine Frucht
mehr.

Zwei Änderungen, beide oben schon zu sehen: Der Bau steht nur noch im Zustand,
wenn die Ameise trägt. Und die Frage nennt beide Aufgaben.

**Was im Zustand steht, ist das Verhalten.** Das ist die Lektion dieses
Kapitels, und sie ist mehr wert als der Code darin.

## Was jetzt passiert

Dieselbe Kolonie, dasselbe Level, nach den Änderungen:

> Round 15 · **3 of 5 stored** · 3 carried · 2 on the board · 120 decisions from
> Jev, 28 discarded

Aus dem Herumirren von Kapitel 4 ist eine Kolonie geworden, die liefert. Und die
verworfenen Antworten (28 von 120) haben fast alle dieselbe Form:

```
· west at 0.19
· north at 0.18
· south at 0.15
```

Knapp unter der Schwelle, alle von Ameisen, die gerade nichts sehen. Kein Mangel
des Modells — wer nichts sieht, hat keinen Grund für eine Richtung. Diese Zahl
fällt, sobald jemand etwas sagt. Das ist Kapitel 6.

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

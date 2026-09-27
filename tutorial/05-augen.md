# Schritt 5 — Augen

**Ziel:** Die Ameise erfährt, was um sie herum liegt, und die Auswahl, die sie
bekommt, sagt ihr, wohin es dort ginge. Dazu eine Schwelle, unter der eine
Antwort verworfen wird.

Bis hierher hat Jev geraten, weil im Zustand nichts stand, woraus sich etwas
schließen ließe. Das ändert sich jetzt — und die Kolonie fängt an zu arbeiten.

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

`phrase` erzeugt Sätze wie `2 cells to the north-east`. **Relativ, niemals
absolut.** Die Ameise erfährt, was um sie herum liegt — nicht, wo sie auf einem
Gitter steht, das sie nicht überblickt. Eine Koordinate wäre eine Angabe, mit
der sie nichts anfangen kann, und Token kostet sie auch.

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

Drei Felder weit, und das ist wenig — mit Absicht. Die Königin sieht in
Kapitel 6 das ganze Brett und die Ameise nicht. Dieser Unterschied ist es, der
ihren Satz später wertvoll macht.

Der Bau ist die Ausnahme: Er wird aus **jeder** Entfernung genannt, aber nur
einer Ameise, die etwas trägt. Echte Ameisen finden über ihre eigenen Schritte
heim, und diese Fassung hat keine Pheromonspuren, die die Arbeit übernehmen
könnten. Ohne diese Ausnahme bliebe das Problem aus Kapitel 4 bestehen.

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
        home = direction_of(nx - ant["x"], ny - ant["y"])
        if home:
            towards[home] = f"towards the nest, {phrase(nx - ant['x'], ny - ant['y'])}"
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

Erinnere dich an `dict.fromkeys(ways)` aus Kapitel 2: Dort standen überall
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

* Sieh einer einzelnen Ameise zu, wenn eine Frucht in ihr Sichtfeld kommt.
* Klapp die verworfenen Antworten auf. Wer verwirft — die Ameisen im Gedränge
  oder die im Freien?
* `VISION_RADIUS` auf 1 setzen. Die Kolonie wird deutlich schlechter, und die
  Zahl der Verwürfe steigt.
* `VISION_RADIUS` auf 8 setzen. Wird sie besser? Und was passiert mit der
  Tokenzahl?
* `MIN_CONFIDENCE` auf 0.0 setzen: Jetzt wird jede Antwort angenommen, auch die
  geratene. Wird die Kolonie schneller oder langsamer?
* Nimm den Satz über das Ausschwärmen aus `STEP_QUESTION` heraus und fang neu
  an. Es lohnt sich, das einmal selbst gesehen zu haben.

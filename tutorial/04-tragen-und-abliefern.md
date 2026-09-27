# Schritt 4 — Tragen und abliefern

**Ziel:** Eine Ameise, die an einer Frucht vorbeikommt, nimmt sie auf. Kommt sie
damit in den Bau, wandert die Frucht in den Vorrat. Fünf Früchte gewinnen das
Level.

Damit ist das Spiel vollständig — es hat ein Ziel, einen Weg dorthin und ein
Ende. Und es ist mühsam anzusehen: Jev entscheidet zwar jeden Schritt, aber die
Ameisen sind blind und niemand hat ihnen etwas gesagt. Sie stolpern in Früchte
und in den Bau. Genau daran arbeiten die beiden nächsten Kapitel.

## Eine Ameise trägt etwas

In `start()` bekommt jede Ameise ein Feld dazu:

```python
        {
            "x": nest["x"] + i % nest["size"],
            "y": nest["y"] + i // nest["size"],
            "carrying": False,
        }
```

Ein Wahrheitswert, keine Fruchtkennung. Eine Ameise trägt höchstens eine
Frucht, und welche es ist, spielt nie eine Rolle — Früchte sind austauschbar.
Das ist die Art Vereinfachung, die man treffen darf, solange sie stimmt.

Dazu der Vorratszähler:

```python
    st.session_state.stores = 0
```

## Wo ist der Bau, wo ist Obst

```python
def in_nest(level: dict, x: int, y: int) -> bool:
    nest = level["nest"]
    return (
        nest["x"] <= x < nest["x"] + nest["size"]
        and nest["y"] <= y < nest["y"] + nest["size"]
    )


def fruit_beside(ant: dict) -> tuple[int, int] | None:
    for dx, dy in DIRECTIONS.values():
        cell = (ant["x"] + dx, ant["y"] + dy)
        if cell in st.session_state.fruit:
            return cell
    return None
```

**Daneben, nicht darunter.** Eine Ameise steht nie auf einer Frucht — das
verhindert `taken_cells()` seit Schritt 3. Aufgenommen wird also immer vom
Nachbarfeld aus. Deshalb geht `fruit_beside` die acht Richtungen durch, dieselben
wie beim Laufen.

## Die Folgen eines Schrittes

```python
def pick_up_and_deliver(level: dict, ant: dict) -> None:
    if ant["carrying"]:
        if in_nest(level, ant["x"], ant["y"]):
            ant["carrying"] = False
            st.session_state.stores += 1
        return

    fruit = fruit_beside(ant)
    if fruit is not None:
        st.session_state.fruit.remove(fruit)
        ant["carrying"] = True
```

Hier steckt eine Entwurfsentscheidung, die später Geld spart, deshalb steht sie
ausführlich hier:

**Aufnehmen und Abliefern sind keine Entscheidungen, sondern Folgen.** Jev
entscheidet nur, wohin die Ameise geht. Steht danach eine Frucht neben ihr,
nimmt sie sie; steht sie mit Frucht im Bau, legt sie sie ab.

Man könnte es anders bauen und das Modell fragen: „Willst du diese Frucht
aufnehmen?" Diese Frage hat aber praktisch immer dieselbe Antwort —
und jede Frage kostet eine Anfrage, also Zeit und Geld. Fragen lohnt sich nur,
wo die Antwort offen ist.

## Eine Feinheit in der Runde

In `next_round` wird der Schritt jetzt so abgeschlossen:

```python
        # After the step, not before: a fruit picked up here is gone from
        # `taken` for everybody who moves after this ant.
        before = set(st.session_state.fruit)
        pick_up_and_deliver(level, ant)
        taken -= before - set(st.session_state.fruit)
```

Wenn eine Ameise eine Frucht aufnimmt, verschwindet die vom Brett — und das
Feld, auf dem sie lag, ist frei. Die Ameisen, die in derselben Runde noch
laufen, müssen das wissen, sonst weichen sie einem Hindernis aus, das es nicht
mehr gibt.

Die Zeile zieht aus `taken` genau die Felder ab, die dieser Aufnahmevorgang
geleert hat. Beachten Sie auch, dass `pick_up_and_deliver` **nach** dem Laufen
aufgerufen wird, nicht davor: Was zählt, ist, wo die Ameise jetzt steht.

Und aus dem `continue` von vorher wird ein `if ways:` — eine Ameise, die nicht
laufen kann, weil ringsum alles besetzt ist, kann trotzdem etwas aufnehmen
oder abliefern.

## Die Frucht auf dem Rücken

`cell_text` bekommt zwei Parameter dazu:

```python
def cell_text(x: int, y: int, glyph: str, size: float = 0.7, lift: float = 0.0) -> str:
    return (
        f'  <text x="{x * CELL + CELL / 2}" y="{(y - lift) * CELL + CELL / 2}" '
        f'font-size="{CELL * size}" text-anchor="middle" '
        f'dominant-baseline="central">{glyph}</text>'
    )
```

Und in `board()` bekommt eine tragende Ameise eine kleine Frucht darüber:

```python
    ants_svg = "\n".join(
        cell_text(ant["x"], ant["y"], "🐜")
        + (
            "\n" + cell_text(ant["x"], ant["y"], "🍎", size=0.45, lift=0.3)
            if ant["carrying"]
            else ""
        )
        for ant in st.session_state.ants
    )
```

Kleiner und höher, damit man beladene von leeren Ameisen über das ganze Brett
hinweg unterscheiden kann. Genau hier zahlt sich SVG aus: „ein bisschen höher"
ist `y - 0.3`, nicht ein CSS-Rätsel.

## Vorrat und Sieg

```python
won = st.session_state.stores >= level["target"]
carried = sum(ant["carrying"] for ant in st.session_state.ants)

st.write(
    f"Round **{st.session_state.round}** · "
    f"**{st.session_state.stores}** of {level['target']} stored · "
    f"**{carried}** being carried · "
    f"**{len(st.session_state.fruit)}** left on the board"
)

if won:
    st.success(...)
```

Beide Knöpfe werden abgeschaltet, sobald gewonnen ist:

```python
ready = bool(api_key()) and not won

if one.button("Next round", type="primary", disabled=not ready):
    ...

if five.button("Five rounds", disabled=not ready):
    for _ in range(5):
        if st.session_state.stores >= level["target"]:
            break
        next_round(level)
```

## Warum es so zäh ist

Sehen Sie eine Weile zu, dann sehen Sie das Muster: Eine Frucht ist schnell
aufgenommen — acht Ameisen decken viel Fläche ab, und sie müssen nur daneben
geraten. Zurück in den Bau zu finden, ist das Problem. Der Bau sind 16 von 384
Feldern, und eine Ameise, die nicht weiß, wo er liegt, findet ihn nur zufällig.

Sie werden fast alle Ameisen beladen herumirren sehen.

Das ist kein Fehler im Programm und auch keiner des Modells. Es ist eine Frage,
die mit nichts zu beantworten ist: Im Zustand steht nicht, wo der Bau liegt, und
im Sichtfeld — das es noch gar nicht gibt — auch nicht. **Kapitel 5 gibt der
Ameise Augen**, und dort wird aus dem Herumirren ein Heimweg.

Wie schlecht „zäh" genau ist, messen wir in Kapitel 8 gegen einen Würfel. Für
den Moment reicht das Gefühl.

## Ausprobieren

* Drücken Sie „Five rounds" ein paarmal. Bald tragen die meisten Ameisen eine
  Frucht, und im Vorrat liegt kaum etwas.
* Sehen Sie sich eine beladene Ameise genau an: die Frucht sitzt klein über ihr.
* Halten Sie durch bis fünf — es dauert, und es kostet: acht Anfragen pro Runde.
  Die Erfolgsmeldung nennt die Rundenzahl; merken Sie sie sich für Kapitel 8.
* Setzen Sie in `level1.json` den Bau probeweise auf `"size": 10` und drücken
  Sie „Start over". Mit einem riesigen Bau ist das Spiel plötzlich leicht. Das ist kein
  Balancing-Tipp, sondern die Bestätigung, woran es liegt: am Heimfinden.
* Sehen Sie sich den Zustand an, der jetzt verschickt wird — er hat zwei Zeilen
  bekommen (`carrying`, `in the nest`). Jede davon war eine Entscheidung. Was
  fehlt, ist alles, was die Ameise *sieht*.

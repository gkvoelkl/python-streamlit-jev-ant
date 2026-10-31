# Schritt 4 — Tragen und abliefern

*[English version](../en/04-tragen-und-abliefern.md)*

![Eine Arbeiterin mit weißem Helm schleppt einen großen roten Apfel über das
Brett und läuft dabei vom Bau weg, der gleich hinter ihr liegt; daneben zeigt
eine Leuchttafel „0/5"](../bilder/schritt-4-titel.png)

*Tragen kann sie jetzt. Sehen noch nicht.*

**Ziel:** Eine Ameise, die an einer Frucht vorbeikommt, nimmt sie auf. Kommt sie
damit in den Bau, wandert die Frucht in den Vorrat. Sobald fünf Früchte im Bau sind, ist das Level gewonnen.

![Das Brett von Schritt 4 nach 25 Runden: mehrere Ameisen stehen am oberen
Rand, eine davon trägt eine Frucht, zwei sitzen im Bau, die Früchte liegen
unberührt](../bilder/schritt-4-tragen.png)

*Fünfundzwanzig Runden, kein einziges Stück im Vorrat. Woran das liegt, steht
weiter unten — und es ist aufschlussreicher, als es aussieht.*

Damit ist das Spiel vollständig — es gibt ein Ziel, einen Weg dorthin und ein
Ende. Das Decision-Model entscheidet zwar jeden Schritt, aber die Ameisen sehen nicht und niemand sagt ihnen etwas. Sie stolpern in Früchte und in den Bau. 

Daran arbeiten die beiden nächsten Kapitel.

## Eine Ameise trägt etwas

In `start()` bekommt jede Ameise ein Feld dazu:

```python
        {
            "x": nest["x"] + i % nest["size"],
            "y": nest["y"] + i // nest["size"],
            "carrying": False,
        }
```

Eine Ameise trägt höchstens eine Frucht, und welche es ist, spielt nie eine
Rolle. Daher genügt der Wahrheitswert `carrying` — eine Kennung wäre eine
Angabe, die nie jemand liest.

Dazu der Vorratszähler, wie viele Früchte bereits im Bau sind:

```python
    st.session_state.stores = 0
```

## Wo ist der Bau? Wo ist Obst?

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
verhindert `taken_cells()` seit Schritt 3. Aufgenommen wird also immer von einem
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

**Aufnehmen und Abliefern sind keine Entscheidungen, sondern Folgen.** Das Modell
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

Ein Nebeneffekt, der später noch eine Rolle spielt: Scheitert die Anfrage einer
Ameise, springt die Schleife mit `continue` weiter — und überspringt damit auch
`pick_up_and_deliver`. Diese Ameise nimmt in der Runde also nicht einmal eine
Frucht auf, neben der sie steht. Eine Ameise, die nur nicht laufen **konnte**,
weil das Zielfeld besetzt war, nimmt dagegen auf. In Kapitel 5, wo die
verworfenen Antworten ein eigenes Thema werden, wird das begradigt.

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

![Nahaufnahme: zwei Ameisen nebeneinander unterhalb des Baus, die rechte trägt
eine kleine Frucht auf dem Rücken](../bilder/ameise-mit-frucht.png)

*Links leer, rechts beladen, darüber die gelbe Kante des Baus. Der Unterschied
muss über das ganze Brett hinweg erkennbar sein, nicht nur in der
Nahaufnahme.*

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

Eine Frucht ist schnell aufgenommen — acht Ameisen decken viel Fläche ab, und
sie müssen nur daneben geraten. Zurück in den Bau zu finden, ist das Problem.
Der Bau sind 16 von 384 Feldern, und eine Ameise, die nicht weiß, wo er liegt,
findet ihn nur durch Zufall.

Beim Zusehen kommt aber noch etwas heraus, das ich nicht erwartet hatte. Nach
fünfundzwanzig Runden stand die Kolonie so da:

```
Ameise 1: (17,  0)        Ameise 5: (14,  0)
Ameise 2: ( 6,  0) trägt  Ameise 6: (11, 10)
Ameise 3: (21,  0)        Ameise 7: (18,  0)
Ameise 4: (22,  0)        Ameise 8: (13, 10)
```

**Sechs von acht kleben am oberen Rand.** `y = 0`, quer über das ganze Brett
verteilt.

Das ist kein Herumirren, das ist eine Richtung. Erinnern Sie sich an die erste
Runde aus Kapitel 3: Vier von acht Ameisen wählten `north`, alle mit niedriger
Konfidenz. Wenn nichts eine Richtung von der anderen unterscheidet, hat das
Modell trotzdem eine leichte Vorliebe — und acht Ameisen, die alle derselben
leichten Vorliebe folgen, landen nach fünfundzwanzig Runden gemeinsam an der
Wand.

Weder ein Fehler im Programm noch einer des Modells. Es ist die ehrliche
Antwort auf eine Frage ohne Anhaltspunkte. Im Zustand steht nicht, wo der Bau
liegt, es steht nicht darin, wo Obst liegt, und ein Sichtfeld gibt es noch gar
nicht. Gefragt wird trotzdem — achtmal pro Runde, und bezahlt wird auch.

Merken Sie sich das Bild für den Vergleich. **In Kapitel 5 lernen die Ameisen
zu sehen**, und dort wird aus dem Herumirren ein Heimweg; in Kapitel 6 bekommt
die Königin eine Stimme, und dann ist die leichte Vorliebe des Modells nicht
mehr das Stärkste im Zustand.

## Ausprobieren

* Drücken Sie „Five rounds" ein paarmal. Bald tragen die meisten Ameisen eine
  Frucht, und im Vorrat liegt kaum etwas.

* Sehen Sie sich eine beladene Ameise genau an: die Frucht sitzt klein über ihr.

* Setzen Sie in `level1.json` den Bau probeweise auf `"size": 10` und drücken
  Sie „Start over". Mit einem riesigen Bau ist das Spiel plötzlich leicht. Das ist kein
  Balancing-Tipp, sondern die Bestätigung, woran es liegt: am Heimfinden.
  
* Sehen Sie sich den Zustand an, der jetzt verschickt wird — er hat zwei Zeilen
  bekommen (`carrying`, `in the nest`). Jede davon war eine Entscheidung. Was
  fehlt, ist alles, was die Ameise *sieht*.

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

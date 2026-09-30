# Anhang A — Die Planke und der Fluss

Das Spiel der acht Schritte, um drei Dinge erweitert: **Wasser**, das keine
Ameise durchquert, eine **Planke**, die eine Ameise aufheben kann, und einen
**Übergang**, der dort entsteht, wo sie abgelegt wird.

Alles andere ist unverändert übernommen, die Duftspur aus Kapitel 5
eingeschlossen — eine Ameise mit Frucht findet hier genauso über den Geruch nach
Hause wie auf dem ersten Brett.

Das Level ist das zweite aus der Rust-Fassung dieses Spiels, mit gespiegeltem y.

Das fertige Programm liegt unter `anhang/app_mit_planke.py`, das Level daneben
als `anhang/level-planke.json`:

```sh
uv run streamlit run anhang/app_mit_planke.py
```

## Das Level

![Das Plankenlevel zu Beginn: die Früchte in der Nordwest-Ecke, davor ein
L-förmiger Fluss, in der Mitte der Bau mit acht Ameisen, weit im Südosten die
kleine braune Planke](bilder/planke-start.png)

Die Aufgabe steckt nicht im Tragen, sondern im **Sehen**. Keine Ameise weiß,
dass hinter dem Fluss Obst liegt. Keine weiß, dass eine Planke helfen würde.
Und keine sieht beides — drei Felder Sicht, und die beiden Dinge liegen eine
halbe Brettbreite auseinander.

Nur Sie sehen das ganze Bild, und ein Satz ist alles, was Sie haben.

```json
{
  "columns": 30,
  "rows": 20,
  "nest": { "x": 13, "y": 8, "size": 4 },
  "water": [[7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6],
            [6, 6], [5, 6], [4, 6], [3, 6], [2, 6], [1, 6], [0, 6]],
  "plank": [22, 15],
  "target": 5
}
```

Der Fluss ist überall ein Feld breit. Das genügt: Niemand watet.

## Eine Hand statt eines Schalters

Bisher war `carrying` ein Wahrheitswert — trägt eine Frucht, ja oder nein. Jetzt
gibt es zwei Dinge zu tragen, also wird daraus ein Wort:

```python
            "holding": None,        # oder "a fruit" oder "the plank"
```

Das zahlt sich gleich zweimal aus. Im Zustand steht der Wert unverändert drin:

```python
        "the ant is carrying": ant["holding"] or "nothing",
```

Aus `"a fruit"` wird `"the plank"`, und die Frage versteht das ohne weiteres
Zutun.

## Wasser ist besetzt, der Übergang ist es nicht

```python
def taken_cells() -> set[tuple[int, int]]:
    blocked = {(ant["x"], ant["y"]) for ant in st.session_state.ants}
    blocked |= set(st.session_state.fruit)
    blocked |= st.session_state.water - {st.session_state.bridge}
    if st.session_state.plank:
        blocked.add(st.session_state.plank)
    return blocked
```

Eine einzige Zeile macht den Fluss unpassierbar, und der Mengenabzug
`- {st.session_state.bridge}` macht genau ein Feld davon wieder begehbar. Weil
`free_directions` auf dieser Menge aufbaut, wirkt das sofort überall: Kein
Nachbarfeld im Wasser wird angeboten, das Feld mit der Planke schon.

Ein Hindernis einzuführen kostet in diesem Programm eine Zeile. Das ist kein
Zufall, sondern die Ernte aus Schritt 3: Alles, was „hier steht schon etwas"
heißt, sammelt sich an einer Stelle.

## Die eine Option, die keine Richtung ist

```python
TAKE_PLANK = "take the plank"

    plank = st.session_state.plank
    if plank and not ant["holding"] and steps_away(...) == 1:
        extra[TAKE_PLANK] = "pick up the plank lying beside this ant"

    return {way: towards.get(way) for way in ways} | extra
```

Die Regel ist dieselbe wie bei allen anderen Optionen: Sie existiert nur, wenn
sie möglich ist. Eine Ameise mit vollen Händen sieht sie nie, eine weit weg
auch nicht.

**Warum ist das Aufnehmen eine Entscheidung und das Ablegen nicht?** In Kapitel
4 war beides eine Folge, und die Begründung war: Eine Frage, deren Antwort fast
immer dieselbe ist, ist eine bezahlte und weggeworfene Anfrage.

Bei der Planke liegt es andersherum. Eine Ameise, die gerade zu einer Frucht
unterwegs ist, soll nicht im Vorbeigehen eine Planke aufheben — hier ist die
Antwort offen, also wird gefragt. Umgekehrt hat eine Ameise, die mit der Planke
am Wasser ankommt, genau eine sinnvolle Möglichkeit, also wird nicht gefragt:

```python
    if ant["holding"] == "the plank":
        water = water_beside(ant)
        if water is not None:
            ant["holding"] = None
            st.session_state.bridge = water
        return
```

> Die Rust-Fassung sucht sich das Feld genauer aus: `nearest_crossing` nimmt
> nur Wasser mit mindestens zwei begehbaren Nachbarn, damit die Planke nicht
> ins Nichts gelegt wird. Hier ist der Fluss überall ein Feld breit, also
> erfüllt jedes Wasserfeld diese Bedingung, und die Prüfung kann entfallen.

## Drei Ausnahmen, und alle aus demselben Grund

Beim Bauen bin ich dreimal in dieselbe Grube gefallen. Sie ist es wert,
aufgeschrieben zu werden, denn es ist dieselbe wie in Kapitel 5.

**Erstens: Die Planke muss weiter zu sehen sein als alles andere.**

```python
PLANK_VISIBLE_FROM = 8
```

Mit den üblichen drei Feldern Sicht ging das Level nicht. Über dreißig Runden
hinweg lief keine einzige Ameise zur Planke — sie konnte gar nicht wissen, dass
es sie gibt. Die Rust-Fassung hat dieselbe Konstante mit demselben Wert. Eine
Planke ist ein großes Ding, das offen herumliegt.

**Zweitens: Wer die Planke trägt, darf nicht erfahren, wo der Bau ist.**

Im ersten Versuch bekam jede Ameise mit vollen Händen den Bau genannt. Die
Trägerin trug die Planke also brav nach Hause und lief damit dreißig Runden im
Kreis. Jetzt erfährt jede Last nur ihr eigenes Ziel:

```python
    if ant["holding"] == "a fruit":
        ...  # der Bau
    elif ant["holding"] == "the plank":
        ...  # das nächste Wasser
```

**Drittens: Der Übergang muss von überall sichtbar sein.**

Sonst wird die Planke gelegt — und danach findet niemand die Stelle wieder.
Gemessen: achtzig Runden, eine Frucht. Der Übergang ist jetzt ein Wahrzeichen
wie der Bau.

Dreimal dieselbe Lehre, und sie ist die wichtigste dieses Tutorials:

> Was im Zustand steht, ist das Verhalten. Was nicht darin steht, existiert für
> die Ameise nicht — egal, wie offensichtlich es auf dem Bildschirm aussieht.

## Was dabei herauskommt

Der Satz, mit dem ich gespielt habe:

> The fruit is all in the far north-west, behind a river you cannot wade. A
> plank lies in the south-east: whoever sees it, fetch it, carry it west to the
> river and lay it down there. Everyone else go north-west, cross where the
> plank lies, and carry fruit back to the nest.

![Das Brett nach 25 Runden: die Planke liegt als brauner Übergang im Fluss,
mehrere Ameisen sind hinüber, eine trägt schon eine Frucht](bilder/planke-bruecke.png)

Der Ablauf, gemessen: Die Planke wird um Runde 6 bis 10 aufgenommen, nach
Nordwesten getragen — eine Antwort davon mit **0,96** Konfidenz — und zwischen
Runde 20 und 30 abgelegt. Danach strömt die Kolonie über das eine Feld.

**Das Rätsel ist damit gelöst**, und zwar von einem Satz. Keine Ameise hätte
das herausfinden können.

## Wo dieser Anhang an seine Grenze kommt

Und dann wird es zäh. Vier volle Durchläufe, in der Reihenfolge, in der ich sie
gefahren habe:

| | Brücke ab | Vorrat | Kosten |
|---|---|---|---|
| Übergang nur aus drei Feldern sichtbar | Runde 30 | 1 von 5 nach 80 Runden | 0,016 $ |
| Übergang als Wahrzeichen | Runde 25 | 1 von 5 nach 70 Runden | 0,015 $ |
| dazu die Duftspur, Halbwertszeit 12 | Runde 25 | **0** von 5 nach 60 Runden | 0,013 $ |
| Halbwertszeit 30 | Runde 30 | **0** von 5 nach 60 Runden | 0,012 $ |

Eine Frucht, dann keine. Das Rätsel ist gelöst, der Abtransport nicht — und mit
der Duftspur wird er sogar schlechter.

Das ist erklärbar und ehrlicherweise zu erwarten gewesen. Auf dem ersten Brett
ist die Spur so gut wie perfekte Information (Kapitel 5). Hier ist der Heimweg
dreimal so lang und führt durch **ein** Feld — und eine Spur, die niemand
auffrischt, weil gerade niemand denselben Weg geht, ist verblasst, bevor die
Trägerin zurück ist.

Meine erste Vermutung war deshalb die Halbwertszeit. Sie steht jetzt im Level
statt im Code:

```json
  "scent_half_life": 30
```

Gebracht hat es **nichts** — Zeile vier der Tabelle. Die Einstellmöglichkeit ist
trotzdem geblieben, weil die Überlegung dahinter stimmt: Wie lange eine Spur
halten muss, hängt daran, wie weit die Kolonie läuft. Nur war sie hier nicht
das Problem.

Der Grund ist keine Schwäche des Modells, sondern der Bauart dieses Ports:
**Jeder einzelne Schritt ist eine eigene Frage.** Eine Ameise, die Obst holen
und über ein bestimmtes Feld zurückkommen soll, braucht dafür zwanzig
Entscheidungen hintereinander, jede ohne Gedächtnis an die vorige. Dazu kommt,
dass acht Ameisen sich durch ein einziges Feld zwängen.

Genau dafür hat die Rust-Fassung **Absichten statt Einzelschritten**: Dort wird
einmal gefragt „hol die Frucht im Nordwesten", und die Ameise arbeitet mehrere
Sekunden daran. Das ist der Punkt aus Kapitel 8, an dem sich die Fortsetzung
lohnt — und dieser Anhang ist der Beweis, dass er nicht theoretisch ist.

## Ausprobieren

* Sagen Sie zuerst gar nichts und drücken Sie zwanzig Runden. Die Kolonie
  findet den Fluss, und dort endet sie.
* Sagen Sie nur „Fetch the plank in the south-east". Wird sie geholt? Und wohin
  wird sie getragen?
* Setzen Sie `PLANK_VISIBLE_FROM` auf 3 zurück und spielen Sie noch einmal.
* Verschieben Sie in `level-planke.json` die Planke näher an den Fluss. Wie viel
  leichter wird das Level?
* Legen Sie ein zweites Wasserfeld dazu, sodass der Fluss an einer Stelle zwei
  Felder breit ist. Was passiert, wenn die Planke dort gelegt wird? (Und jetzt
  wissen Sie, wofür die Rust-Fassung `nearest_crossing` hat.)

* Sehen Sie dem Brett zu, nachdem die Brücke liegt: Wo wird es grün? Die Spur
  zeigt, welchen Weg die Kolonie tatsächlich nimmt — und wie schnell er wieder
  verblasst, wenn niemand ihn benutzt.

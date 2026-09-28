# Schritt 8 — Was bringt das Modell?

**Ziel:** Ein Schalter, der Jev durch einen Würfel ersetzt. Dieselbe Kolonie,
dasselbe Brett, dieselben Möglichkeiten — nur entscheidet niemand mehr, sondern
der Zufall.

Das ganze Tutorial über hat ein Modell entschieden, und es sah gut aus. „Sah gut
aus" ist keine Messung. Dieses Kapitel baut das Vergleichsmaß.

## Ein Würfel, der dieselben Optionen bekommt

```python
def decide_with_dice(level: dict, taken: set[tuple[int, int]]) -> list[str | None]:
    ways = []
    for ant in st.session_state.ants:
        open_ways = free_directions(level, ant, taken)
        ant["said"] = None
        ways.append(random.choice(open_ways) if open_ways else None)
    return ways
```

Entscheidend ist `free_directions` — **dieselbe** Funktion, die dem Modell die
Auswahl baut. Der Würfel zieht aus genau dem, was Jev vorgelegt bekommen hätte.
Damit ist der Unterschied zwischen beiden das Auswählen und nicht das, was zur
Auswahl stand. Ein Vergleich, bei dem der Zufall schlechtere Optionen bekäme,
wäre keiner.

## Wer entscheidet, ist eine Zeile

```python
def next_round(level: dict) -> None:
    taken = taken_cells()
    decide = decide_with_dice if st.session_state.dice else decide_with_jev

    for ant, way in zip(st.session_state.ants, decide(level, taken)):
        ...
```

Die Runde weiß nicht mehr, wer entscheidet. Sie bekommt eine Liste von
Richtungen und führt sie aus — mit derselben Prüfung beim Ausführen wie seit
Kapitel 3, denn auch ein Würfel kann zwei Ameisen auf dasselbe Feld schicken.

In der Rust-Fassung dieses Spiels heißt das `DecisionSource` und ist ein Trait
mit zwei Implementierungen. In Python ist es ein Name, der auf eine Funktion
zeigt. Dasselbe Muster, weniger Zeremonie.

## Der Schalter

```python
    st.session_state.dice = st.toggle(
        "A dice instead of Jev",
        value=st.session_state.dice,
        help=(
            "Draws blindly from the same options the model would have been "
            "given. Nothing is asked and nothing is paid. It is a yardstick, "
            "not a fallback."
        ),
    )
```

Und die Sperren lockern sich, wenn er an ist:

```python
ready = (st.session_state.dice or (bool(api_key()) and st.session_state.awake)) and not won
```

Mit dem Würfel braucht es weder Schlüssel noch Befehl — es wird ja nichts
gefragt. Genau das macht ihn als Maßstab benutzbar: Man kann ihn hundert Runden
laufen lassen, ohne einen Cent auszugeben.

## Warum das kein Rückfall ist

Die Versuchung ist groß, denselben Würfel einspringen zu lassen, wenn eine
Anfrage scheitert. Tun Sie es nicht.

Eine Kolonie, die beim kleinsten Aussetzer auf den Zufall umschaltet, sieht
immer gut aus — und man kann nicht mehr erkennen, welcher Teil des Verhaltens
vom Modell kommt. Dann misst man nichts mehr, man sieht nur noch etwas laufen.

Deshalb gilt weiter, was in Kapitel 5 eingebaut wurde: Eine abgelehnte Antwort
heißt, dass diese Ameise nichts tut. Der Würfel läuft nur, wenn Sie ihn
einschalten, und dann wird das Modell überhaupt nicht gefragt.

## Zweihundert Läufe ohne Streamlit

Im Spiel selbst kann man den Unterschied sehen. Messen kann man ihn dort
schlecht: Jede Runde ist ein Klick, und ein Lauf dauert Hunderte davon.

`tutorial/baseline.py` spielt dieselben Regeln ohne Streamlit und ohne Zeichnen
— zweihundert Läufe in einer Sekunde:

```sh
python3 tutorial/baseline.py
```

```
200 von 200 Läufen haben fünf Früchte heimgebracht
Median   237 Runden
Mittel   256 Runden
Spanne   97 bis 523
Mitte 80% 154 bis 383
```

## Das Ergebnis

| | Runden bis fünf Früchte |
|---|---|
| Würfel (Median aus 200 Läufen) | **237** |
| Jev, ohne Befehl | ~20 |
| Jev, mit einem brauchbaren Befehl | ~15–20 |

Etwa **zwölfmal** schneller. Und es kostet in derselben Zeit rund 160 Anfragen,
also etwa einen Fünftel-Cent.

Der Grund für den großen Abstand ist nicht, dass das Modell geschickter wählt,
wenn eine Frucht danebenliegt — das tut ein Würfel in einem Achtel der Fälle
auch. Der Abstand entsteht beim **Heimweg**. Eine tragende Ameise, der im
Zustand steht, wo der Bau liegt, geht dorthin. Ein Würfel findet 16 von 384
Feldern durch Herumlaufen.

Merken Sie sich den allgemeinen Teil davon: Der Nutzen lag nicht dort, wo die
Entscheidung schwierig aussah, sondern dort, wo eine **Information** im Zustand
stand, die der Zufall nicht verwerten kann.

## Drei Einschränkungen, die dazugehören

**Die Zahlen sind nicht gleichwertig gemessen.** 237 ist ein Median aus
zweihundert Läufen. Die ~20 für Jev sind Einzelläufe, weil jeder davon
Hunderte von Anfragen kostet. Bei der Streuung des Würfels (97 bis 523!) sollte
man auch beim Modell mehrere Läufe machen, bevor man eine Zahl ernst nimmt.

**Ein Würfel ist eine niedrige Latte.** Die faire Gegenprobe wäre nicht der
Zufall, sondern eine handgeschriebene Regel: „Siehst du Obst, geh hin; trägst
du etwas, geh heim." Die Rust-Fassung dieses Spiels hat das gemessen — und
dort liefert die **Regel** 7 bis 13 % mehr Früchte als das Modell. Das ist kein
Widerspruch, sondern die richtige Einordnung: Für eine Aufgabe, die sich in zwei
Zeilen Regel fassen lässt, ist ein Modell nicht die schnellere Lösung.

**Der Anspruch liegt woanders.** Was die Regel nicht kann, ist: auf „Lasst die
Früchte im Norden liegen" reagieren. Oder auf „Bleibt beieinander". Oder auf
einen Satz, den Sie sich gerade erst ausgedacht haben. Dafür gibt es das Textfeld
aus Kapitel 6, und dafür ist das Ganze gebaut.

## Ausprobieren

* Schalter an, „Five rounds" ein paar Dutzend Mal. Es kostet nichts, und es
  dauert. Genau das ist die Aussage.
* Schalter aus, „Start over", einen guten Satz sagen, und mitzählen.
* Öffnen Sie `tutorial/baseline.py` und bauen Sie die Regel ein, die oben fehlt: Frucht in
  Sicht → hin; tragend → heim. Wie viele Runden braucht sie?
* Setzen Sie `RUNS` auf 20 und lassen Sie es zweimal laufen. Die Mediane werden
  auseinanderliegen — bei dieser Streuung sagen zwanzig Läufe wenig. Das ist
  die wichtigste Lektion über Messungen in diesem Tutorial.

---

# Geschafft

Acht Schritte, ein Spiel. Was jetzt dasteht:

* ein Brett aus SVG, das ein Level aus einer JSON-Datei zeichnet
* **Auswahlmöglichkeiten, die in jeder Runde aus der Lage jeder einzelnen
  Ameise neu entstehen** — das Modell bekommt nie etwas Unmögliches zu sehen
* acht parallele Anfragen pro Runde in gut einer halben Sekunde
* eine Kolonie, die Früchte findet, trägt und heimbringt
* eine Schwelle, unter der Antworten verworfen und gezählt statt versteckt
  werden, und keinen Regelfallback darunter
* ein Textfeld, in das Sie einen Satz tippen, den acht Ameisen für sich lesen
* die Anzeige, an der man sieht, ob er etwas genützt hat
* und ein Maßstab, an dem sich das alles messen lässt

## Wohin es weitergehen könnte

* **Ins Netz stellen.** Streamlit Community Cloud nimmt das Repository direkt
  und installiert aus `uv.lock`. Der Schlüssel kommt dann aus der Seitenleiste
  — jeder bringt seinen eigenen mit. Weil Streamlit die Anfrage auf dem Server
  stellt, gibt es kein CORS-Problem; die Rust-Fassung dieses Spiels brauchte
  dafür einen eigenen Proxy.
* **Ein zweites Level** liegt schon dabei: `level2.json`. Mehr als eine zweite
  Datei war nicht nötig; gespielt wird es, indem Sie in `app.py` eine Zeile
  ändern:

  ```python
  LEVEL_FILE = "level2.json"
  ```

  ![Level 2 zu Beginn: der Bau mit acht Ameisen unten rechts, alle acht Früchte
  weit oben links, dazwischen ein leeres Brett](bilder/level-2.png)

  Der Bau steht im Südosten, das ganze Obst im Nordwesten — 13 bis 17 Felder
  entfernt, bei einer Sichtweite von drei. Ohne einen Satz der Königin sucht
  die Kolonie ein leeres Brett ab. Mit „Das Obst liegt weit im Nordwesten, geht
  dorthin" hat sie eine Richtung. Das ist dasselbe Level wie das erste, nur
  ohne die Möglichkeit, durch Herumlaufen Glück zu haben.

* **Ein Hindernis.** In der Rust-Fassung gibt es ein Level mit einem Fluss und
  einer Planke, die zwei Ameisen gemeinsam tragen müssen — Koordination ohne
  Absprache ist der interessanteste Teil des Ganzen.
* **Absichten statt Einzelschritten.** Statt jede Runde „welche Richtung?" zu
  fragen, einmal „hol die Frucht im Nordosten" fragen und die Ameise mehrere
  Runden daran arbeiten lassen. Das spart den Großteil der Anfragen.
* **Die Frage verfeinern.** Der lohnendste Punkt und der billigste: An
  `STEP_QUESTION` zu drehen kostet keine Zeile Code und ändert das Verhalten
  der ganzen Kolonie. Sie haben in Kapitel 5 gesehen, was ein einziger Satz
  ausmacht.

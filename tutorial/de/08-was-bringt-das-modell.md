# Schritt 8 — Was bringt das Decision-Model?

*[English version](../en/08-was-bringt-das-modell.md)*

![Queeny, von hinten gesehen, hält einen leuchtenden Würfel auf der Hand;
links von ihr stehen Arbeiterinnen mit Äpfeln ungeordnet auf dem Brett, über
ihnen schwebt ein zweiter Würfel; rechts gehen Arbeiterinnen mit weißen Helmen
in einer Reihe eine grün leuchtende Spur entlang, über den meisten ein grüner
Pfeil](../bilder/schritt-8-titel.png)

*Vergleich von Zufalls-Aktionen (Würfel) im Vergleich zum Decision-Modell — dieselben Ameisen, dieselben Wege.*

**Ziel:**

* Ein Schalter, der das Decision-Model durch einen Würfel ersetzt.
* Dieselbe Kolonie, dasselbe Spiel-Brett, dieselben Möglichkeiten — nur entscheidet
  niemand mehr, sondern der Zufall.

![Das Brett nach 40 Runden mit dem Würfel: die Ameisen über das ganze Brett
verstreut, vier von ihnen tragen eine Frucht, keine davon ist im Bau; um den
Bau herum ist der Boden schwach grün von der Spur](../bilder/schritt-8-wuerfel.png)

*Vierzig Runden Zufall: vier Früchte unterwegs, keine im Vorrat.*

Das ganze Tutorial über hat ein Modell entschieden, und es sah gut aus. 

„Sah gut aus" ist keine objektive Aussage, keine Messung. Dieses Kapitel baut den Maßstab, an dem sich das Modell messen lässt.

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

Entscheidend ist `free_directions`. Das ist **dieselbe** Funktion, aus der
`options()` die Auswahl für das Decision Modell baut. 

Der Würfel bekommt als Eingabe das, was das Modell vorgelegt bekommen hätte — nur ohne die Beschreibungen, denn lesen kann er sie nicht. 

Der Unterschied ist damit das Auswählen selbst und nicht das, was zur Auswahl steht. 

`ant["said"] = None` sorgt dafür, dass über keiner Ameise ein Etikett aus einer
früheren Runde stehen bleibt.

## Es entscheidet eine Zeile

```python
def next_round(level: dict) -> None:
    taken = taken_cells()
    decide = decide_with_dice if st.session_state.dice else decide_with_jev

    for ant, way in zip(st.session_state.ants, decide(level, taken)):
        ...
```

Jede Runde bekommt eine Liste von Richtungen und führt sie aus — mit derselben Prüfung beim Ausführen wie seit Kapitel 3, denn auch ein Würfel kann zwei Ameisen auf dasselbe Feld schicken.

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
    if st.session_state.dice:
        st.caption("Nobody is being asked. Watch how long five fruits take now.")
```

Ist der Schalter an, fallen zwei Sperren weg:

```python
ready = (st.session_state.dice or (bool(api_key()) and st.session_state.awake)) and not won
```

Mit dem Würfel braucht es weder Schlüssel noch Befehl — es wird ja niemand
gefragt. Genau das macht ihn als Maßstab brauchbar.

## Zweihundert Läufe ohne Streamlit

Im Spiel selbst kann man den Unterschied sehen. Messen lässt er sich dort
schlecht: Jede Runde ist ein Klick, und ein Lauf mit dem Würfel dauert Hunderte
davon.

`tutorial/baseline.py` spielt die Würfelregeln ohne Streamlit und ohne Zeichnen
— zweihundert Läufe in einer Sekunde:

```sh
python3 tutorial/baseline.py
```

```
200 of 200 runs brought five fruits home
median    240 rounds
mean      248 rounds
range     75 to 603
middle 80% 146 to 361
```

Ihre Zahlen werden etwas anders aussehen, der Würfel ist ja ein Würfel. Der
Median bleibt bei zweihundert Läufen aber in der Gegend um 240.

## Das Ergebnis

Für das Modell drei Läufe mit demselben Befehl, „Fan out and search, and carry
what you find straight home.":

| Lauf | Runden | Anfragen | verworfen | Kosten |
|---|---|---|---|---|
| 1 | 59 | 472 | 222 (47 %) | 0,0100 $ |
| 2 | 23 | 184 | 68 (37 %) | 0,0040 $ |
| 3 | 26 | 208 | 74 (36 %) | 0,0045 $ |

| | Runden bis fünf Früchte |
|---|---|
| Würfel (Median aus 200 Läufen) | **240** |
| Decision-Model (Jev), Median aus 3 Läufen | **26** |

Das Modell ist rund **neunmal** schneller. Ein ganzes Spiel kostet dabei
zwischen einem halben und einem ganzen Cent.

Der erste Lauf zeigt, wie viel Streuung auch beim Decision Modell zu sehen ist: Mehr als doppelt so lang wie die beiden anderen, und fast jede zweite Antwort wurde
verworfen. Schneller als der schnellste Würfellauf (75 Runden) war er trotzdem.

Woher kommt der große Abstand? 

Nicht vom Aufheben: Eine Frucht direkt neben einer Ameise wird in beiden Kolonien aufgenommen, ohne dass jemand entscheidet (`pick_up_and_deliver` aus Kapitel 4). 

Einen kleinen Teil macht aus, dass das Modell eine Frucht ansteuert, die es drei Felder entfernt sieht. Der Würfel läuft daran vorbei.

Der große Teil aber entsteht auf dem **Heimweg**. Eine tragende Ameise folgt der
Duftspur bergauf und kommt an. Ein Würfel müsste die 16 Felder des Baus unter
384 Feldern durch Herumlaufen treffen. Im Bild oben sieht man das: Vier
Ameisen tragen eine Frucht, keine findet heim.

Und jetzt kommt die Feinheit, die diesen Vergleich erst scharf macht: **Die
Würfel-Kolonie legt dieselbe Spur.** `lay_scent` hängt am Laufen, nicht am
Entscheiden, also duftet ihr Brett genauso — auch das zeigt das Bild. Sie kann
die Spur nur nicht lesen, denn dazu müsste jemand aus dem Angebotenen etwas
auswählen.

Die Spur ist also nicht das, was den Unterschied macht. Sie ist nur die
Information — und der Unterschied ist, dass eine Seite sie verwerten kann und
die andere nicht.

Merken Sie sich den allgemeinen Teil davon: Der Nutzen lag nicht dort, wo die
Entscheidung schwierig aussah, sondern dort, wo eine **Information** vorlag,
die der Zufall nicht verwerten kann.

## Einschränkungen

**Die Zahlen sind nicht gleichwertig gemessen.** 240 ist ein Durchschnittswert (Median) aus zweihundert Läufen, die 26 für das Decision-Model ein Median aus drei, weil jeder davon mehrere hundert Anfragen kostet.

Die Läufe streuen von 23 bis 59 Runden. Bevor Sie eine Zahl für das Modell ernst nehmen, sollten Sie mehr Läufe machen — und auch ausprobieren, wie viel ein anderer Befehl ausmacht.

**Der Anspruch liegt woanders.** Was die Regel nicht kann: auf „Leave the fruit
in the north alone" reagieren. Oder auf „Stay together". Oder auf einen Satz,
den Sie sich gerade erst ausgedacht haben. Dafür gibt es das Textfeld aus
Kapitel 6, und dafür ist das Ganze gebaut.

## Ausprobieren

* Schalter an, „Five rounds" ein paar Dutzend Mal. Es kostet nichts, und es
  dauert. Genau das ist die Aussage.
* Schalter aus, „Start over", einen guten Satz sagen und die Runden mitzählen.
* Öffnen Sie `tutorial/baseline.py` und bauen Sie die Regel ein, die oben
  fehlt: Frucht in Sicht → hin; tragend → heim. Wie viele Runden braucht sie?
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
  werden, und keinen Rückfall auf Regeln darunter
* ein Textfeld, in das Sie einen Satz tippen, den jede der acht Ameisen für
  sich liest
* die Anzeige, an der man sieht, ob er etwas genützt hat
* und einen Maßstab, an dem sich das alles messen lässt

## Wohin es weitergehen könnte

* **Ein zweites Level** liegt schon dabei: `level2.json`. Mehr als eine zweite
  Datei war nicht nötig; gespielt wird es, indem Sie in `app.py` eine Zeile
  ändern:

  ```python
  LEVEL_FILE = "level2.json"
  ```

  ![Level 2 zu Beginn: der Bau mit acht Ameisen unten rechts, alle acht Früchte
  weit oben links, dazwischen ein leeres Brett](../bilder/level-2.png)

  Der Bau steht im Südosten, das ganze Obst im Nordwesten — 13 bis 17 Felder
  entfernt, bei einer Sichtweite von drei. Mit einem vagen Befehl sucht die
  Kolonie ein leeres Brett ab. Mit „The fruit lies far to the north-west, go
  there" hat sie eine Richtung. Die Regeln sind dieselben wie im ersten Level,
  nur ohne die Möglichkeit, durch Herumlaufen Glück zu haben.

* **Ein Hindernis.** In der Rust-Fassung gibt es ein Level mit einem Fluss und
  einer Planke, die zwei Ameisen gemeinsam tragen müssen — Koordination ohne
  Absprache ist der interessanteste Teil des Ganzen. Anhang A zeigt, wie weit
  sich das hier nachbauen lässt.
* **Absichten statt Einzelschritten.** Statt jede Runde „welche Richtung?" zu
  fragen, einmal „hol die Frucht im Nordosten" fragen und die Ameise mehrere
  Runden daran arbeiten lassen. Das spart den Großteil der Anfragen.
* **Die Frage verfeinern.** Der lohnendste Punkt und der billigste: An
  `STEP_QUESTION` zu drehen kostet keine Zeile Code und ändert das Verhalten
  der ganzen Kolonie. Eine der Übungen in Kapitel 5 zeigt es: Nehmen Sie den
  Satz über das Ausschwärmen heraus, und die Kolonie verhält sich anders.

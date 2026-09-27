# Wenn Ameisen Jev fragen

## Spielerisch den Umgang mit dem Modell Jev von TypSave mit Python austesten

Das neuartigen Modell Jev von TypSave trifft schnelle Bewertungen und Entscheidungen, die Programme in ihren Ablauf einbauen können.

Das Beipspiel in diesem Tutorial ist eine Ameisen-Kolonie, die im Browser zu sehen ist. Jev steuert jede einzelne Ameisen nach den Anweisungen der Königin, die Sie sind. Die Ameisen sollen Früchte in den Bau bringen oder Hindernisse überwinden.

![Das fertige Spiel: acht Ameisen auf dem Brett, über jeder steht, wofür Jev sich
entschieden hat und wie sicher — grün bei hoher, rot bei knapper
Zuversicht](bilder/das-spiel.png)

*So sieht es am Ende von Schritt 7 aus. Über jeder Ameise steht, wofür Jev sich
entschieden hat und wie sicher es sich war.*

Kein Klicken, keine Tasten, keine Joy-Stick. Sie tippen ein „Holt die Früchte aus
dem Norden", und jede Ameise entscheidet für sich, was das für sie bedeutet.
Die Entscheidung trifft das Modell **TypeSafe Jev**.

Jev ist kein Chat-Modell. Es beantwortet keine Fragen in Prosa, sondern trifft
**typisierte Entscheidungen mit kalibrierter Zuversicht** — genau das, was ein
Programm in seinen Ablauf einbauen kann. Drei Adressen, die Sie brauchen
werden:

| | |
|---|---|
| Die Website | [typesafe.ai](https://typesafe.ai) |
| Die Dokumentation | [docs.typesafe.ai](https://docs.typesafe.ai/introduction) |
| Der Schlüssel | [console.typesafe.ai/keys](https://console.typesafe.ai/keys) |

/* ScreenShot von Web-Seite TypeSafe einfügen — Chrome liefert hier gerade
   keine Screenshots; Bild bitte selbst ablegen unter
   tutorial/bilder/typesafe-website.png, dann binde ich es ein */

Jede Ameise stellt ihm einmal pro Runde eine Frage an Jev und die Antwort ist eine von genau eine der Möglichkeiten, die diese eine Ameise in
diesem Moment wirklich zur Auswahl hat.

Das Programm baut die Auswahlmöglichkeiten **zur Laufzeit** aus dem, was die Ameise
sieht. Ist keine Frucht in Sichtweite, gibt es die Antwort-Möglichkeit „hol die Frucht" nicht. 

## Was Sie brauchen

* **Python 3.12 oder neuer.**
* **[uv](https://docs.astral.sh/uv/)** als Paketverwaltung. Es geht auch mit
  `pip`; an den Stellen, an denen es einen Unterschied macht, steht beides da.
* **Einen TypeSafe-Schlüssel** von
  [console.typesafe.ai/keys](https://console.typesafe.ai/keys). Gebraucht wird
  er **ab Schritt 2**: Das Modell ist das Thema, also kommt es früh und bleibt.
  Nur Schritt 1 läuft ohne.
* Einen Texteditor und einen Browser.

Kosten: Eine Anfrage sind rund 350 bis 600 Eingabe-Tokens, und eine Million
davon kostet 0,042 Dollar. Ein komplettes Spiel — acht Ameisen, zwanzig Runden
— liegt bei etwa **einem Fünftel-Cent**. Zum Durcharbeiten des ganzen Tutorials reicht wahrscheinlich ein einstelliger Centbetrag.

## Die acht Schritte des Tutorial

Nach **jedem** Schritt haben Sie ein Programm, das läuft. Sie sehen immer etwas Neues auf dem Bildschirm.

| Schritt | Was danach läuft |
|---|---|
| 1 | Das Brett — ein Gitter im Browser |
| 2 | **Eine Ameise, die Jev fragt** — ein Klick, eine Anfrage, ein Schritt |
| 3 | Die Kolonie — acht Ameisen mit acht parallele Anfragen |
| 4 | Tragen und abliefern — Früchte heimbringen, gewinnen |
| 5 | Augen — Sichtfeld, bessere Optionen, eine Schwelle |
| 6 | Die Königin — dein Satz |
| 7 | Zusehen — was jede Ameise gewählt hat, und was es kostet |
| 8 | Was bringt das Modell? — der Vergleich mit einem Würfel |

 **Ab Schritt 2 entscheidet das Modell**, und alles danach handelt davon, was es
dabei zu sehen bekommt. 
 
Erst ist die Ameise blind und allein; dann sind es acht; dann haben sie eine Aufgabe; dann können sie sehen; dann eine Königin, die ihnen etwas sagt. 


## Wie Sie den Code bekommen

Jeder Schritt ist im Repository ein eigener Stand:

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
git checkout step-3        # der Stand nach Schritt 3
uv run streamlit run app.py
```

Dieselben acht Stände liegen auch als einzelne Dateien unter `steps/`, falls das 
für Sie einfacher ist:

```sh
uv run streamlit run steps/03_colony.py
```

Starten Sie sie vom Wurzelverzeichnis aus — `level1.json` und `.env` werden
dort gesucht, wo Sie das Programm aufrufen.

Sie können aber genauso gut mit einer leeren Datei anfangen und die Programme
selbst mittippen. Dafür ist das Tutorial geschrieben.

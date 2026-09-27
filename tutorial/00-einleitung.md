# Ameisen, die fragen

## Ein Spiel in acht Schritten mit Python, Streamlit und TypeSafe Jev

Am Ende dieses Tutorials hast du ein Spiel, das im Browser läuft und so
funktioniert: Auf einem Brett sitzen acht Ameisen. Irgendwo liegen Früchte. Du
bist die Königin — und das Einzige, was du tun kannst, ist **einen Satz sagen**.

Kein Klicken, keine Tasten, keine Wegpunkte. Du tippst „Holt die Früchte aus
dem Norden", und jede Ameise entscheidet für sich, was das für sie bedeutet.
Entschieden wird nicht von Regeln, die du programmiert hast, sondern von einem
Modell: **TypeSafe Jev**. Jede Ameise stellt ihm einmal pro Runde eine Frage,
und die Antwort ist eine von genau den Möglichkeiten, die diese eine Ameise in
diesem Moment wirklich hat.

Der letzte Satz ist der Kern des Ganzen, deshalb gleich hier ausführlich: Das
Programm baut die Auswahlmöglichkeiten **zur Laufzeit** aus dem, was die Ameise
sieht. Steht keine Frucht in Sichtweite, gibt es die Antwort „hol die Frucht"
gar nicht erst. Das Modell kann also nichts wählen, was es nicht gibt. Diese
Eigenschaft ist der Grund, warum das Spiel existiert — und sie ist in Python in
etwa fünfzehn Zeilen zu haben.

## Woher das kommt

Es gibt dieses Spiel schon einmal, größer: als Rust-Programm mit der
Spiele-Engine Bevy, mit Pheromonspuren, mehreren Levels und einer Planke, die
zwei Ameisen gemeinsam tragen müssen. Diese Python-Fassung nimmt davon Level 1
und lässt alles weg, was nicht gebraucht wird.

Das ist keine Einschränkung, sondern der Zweck: Was hier steht, ist das
Minimum, mit dem man die Idee bauen und begreifen kann.

## Was du brauchst

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
— liegt bei etwa **einem Fünftel-Cent**. Das Spiel rechnet ab Schritt 7 selbst
mit. Zum Durcharbeiten des ganzen Tutorials reicht ein einstelliger Centbetrag.

## Die acht Schritte

Nach **jedem** Schritt hast du ein Programm, das läuft. Das ist keine
Höflichkeit gegenüber dem Leser, sondern die einzige Art, so etwas zu bauen:
Wenn nach jedem Schritt etwas auf dem Bildschirm steht, weißt du immer, welche
Änderung schuld ist, wenn etwas nicht geht.

| Schritt | Was danach läuft |
|---|---|
| 1 | Das Brett — ein Gitter im Browser |
| 2 | **Eine Ameise, die fragt** — ein Klick, eine Anfrage, ein Schritt |
| 3 | Die Kolonie — acht Ameisen, acht parallele Anfragen |
| 4 | Tragen und abliefern — Früchte heimbringen, gewinnen |
| 5 | Augen — Sichtfeld, bessere Optionen, eine Schwelle |
| 6 | Die Königin — dein Satz |
| 7 | Zusehen — was jede Ameise gewählt hat, und was es kostet |
| 8 | Was bringt das Modell? — der Vergleich mit einem Würfel |

Die Reihenfolge hat einen Grund. **Ab Schritt 2 entscheidet das Modell**, und
alles danach handelt davon, was es dabei zu sehen bekommt. Erst ist die Ameise
blind und allein; dann sind es acht; dann haben sie eine Aufgabe; dann Augen;
dann eine Königin, die ihnen etwas sagt. Man kann bei jedem Schritt zusehen, wie
die Konfidenz steigt, weil das Modell mehr hat, woran es sich halten kann.

Der Zufall kommt erst am Schluss, in Schritt 8 — nicht als Bauteil, sondern als
**Maßstab**: Was hätte ein Würfel geschafft?

Ein Grundsatz gilt dabei von Anfang an: **kein Rückfall auf Regeln.** Scheitert
eine Anfrage oder ist die Antwort zu unsicher, tut die betroffene Ameise in
dieser Runde nichts. Eine Kolonie, die ohne das Modell weiterarbeitet, würde
genau das verstecken, was man sehen will.

## Wie du den Code bekommst

Jeder Schritt ist im Repository ein eigener Stand:

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
git checkout step-3        # der Stand nach Schritt 3
uv run streamlit run app.py
```

Dieselben acht Stände liegen auch als einzelne Dateien unter `steps/`, falls du
mit Git nichts zu tun haben willst:

```sh
uv run streamlit run steps/03_colony.py
```

Starte sie vom Wurzelverzeichnis aus — `level1.json` und `.env` werden dort
gesucht, wo du das Programm aufrufst.

Du kannst aber genauso gut mit einer leeren Datei anfangen und mittippen. Dafür
ist das Tutorial geschrieben.

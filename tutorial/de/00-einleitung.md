# Wenn Ameisen ein Decision-Model fragen

*[English version](../en/00-einleitung.md)*

![Queeny, die Königin mit Krone, steht im Kontrollraum der Kolonie, links und
rechts von ihr vier Arbeiterinnen mit Schutzhelmen und
Werkzeug](../bilder/queeny-und-arbeiterinnen.png)

*Queeny und ihre Arbeiterinnen.*

## Spielerisch den Umgang mit einem Decision-Model mit Python austesten

Ein Decision-Model ist eine neue Art von KI-Modell: Es trifft schnelle Bewertungen und Entscheidungen, die Programme in ihren Ablauf einbauen können.

Das Beispiel in diesem Tutorial ist eine Ameisen-Kolonie, die im Browser zu sehen ist. Das Decision-Model steuert jede einzelne Ameise nach den Anweisungen der Königin, die Sie sind. Die Ameisen sollen Früchte in den Bau bringen oder Hindernisse überwinden.

![Das fertige Spiel: acht Ameisen auf dem Brett, über jeder steht, wofür das Modell sich
entschieden hat und wie sicher — grün bei hoher, rot bei knapper
Zuversicht](../bilder/das-spiel.png)

*So sieht es am Ende von Schritt 7 aus. Über jeder Ameise steht, wofür das Modell sich
entschieden hat und wie sicher es sich war — und die grünen Felder sind die
Duftspur, die die Kolonie beim Suchen hinterlässt. Sie ist am Bau am stärksten,
und bergauf ist heimwärts.*

Kein Klicken, keine Tasten, kein Joystick. Sie tippen ein „Holt die Früchte aus
dem Norden", und jede Ameise entscheidet für sich, was das für sie bedeutet.
Die Entscheidung trifft ein **Decision-Model**, in diesem Tutorial **TypeSafe Jev**.

Ein Decision-Model ist kein Chat-Modell. Es beantwortet keine Fragen in Prosa, sondern trifft
**typisierte Entscheidungen mit kalibrierter Zuversicht** — genau das, was ein
Programm in seinen Ablauf einbauen kann. Für TypeSafe Jev brauchen Sie drei
Adressen:

| | |
|---|---|
| Die Website | [typesafe.ai](https://typesafe.ai) |
| Die Dokumentation | [docs.typesafe.ai](https://docs.typesafe.ai/introduction) |
| Der Schlüssel | [console.typesafe.ai/keys](https://console.typesafe.ai/keys) |

![Die TypeSafe-Konsole nach der Anmeldung: links die Navigation mit Playground,
Usage, API Keys, Billing und Documentation, rechts Beispiele für die
Fragetypen Noul und Choice](../bilder/typesafe-website.png)

*Die Konsole unter [console.typesafe.ai](https://console.typesafe.ai). Den
Schlüssel, den Sie ab Schritt 2 brauchen, holen Sie sich links unter **API
Keys**; unter **Usage** sehen Sie später, was das Tutorial gekostet hat. Oben
rechts im Bild stehen schon die beiden Fragetypen, um die es gehen wird:*
`noul` *für ein Ja/Nein mit Wahrscheinlichkeit und* `choice` *für eine Auswahl
— die zweite ist die, die jede Ameise stellt.*

Jede Ameise stellt dem Decision-Model einmal pro Runde eine Frage, und die Antwort ist genau eine der Möglichkeiten, die diese eine Ameise in
diesem Moment wirklich zur Auswahl hat.

Das Programm baut die Auswahlmöglichkeiten **zur Laufzeit** aus dem, was die Ameise
sieht. Ist keine Frucht in Sichtweite, gibt es die Antwort-Möglichkeit „hol die Frucht" nicht. 


**Lokale Alternative Ollama mit Decision-Models.** Seit Version 0.35 bietet Ollama den
Endpunkt `/v1/systemone` an, mit denselben Fragen, Auswahlen,
Wahrscheinlichkeiten und derselben Konfidenz wie Jev. Das Modell läuft dann
auf Ihrem eigenen Rechner, ohne Schlüssel und ohne Kosten pro Anfrage. Die
Bibliothek aus diesem Tutorial spricht unverändert mit Ollama, es reichen drei
Einträge in der `.env`. Wie das geht und wie schnell es ist, steht in
Anhang B.

Der Markt bewegt sich schnell. Für das Tutorial gilt: Was ein Decision-Model ist und wie man es
fragt, bleibt gleich, egal von wem es kommt.

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
davon kostet 0,042 Dollar. Ein komplettes Spiel — acht Ameisen, zwanzig bis
sechzig Runden — liegt bei **einem halben bis einem ganzen Cent**. Zum
Durcharbeiten des ganzen Tutorials reichen wahrscheinlich ein paar Cent.

## Die acht Schritte des Tutorials

Nach **jedem** Schritt haben Sie ein Programm, das läuft. Sie sehen immer etwas Neues auf dem Bildschirm.

| Schritt | Was danach läuft |
|---|---|
| 1 | Das Brett — ein Gitter im Browser |
| 2 | **Eine Ameise, die das Modell fragt** — ein Klick, eine Anfrage, ein Schritt |
| 3 | Die Kolonie — acht Ameisen mit acht parallelen Anfragen |
| 4 | Tragen und abliefern — Früchte heimbringen, gewinnen |
| 5 | Augen — Sichtfeld, bessere Optionen, eine Schwelle |
| 6 | Die Königin — Ihr Satz |
| 7 | Einblicke — was jede Ameise gewählt hat, und was es kostet |
| 8 | Was bringt das Decision-Model? — der Vergleich mit einem Würfel |

 **Ab Schritt 2 entscheidet das Modell**, und alles danach handelt davon, was es
dabei zu sehen bekommt. 
 
Erst ist die Ameise blind und allein; dann sind es acht; dann haben sie eine Aufgabe; dann können sie sehen; dann eine Königin, die ihnen etwas sagt. 


## Wie Sie den Code bekommen

Jeder Schritt ist im Repository ein eigener Stand:

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
git checkout step-1        # der Stand nach Schritt 1
uv run streamlit run app.py
```

Dieselben acht Stände liegen auch als einzelne Dateien unter `steps/`, falls das 
für Sie einfacher ist:

```sh
uv run streamlit run steps/01_board.py
```

Starten Sie sie vom Wurzelverzeichnis aus — `level1.json` und `.env` werden
dort gesucht, wo Sie das Programm aufrufen.

Sie können aber genauso gut mit einer leeren Datei anfangen und die Programme
selbst mittippen. Dafür ist das Tutorial geschrieben.

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

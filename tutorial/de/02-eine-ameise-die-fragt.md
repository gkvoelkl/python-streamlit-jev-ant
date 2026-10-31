# Schritt 2 — Eine Ameise fragt das Decision-Model

*[English version](../en/02-eine-ameise-die-fragt.md)*

![Eine Arbeiterin mit weißem Schutzhelm und Funkgerät steht allein auf dem
leuchtenden Brett, über ihr eine Sprechblase mit einem Fragezeichen; von den
Pfeilen um sie herum leuchtet einer golden und trägt die Aufschrift
„Jev"](../bilder/schritt-2-titel.png)

*Sie fragt, und das Modell zeigt ihr den Weg.*

**Ziel:** Eine Ameise steht auf dem Brett. Sie drücken einen Knopf, und die Ameise geht dorthin, wo das **Decision-Model** es sagt — in diesem Tutorial **TypeSafe Jev**.

![Das Brett von Schritt 2 mit der einen Ameise, die auf dem Feld steht, auf das
das Modell sie geschickt hat](../bilder/schritt-2-ameise.png)

*Eine Ameise, und jeder Schritt, den sie getan hat, kam vom Decision-Model.*

## Der API-KEY

Für Anfragen bei TypeSafe Jev brauchen Sie einen persönlichen **API-KEY**. Diesen bekommen Sie von der Web-Seite [console.typesafe.ai/keys](https://console.typesafe.ai/keys). 

Entweder schreiben Sie diesen Schlüssel **in die Datei `.env`**.

```
TYPESAFE_API_KEY=ihr-schlüssel
```

**Oder in die Seitenleiste** der laufenden Anwendung. Das ist der Weg für alle,
die das Spiel später direkt im Netz benutzen: Jeder bringt seinen eigenen  Schlüssel mit.

![Die Seitenleiste mit der Überschrift „TypeSafe key", einem leeren Passwortfeld
mit dem Hinweis „paste your key" und dem Auge zum Sichtbarmachen, darunter der
Hinweis, dass der Schlüssel nirgends gespeichert
wird](../bilder/schluessel-seitenleiste.png)

*Das Feld erscheint nur, wenn in `.env` kein Schlüssel steht — sonst zeigt die
Seitenleiste bloß „Found in .env". Das Auge rechts macht das Eingefügte
sichtbar, was nach einem missglückten Einfügen die einzige Möglichkeit ist,
den Fehler zu sehen, ohne eine Anfrage dafür auszugeben.*

```python
import os
from dotenv import load_dotenv

load_dotenv()


def api_key() -> str:
    return st.session_state.get("typed_key", "").strip() or os.getenv(
        "TYPESAFE_API_KEY", ""
    ).strip()
```

Das Getippte hat Vorrang vor der Datei `.env` — sonst könnten Sie einen
veralteten Schlüssel dort nicht übergehen.

> **Es geht auch ohne Schlüssel.** Seit Ollama 0.35 beantwortet ein lokal
> laufendes Modell dieselben Anfragen: keine Kosten, kein Netz, und keine Zeile
> Code anders — nur drei Zeilen in `.env`. Wie das geht, steht in **Anhang B**.
> Wenn Sie das Tutorial lieber so durcharbeiten wollen, richten Sie es dort ein
> und kommen hierher zurück; alles Weitere bleibt gleich.

## Die Ameise

```python
def start() -> None:
    if "ant" in st.session_state:
        return

    st.session_state.ant = {"x": COLUMNS // 2, "y": ROWS // 2}
    st.session_state.said = None
    st.session_state.failure = None
```

**Streamlit führt bei jeder Interaktion das komplette Skript neu aus.** Jeder
Klick: Die Datei läuft wieder von oben nach unten durch, und alles, was in
gewöhnlichen Variablen steht, ist weg.

Was einen Klick überleben soll, muss in `st.session_state` — und darf nur
geschrieben werden, **wenn es noch nicht da ist**. 

Genau das macht

`if "ant" in st.session_state: return`

Es verwandelt einen Neudurchlauf in ein Neuzeichnen statt in einen Neustart. 

## Die acht Richtungen

```python
DIRECTIONS = {
    "north": (0, -1),
    "north-east": (1, -1),
    "east": (1, 0),
    "south-east": (1, 1),
    "south": (0, 1),
    "south-west": (-1, 1),
    "west": (-1, 0),
    "north-west": (-1, -1),
}
```

y zählt nach unten (Kapitel 1), also ist Norden `(0, -1)`.

![Die acht Richtungen um eine Ameise herum, jede mit ihrem Namen und ihrem
Versatz; Norden ist (0, −1), weil y nach unten
zählt](../bilder/richtungen.png)

Dass die Richtungen **Namen** haben und nicht durchnummeriert sind, ist eine
Frage der Lesbarkeit und der Kommunikaktion. Die Ameisen-Königin, der Spieler kann sagen: "Alle Ameisen bewegen sich nach Norden." Koordinaten würden hier nichts bringen.

Darüber hinaus sind diese Namen das, was dem Decision-Model zur Auswahl gestellt wird und was es zurückgibt. `"north-east"` ist ein Wort, das ein Sprachmodell
versteht; `(1, -1)` ist keines.

## Was diese Ameise aktuell tun kann

```python
def free_directions(ant: dict) -> list[str]:
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            open_ways.append(name)
    return open_ways
```

![Links eine Ameise mitten auf dem Brett mit acht Pfeilen, rechts dieselbe
Ameise am oberen Rand mit nur fünf Pfeilen; drei Richtungen sind durchgestrichen,
weil es dort keine Felder gibt](../bilder/optionen.png)

*Genau die grünen Pfeile werden zu `criteria`. Was durchgestrichen ist, bekommt
das Modell nie zu sehen.*

Diese Funktion ermittelt, welche Nachbarfelder der Ameise frei und damit für den nächsten Schritt in Frage kommen. Zusätzlich gibt es eine Prüfung, ob nich der Rand des Spielfeldes erreicht ist.

## Die Frage

```python
STEP_QUESTION = (
    "An ant is standing on a board and has to decide where to go next. "
    "Which way should it go?"
)
```

Dies ist die grundsätzliche Frage, die sich bei jedem Schritt der Ameise stellt.

## Die Anfrage an das Decision-Model

```python
from typesafe_sdk import Choice, TypeSafeClient, TypeSafeError


def ask_jev(ant: dict) -> object:
    ways = free_directions(ant)

    state = {"the ant is": "standing on open ground"}
    questions = {
        "step": Choice(instructions=STEP_QUESTION, criteria=dict.fromkeys(ways))
    }

    client = TypeSafeClient(api_key=api_key(), timeout=15)
    return client.system_one(state=state, questions=questions)
```

Eine Frage an das Decision-Model besteht immer aus:

* **state** : Die Grundlage für die Entscheidung des Modells. In diesem Beispiel die aktuelle Situation der Ameise.

* **question** : Frage, die das Modell beantworten soll. 

Das Besondere an einem Decision-Model ist, dass es nicht wie Chat-Modelle mit Text antwortet,
sondern man gibt ihm den Datentyp für die Antwort vor.

**Choice** gibt eine Auswahl vor, die **criteria**, aus denen das Modell eine auswählt. Bei der Ameise sind dies die Richtungen, in die sie gehen kann.

### Die Auswahl entsteht zur Laufzeit

```python
criteria=dict.fromkeys(ways)
```

`ways` kommt aus der Funktion `free_directions`. Das ist **keine feste Liste von acht Richtungen**, sondern das, was für die Ameise jetzt möglich. Eine Ameise am Rand bekommt den Rand nicht angeboten.

`dict.fromkeys(ways)` enthält `{"north": None, "east": None, …}`. Die Werte sind
Beschreibungen, die man den Möglichkeiten mitgeben kann.

### Der Zustand **state** ist möglichst klein

```python
state = {"the ant is": "standing on open ground"}
```

Eine Angabe. Das ist keine Faulheit: Ein Zustand **state**, der mit Unwesentlichem
aufgefüllt ist, macht die Antwort **schlechter** — und kostet pro Wort Geld.
Jede Zeile, die in den nächsten Kapiteln dazukommt, muss sich rechtfertigen.

### Ein Client, synchron

Das SDK bietet `TypeSafeClient` und `AsyncTypeSafeClient`. Hier reicht der
synchrone: Streamlit arbeitet ein Skript von oben nach unten ab, und eine
Anfrage, auf die gewartet wird, passt genau dazu. Der asynchrone lohnt sich ab
Kapitel 3, wenn acht Ameisen gleichzeitig fragen.

## Den Schritt tun

```python
def take_a_step() -> None:
    ant = st.session_state.ant

    try:
        answer = ask_jev(ant)
    except TypeSafeError as failed:
        st.session_state.said = None
        st.session_state.failure = f"{type(failed).__name__}: {failed}"
        return

    step = answer.choices["step"]
    dx, dy = DIRECTIONS[step.choice]
    ant["x"] += dx
    ant["y"] += dy
    ...
```

`answer.choices["step"]` — der Schlüssel ist derselbe, unter dem die Frage
gestellt wurde. Darin: `choice`, `confidence` und `probabilities`.

Alles, was das SDK an Fehlern kennt, ist von `TypeSafeError` abgeleitet:
falscher Schlüssel, überschrittenes Limit, Zeitüberschreitung. Der Klassenname
steht mit in der Meldung, weil `TypeSafeAuthenticationError` etwas ganz anderes
bedeutet als `TypeSafeRateLimitError`.

Scheitert die Anfrage, bleibt die Ameise stehen.

## Die Antwort zusätzlich anzeigen

```python
    chosen, sure, tokens = st.columns(3)
    chosen.metric("Chosen", said["choice"])
    sure.metric("Confidence", f"{said['confidence']:.2f}")
    tokens.metric("Input tokens", said["tokens"])

    st.bar_chart(
        {"probability": dict(sorted(said["probabilities"].items()))},
        horizontal=True, height=260,
    )
```

Die Antworten des Modells sind zusätzlich in einem Balkendiagramm zu sehen. Eine klare
Antwort ist ein hoher Balken.

## Eine Antwort des Decision-Models

Eine Anwort auf eine echte Anfrage:

| | |
|---|---|
| Modell | `jev-1.13.0` |
| Gewählt | `north` |
| Konfidenz | **0,33** |
| Eingabe-Tokens | 356 |

### Was Konfidenz wirklich misst

Der Wert **Konfidenz** sagt, wie sich die Wahrscheinlichkeit über die Optionen
verteilt: Liegt alles auf einer, ist er 1. Je gleichmäßiger sie sich verteilt,
desto kleiner wird er, bis auf 0 bei völliger Gleichverteilung.

Das ist ein feiner, aber wichtiger Unterschied zu „wie sicher ist das Modell, dass die
Antwort **richtig** ist". Darüber sagt der Wert nichts. Er misst nur, wie klar
eine Option herausragt. Ein Modell kann sich sehr sicher sein und trotzdem
danebenliegen — dann ist die Konfidenz hoch und die Antwort falsch.

### Konfidenz im Detail

Die Dokumentation von TypeSafe gibt die Rechnung für drei Optionen an:
`(3 × höchste Wahrscheinlichkeit − 1) ÷ 2`. Verallgemeinert, mit *n* Optionen:

> **Konfidenz = (n × höchste Wahrscheinlichkeit − 1) ÷ (n − 1)**

An der Antwort oben nachgerechnet — acht Optionen, die höchste bei 0,37:
`(8 × 0,37 − 1) ÷ 7 = 0,28`. Gemeldet hat das Modell 0,29; der Rest ist Rundung, weil
die Wahrscheinlichkeiten auf zwei Stellen kommen.

![Die acht Wahrscheinlichkeiten einer echten Antwort als Balken, mit der Linie
für den reinen Zufall bei 0,125 und der daraus berechneten
Konfidenz](../bilder/konfidenz.png)

Der Teiler `n − 1` ist der Grund, warum man Konfidenzen **nicht** mit der
höchsten Wahrscheinlichkeit verwechseln darf: Er rechnet die Zahl der Optionen
heraus. 0,37 sind bei acht Möglichkeiten dreimal so viel wie Zufall, bei zwei
Möglichkeiten dagegen weniger als die Hälfte. Genau das braucht dieses Spiel,
denn die Zahl der Optionen ändert sich hier mit jedem Schritt.

0,33 ist auf dem ersten Blick zwar wenig, aber eigentlich richtig.

Fragen Sie sich, was die Ameise weiß: 

Sie steht irgendwo, und sonst nichts. Sie sieht kein Ziel (z.B. eine Frucht), weil es keines gibt. Niemand hat ihr etwas gesagt. Unter diesen Umständen ist eine Himmelsrichtung so gut wie die andere — und das Modell sagt das, indem es mit einer
Konfidenz von 0,33 antwortet.

Eine hohe Konfidenz wäre hier das **schlechtere** Ergebnis: ein Modell, das sich
sicher ist, ohne einen Grund zu haben.

### Ab wann darf man einer Antwort folgen?

TypeSafe empfiehlt drei Stufen: **unter 0,5** ist das Modell wirklich unsicher
und man sollte nicht raten; **0,5 bis 0,9** heißt weitermachen, aber mit
Vorsicht; **über 0,9** erst darf etwas Riskantes passieren. Welche Stufe gilt,
hängt davon ab, was eine falsche Entscheidung anrichtet.

Dieses Spiel legt die Schwelle in Kapitel 5 auf **0,22** — deutlich darunter.
Das ist kein Widerspruch, sondern dieselbe Überlegung: Was eine Ameise mit
einem verkehrten Schritt anrichtet, ist ein verkehrter Schritt. Er kostet eine
Runde und ist in der nächsten korrigierbar. Bei einer Überweisung oder einer
Kündigung wären 0,9 zu niedrig.

Diese 0,33 sind die Zahl, die der Rest des Tutorials verbessern will. Kapitel 5
gibt der Ameise die Möglichkeit mehr zu sehen, Kapitel 6 gibt der Königin eine Stimme. Beides sollte den Wert steigen lassen.

## Ausprobieren

* Drücken Sie mehrmals. Die Antwort schwankt — bei 0,33 Konfidenz ist das keine
  Fehlfunktion, sondern die Aussage.
* Laufen Sie mit der Ameise in eine Ecke. Dort hat sie nur noch drei Möglichkeiten,
  und im Diagramm sind es auch nur noch drei Balken. Das ist die Auswahl zur
  Laufzeit, in Bildern.
* Ändern Sie `STEP_QUESTION` in „Which way should it go? It is looking for food
  in the north." und sehen Sie sich die Konfidenz an.

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

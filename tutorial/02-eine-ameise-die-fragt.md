# Schritt 2 — Eine Ameise, die fragt

**Ziel:** Eine Ameise steht auf dem Brett. Du drückst einen Knopf, und sie geht
dorthin, wo **TypeSafe Jev** es sagt.

Das ist der wichtigste Schritt des Tutorials, und er kommt bewusst früh. Alles,
worum es geht, steht danach schon da — die sechs Kapitel danach handeln nur
noch davon, was die Ameise gezeigt bekommt und wie man sie fragt.

## Der Schlüssel

Ab hier brauchst du einen von
[console.typesafe.ai/keys](https://console.typesafe.ai/keys). Zwei Wege hinein:

**In eine Datei `.env` neben `app.py`:**

```
TYPESAFE_API_KEY=dein-schlüssel
```

Sie gehört nicht ins Repository; in `.gitignore` steht sie schon.

**Oder in die Seitenleiste** der laufenden Anwendung. Das ist der Weg für alle,
die das Spiel später im Netz benutzen: Jeder bringt seinen eigenen mit.

```python
import os
from dotenv import load_dotenv

load_dotenv()


def api_key() -> str:
    return st.session_state.get("typed_key", "").strip() or os.getenv(
        "TYPESAFE_API_KEY", ""
    ).strip()
```

Das Getippte gewinnt gegen die Datei — sonst könnte man einen veralteten
Schlüssel in `.env` nicht übergehen. Und es liegt in `st.session_state`, also im
Arbeitsspeicher dieser einen Sitzung: Tab zu, Schlüssel weg. `type="password"`
im Feld macht Punkte statt Zeichen.

**Was das kostet:** Eine Anfrage sind rund 350 Eingabe-Tokens, und eine Million
davon kostet 0,042 Dollar. Du kannst dieses Kapitel hundertmal durchklicken für
weniger als einen Cent. In Kapitel 7 rechnet das Programm selbst mit.

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
geschrieben werden, **wenn es noch nicht da ist**. Genau das macht das
`if "ant" in st.session_state: return`: Es verwandelt einen Neudurchlauf in ein
Neuzeichnen statt in einen Neustart. Wer das übersieht, baut ein Spiel, das bei
jedem Klick von vorn anfängt.

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

Dass die Richtungen **Namen** haben und nicht durchnummeriert sind, ist keine
Frage der Lesbarkeit. Diese Namen sind das, was dem Modell zur Auswahl gestellt
wird und was es zurückgibt. `"north-east"` ist ein Wort, das ein Sprachmodell
versteht; `(1, -1)` ist keines.

## Was diese Ameise kann

```python
def free_directions(ant: dict) -> list[str]:
    open_ways = []
    for name, (dx, dy) in DIRECTIONS.items():
        x, y = ant["x"] + dx, ant["y"] + dy
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            open_ways.append(name)
    return open_ways
```

Zehn Zeilen, und sie sind der Grund, warum es dieses Spiel gibt. Merk dir die
Funktion; sie wächst noch, aber ihre Aufgabe bleibt: **Was kann diese eine
Ameise gerade wirklich tun?** Vom Brett herunter ist keine Richtung.

## Die Frage

```python
STEP_QUESTION = (
    "An ant is standing on a board and has to decide where to go next. "
    "Which way should it go?"
)
```

Ganz oben bei den Konstanten und nicht irgendwo mitten im Code — weil das
Umformulieren dieses Textes die **eigentliche Arbeit** an einem solchen
Programm ist. Du wirst ihn mehrfach ändern und zusehen, wie sich die Antworten
ändern. Was man oft anfasst, soll leicht zu finden sein.

## Die Anfrage

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

Sieben Zeilen. Zwei davon sind der Kern.

### Die Auswahl entsteht zur Laufzeit

```python
criteria=dict.fromkeys(ways)
```

`ways` kommt aus `free_directions`. Das ist **keine feste Liste von acht
Richtungen**, sondern das, was diese Ameise jetzt kann. Eine Ameise am Rand
bekommt den Rand nicht angeboten.

Das Modell kann deshalb nichts Unmögliches antworten. Nicht, weil es klug genug
wäre, es zu lassen — sondern weil das Unmögliche nie auf der Karte stand. Das
ist gemeint, wenn von Typsicherheit die Rede ist, und es ist in Python eine
Zeile.

`dict.fromkeys(ways)` baut `{"north": None, "east": None, …}`. Die Werte sind
Beschreibungen, die man den Möglichkeiten mitgeben kann; hier sprechen die
Namen für sich, ab Kapitel 5 werden sie gebraucht.

### Der Zustand ist klein

```python
state = {"the ant is": "standing on open ground"}
```

Eine Angabe. Das ist keine Faulheit: Ein Zustand, der mit Unwesentlichem
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

Alles, was das SDK an Unglück kennt, ist von `TypeSafeError` abgeleitet:
falscher Schlüssel, überschrittenes Limit, Zeitüberschreitung. Der Klassenname
steht mit in der Meldung, weil `TypeSafeAuthenticationError` etwas ganz anderes
bedeutet als `TypeSafeRateLimitError`.

**Und es gibt keinen Ersatz.** Scheitert die Anfrage, bleibt die Ameise stehen.
Kein Zufallsschritt, keine Regel, die einspringt. Ein Spiel, das ohne das Modell
weiterläuft, verbirgt genau das, was man sehen will.

## Die Antwort zeigen

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

Das Balkendiagramm ist das, was man sich wirklich ansehen sollte. Eine klare
Antwort ist ein hoher Balken; eine Ameise ohne Grund, etwas zu bevorzugen, sind
acht ähnliche.

## Was herauskommt — und warum es enttäuschend aussieht

Meine erste echte Anfrage:

| | |
|---|---|
| Modell | `jev-1.13.0` |
| Gewählt | `north` |
| Konfidenz | **0,33** |
| Eingabe-Tokens | 356 |

0,33 ist wenig. Und das ist genau richtig.

Frag dich, was die Ameise weiß: Sie steht irgendwo, und sonst nichts. Sie sieht
keine Frucht, weil es noch keine gibt. Niemand hat ihr etwas gesagt. Unter
diesen Umständen ist eine Himmelsrichtung so gut wie die andere — und das
Modell sagt das, indem es unsicher antwortet.

Eine hohe Konfidenz wäre hier das **schlechtere** Ergebnis: ein Modell, das sich
sicher ist, ohne einen Grund zu haben.

**Konfidenz ist nicht die höchste Wahrscheinlichkeit.** Sie misst, wie weit die
Antwort vom reinen Zufall entfernt liegt, verrechnet mit der Zahl der
Möglichkeiten. Bei acht Optionen ist Zufall 0,125 pro Stück. Das ist das
richtige Maß, wenn die Zahl der Möglichkeiten von Zug zu Zug schwankt — und sie
schwankt hier bei jedem Schritt.

Diese 0,33 sind die Zahl, gegen die der Rest des Tutorials arbeitet. Kapitel 5
gibt der Ameise Augen, Kapitel 6 gibt der Königin eine Stimme. Beides sollte sie
steigen lassen. Schreib sie dir auf.

## Ausprobieren

* Drück mehrmals. Die Antwort schwankt — bei 0,33 Konfidenz ist das keine
  Fehlfunktion, sondern die Aussage.
* Lauf mit der Ameise in eine Ecke. Dort hat sie nur noch drei Möglichkeiten,
  und im Diagramm sind es auch nur noch drei Balken. Das ist die Auswahl zur
  Laufzeit, in Bildern.
* Ändere `STEP_QUESTION` in „Which way should it go? It is looking for food in
  the north." und sieh dir die Konfidenz an.
* Lösch ein Zeichen aus dem Schlüssel in der Seitenleiste. Du bekommst
  `TypeSafeAuthenticationError` zu sehen statt eines Absturzes.

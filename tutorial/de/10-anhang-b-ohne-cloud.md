# Anhang B — Dasselbe Spiel ohne Cloud

*[English version](../en/10-anhang-b-ohne-cloud.md)*

![Queeny, von hinten über die Schulter gesehen, sitzt nachts an einem
Schreibtisch vor einem Laptop; auf dem Bildschirm leuchtet das Spielbrett mit
Arbeiterinnen und Äpfeln, ein Kabel führt zur Steckdose, daneben eine
Tischlampe, draußen vor dem Fenster ziehen Wolken](../bilder/anhang-b-titel.png)

*Dasselbe Spiel, aber diesmal auf dem eigenen Rechner.*

Seit Version 0.35 führt **Ollama** Decision-Models auf dem eigenen Rechner aus
und beantwortet Entscheidungsfragen im selben Format wie TypeSafe: derselbe Pfad `/v1/systemone`, dieselben Fragetypen `choice`, `noul`
und `score`, dieselben `criteria`, und in der Antwort `probabilities`,
`confidence` und `usage`. Die Ankündigung sagt das auch offen — die Schnittstelle
sei „based on TypeSafe's Jev API".

Für dieses Spiel heißt das: Es läuft **ohne Schlüssel, ohne Kosten und ohne
Netz**. Und zwar ohne eine Zeile Code zu ändern.

## Einrichten

```sh
ollama pull nimble
```

Zur Einführung gab es drei Modelle: `nimble` (9B), `tev1` (4B) und
`tev1:0.8b`. Alle drei gibt es noch. Inzwischen ist die Auswahl größer: Unter
[ollama.com/search?c=decision](https://ollama.com/search?c=decision) stehen
Ende Oktober 2026 zwölf Decision-Models, darunter:

| Modell | Größe auf der Platte | Hinweis |
|---|---|---|
| `nimble` | 9,3 GB (9B) | hier gemessen, Apache 2.0 |
| `kev` | 6,7 GB (9B) | hier gemessen, Apache 2.0, ab Ollama 0.40.4 |
| `strands-decider` | 2,0 GB (2B) | hier gemessen, Apache 2.0, nur Apple Silicon |
| `nimble-v3` | 9,3 GB (9B) | Nachfolger von nimble, nur **nicht-kommerziell** (CC BY-NC 4.0) |
| `tev1` | 4,5 GB (4B), 0,8 GB (0.8B) | antwortet mit nur etwa 2000 Token Kontext |
| `d3` | 3 bis 30 GB (2B bis 27B) | ab Ollama 0.40.9, versteht auch Bilder |

Dann in `.env`:

```
TYPESAFE_API_KEY=ollama
TYPESAFE_BASE_URL=http://localhost:11434
TYPESAFE_DEFAULT_MODEL=nimble
```

Mehr nicht. Das `typesafe-sdk` liest beide Adressen aus der Umgebung
(`TYPESAFE_BASE_URL` und `TYPESAFE_DEFAULT_MODEL`), und einen Schlüssel braucht
Ollama nicht — das Feld darf nur nicht leer sein. Ein anderes Modell ist eine
andere Zeile `TYPESAFE_DEFAULT_MODEL`.

Hier zahlt sich aus, was in Kapitel 2 nur ein Satz war: dass die Basis-URL
konfigurierbar ist.

> **Stolperfalle.** Die Basis darf **kein** `/v1` enthalten. Das SDK hängt
> `/v1/systemone` selbst an, und aus `…:11434/v1` wird `…/v1/v1/systemone`. Die
> Fehlermeldung lautet dann `404 page not found` und sieht aus, als fehlte das
> Modell. Richtig ist `http://localhost:11434`.

Gemessen habe ich auf einem Apple M4 mit 32 GB und Ollama 0.40.13. Ollama
rechnet die drei Modelle dort über MLX auf der GPU.

## Antwortet es brauchbar?

Eine Ameise, die eine Frucht zwei Felder im Nordosten sieht:

| | nimble | kev | strands-decider |
|---|---|---|---|
| Gewählt | `north-east` | `north-east` | `north-east` |
| Konfidenz | **0,99** | 0,78 | 0,75 |
| Eingabe-Tokens | 328 | 128 | 196 |
| erster Aufruf (Modell wird geladen) | 3,8–8,8 s | 4,7 s | 1,9 s |
| danach, Median | **1,4–2,8 s** | 1,2 s | **0,4 s** |

Alle drei wählen richtig. nimble ist dabei am entschlossensten, aber auch am
langsamsten.

In der Cloud habe ich für eine Anfrage rund 600 ms gemessen. Lokal ist also nur
das kleinste Modell schneller.

## Die Zahl, die mich zuerst getäuscht hat

In einer früheren Fassung dieses Anhangs stand für nimble: **163 ms**. Heute
messe ich dasselbe noch einmal, fünfmal dieselbe Anfrage hintereinander:

```
gleiche Anfrage:       6918, 5, 4, 4, 4, 5 ms
verschiedene Anfragen: 4242, 2582, 2440, 2888, 2644, 2377 ms
```

Nach dem ersten Aufruf kommt die gleiche Anfrage in 4 ms zurück. Das ist keine
Rechenzeit, das ist ein **Cache**: Ollama merkt sich die Antwort auf einen
Prompt, den es schon einmal gesehen hat. Fünfmal dieselbe Anfrage misst also
nichts.

Dieselbe Falle gibt es bei acht Ameisen gleichzeitig:

```
8 gleiche Anfragen:        2,7 s
8 verschiedene Anfragen:  22,7 s
8 verschiedene, nochmal:  22,4 s
```

Acht verschiedene brauchen etwa achtmal so lange wie eine. Acht verschiedene
Prompts brauchen acht eigene Vorberechnungen, und eine Maschine mit einer GPU
arbeitet sie praktisch nacheinander ab. Ein Dienst im Netz hat viele.

Daraus folgt etwas, das in Kapitel 3 so nicht stehen konnte:

> `asyncio.gather` zahlt sich gegen einen **entfernten** Dienst aus und bringt
> **lokal fast nichts**. Dieselbe Zeile Code, gegensätzlicher Nutzen — je
> nachdem, ob die Wartezeit Netzwerk ist oder Rechenzeit.

Messen Sie lokal deshalb immer mit Anfragen, die sich unterscheiden. Im Spiel
passiert das von selbst, weil jede Ameise woanders steht.

## Ein ganzes Level

Dasselbe Brett und derselbe Befehl wie in Kapitel 8, „Fan out and search, and
carry what you find straight home.", je drei Läufe, höchstens 60 Runden:

| | Jev (Cloud, Kapitel 8) | nimble | kev | strands-decider |
|---|---|---|---|---|
| Runden bis fünf Früchte | 23 · 26 · 59 | **19 · 22 · 23** | nicht geschafft | nicht geschafft |
| verworfene Antworten | 36–47 % | 28–41 % | 100 % | 100 % |
| eine Runde mit acht Ameisen, Median | 0,6 s | **11–18 s** | — | — |
| ein ganzes Spiel | unter einer Minute | **5–6 Minuten** | — | — |
| Kosten für das Spiel | ~0,005 $ | **0** | 0 | 0 |
| Schlüssel nötig | ja | nein | nein | nein |

**nimble spielt so gut wie Jev.** Drei Läufe sind zu wenig, um zu sagen, dass
es besser ist. Aber es ist nicht schlechter. Der Preis ist die Zeit: Eine
Runde dauert lokal zwanzig- bis dreißigmal so lange.

**kev und strands-decider kommen nicht aus dem Bau.** Im Bau sieht eine Ameise
nur die anderen Ameisen. Darauf antworten beide Modelle unentschlossen: kev mit
einer Konfidenz von höchstens 0,18, strands-decider mit 0,02 bis 0,07. Beides
liegt unter der Schwelle von 0,22 aus Kapitel 5, also wird jede Antwort
verworfen, und keine Ameise bewegt sich.

Und weil sich im Bau dann nichts ändert, ändert sich auch die Frage nicht: Die
Modelle laufen mit Temperatur 0, jede Runde kommt dieselbe Antwort, und die
Kolonie steckt für immer fest.

### Tipp: Die Schwelle gehört zum Modell

Die 0,22 wurden mit Jev gemessen. Konfidenz ist bei jedem Modell anders
geeicht, und eine Schwelle, die für das eine Modell passt, kann ein anderes
komplett lahmlegen. Wer das Modell wechselt, muss die Schwelle neu messen.

## Was damit nicht geht

**Die Fassung in der Streamlit-Cloud.** Dort läuft kein Ollama, und `localhost`
zeigt auf den Server von Streamlit. Wer das Spiel im Netz anbietet, braucht
weiterhin einen Schlüssel — der lokale Weg ist der für die eigene Maschine.

**Ein kleiner Rechner.** nimble will 9,3 GB geladen und im Speicher gehalten
haben. Die kleinen Modelle wären schnell genug, spielen aber mit der Schwelle
aus Kapitel 5 nicht.

## Ausprobieren

* Fangen Sie klein an: Setzen Sie `.env` um und drücken Sie einmal „Next
  round". Dass es überhaupt funktioniert, ohne dass Sie eine Zeile Code
  angefasst haben, ist der eigentliche Punkt dieses Anhangs.
* Vergleichen Sie die Konfidenzen. Stellen Sie eine Ameise neben eine Frucht
  und eine ins Leere — wo unterscheiden sich Cloud und lokal, und wo nicht?
* Setzen Sie in `level1.json` `"ants"` auf 3 und spielen Sie lokal. Eine Runde
  wird dreimal schneller, das Spiel dafür zäher. Welcher Tausch ist Ihnen
  lieber?
* Nehmen Sie `kev` und senken Sie `MIN_CONFIDENCE` auf 0,1. Kommt die Kolonie
  jetzt aus dem Bau? Und was ist eine Antwort mit 0,1 Konfidenz noch wert?

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

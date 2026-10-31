# Anhang B — Dasselbe Spiel ohne Cloud

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
`tev1:0.8b`. Alle drei gibt es noch, und das hier Gemessene ist `nimble`; auf
der Platte belegt es **9,5 GB**.

Inzwischen ist die Auswahl größer. Unter
[ollama.com/search?c=decision](https://ollama.com/search?c=decision) stehen
Ende Oktober 2026 zwölf Decision-Models, darunter:

| Modell | Größen | Hinweis |
|---|---|---|
| `nimble` | 9B | hier gemessen, Apache 2.0 |
| `nimble-v3` | 9B | Nachfolger, ab Ollama 0.40.4, nur **nicht-kommerziell** (CC BY-NC 4.0) |
| `tev1` | 4B, 0.8B | antwortet mit nur etwa 2000 Token Kontext |
| `d3` | 2B bis 27B | ab Ollama 0.40.9, versteht auch Bilder |

Gemessen habe ich nur `nimble`. Die anderen sprechen dieselbe Schnittstelle
`/v1/systemone` und sollten sich ebenso über `TYPESAFE_DEFAULT_MODEL` einsetzen
lassen; ausprobiert habe ich es nicht.

Dann in `.env`:

```
TYPESAFE_API_KEY=ollama
TYPESAFE_BASE_URL=http://localhost:11434
TYPESAFE_DEFAULT_MODEL=nimble
```

Mehr nicht. Das `typesafe-sdk` liest beide Adressen aus der Umgebung
(`TYPESAFE_BASE_URL` und `TYPESAFE_DEFAULT_MODEL`), und einen Schlüssel braucht
Ollama nicht — das Feld darf nur nicht leer sein.

Hier zahlt sich aus, was in Kapitel 2 nur ein Satz war: dass die Basis-URL
konfigurierbar ist.

> **Stolperfalle.** Die Basis darf **kein** `/v1` enthalten. Das SDK hängt
> `/v1/systemone` selbst an, und aus `…:11434/v1` wird `…/v1/v1/systemone`. Die
> Fehlermeldung lautet dann `404 page not found` und sieht aus, als fehlte das
> Modell. Richtig ist `http://localhost:11434`.

## Antwortet es brauchbar?

Eine Ameise, die eine Frucht zwei Felder im Nordosten sieht:

| | |
|---|---|
| Gewählt | `north-east` |
| Konfidenz | **0,985** |
| Wahrscheinlichkeit darauf | 0,996 |
| Eingabe-Tokens | 289 |
| Latenz, erster Aufruf | 1442 ms (das Modell wird geladen) |
| Latenz, danach | **163 ms** im Median aus fünf Aufrufen |

Eine einzelne Anfrage beantwortet nimble also **schneller als die Cloud**, wo
ich rund 600 ms gemessen habe.

## Ein ganzes Level

Dasselbe Brett, derselbe Befehl wie in Kapitel 5:

| | Jev (Cloud) | nimble (lokal) |
|---|---|---|
| Runden bis fünf Früchte | 16 · 17 | **26** |
| verworfene Antworten | 23–26 % | **53 %** |
| eine Runde mit acht Ameisen | 0,6 s | **15–25 s** |
| Kosten für das Spiel | ~0,0005 $ | **0** |
| Schlüssel nötig | ja | nein |

Das Spiel geht also auf, nur langsamer und mit mehr Verwürfen. Die doppelte
Verwurfsquote entsteht dort, wo eine Ameise **nichts** sieht: Bei einer
sichtbaren Frucht ist nimble so entschlossen wie Jev, bei einer Frage ohne
Anhaltspunkte ist es unentschlossener — und die Schwelle aus Kapitel 5 fängt
mehr davon ab.

## Die Zahl, die mich zuerst getäuscht hat

Eine einzelne Anfrage: 163 ms. Eine Runde: 25 Sekunden. Das ist Faktor 150 bei
acht Anfragen, und das kann nicht stimmen.

Ich habe deshalb acht Anfragen gleichzeitig abgeschickt und gemessen — 1,5
Sekunden. Also doch alles in Ordnung? Nein: **Ich hatte achtmal dieselbe Anfrage
geschickt.** Gleiche Prompts teilen sich den Cache, und das misst nichts.

Mit acht *verschiedenen* Zuständen, also dem echten Fall:

```
8 gleiche Anfragen:        3,4 s
8 verschiedene Anfragen:  20,5 s
8 verschiedene, nochmal:  15,5 s
```

Das deckt sich mit den 25 Sekunden im Spiel.

**Der Grund:** Acht verschiedene Prompts brauchen acht eigene Vorberechnungen,
und eine Maschine mit einer GPU arbeitet sie praktisch nacheinander ab. Ein
Dienst im Netz hat viele.

Daraus folgt etwas, das in Kapitel 3 so nicht stehen konnte:

> `asyncio.gather` zahlt sich gegen einen **entfernten** Dienst aus und bringt
> **lokal fast nichts**. Dieselbe Zeile Code, gegensätzlicher Nutzen — je
> nachdem, ob die Wartezeit Netzwerk ist oder Rechenzeit.

Wer lokal ernsthaft spielen will, dreht deshalb nicht an der Parallelität,
sondern an der Zahl der Fragen: weniger Ameisen, ein größeres Denkintervall,
oder Absichten statt Einzelschritten, wie es Kapitel 8 vorschlägt. Genau dort
wird die Ersparnis lokal zur Geschwindigkeit, während sie in der Cloud nur Geld
spart.

## Was damit nicht geht

**Die Fassung in der Streamlit-Cloud.** Dort läuft kein Ollama, und `localhost`
zeigt auf den Server von Streamlit. Wer das Spiel im Netz anbietet, braucht
weiterhin einen Schlüssel — der lokale Weg ist der für die eigene Maschine.

**Ein kleiner Rechner.** 9,5 GB Modell wollen geladen und im Speicher gehalten
werden. `tev1:0.8b` und `d3:2b` sind der Weg für schwächere Hardware; gemessen
habe ich sie nicht.

## Ausprobieren

* Fangen Sie klein an: Setzen Sie `.env` um und drücken Sie einmal „Next
  round". Dass es überhaupt funktioniert, ohne dass Sie eine Zeile Code
  angefasst haben, ist der eigentliche Punkt dieses Anhangs.
* Vergleichen Sie die Konfidenzen. Stellen Sie eine Ameise neben eine Frucht
  und eine ins Leere — wo unterscheiden sich Cloud und lokal, und wo nicht?
* Setzen Sie in `level1.json` `"ants"` auf 3 und spielen Sie lokal. Eine Runde
  wird dreimal schneller, das Spiel dafür zäher. Welcher Tausch ist Ihnen
  lieber?
* Laden Sie `tev1:0.8b` und messen Sie dagegen. Reicht ein Modell mit 0,8
  Milliarden Parametern für acht Ameisen, die nur eine Himmelsrichtung wählen
  sollen?

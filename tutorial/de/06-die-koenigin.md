# Schritt 6 — Die Königin

*[English version](../en/06-die-koenigin.md)*

![Queeny mit Krone und blauem Kleid, von hinten über die Schulter gesehen,
hebt die Hand und spricht zu fünf Arbeiterinnen mit bunten Helmen, die vor ihr
auf dem leuchtend grünen Spielbrett stehen und zu ihr aufsehen](../bilder/schritt-6-titel.png)

*Ein Satz von ihr, und die Kolonie wird aktiv.*

**Ziel:**

* Ein Textfeld.
* Was Sie hineinschreiben, ist eine Nachricht an jede Ameise und steht in deren Zustand.
* Und: Bis zur ersten Nachricht schläft die Kolonie.

Jetzt können Sie aktiv eingreifen.

## Die Kolonie schläft

In `start()`:

```python
    st.session_state.order = ""
    st.session_state.awake = False
```

Es gibt zwei neue zentrale Attribute.

Das Attribut `awake` legt fest, ob die Kolonie aktiv ist.
Das zweite Attribut `order` enthält den aktuellen Befehl der Königin.

Vor dem ersten Satz der Königin gibt es keine Aktivitäten, und somit ist keine Anfrage an das Decision-Model notwendig.

```python
ready = bool(api_key()) and st.session_state.awake and not won
```

## Die Leiste

```python
with st.form("order_form", clear_on_submit=True, border=False):
    field, say = st.columns([6, 1])
    draft = field.text_input(
        "The queen says", placeholder="say something to the colony",
        label_visibility="collapsed",
    )
    if say.form_submit_button("Say", width="stretch") and draft.strip():
        st.session_state.order = draft.strip()
        st.session_state.awake = True
        st.rerun()
```

`st.form` statt eines nackten Textfeldes, aus einem Grund: Ein Formular wird
mit **Enter** abgeschickt, nicht erst beim Klick. In ein Feld, in das man einen
Satz tippt, gehört das. `clear_on_submit=True` leert es danach, damit der
nächste Satz sofort getippt werden kann.

Dazu ein Knopf, der den Befehl zurücknimmt:

```python
if hush.button("Say nothing", disabled=not st.session_state.order):
    st.session_state.order = ""
    st.rerun()
```

Er weckt nicht und schläfert nicht ein. Er nimmt nur zurück, was gesagt wurde.

## Tipp: Widget-Namen und `session_state` teilen sich einen Namensraum

In einer früheren Fassung hieß das Formular `st.form("order")`, und die Anwendung brach ab:

```
StreamlitValueAssignmentNotAllowedError:
Values for the widget with key 'order' cannot be set using st.session_state.
```

**Die Erklärung**

Ein Widget mit dem Namen `order` verwendet automatisch `st.session_state.order`.

Das Programm setzt in der Variable `st.session_state.order` die aktuelle Nachricht der Königin. Beides geht aber nicht.

Die Lösung ist banal: das Formular in `order_form` umbenennen.

## Der Befehl der Königin im Zustand jeder Ameise

In `question_for`:

```python
    state = {
        **(
            {"the ant queen says": st.session_state.order}
            if st.session_state.order
            else {}
        ),
        "the ant is carrying": ...,
    }
```

Dazu ein Satz in der Frage:

> If the ant queen has said something, it applies to this ant too and comes
> before the rest.

Der Befehl der Königin wird **unverändert** weitergegeben. Sie können auf Deutsch schreiben, das Modell versteht es genauso.

## Vier Sätze, vier Ergebnisse

Hier wird es interessant. Dieselbe Kolonie, dasselbe Level, vier Läufe:

| Was gesagt wurde | Verworfene Antworten | Was passierte |
|---|---|---|
| nichts (wie Kapitel 5) | 31 % | Sieg in 20 Runden |
| „Spread out to the corners, the fruit is far from the nest…" | **61 %** | 3 von 5 nach 15 Runden |
| „The fruit lies far out near the edges, most of it to the north and the west. Go there…" | **3 %** | Kolonie klemmt in der Nordwest-Ecke |
| „You are all crowded in one corner… turn around, search the middle and the south" | 10 % | löst sich, holt weiter |

### Tipp: Vage Sätze machen unsicher

„Verteilt euch in die Ecken" verdoppelte die Verwurfsquote von 31 % auf 61 %.
Kein Wunder: Vier Ecken sind vier Richtungen, und der Satz sagt nicht, welche.
Die Konfidenz misst genau das.

### Tipp: Sichere Kolonien sind nicht bessere Kolonien

Der dritte Satz ist der aufschlussreichste. „Die Früchte liegen im Norden und
Westen, geht dorthin" wurde mit **97 % angenommenen Antworten** befolgt — die
niedrigste Verwurfsquote aller Läufe. Und das Ergebnis war das schlechteste:
Nach vierzig Runden standen alle acht Ameisen zusammengedrängt in der
Nordwest-Ecke, während sechs Früchte anderswo lagen.

Sie haben getan, was man ihnen gesagt hat. Sehr entschlossen.

**Die Verwurfsquote misst Entschlossenheit, nicht Richtigkeit.** Wer sie als
Gütemaß liest, optimiert auf Befehle, die keinen Spielraum lassen — und die
sind selten die besten. Behalten Sie das im Kopf, wenn in Kapitel 7 alle Zahlen
nebeneinander stehen und in Kapitel 8 gemessen wird.

### Tipp: Nachsteuern

Der vierte Satz wurde als Befehl in einer schwierigen Situation gegeben:

„Ihr steht alle in einer Ecke, und dort ist nichts mehr. Dreht um, geht auseinander, sucht die Mitte und den Süden."

Innerhalb von fünfzehn Runden löste sich das Knäuel auf, und der Vorrat wuchs weiter.

Immer einen Satz sagen, zusehen, ob er erfolgreich ist. Dann nachjustieren.

## Ausprobieren

Das Eingabefeld ist die Schnittstelle zur Ameisenkolonie.

* Fangen Sie mit „Go west" an und sehen Sie zu, wie wörtlich das genommen wird.
* Sagen Sie etwas, das die Ameisen nicht wissen können, weil sie nur drei Felder
  weit sehen: wo das Obst wirklich liegt. Nur Sie sehen das Brett.
* Sagen Sie etwas Widersprüchliches („Bleibt zusammen und verteilt euch") und
  schauen Sie in die verworfenen Antworten.
* Sagen Sie etwas auf Deutsch. Dann denselben Satz auf Englisch. Ändert sich die
  Konfidenz?
* Drücken Sie „Say nothing" mitten im Spiel. Die Kolonie bleibt wach und entscheidet
  weiter für sich — sie schläft nicht wieder ein.

---

*Dieses Tutorial wurde von Gerhard Völkl unter Verwendung von Claude Code (Anthropic) erstellt. Es soll helfen, mehr über das Thema „Wenn Ameisen ein Decision-Model fragen“ zu lernen. Verbesserungsvorschläge gerne an gkvoelkl@nelson-games.de.*

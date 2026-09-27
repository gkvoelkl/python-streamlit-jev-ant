# Schritt 6 — Die Königin

**Ziel:** Ein Textfeld. Was du hineinschreibst, steht im Zustand jeder Ameise,
und jede liest es für sich. Und: Bis der erste Satz gesagt ist, schläft die
Kolonie und es geht keine einzige Anfrage hinaus.

Das ist der Schritt, der aus der Simulation ein Spiel macht.

## Die Kolonie schläft

In `start()`:

```python
    st.session_state.order = ""
    st.session_state.awake = False
```

Zwei Dinge, nicht eines. `awake` ist nicht dasselbe wie „der Befehl ist nicht
leer": Einmal geweckt bleibt die Kolonie wach, und einen Befehl
zurückzunehmen ist etwas anderes, als sie wieder schlafen zu legen.

Warum überhaupt schlafen? Weil eine Frage vor dem ersten Befehl wenig hergibt.
In Kapitel 2 hast du gesehen, was dabei herauskommt: Konfidenz 0,33 für eine
Ameise, die nichts weiß. Seit Kapitel 5 sieht sie wenigstens etwas — aber im
Bau, wo alle stehen, sieht sie nur die anderen. Solche Anfragen kosten Geld und
liefern Rauschen.

Das ist eine Entwurfsentscheidung mit Nachdruck: **Vor dem ersten Satz der
Königin geht keine einzige Anfrage hinaus.**

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

## Stolperstein: Widget-Namen und `session_state` teilen sich einen Namensraum

Meine erste Fassung hieß `st.form("order")`, und die Anwendung brach ab:

```
StreamlitValueAssignmentNotAllowedError:
Values for the widget with key 'order' cannot be set using st.session_state.
```

Ein Widget mit dem Namen `order` beansprucht `st.session_state.order` für sich
— und dann darf das Programm den Wert nicht mehr selbst setzen. Die Lösung ist
banal (`order_form`), aber die Fehlermeldung findet man schneller, wenn man
weiß, wonach sie klingt: Streamlit hat **einen** Namensraum für Widget-Schlüssel
und eigene Zustandsschlüssel.

## Der Befehl im Zustand

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

Zuerst, weil es das eine ist, gegen das die Ameise alles andere abwägen soll.
Und nur wenn etwas gesagt wurde — ein leeres Feld hat im Zustand nichts
verloren.

Dazu ein Satz in der Frage:

> If the ant queen has said something, it applies to this ant too and comes
> before the rest.

Der Befehl wandert **unverändert** hinein. Du kannst auf Deutsch schreiben, das
Modell versteht es. Die Rust-Fassung dieses Spiels hat nachgemessen: Die Wahl
ist dieselbe, nur die Sicherheit liegt bei mehrdeutigen deutschen Sätzen etwas
niedriger.

## Vier Sätze, vier Ergebnisse

Hier wird es interessant. Dieselbe Kolonie, dasselbe Level, vier Läufe:

| Was gesagt wurde | Verworfene Antworten | Was passierte |
|---|---|---|
| nichts (wie Kapitel 5) | 31 % | Sieg in 20 Runden |
| „Spread out to the corners, the fruit is far from the nest…" | **61 %** | 3 von 5 nach 15 Runden |
| „The fruit lies far out near the edges, most of it to the north and the west. Go there…" | **3 %** | Kolonie klemmt in der Nordwest-Ecke |
| „You are all crowded in one corner… turn around, search the middle and the south" | 10 % | löst sich, holt weiter |

Drei Lehren stecken darin, und alle drei sind unbequem.

### Vage Sätze machen unsicher

„Verteilt euch in die Ecken" verdoppelte die Verwurfsquote von 31 % auf 61 %.
Kein Wunder: Vier Ecken sind vier Richtungen, und der Satz sagt nicht, welche.
Die Konfidenz misst genau das — den Abstand zum Münzwurf.

### Sichere Kolonien sind nicht bessere Kolonien

Der dritte Satz ist der aufschlussreichste. „Die Früchte liegen im Norden und
Westen, geht dorthin" wurde mit **97 % angenommenen Antworten** befolgt — die
niedrigste Verwurfsquote aller Läufe. Und das Ergebnis war das schlechteste:
Nach vierzig Runden standen alle acht Ameisen zusammengedrängt in der
Nordwest-Ecke, während sechs Früchte anderswo lagen.

Sie haben getan, was man ihnen gesagt hat. Sehr entschlossen.

**Die Verwurfsquote misst Entschlossenheit, nicht Richtigkeit.** Wer sie als
Gütemaß liest, optimiert auf Befehle, die keinen Spielraum lassen — und die
sind selten die besten. Behalte das im Kopf, wenn in Kapitel 7 alle Zahlen
nebeneinander stehen und in Kapitel 8 gemessen wird.

### Nachsteuern ist der eigentliche Spielzug

Der vierte Satz wurde in die feststeckende Lage hineingesagt, ohne Neustart:
„Ihr steht alle in einer Ecke und dort ist nichts mehr. Dreht um, geht
auseinander, sucht die Mitte und den Süden." Innerhalb von fünfzehn Runden
löste sich das Knäuel, und der Vorrat wuchs weiter.

Das ist die Schleife, um die es geht: einen Satz sagen, zusehen, wie er
scheitert, einen besseren sagen. Nichts daran ist Programmierarbeit.

## Ausprobieren

Das Feld ist die Schnittstelle — benutze sie.

* Fang mit „Go west" an und sieh zu, wie wörtlich das genommen wird.
* Sag etwas, das die Ameisen nicht wissen können, weil sie nur drei Felder
  weit sehen: wo das Obst wirklich liegt. Nur du siehst das Brett.
* Sag etwas Widersprüchliches („Bleibt zusammen und verteilt euch") und schau
  in die verworfenen Antworten.
* Sag etwas auf Deutsch. Dann denselben Satz auf Englisch. Ändert sich die
  Konfidenz?
* Drücke „Say nothing" mitten im Spiel. Die Kolonie bleibt wach und entscheidet
  weiter für sich — sie schläft nicht wieder ein.
* Und der Versuch, der am meisten über das Spiel verrät: Starte neu und drücke
  sofort „Next round". Geht nicht. Die Kolonie wartet auf dich.

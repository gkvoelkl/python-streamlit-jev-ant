# Tutorial: Wenn Ameisen ein Decision-Model fragen

*[English version](../en/README.md) – Schritt 1 ist übersetzt, die übrigen folgen.*

Eine Ameisen-Kolonie im Browser, gebaut in acht Schritten mit Python und
Streamlit. Jede Ameise fragt ein Decision-Model, was sie als Nächstes tun soll –
in diesem Tutorial TypeSafe Jev. Sie sind die Königin, und Ihr einziges
Steuer ist ein Satz.

Nach jedem Schritt läuft ein Programm, und ab Schritt 2 kommt jeder Schritt,
den eine Ameise macht, vom Modell.

## Loslegen

```sh
git clone https://github.com/gkvoelkl/python-streamlit-jev-ant
cd python-streamlit-jev-ant
uv run streamlit run app.py
```

Ab Schritt 2 brauchen Sie einen Schlüssel von
[console.typesafe.ai/keys](https://console.typesafe.ai/keys) – oder Ollama auf
dem eigenen Rechner, siehe Anhang B.

## Inhalt

[Einleitung](00-einleitung.md)

1. [Das Brett](01-das-brett.md)
2. [Eine Ameise fragt das Decision-Model](02-eine-ameise-die-fragt.md)
3. [Die Ameisen-Kolonie](03-die-kolonie.md)
4. [Tragen und abliefern](04-tragen-und-abliefern.md)
5. [Sehen](05-augen.md)
6. [Die Königin](06-die-koenigin.md)
7. [Zusehen](07-zusehen.md)
8. [Was bringt das Modell?](08-was-bringt-das-modell.md)

**Anhang**

- A · [Die Planke und der Fluss](09-anhang-die-planke.md)
- B · [Dasselbe Spiel ohne Cloud](10-anhang-b-ohne-cloud.md)

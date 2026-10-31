"""Writes English copies of the German diagrams into tutorial/bilder/en.

    python3 tools/translate_svg.py && uv run python tools/svg_to_png.py

Every German text in a diagram is looked up in EN below; a bare number like
0,37 just gets a decimal point. Anything with an umlaut or a decimal comma
left over is printed, so a new label in a German diagram cannot slip through
untranslated. `koordinaten.svg` was translated by hand and is not touched.
"""
import re
import sys
from pathlib import Path

EN = {
    # konfidenz
    "Eine echte Antwort: acht Optionen, acht Wahrscheinlichkeiten": "A real answer: eight options, eight probabilities",
    "dieser Abstand zählt": "this gap is what counts",
    "reiner Zufall: 1 / 8 = 0,125": "pure chance: 1 / 8 = 0.125",
    "Konfidenz = (8 × 0,37 − 1) ÷ 7 = 0,29": "confidence = (8 × 0.37 − 1) ÷ 7 = 0.29",
    "Allgemein: (Anzahl Optionen × höchste Wahrscheinlichkeit − 1) ÷ (Anzahl − 1).": "In general: (number of options × highest probability − 1) ÷ (number − 1).",
    "Gleichverteilt ergibt 0, alles auf einer Option ergibt 1.": "An even spread gives 0, everything on one option gives 1.",
    # optionen
    "Mitten auf dem Brett": "In the middle of the board",
    "8 Optionen": "8 options",
    "Am oberen Rand": "At the top edge",
    "Rand des Bretts — hier gibt es keine Felder": "edge of the board — there are no squares here",
    "5 Optionen": "5 options",
    "Was übrig bleibt, wird zu `criteria` — nur daraus wählt das Modell.": "What is left becomes `criteria` — the model chooses only from that.",
    "Eine Antwort, die es nicht gibt, stand nie zur Wahl.": "An answer that does not exist was never on offer.",
    # richtungen
    "Der Name ist": "The name is",
    "fürs Modell, das": "for the model, the",
    "Zahlenpaar für": "pair of numbers for",
    "die Rechnung.": "the arithmetic.",
    "Norden ist (0, −1),": "North is (0, −1),",
    "weil y nach unten": "because y counts",
    "zählt.": "downwards.",
    "`DIRECTIONS` ist genau diese Tabelle: acht Namen, acht Versätze.": "`DIRECTIONS` is exactly this table: eight names, eight offsets.",
    # runde
    "Eine Runde": "One round",
    "Ein Bild des Bretts machen": "Take a picture of the board",
    "taken_cells() — welche Felder sind besetzt": "taken_cells() — which squares are taken",
    "Ein einziger Stand,": "One single state,",
    "gegen den alle acht entscheiden.": "against which all eight decide.",
    "Ameise 1": "Ant 1",
    "Ameise 2": "Ant 2",
    "Ameise 8": "Ant 8",
    "freie Wege": "free ways",
    "Jede Frage enthält nur,": "Each question holds only",
    "was diese eine Ameise angeht.": "what concerns this one ant.",
    "asyncio.gather — alle acht Anfragen gleichzeitig": "asyncio.gather — all eight requests at once",
    "rund 0,6 Sekunden für die ganze Runde": "about 0.6 seconds for the whole round",
    "Nacheinander wären es vier —": "One after the other it would be four —",
    "eine Runde, die niemand ansieht.": "a round nobody watches.",
    "Antworten ausführen, eine nach der anderen": "Carry out the answers, one after the other",
    "jetzt ändert sich das Brett bei jedem Schritt": "now the board changes with every step",
    "Zielfeld": "target",
    "noch frei?": "still free?",
    "Zwei Ameisen können dasselbe": "Two ants may have chosen",
    "Feld gewählt haben — beide": "the same square — both",
    "gegen das Bild von vorhin.": "against the earlier picture.",
    "nein": "no",
    "ja": "yes",
    "bleibt stehen": "stays put",
    "geht": "moves",
    "Runde + 1": "round + 1",
    "Eine Antwort ist": "An answer is",
    "ein Wunsch, kein Zug.": "a wish, not a move.",
    # schwelle
    "Die Konfidenzskala, und wo dieses Spiel den Schnitt macht": "The confidence scale, and where this game makes the cut",
    "verworfen": "discarded",
    "angenommen, knapp": "accepted, narrowly",
    "deutlich": "clear",
    "sicher": "sure",
    "MIN_CONFIDENCE = 0,22": "MIN_CONFIDENCE = 0.22",
    "Warum so niedrig?": "Why so low?",
    "Weil Konfidenz den Abstand zum Zufall misst, nicht die Wahrscheinlichkeit.": "Because confidence measures the distance from chance, not the probability.",
    "Bei acht Optionen ist reiner Zufall 1/8 = 0,125 je Option.": "With eight options, pure chance is 1/8 = 0.125 per option.",
    "Konfidenz 0,22 heißt: die gewählte Option liegt bei 0,32 — zweieinhalbmal Zufall.": "Confidence 0.22 means: the chosen option is at 0.32 — two and a half times chance.",
    "Die Dokumentation von TypeSafe rät zu 0,5 und für Riskantes zu 0,9. Das gilt": "TypeSafe's documentation advises 0.5, and 0.9 for anything risky. That holds",
    "für Entscheidungen mit Folgen. Was hier schiefgeht, ist ein verkehrter Schritt,": "for decisions with consequences. What goes wrong here is one wrong step,",
    "und der ist in der nächsten Runde korrigiert.": "and that is put right in the next round.",
    # sichtweite
    "VISION_RADIUS = 3 — was die Ameise in der Mitte wahrnimmt": "VISION_RADIUS = 3 — what the ant in the middle notices",
    "sieben mal sieben Felder — drei in jede Richtung": "seven by seven squares — three in every direction",
    "3 Felder": "3 cells",
    "2 Felder": "2 cells",
    "4 Felder": "4 cells",
    "— zu weit": "— too far",
    "Im Zustand steht dann:": "The state then says:",
    "Die Frucht vier Felder weiter": "The fruit four squares away",
    "kommt nicht vor. Für diese": "does not appear. For this",
    "Ameise gibt es sie nicht.": "ant it does not exist.",
    "Gemessen wird in Schritten,": "Distance is counted in steps,",
    "nicht in Luftlinie: schräg ist": "not as the crow flies: diagonal",
    "genauso weit wie gerade.": "is as far as straight.",
    "Darum ist das Sichtfeld ein": "That is why the field of vision",
    "Quadrat und kein Kreis.": "is a square and not a circle.",
}

bilder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "tutorial" / "bilder"
for n in ["konfidenz", "optionen", "richtungen", "runde", "schwelle", "sichtweite"]:
    s = (bilder / f"{n}.svg").read_text(encoding="utf-8")

    def swap(m: re.Match) -> str:
        raw = m.group(1)
        text = raw.strip()
        if text in EN:
            new = EN[text]
        elif re.fullmatch(r"[\d,]+", text):
            new = text.replace(",", ".")
        else:
            return m.group(0)
        return ">" + raw.replace(text, new) + "<"

    out = re.sub(r">([^<]+)<", swap, s)
    left = [t.strip() for t in re.findall(r">([^<]+)<", re.sub(r"<!--.*?-->", "", out, flags=re.S))
            if re.search(r"[äöüßÄÖÜ]|\d,\d", t)]
    (bilder / "en" / f"{n}.svg").write_text(out, encoding="utf-8")
    print(n, "left untranslated:", left)

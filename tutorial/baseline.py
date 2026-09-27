"""Wie lange braucht der Zufall für fünf Früchte?

Dieselben Regeln wie `app.py` nach Schritt 4, nur ohne Streamlit und ohne
Zeichnen — damit sich zwanzig Durchläufe in einer Sekunde rechnen statt in
zweitausend Klicks.

Die Zahl aus Kapitel 4 kommt hierher. Nach Schritt 6 lohnt es sich, sie neu zu
messen und zu vergleichen.

    python3 tutorial/baseline.py
"""
import json, random, statistics

L = json.load(open('/Users/monikagerhard25/Desktop/git/python-streamlit-jev-ant/level1.json'))
D = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
N = L["nest"]

def in_nest(x,y): return N["x"] <= x < N["x"]+N["size"] and N["y"] <= y < N["y"]+N["size"]

def run(limit=20000):
    ants = [{"x": N["x"]+i%N["size"], "y": N["y"]+i//N["size"], "c": False} for i in range(L["ants"])]
    fruit = {tuple(c) for c in L["fruit"]}
    stores = 0
    for rnd in range(1, limit+1):
        taken = {(a["x"],a["y"]) for a in ants} | fruit
        for a in ants:
            ways = [(dx,dy) for dx,dy in D
                    if 0 <= a["x"]+dx < L["columns"] and 0 <= a["y"]+dy < L["rows"]
                    and (a["x"]+dx, a["y"]+dy) not in taken]
            if ways:
                dx,dy = random.choice(ways)
                taken.discard((a["x"],a["y"])); a["x"]+=dx; a["y"]+=dy; taken.add((a["x"],a["y"]))
            if a["c"]:
                if in_nest(a["x"],a["y"]):
                    a["c"] = False; stores += 1
                    if stores >= L["target"]: return rnd
            else:
                for dx,dy in D:
                    cell = (a["x"]+dx, a["y"]+dy)
                    if cell in fruit:
                        fruit.discard(cell); taken.discard(cell); a["c"] = True; break
        if not fruit and not any(a["c"] for a in ants):
            return None  # nichts mehr zu holen
    return limit

# Zwanzig Läufe reichen nicht: der Median schwankte zwischen zwei Messungen um
# vierzig Runden. Zweihundert sind in einer Sekunde gerechnet und stehen still.
RUNS = 200

results = sorted(r for r in (run() for _ in range(RUNS)) if isinstance(r, int))
print(f"{len(results)} von {RUNS} Läufen haben fünf Früchte heimgebracht")
print(f"Median   {statistics.median(results):.0f} Runden")
print(f"Mittel   {statistics.mean(results):.0f} Runden")
print(f"Spanne   {results[0]} bis {results[-1]}")
print(f"Mitte 80% {results[len(results)//10]} bis {results[-len(results)//10]}")

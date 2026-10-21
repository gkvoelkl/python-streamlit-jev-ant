"""How long does chance take for five fruits?

The same rules as the dice in `app.py`, without Streamlit and without drawing,
so that two hundred runs take a second instead of thousands of clicks. No trail
either: the dice could not read one anyway.

    python3 tutorial/baseline.py
"""
import json, random, statistics
from pathlib import Path

L = json.loads((Path(__file__).resolve().parent.parent / "level1.json").read_text(encoding="utf-8"))
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
            return None  # nothing left to fetch
    return limit

# Twenty runs are not enough: the median moved by forty rounds between two
# measurements. Two hundred take a second and hold still.
RUNS = 200

results = sorted(r for r in (run() for _ in range(RUNS)) if isinstance(r, int))
print(f"{len(results)} of {RUNS} runs brought five fruits home")
print(f"median    {statistics.median(results):.0f} rounds")
print(f"mean      {statistics.mean(results):.0f} rounds")
print(f"range     {results[0]} to {results[-1]}")
print(f"middle 80% {results[len(results)//10]} to {results[-len(results)//10]}")

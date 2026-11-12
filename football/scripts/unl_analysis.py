"""UEFA national-team games before and after the Nations League (first played Sept 2018).
Input: martj42/international_results results.csv. Output: football/data/unl/unl_matches.json"""
import csv, json, collections, sys
D = sys.argv[1] if len(sys.argv) > 1 else "football/data/unl"
rows = list(csv.DictReader(open(D + "/results.csv", encoding="utf-8")))
uefa = {t for r in rows if r["tournament"] == "UEFA Nations League" for t in (r["home_team"], r["away_team"])}
print("UEFA teams:", len(uefa))
def kind(t):
    if t == "Friendly": return "friendly"
    if t == "UEFA Nations League": return "nations_league"
    if t in ("UEFA Euro qualification", "FIFA World Cup qualification"): return "qualifier"
    if t in ("UEFA Euro", "FIFA World Cup"): return "tournament"
    return "other"
per_year = collections.defaultdict(lambda: collections.Counter())
margin = collections.defaultdict(list)
team_games = collections.defaultdict(collections.Counter)
for r in rows:
    y = int(r["date"][:4])
    if y < 2010 or y > 2025: continue
    h, a = r["home_team"], r["away_team"]
    hu, au = h in uefa, a in uefa
    if not (hu or au): continue
    k = kind(r["tournament"])
    for t in (h, a):
        if t in uefa: team_games[y][k] += 1
    if hu and au:
        per_year[y][k] += 1
        if k in ("friendly", "nations_league", "qualifier"):
            era = "before" if y <= 2017 else "after" if y >= 2019 else None
            if era: margin[(k, era)].append(abs(int(r["home_score"]) - int(r["away_score"])))
years = list(range(2010, 2026))
out = dict(teams=len(uefa), years=years,
  uefa_v_uefa={k: [per_year[y][k] for y in years] for k in ("friendly", "nations_league", "qualifier", "tournament")},
  per_team={k: [round(team_games[y][k] / len(uefa), 2) for y in years] for k in ("friendly", "nations_league", "qualifier", "tournament", "other")},
  margins={f"{k}_{e}": dict(n=len(v), avg=round(sum(v)/len(v), 2), blowout=round(100*sum(x >= 3 for x in v)/len(v), 1), close=round(100*sum(x <= 1 for x in v)/len(v), 1)) for (k, e), v in margin.items()})
out["per_team_total"] = [round(sum(out["per_team"][k][i] for k in out["per_team"]), 2) for i in range(len(years))]
json.dump(out, open(D + "/unl_matches.json", "w"), indent=1)
for k, v in out["uefa_v_uefa"].items(): print(k, v)
for k, v in out["per_team"].items(): print("per team", k, v)
print("total", out["per_team_total"])
for k, v in sorted(out["margins"].items()): print(k, v)

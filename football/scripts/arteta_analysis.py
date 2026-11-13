"""Arteta's Arsenal vs Guardiola's City, season by season, from every Premier League result.
Input: football/data/city115/season-*.csv. Output: football/data/arteta/seasons.json"""
import csv, glob, json, collections
D = "football/data/city115"
out = []
for f in sorted(glob.glob(D + "/season-*.csv")):
    code = f.split("season-")[1][:4]; y = 2000 + int(code[:2])
    if y < 2016: continue
    rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    pts = collections.Counter(); gd = collections.Counter()
    st = {t: collections.Counter() for t in ("Arsenal", "Man City")}
    for r in rows:
        h, a, hg, ag = r["HomeTeam"], r["AwayTeam"], int(r["FTHG"]), int(r["FTAG"])
        for t, gf, ga in ((h, hg, ag), (a, ag, hg)):
            pts[t] += 3 if gf > ga else 1 if gf == ga else 0; gd[t] += gf - ga
            if t in st:
                s = st[t]; s["p"] += 1; s["gf"] += gf; s["ga"] += ga; s["cs"] += ga == 0
                s["w"] += gf > ga; s["one"] += gf - ga == 1; s["big"] += gf - ga >= 3
                s["pts"] += 3 if gf > ga else 1 if gf == ga else 0
        if {h, a} == {"Arsenal", "Man City"}:
            pass
    table = sorted(pts, key=lambda t: (-pts[t], -gd[t]))
    for t, s in st.items():
        out.append(dict(season=f"{y}/{str(y+1)[2:]}", y=y, team=t, pos=table.index(t) + 1, **s))
json.dump(out, open("football/data/arteta/seasons.json", "w"), indent=1)
for o in out: print(o["season"], o["team"], o["pos"], o["pts"], o["gf"], o["ga"], "cs", o["cs"], "1-goal wins", o["one"], "of", o["w"], "3+", o["big"])

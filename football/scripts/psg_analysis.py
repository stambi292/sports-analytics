"""PSG in Ligue 1, 2010/11-2025/26, from every result (football-data.co.uk via datasets/football-datasets).
Output: football/data/psg/psg_seasons.json"""
import csv, glob, json, collections
out = []
for f in sorted(glob.glob("football/data/psg/ligue1-*.csv")):
    code = f.split("ligue1-")[1][:4]; y = 2000 + int(code[:2])
    rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    pts = collections.Counter(); gd = collections.Counter(); s = collections.Counter()
    for r in rows:
        if not r.get("FTHG"): continue
        h, a, hg, ag = r["HomeTeam"], r["AwayTeam"], int(r["FTHG"]), int(r["FTAG"])
        for t, gf, ga, sf, sa in ((h, hg, ag, r.get("HS"), r.get("AS")), (a, ag, hg, r.get("AS"), r.get("HS"))):
            pts[t] += 3 if gf > ga else 1 if gf == ga else 0; gd[t] += gf - ga
            if t == "Paris SG":
                s["p"] += 1; s["gf"] += gf; s["ga"] += ga; s["w"] += gf > ga; s["l"] += gf < ga
                if sf and sa: s["sf"] += int(sf); s["sa"] += int(sa); s["sg"] += 1
    table = sorted(pts, key=lambda t: (-pts[t], -gd[t]))
    second = table[1] if table[0] == "Paris SG" else table[0]
    out.append(dict(season=f"{y}/{str(y+1)[2:]}", y=y, pos=table.index("Paris SG") + 1, pts=pts["Paris SG"], margin=pts["Paris SG"] - pts[second],
                    p=s["p"], gf=s["gf"], ga=s["ga"], w=s["w"], l=s["l"], shot_share=round(100 * s["sf"] / (s["sf"] + s["sa"]), 1) if s["sg"] else None))
json.dump(out, open("football/data/psg/psg_seasons.json", "w"), indent=1)
for o in out: print(o)

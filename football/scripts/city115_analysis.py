"""Man City and the 115 charges: final tables 2009/10-2024/25 from match results,
and how many points City would have had to lose to change each outcome."""
import csv, json, glob, collections, sys
D = sys.argv[1] if len(sys.argv) > 1 else "football/data/city115"

def table(path):
    pts, gd, gf, pl = (collections.Counter() for _ in range(4))
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        if not r.get("FTHG"): continue
        h, a, g1, g2 = r["HomeTeam"], r["AwayTeam"], int(r["FTHG"]), int(r["FTAG"])
        for t, f, ag in ((h, g1, g2), (a, g2, g1)):
            pl[t] += 1; gf[t] += f; gd[t] += f - ag
            pts[t] += 3 if f > ag else 1 if f == ag else 0
    rows = [dict(team=t, p=pl[t], pts=pts[t], gd=gd[t], gf=gf[t]) for t in pts]
    rows.sort(key=lambda r: (-r["pts"], -r["gd"], -r["gf"]))
    return rows

def rank_after(rows, team, d):
    me = next(r for r in rows if r["team"] == team)
    key = lambda r: (-(r["pts"] - (d if r is me else 0)), -r["gd"], -r["gf"])
    return sorted(rows, key=key).index(me) + 1

seasons = []
for f in sorted(glob.glob(D + "/season-*.csv"), key=lambda f: ("1" if f[-8] == "9" and f[-8:-6] == "99" else "2") + f):
    code = f.split("season-")[1][:4]
    y = 2000 + int(code[:2]); label = f"{y}/{str(y+1)[2:]}"
    rows = table(f)
    if len(rows) != 20 or any(r["p"] != 38 for r in rows): print("incomplete", label); continue
    city = next(r for r in rows if r["team"] == "Man City")
    pos = rows.index(city) + 1
    def need(target):  # smallest deduction that pushes City below `target` position
        if pos > target: return 0
        d = 0
        while rank_after(rows, "Man City", d) <= target: d += 1
        return d
    s = dict(season=label, y=y, pos=pos, pts=city["pts"], gd=city["gd"],
             champion=rows[0]["team"], runner_up=rows[1]["team"], second_pts=rows[1]["pts"],
             lose_title=need(1) if pos == 1 else None, out_top4=need(4), relegated=need(17),
             new_champion=(sorted([r for r in rows if r["team"] != "Man City"], key=lambda r: (-r["pts"], -r["gd"], -r["gf"]))[0]["team"] if pos == 1 else None),
             in_charge_period=y <= 2017)
    seasons.append(s)
    print(s)
json.dump(seasons, open(D + "/city_seasons.json", "w"), indent=1)

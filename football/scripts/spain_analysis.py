"""Why Spain are the best: Elo ratings for every national team from every international result
(eloratings.net method), plus Spain's runs, records against the best, and tournament knockouts.
Input: football/data/spain/results.csv (martj42) + extra_results.csv (results after the dataset ends)."""
import csv, json, collections, math, sys, datetime
D = sys.argv[1] if len(sys.argv) > 1 else "football/data/spain"
rows = list(csv.DictReader(open(D + "/results.csv", encoding="utf-8"))) + list(csv.DictReader(open(D + "/extra_results.csv")))
rows = [r for r in rows if r["home_score"] not in ("", "NA")]
rows.sort(key=lambda r: r["date"])

def K(t):
    if t == "FIFA World Cup": return 60
    if t in ("UEFA Euro", "Copa América", "African Cup of Nations", "AFC Asian Cup", "Gold Cup", "Confederations Cup"): return 50
    if "qualification" in t or "Nations League" in t: return 40
    if t == "Friendly": return 20
    return 30
elo = collections.defaultdict(lambda: 1500.0)
last_played = {}
spain_series = []          # (date, rating, rank among active teams)
peers = ["Spain", "Argentina", "France", "Brazil", "England", "Germany", "Portugal", "Netherlands", "Italy"]
peer_series = {p: [] for p in peers}
days_no1 = collections.Counter(); days08 = collections.Counter(); top_log = []; prev_date = None; prev_top = None
vs_top = collections.defaultdict(lambda: [0, 0, 0])   # Spain record vs teams then in Elo top 10, by era
def era(y): return "2008–12" if 2008 <= y <= 2012 else "2013–21" if 2013 <= y <= 2021 else "2022–26" if y >= 2022 else None
for r in rows:
    d = r["date"]; y = int(d[:4]); h, a = r["home_team"], r["away_team"]; hs, as_ = int(r["home_score"]), int(r["away_score"])
    # days at number one (among teams active in the last 4 years), counted from 1990
    if y >= 1990 and d != prev_date:
        cutoff = str(y - 4) + d[4:]
        active = {t: v for t, v in elo.items() if last_played.get(t, "") >= cutoff}
        top = max(active, key=active.get) if active else None
        if prev_date and prev_top:
            nd = (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(prev_date)).days
            days_no1[prev_top] += nd
            if y >= 2008: days08[prev_top] += nd
        if top != prev_top: top_log.append((d, top))
        prev_top = top; prev_date = d
    if "Spain" in (h, a) and era(y):
        opp = a if h == "Spain" else h
        cutoff = str(y - 4) + d[4:]
        ranked = sorted((t for t in elo if last_played.get(t, "") >= cutoff), key=lambda t: -elo[t])
        if opp in ranked[:10]:
            f, g = (hs, as_) if h == "Spain" else (as_, hs)
            vs_top[era(y)][0 if f > g else 1 if f == g else 2] += 1
    dr = elo[h] - elo[a] + (0 if r["neutral"] == "TRUE" else 100)
    we = 1 / (10 ** (-dr / 400) + 1)
    w = 1 if hs > as_ else 0.5 if hs == as_ else 0
    gd = abs(hs - as_); gm = 1 if gd <= 1 else 1.5 if gd == 2 else (11 + gd) / 8
    ch = K(r["tournament"]) * gm * (w - we)
    elo[h] += ch; elo[a] -= ch; last_played[h] = d; last_played[a] = d
    if y >= 1990 and ("Spain" in (h, a) or h in peers or a in peers):
        for p in peers:
            if p in (h, a): peer_series[p].append((d, round(elo[p])))
end = rows[-1]["date"]
days_no1[prev_top] += 1
cut = str(int(end[:4]) - 4) + end[4:]
final = sorted(((t, round(v)) for t, v in elo.items() if last_played.get(t, "") >= cut), key=lambda x: -x[1])[:10]
# yearly end-of-year rating for peers (for the chart)
yearly = {p: {} for p in peers}
for p, s in peer_series.items():
    for dd, v in s: yearly[p][int(dd[:4])] = v
years = list(range(1990, int(end[:4]) + 1))
yr = {p: [yearly[p].get(yy) for yy in years] for p in peers}
for p in peers:   # carry forward years without games
    for i in range(1, len(years)):
        if yr[p][i] is None: yr[p][i] = yr[p][i - 1]
peak = {p: max(v for _, v in peer_series[p]) for p in peers}
since08 = {t: d for t, d in days_no1.items()}
out = dict(end=end, final_top10=final, years=years, yearly=yr, peak=peak,
           days_no1_since2008=sorted(days08.items(), key=lambda x: -x[1])[:6], no1_since=top_log[-1],
           days_no1_since1990=sorted(days_no1.items(), key=lambda x: -x[1])[:8], vs_top10=dict(vs_top))
json.dump(out, open(D + "/spain_elo.json", "w"), indent=1)
print("top10 now", final)
print("days at #1 since 1990", out["days_no1_since1990"])
print("since 2008", out["days_no1_since2008"], "current #1 since", out["no1_since"])
print("peaks", sorted(peak.items(), key=lambda x: -x[1]))
print("Spain vs top-10", dict(vs_top))

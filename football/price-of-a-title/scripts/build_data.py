"""Combine UEFA wage figures with final league tables -> data/title_cost.json.

Wages (EUR m) were read from the club wage charts in UEFA's
"The European Club Finance and Investment Landscape" reports:
  FY2023: edition with 2023 data (p.29)   FY2024/FY2025: 2025 edition (p.35), 2024 edition (p.31)
Financial year N is mapped to the season ending in N (most top clubs have a summer year end).
"""
import json, glob, collections, sys
D = "data"

# season -> {UEFA club name: wages EUR m}
WAGES = {
 "2022-23": {"FC Barcelona": 639, "Paris Saint-Germain": 617, "Manchester City": 554, "Real Madrid": 453,
             "Liverpool": 429, "FC Bayern München": 416, "Manchester United": 381, "Tottenham Hotspur": 289,
             "Juventus": 283, "Arsenal": 270, "Atlético de Madrid": 245, "Borussia Dortmund": 236,
             "Inter": 230, "Aston Villa": 223, "Newcastle United": 215, "RB Leipzig": 192, "AS Roma": 181},
 "2023-24": {"Paris Saint-Germain": 658, "Manchester City": 554, "Real Madrid": 503, "FC Barcelona": 478,
             "Liverpool": 449, "FC Bayern München": 430, "Manchester United": 429, "Chelsea": 395, "Arsenal": 381,
             "Aston Villa": 293, "Borussia Dortmund": 269, "Atlético de Madrid": 268, "Juventus": 264,
             "Tottenham Hotspur": 260, "Newcastle United": 255, "Inter": 232, "RB Leipzig": 202, "AS Roma": 202,
             "Nottingham Forest": 194, "Bayer 04 Leverkusen": 192, "AC Milan": 189, "West Ham United": 187,
             "Everton": 182, "Fulham": 180, "Olympique Lyonnais": 162},
 "2024-25": {"Manchester City": 557, "FC Barcelona": 551, "Paris Saint-Germain": 551, "Real Madrid": 514,
             "Liverpool": 509, "Chelsea": 445, "FC Bayern München": 443, "Manchester United": 416, "Arsenal": 413,
             "Tottenham Hotspur": 318, "Aston Villa": 309, "Newcastle United": 289, "Atlético de Madrid": 280,
             "Borussia Dortmund": 268, "Inter": 260, "Juventus": 245, "Bayer 04 Leverkusen": 209,
             "Nottingham Forest": 192, "AC Milan": 189, "Olympique Lyonnais": 178},
}
# lowest wage bill in each UEFA list: a club not listed paid less than this
LIST_FLOOR = {"2022-23": 181, "2023-24": 157, "2024-25": 178}

# UEFA name -> (league file, openfootball names, display name)
CLUBS = {
 "Manchester City": ("en.1", ["Manchester City FC"], "Man City"), "Liverpool": ("en.1", ["Liverpool FC"], "Liverpool"),
 "Manchester United": ("en.1", ["Manchester United FC"], "Man United"), "Chelsea": ("en.1", ["Chelsea FC"], "Chelsea"),
 "Arsenal": ("en.1", ["Arsenal FC"], "Arsenal"), "Tottenham Hotspur": ("en.1", ["Tottenham Hotspur FC"], "Tottenham"),
 "Aston Villa": ("en.1", ["Aston Villa FC"], "Aston Villa"), "Newcastle United": ("en.1", ["Newcastle United FC"], "Newcastle"),
 "Nottingham Forest": ("en.1", ["Nottingham Forest FC"], "Nottingham Forest"), "West Ham United": ("en.1", ["West Ham United FC"], "West Ham"),
 "Everton": ("en.1", ["Everton FC"], "Everton"), "Fulham": ("en.1", ["Fulham FC"], "Fulham"),
 "FC Bayern München": ("de.1", ["FC Bayern München"], "Bayern Munich"), "Borussia Dortmund": ("de.1", ["Borussia Dortmund"], "Dortmund"),
 "RB Leipzig": ("de.1", ["RB Leipzig"], "RB Leipzig"), "Bayer 04 Leverkusen": ("de.1", ["Bayer 04 Leverkusen"], "Leverkusen"),
 "FC Barcelona": ("es.1", ["FC Barcelona"], "Barcelona"), "Real Madrid": ("es.1", ["Real Madrid CF"], "Real Madrid"),
 "Atlético de Madrid": ("es.1", ["Club Atlético de Madrid"], "Atlético Madrid"),
 "Juventus": ("it.1", ["Juventus FC"], "Juventus"), "Inter": ("it.1", ["FC Internazionale Milano"], "Inter"),
 "AC Milan": ("it.1", ["AC Milan"], "AC Milan"), "AS Roma": ("it.1", ["AS Roma"], "Roma"),
 "Paris Saint-Germain": ("fr.1", ["Paris Saint-Germain", "Paris Saint-Germain FC"], "PSG"),
 "Olympique Lyonnais": ("fr.1", ["Olympique Lyonnais"], "Lyon"),
}
LEAGUE = {"en.1": "Premier League", "de.1": "Bundesliga", "es.1": "La Liga", "it.1": "Serie A", "fr.1": "Ligue 1"}
# official adjustments not in the results data: points deductions, and two seasons incomplete in the source
DEDUCT = {("2022-23", "Juventus FC"): 10, ("2023-24", "Everton FC"): 8, ("2023-24", "Nottingham Forest FC"): 4}
OFFICIAL = {  # final tables (sportsmole / NBC Sports) where the source file is incomplete
 ("2024-25", "it.1"): {"SSC Napoli": 82, "FC Internazionale Milano": 81, "Atalanta BC": 74, "Juventus FC": 70, "AS Roma": 69,
                       "ACF Fiorentina": 65, "SS Lazio": 65, "AC Milan": 63, "Bologna FC 1909": 62},
 ("2024-25", "es.1"): {"FC Barcelona": 88, "Real Madrid CF": 84, "Club Atlético de Madrid": 76, "Athletic Club": 70, "Villarreal CF": 70},
}

def table(season, lg):
    d = json.load(open(f"{D}/{season}-{lg}.json"))
    pts, gd, gp = collections.Counter(), collections.Counter(), collections.Counter()
    for x in d["matches"]:
        if not (isinstance(x.get("score"), dict) and x["score"].get("ft")): continue
        a, b = x["score"]["ft"]; h, w = x["team1"], x["team2"]
        pts[h] += 3 if a > b else 1 if a == b else 0; pts[w] += 3 if b > a else 1 if a == b else 0
        gd[h] += a - b; gd[w] += b - a; gp[h] += 1; gp[w] += 1
    for (s, t), n in DEDUCT.items():
        if s == season and t in pts: pts[t] -= n
    off = OFFICIAL.get((season, lg))
    if off:
        for t, p in off.items(): pts[t] = p
        # order: official top first, then everyone else by points
    teams = sorted(pts, key=lambda t: (-pts[t], -gd[t]))
    if off:
        teams = list(off) + [t for t in teams if t not in off]
    return {t: (i + 1, pts[t]) for i, t in enumerate(teams)}, teams[0], len(teams)

rows, champions = [], {}
for season, w in WAGES.items():
    for lg in LEAGUE:
        tab, champ, n = table(season, lg)
        champions[(season, lg)] = (champ, tab[champ][1])
    for club, wage in w.items():
        lg, names, disp = CLUBS[club]
        tab, champ, n = table(season, lg)
        name = next(nm for nm in names if nm in tab)
        pos, pts = tab[name]
        rows.append(dict(season=season.replace("-", "/"), league=LEAGUE[lg], club=disp, wages=wage, points=pts,
                         position=pos, teams=n, champion=(name == champ), cost_per_point=round(wage / pts, 2)))
champ_list = []
for (season, lg), (champ, pts) in sorted(champions.items()):
    listed = any(r["champion"] and r["league"] == LEAGUE[lg] and r["season"] == season.replace("-", "/") for r in rows)
    champ_list.append(dict(season=season.replace("-", "/"), league=LEAGUE[lg], club=champ, points=pts, in_uefa_list=listed,
                           below_eur_m=None if listed else LIST_FLOOR[season]))
json.dump(dict(rows=rows, champions=champ_list, list_floor=LIST_FLOOR), open(f"{D}/title_cost.json", "w"), indent=1, ensure_ascii=False)
for c in champ_list: print(c)
print(len(rows), "club-seasons")

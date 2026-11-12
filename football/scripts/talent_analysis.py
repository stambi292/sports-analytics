"""Where did Germany's talent go? Builds football/data/talent/talent_web.json.

Raw inputs (not stored in the repo, too large):
- FIFA 15-22 male player ratings (sofifa scrape) from github.com/eddwebster/football_analytics/data/fifa/raw/
- EA FC 24 club squads for the Big-5 leagues from github.com/fpessolano/FantasyFootball/assets/data/
- World Cup squads, players, goals and team appearances from github.com/jfjelstul/worldcup (data-csv)
Usage: python3 talent_analysis.py <dir with fifa_all.parquet, squads.csv, players.csv, goals.csv, ta.csv>
FIFA ratings are a game's judgement, so they are used as a consistent proxy for quality, not as truth.
"""
import json, sys, pathlib
import pandas as pd

raw = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parents[1] / 'data' / 'talent'
out.mkdir(parents=True, exist_ok=True)

# ---------- FIFA ratings, Big-5 top divisions ----------
A = pd.read_parquet(raw / 'fifa_all.parquet')
lg = {'English Premier League': 'EPL', 'Premier League': 'EPL', 'Spain Primera Division': 'LaLiga', 'La Liga': 'LaLiga',
      'Primera Division': 'LaLiga', 'German 1. Bundesliga': 'BL', 'Bundesliga': 'BL', 'Italian Serie A': 'SA', 'Serie A': 'SA',
      'French Ligue 1': 'L1', 'Ligue 1': 'L1'}
A['lg'] = A.league_name.map(lg)
B = A[A.lg.notna()].copy()
POS = {'GK': 'GK', 'CB': 'CB', 'LB': 'FB', 'RB': 'FB', 'LWB': 'FB', 'RWB': 'FB', 'CDM': 'CM', 'CM': 'CM', 'CAM': 'AM/W',
       'LM': 'AM/W', 'RM': 'AM/W', 'LW': 'AM/W', 'RW': 'AM/W', 'ST': 'ST', 'CF': 'ST'}
B['pos'] = B.player_positions.map(lambda p: POS.get(str(p).split(',')[0].strip(), 'AM/W'))
B['starter'] = B.club_position.notna() & ~B.club_position.isin(['SUB', 'RES'])
season = {v: f"20{v-1}/{v}" for v in B.ver.unique()}
N = ['Germany', 'Spain', 'France', 'England']
vers = sorted(B.ver.unique())

def counts(mask):
    t = B[mask].groupby(['ver', 'nationality_name']).size().unstack(fill_value=0)
    return {n: [int(t.loc[v, n]) if (v in t.index and n in t.columns) else 0 for v in vers] for n in N}

elite = counts(B.overall >= 80)
young = counts((B.age <= 21) & (B.potential >= 83))
elite_pos = {n: {p: [int(((B.ver == v) & (B.nationality_name == n) & (B.overall >= 80) & (B.pos == p)).sum()) for v in vers]
                 for p in ['GK', 'CB', 'FB', 'CM', 'AM/W', 'ST']} for n in N}
home = {'BL': 'Germany', 'LaLiga': 'Spain', 'L1': 'France', 'EPL': 'England'}
league = {}
for l, n in home.items():
    s = B[B.lg == l]
    league[l] = dict(nation=n,
        startersLocal=[round(float((s[(s.ver == v) & s.starter].nationality_name == n).mean() * 100), 1) for v in vers],
        u21LocalStartersPerClub=[round(float(((s.ver == v) & s.starter & (s.nationality_name == n) & (s.age <= 21)).sum() / s[s.ver == v].club_name.nunique()), 2) for v in vers])
# where Germany's best young players play (latest version)
yl = B[(B.ver == vers[-1]) & (B.nationality_name == 'Germany') & (B.age <= 23) & (B.overall >= 75)]
young_list = yl.sort_values('overall', ascending=False)[['short_name', 'age', 'pos', 'overall', 'potential', 'club_name', 'starter']].head(15)

# ---------- World Cups 1990-2026 ----------
ta = pd.read_csv(raw / 'ta.csv'); ta = ta[~ta.tournament_name.str.contains('Women')]
ta['yr'] = ta.tournament_id.str[3:].astype(int); ta = ta[ta.yr >= 1990]
sq = pd.read_csv(raw / 'squads.csv'); sq = sq[~sq.tournament_name.str.contains('Women')]
sq['yr'] = sq.tournament_id.str[3:].astype(int); sq = sq[sq.yr >= 1990]
pl = pd.read_csv(raw / 'players.csv')
sq = sq.merge(pl[['player_id', 'birth_date']], on='player_id', how='left')
sq['age'] = (pd.to_datetime(sq.yr.astype(str) + '-06-15') - pd.to_datetime(sq.birth_date, errors='coerce')).dt.days / 365.25
stage = {'final': 'Final', 'third-place match': 'Semi-final', 'semi-finals': 'Semi-final', 'quarter-finals': 'Quarter-final',
         'round of 16': 'Round of 16', 'group stage': 'Group stage', 'second group stage': 'Second round'}
rank = {'Winner': 6, 'Final': 5, 'Semi-final': 4, 'Quarter-final': 3, 'Round of 16': 2, 'Round of 32': 1.5, 'Second round': 2, 'Group stage': 1}

def wc(teams, winners):
    rows = []
    for yr, g in ta[ta.team_name.isin(teams)].groupby('yr'):
        st = stage.get(g.stage_name.iloc[-1], g.stage_name.iloc[-1])
        if yr in winners: st = 'Winner'
        s = sq[(sq.yr == yr) & sq.team_name.isin(teams)]
        rows.append(dict(yr=int(yr), stage=st, rank=rank[st], games=int(len(g)), gf=int(g.goals_for.sum()), ga=int(g.goals_against.sum()),
                         age=round(float(s.age.mean()), 1), u23=int((s.age < 24).sum())))
    return rows
ger = wc(['Germany', 'West Germany'], {1990, 2014})
ger.append(dict(yr=2026, stage='Round of 32', rank=1.5, games=4, gf=11, ga=5, age=27.5, u23=6))  # 2026 added by hand, see sources
esp = wc(['Spain'], {2010})
esp.append(dict(yr=2026, stage='Winner', rank=6, games=None, gf=None, ga=None, age=None, u23=None))

D = dict(seasons=[season[v] for v in vers], elite=elite, young=young, elitePos=elite_pos, league=league,
         youngList=young_list.to_dict('records'), wcGer=ger, wcEsp=esp)
(out / 'talent_web.json').write_text(json.dumps(D, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print(json.dumps({k: D[k] for k in ['seasons', 'young', 'elite']}))
print(young_list.to_string())
for r in ger: print(r)

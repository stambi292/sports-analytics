"""Build football/the-poacher/index.html: is Niclas Füllkrug's 2026/27 form real?

Sources (copied into football/data/poacher/):
- understat_extract.json: Understat season totals (goals, xG, shots, minutes) for Füllkrug since 2017/18,
  and 2025/26 Bundesliga forwards with 900+ minutes, via the public striker-explorer snapshot.
- statsbomb_fullkrug_shots.json: every Füllkrug shot in StatsBomb open data (World Cup 2022, Euro 2024,
  two Dortmund v Leverkusen games in 2023/24), with location, xG, outcome and body part.
- 2026/27 so far: 9 league goals in 656 minutes (VAVEL, ~10 Nov 2026). No public xG for this season yet.
- Career league goals and games per club: Wikipedia.
"""
import json, math, pathlib

root = pathlib.Path(__file__).resolve().parents[1]
src = root / 'data' / 'poacher'
U = json.loads((src / 'understat_extract.json').read_text())
SB = json.loads((src / 'statsbomb_fullkrug_shots.json').read_text())

# ---- Season by season (Understat) ----
seasons = []
for s, v in U['understat_history']['seasons'].items():
    team = 'Dortmund' if 'Dortmund' in v['team'] else v['team']
    seasons.append(dict(season=s.replace('-20', '/'), team=team, league=v['league'], abroad=v['league'] != 'Bundesliga',
                        mins=int(v['minutes']), goals=int(v['goals']), xg=round(v['xG'], 1), shots=int(v['shots']), npg=int(v['npg'])))
fk = next(p for p in U['understat_2025_26'] if p['id'] == 6098)
seasons.append(dict(season='2025/26', team='AC Milan + West Ham', league='Serie A / EPL', abroad=True, mins=fk['minutes'],
                    goals=fk['goals'], xg=round(fk['xG'], 1), shots=fk['shots'], npg=fk['npg']))
for s in seasons:
    s['xg90'] = round(s['xg'] * 90 / s['mins'], 2)
    s['g90'] = round(s['goals'] * 90 / s['mins'], 2)
    s['sh90'] = round(s['shots'] * 90 / s['mins'], 2)
    s['xgsh'] = round(s['xg'] / s['shots'], 3)
    s['diff'] = round(s['goals'] - s['xg'], 1)

de = [s for s in seasons if not s['abroad']]
ab = [s for s in seasons if s['abroad']]
def agg(rows):
    m = sum(r['mins'] for r in rows); g = sum(r['goals'] for r in rows); x = sum(r['xg'] for r in rows); sh = sum(r['shots'] for r in rows)
    return dict(mins=m, goals=g, xg=round(x, 1), shots=sh, g90=round(g * 90 / m, 2), xg90=round(x * 90 / m, 2),
                sh90=round(sh * 90 / m, 2), xgsh=round(x / sh, 3), ratio=round(g / x, 2))
germany, abroad = agg(de), agg(ab)

now = dict(goals=9, mins=656, games=8)
now['g90'] = round(now['goals'] * 90 / now['mins'], 2)
now['expected_at_career_rate'] = round(germany['xg90'] * now['mins'] / 90, 1)

# ---- Shot map (StatsBomb) ----
names = {'3895309': 'Dortmund 1–1 Leverkusen', '3895158': 'Leverkusen 1–1 Dortmund', '3942226': 'Spain 2–1 Germany (Euro 24)',
         '3930158': 'Germany 5–1 Scotland (Euro 24)', '3930176': 'Switzerland 1–1 Germany (Euro 24)', '3930168': 'Germany 2–0 Hungary (Euro 24)',
         '3940983': 'Germany 2–0 Denmark (Euro 24)', '3857292': 'Costa Rica 2–4 Germany (WC 22)', '3857263': 'Spain 1–1 Germany (WC 22)',
         '3857284': 'Germany 1–2 Japan (WC 22)'}
shots = []
for s in SB['shots']:
    shots.append(dict(x=s['x'], y=s['y'], xg=s['xg'], goal=s['out'] == 'Goal', body='Head' if s['body'] == 'Head' else 'Foot',
                      out=s['out'], game=names[s['match']], min=s['min']))
sb_mins = sum(SB['minutes'].values())
inbox = sum(1 for s in shots if s['x'] >= 102 and 18 <= s['y'] <= 62)
sixyd = sum(1 for s in shots if s['x'] >= 114 and 30 <= s['y'] <= 50)
heads = [s for s in shots if s['body'] == 'Head']
sb = dict(n=len(shots), goals=sum(s['goal'] for s in shots), xg=round(sum(s['xg'] for s in shots), 2), mins=sb_mins, games=len(SB['minutes']),
          inbox=inbox, sixyd=sixyd, heads=len(heads), headGoals=sum(s['goal'] for s in heads),
          g90=round(sum(s['goal'] for s in shots) * 90 / sb_mins, 2))

# ---- German forwards, 2025/26 Bundesliga (Understat) ----
german = {'Deniz Undav': 'VfB Stuttgart', 'Jonathan Burkardt': 'Frankfurt', 'Phillip Tietz': 'Augsburg / Mainz',
          'Serge Gnabry': 'Bayern', 'Karim Adeyemi': 'Dortmund'}
peers = []
for p in U['understat_2025_26']:
    if p['player_name'] in german:
        peers.append(dict(name=p['player_name'], team=german[p['player_name']], mins=p['minutes'], goals=p['goals'],
                          xg90=round(p['xG'] * 90 / p['minutes'], 2), g90=round(p['goals'] * 90 / p['minutes'], 2)))
peers.append(dict(name='Niclas Füllkrug', team='Bundesliga career, 2017–24', mins=germany['mins'], goals=germany['goals'],
                  xg90=germany['xg90'], g90=germany['g90'], me=True))
peers.sort(key=lambda r: -r['xg90'])

d = dict(seasons=seasons, germany=germany, abroad=abroad, now=now, shots=shots, sb=sb, peers=peers,
         clubs=[['Nürnberg', '2014–16', 17, 54, 'de'], ['Hannover 96', '2016–19', 21, 75, 'de'], ['Werder Bremen', '2019–23', 45, 90, 'de'],
                ['Dortmund', '2023–24', 12, 29, 'de'], ['West Ham', '2024–26', 3, 26, 'ab'], ['AC Milan', '2026', 1, 20, 'ab'],
                ['Werder Bremen', '2026/27', 9, 8, 'now']])

html = (root / 'scripts' / 'poacher_template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':'), ensure_ascii=False))
out = root / 'the-poacher'; out.mkdir(exist_ok=True)
(out / 'index.html').write_text(html)
(src / 'poacher_web.json').write_text(json.dumps(d, indent=1, ensure_ascii=False))
print(json.dumps(dict(germany=germany, abroad=abroad, now=now, sb=sb), ensure_ascii=False))
for s in seasons: print(s)
for p in peers: print(p)

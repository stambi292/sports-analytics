"""LALIGA kick-off times 2015/16 to 2026/27 (openfootball): who pays for late and weeknight slots."""
import json, glob, math, sys, pathlib
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from laliga_clubs import NAMES, COORDS
root = pathlib.Path(__file__).resolve().parents[1]
rows = []
for f in sorted(glob.glob(str(root / 'data' / 'es1-*.json'))):
    season = f[-12:-5]
    for m in json.load(open(f))['matches']:
        if m.get('time'):
            rows.append(dict(season=season, date=m['date'], time=m['time'], round=m['round'],
                             home=NAMES.get(m['team1'], m['team1']), away=NAMES.get(m['team2'], m['team2'])))
df = pd.DataFrame(rows)
df['dow'] = pd.to_datetime(df.date).dt.dayofweek
df['hour'] = df.time.str[:2].astype(int) + df.time.str[3:5].astype(int) / 60
def km(a, b):
    (la1, lo1), (la2, lo2) = COORDS[a], COORDS[b]; p = math.pi / 180
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2))
df['km'] = [round(km(h, a)) for h, a in zip(df.home, df.away)]
mw = df.groupby(['season', 'round']).dow.agg(lambda x: x.between(1, 3).mean() > .5).rename('midweek')
df = df.merge(mw.reset_index(), on=['season', 'round'])
df['late'] = df.hour >= 20.75
df['monfri'] = df.dow.isin([0, 4]) & ~df.midweek
df['tough'] = (df.km > 500) & (df.late | df.monfri)
seasons = sorted(df.season.unique())
trend = [{'season': s.replace('-', '/'), 'n': int(len(g)), 'late': round(g.late.mean() * 100, 1), 'monfri': int(g.monfri.sum()),
          'monfriPct': round(g.monfri.mean() * 100, 1), 'tough': int(g.tough.sum()), 'slots': int(g.time.nunique())}
         for s, g in df.groupby('season')]
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
def heat(g):
    t = g.groupby(['dow', 'time']).size()
    return [{'d': DAYS[d], 'time': tm, 'n': int(n)} for (d, tm), n in t.items()]
heats = {s.replace('-', '/'): heat(g) for s, g in df.groupby('season')}
recent = df[df.season.isin(['2021-22', '2022-23', '2023-24', '2024-25', '2025-26'])]
big = ['Real Madrid', 'Barcelona', 'Atlético Madrid']
clubs = recent.groupby('home').agg(n=('home', 'size'), monfri=('monfri', 'mean'), late=('late', 'mean'))
clubs = clubs[clubs.n >= 57].sort_values('monfri', ascending=False)
fair = [{'club': c, 'monfri': round(r.monfri * 100, 1), 'late': round(r.late * 100, 1), 'big': c in big} for c, r in clubs.iterrows()]
bm = recent.home.isin(big) | recent.away.isin(big)
last = df[df.season == '2025-26']
away = {}
for c, g in last.groupby('away'):
    g = g.sort_values('date')
    away[c] = {'km': int(g.km.sum()), 'tough': int(g.tough.sum()),
               'trips': [{'date': d, 'time': t, 'dow': DAYS[w], 'home': h, 'km': int(k), 'tough': bool(tg), 'late': bool(l), 'monfri': bool(mf)}
                         for d, t, w, h, k, tg, l, mf in zip(g.date, g.time, g.dow, g.home, g.km, g.tough, g.late, g.monfri)]}
res = {
    'matches': int(len(df)), 'seasons': len(seasons), 'trend': trend, 'heat': heats, 'fair': fair,
    'bigVsRest': {'bigMonfri': round(recent[bm].monfri.mean() * 100, 1), 'restMonfri': round(recent[~bm].monfri.mean() * 100, 1),
                  'bigLate': round(recent[bm].late.mean() * 100, 1), 'restLate': round(recent[~bm].late.mean() * 100, 1)},
    'distance': {'monfriMedian': int(recent[recent.monfri].km.median()), 'otherMedian': int(recent[~recent.monfri & ~recent.midweek].km.median())},
    'away': away,
    'last': {'late': int(last.late.sum()), 'monfri': int(last.monfri.sum()), 'tough': int(last.tough.sum()),
             'mon': int(((last.dow == 0) & ~last.midweek).sum()), 'fri': int(((last.dow == 4) & ~last.midweek).sum()), 'monLate': int(((last.dow == 0) & last.late & ~last.midweek).sum())},
}
(root / 'data' / 'laliga_kickoffs.json').write_text(json.dumps(res, ensure_ascii=False))
print(json.dumps({k: v for k, v in res.items() if k not in ('heat', 'away')}, ensure_ascii=False, indent=0)[:2500])

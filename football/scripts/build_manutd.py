"""Build football/does-the-pitch-matter/index.html.
Sources: football/data/manutd-money/accounts.json (club results releases, see _note);
football/data/city115/season-*.csv (every Premier League result) -> league finish per season."""
import csv, glob, json, pathlib, collections
root = pathlib.Path(__file__).resolve().parents[1]
D = json.loads((root / 'data/manutd-money/accounts.json').read_text())

def finish(path, team='Man United'):
    t = collections.defaultdict(lambda: [0, 0, 0])
    for r in csv.DictReader(open(path)):
        if not r.get('FTR'): continue
        for tm, gf, ga in ((r['HomeTeam'], int(r['FTHG']), int(r['FTAG'])), (r['AwayTeam'], int(r['FTAG']), int(r['FTHG']))):
            t[tm][0] += 3 if gf > ga else 1 if gf == ga else 0; t[tm][1] += gf - ga; t[tm][2] += gf
    tab = sorted(t, key=lambda k: (-t[k][0], -t[k][1], -t[k][2]))
    return tab.index(team) + 1, t[team][0]

for y in D['years']:
    a, b = y['season'][2:4], y['season'][5:7]
    y['pos'], y['pts'] = finish(root / f'data/city115/season-{a}{b}.csv')
Y = {y['fy']: y for y in D['years']}
c = D['cpi']
s = dict(
    com16=Y[2016]['com'], com26=Y[2026]['com'],
    com_nom=round((Y[2026]['com'] / Y[2016]['com'] - 1) * 100),
    prices=round((c['jun2026'] / c['jun2016'] - 1) * 100),
    com16_real=round(Y[2016]['com'] * c['jun2026'] / c['jun2016']),
    real=round((Y[2026]['com'] / (Y[2016]['com'] * c['jun2026'] / c['jun2016']) - 1) * 100),
    loss_years=sum(1 for y in D['years'] if y['fy'] >= 2020),
    loss_total=round(sum(-y['pl'] for y in D['years'] if y['fy'] >= 2020)),
    bro15=round((Y[2015]['bro'] / Y[2014]['bro'] - 1) * 100), bro25=round((Y[2025]['bro'] / Y[2024]['bro'] - 1) * 100),
    dom=round(D['swing']['domestic_bro'][1] - D['swing']['domestic_bro'][0], 1),
    spon_drop=round(Y[2023]['spon'] - Y[2026]['spon'], 1),
    wage_ratio=round(Y[2026]['wages'] / Y[2026]['tot'] * 100),
)
print(s)
html = (root / 'scripts/manutd_template.html').read_text().replace('/*__DATA__*/null', json.dumps(dict(D, s=s), ensure_ascii=False))
out = root / 'does-the-pitch-matter'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

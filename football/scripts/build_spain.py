"""Build football/why-spain/index.html: why Spain are the best national team in the world, in numbers.

Sources (football/data/spain/):
- results.csv: every international result to 6 Oct 2026 (martj42/international_results on GitHub);
  extra_results.csv: later results added by hand (Czech Republic 0-2 Spain, 12 Nov 2026, ESPN/beIN).
- spain_elo.json: Elo ratings made by spain_analysis.py (eloratings.net method).
"""
import csv, json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
src = root / 'data' / 'spain'
E = json.loads((src / 'spain_elo.json').read_text())
rows = list(csv.DictReader(open(src / 'results.csv', encoding='utf-8'))) + list(csv.DictReader(open(src / 'extra_results.csv')))
rows.sort(key=lambda r: r['date'])
def res(team, r):
    h = r['home_team'] == team; f = int(r['home_score'] if h else r['away_score']); a = int(r['away_score'] if h else r['home_score'])
    return f, a
def rec(team, y0, y1, filt=lambda r: True):
    w = d = l = gf = ga = 0
    for r in rows:
        y = int(r['date'][:4])
        if y0 <= y <= y1 and team in (r['home_team'], r['away_team']) and filt(r):
            f, a = res(team, r); gf += f; ga += a
            w += f > a; d += f == a; l += f < a
    n = w + d + l
    return dict(n=n, w=w, d=d, l=l, win=round(100 * w / n), ppg=round((3 * w + d) / n, 2), ga=round(ga / n, 2))
comp = lambda r: r['tournament'] != 'Friendly'
tour = lambda r: r['tournament'] in ('UEFA Euro', 'FIFA World Cup')
peers = ['Spain', 'England', 'Germany', 'Portugal', 'France', 'Argentina', 'Brazil', 'Italy']
peer_rec = sorted([dict(team=t, **rec(t, 2008, 2026, comp)) for t in peers], key=lambda x: -x['win'])
eras = [('2008–12', 2008, 2012), ('2013–21', 2013, 2021), ('2022–26', 2022, 2026)]
era_rows = [dict(era=e, all=rec('Spain', a, b), tour=rec('Spain', a, b, tour), top10=E['vs_top10'][e]) for e, a, b in eras]
# unbeaten runs
def runs(filt):
    run = 0; since = None
    for r in rows:
        if 'Spain' in (r['home_team'], r['away_team']) and filt(r):
            f, a = res('Spain', r)
            if f < a: run = 0; since = r
            else: run += 1
    return run, since['date'], since['home_team'] if since['home_team'] != 'Spain' else since['away_team']
comp_run = runs(comp); all_run = runs(lambda r: True)
data = dict(elo=E, peers=peer_rec, eras=era_rows, comp_run=comp_run, all_run=all_run, last_game='12 November 2026')
print(peer_rec[:3], era_rows, comp_run, all_run, sep='\n')
html = (root / 'scripts' / 'spain_template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
out = root / 'why-spain'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

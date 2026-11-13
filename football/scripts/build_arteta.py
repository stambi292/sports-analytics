"""Build football/peps-student/index.html: Arteta's Arsenal vs Guardiola's City.

Sources: football/data/city115/season-*.csv (Premier League results, football-data.co.uk) via arteta_analysis.py
-> football/data/arteta/seasons.json; set-piece figures from Opta Analyst (setpieces.json); 2026/27 table 12 Nov 2026.
"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
S = json.loads((root / 'data/arteta/seasons.json').read_text())
P = json.loads((root / 'data/arteta/setpieces.json').read_text())
def agg(team, years):
    xs = [s for s in S if s['team'] == team and s['y'] in years]
    t = {k: sum(x[k] for x in xs) for k in ('p', 'gf', 'ga', 'cs', 'w', 'one', 'big', 'pts')}
    return dict(seasons=len(xs), gf=round(t['gf'] / t['p'], 2), ga=round(t['ga'] / t['p'], 2), cs=round(100 * t['cs'] / t['p']),
                one=round(100 * t['one'] / t['w']), big=round(100 * t['big'] / t['w']), ppg=round(t['pts'] / t['p'], 2))
styles = dict(pep=agg('Man City', range(2017, 2022)), arteta=agg('Arsenal', range(2023, 2026)))
print(styles)
data = dict(seasons=S, sp=P, styles=styles)
html = (root / 'scripts/arteta_template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
out = root / 'peps-student'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

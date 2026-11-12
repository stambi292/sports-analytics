"""Build football/the-115/index.html: what could the 115 charges cost Manchester City?

Sources (football/data/city115/):
- season-XXXX.csv: Premier League results 2009/10-2025/26 (football-data.co.uk, via datasets/football-datasets on GitHub).
- city_seasons.json: made by city115_analysis.py from those results.
- facts.json: charge categories (Premier League, Feb 2023, as reported by SI/LBC), precedents (public rulings),
  and the 2026/27 table after 10 games (12 Nov 2026).
"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
src = root / 'data' / 'city115'
S = json.loads((src / 'city_seasons.json').read_text())
F = json.loads((src / 'facts.json').read_text())
titles = [s for s in S if s['pos'] == 1]
data = dict(seasons=S, charges=F['charges'], precedents=F['precedents'], now=F['now'],
            titles=len(titles), titles_charge=sum(s['in_charge_period'] for s in titles),
            thin=sum(s['lose_title'] <= 3 for s in titles),
            relegate_min=min(s['relegated'] for s in S), relegate_max=max(s['relegated'] for s in S))
print({k: v for k, v in data.items() if k not in ('seasons', 'charges', 'precedents', 'now')})
html = (root / 'scripts' / 'city115_template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
out = root / 'the-115'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

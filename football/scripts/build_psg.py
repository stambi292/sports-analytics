"""Build football/psg-from-stars-to-a-team/index.html.
Sources: football/data/psg/ligue1-*.csv (football-data.co.uk via datasets/football-datasets) -> psg_seasons.json
(psg_analysis.py); football/data/psg/ucl.json (match reports, see its _note)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
L = json.loads((root / 'data/psg/psg_seasons.json').read_text())
U = json.loads((root / 'data/psg/ucl.json').read_text())
for s in L: s['ppg'] = round(s['pts'] / s['p'], 2)
def era(lo, hi): xs = [s for s in L if lo <= s['y'] <= hi]; return dict(ppg=round(sum(s['pts'] for s in xs) / sum(s['p'] for s in xs), 2), shots=round(sum(s['shot_share'] for s in xs) / len(xs), 1), gf=round(sum(s['gf'] for s in xs) / sum(s['p'] for s in xs), 2), ga=round(sum(s['ga'] for s in xs) / sum(s['p'] for s in xs), 2))
ties = lambda e: [t for s in U['seasons'] if s['era'] == e for t in s['ties']]
summary = dict(stars=era(2017, 2023), team=era(2024, 2025),
  ties_stars=[sum(t[1] == 'W' for t in ties('stars')), len(ties('stars'))], ties_team=[sum(t[1] == 'W' for t in ties('team')), len(ties('team'))])
print(summary)
html = (root / 'scripts/psg_template.html').read_text().replace('/*__DATA__*/null', json.dumps(dict(ligue1=L, ucl=U, s=summary), ensure_ascii=False))
out = root / 'psg-from-stars-to-a-team'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

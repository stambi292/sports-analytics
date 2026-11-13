"""Build football/can-data-beat-the-bookmaker/index.html from data/bookmaker/results.json (run bookmaker_analysis.py first)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
D = json.loads((root / 'data/bookmaker/results.json').read_text())
html = (root / 'scripts/bookmaker_template.html').read_text().replace('/*__DATA__*/null', json.dumps(D, ensure_ascii=False))
out = root / 'can-data-beat-the-bookmaker'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)
print('ok')

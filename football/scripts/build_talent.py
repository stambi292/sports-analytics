"""Build football/where-did-germanys-talent-go/index.html from talent_template.html and data/talent/talent_web.json
(run talent_analysis.py first to refresh the data)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'talent' / 'talent_web.json').read_text())
html = (root / 'scripts' / 'talent_template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':'), ensure_ascii=False))
out = root / 'where-did-germanys-talent-go'; out.mkdir(exist_ok=True)
(out / 'index.html').write_text(html)
print('ok', len(html))

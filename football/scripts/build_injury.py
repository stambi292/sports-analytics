"""Build 'The Injury Bill' page from its template and data file."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data' / 'injury_cost_bundesliga.json').read_text())
tpl = (root / 'scripts' / 'injury_template.html').read_text()
(root / 'the-injury-bill' / 'index.html').write_text(tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':'))))
print('built')

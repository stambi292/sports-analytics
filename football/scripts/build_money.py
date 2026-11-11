"""Build the 'Did the money buy points?' page from its template and data file."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data' / 'spend_vs_points_2026_27.json').read_text())
tpl = (root / 'scripts' / 'money_template.html').read_text()
(root / 'did-the-money-buy-points' / 'index.html').write_text(tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':'))))
print('built')

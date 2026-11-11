"""Build the 'Is Frankfurt in crisis?' page from its template and data file."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((root / 'data' / 'frankfurt_2026_27.json').read_text())
tpl = (root / 'scripts' / 'frankfurt_template.html').read_text()
out = tpl.replace('/*__DATA__*/null', json.dumps(data, separators=(',', ':')))
(root / 'is-frankfurt-in-crisis' / 'index.html').write_text(out)
print('built', len(out), 'bytes')

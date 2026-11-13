"""Build football/the-spanish-school/index.html: why Spanish coaches win.

Sources: football/data/spanish-coaches/data.json, compiled from Wikipedia's list of European Cup and
Champions League winning managers, Opta Analyst (May 2026, most European titles), match reports for
2025-26 (PSG, Aston Villa, Spain), and UEFA coaching convention figures (2013) as reported by
These Football Times and Sports Economics.
"""
import json, pathlib, collections
root = pathlib.Path(__file__).resolve().parents[1]
D = json.loads((root / 'data/spanish-coaches/data.json').read_text())
since = collections.Counter(r[2] for r in D['ucl_since2000'])
last20 = collections.Counter(r[2] for r in D['ucl_since2000'] if r[0] >= 2007)
D['ucl_since_counts'] = since.most_common()
D['ucl_last20'] = last20.most_common()
D['intl_counts'] = collections.Counter(r[3] for r in D['intl']).most_common()
print(D['ucl_since_counts'], D['ucl_last20'], D['intl_counts'])
html = (root / 'scripts/spanish_coaches_template.html').read_text().replace('/*__DATA__*/null', json.dumps(D, ensure_ascii=False))
out = root / 'the-spanish-school'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

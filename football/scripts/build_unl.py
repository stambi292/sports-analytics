"""Build football/follow-the-money/index.html: who wins from the UEFA Nations League?

Sources (football/data/unl/):
- money.json: UEFA financial reports 2018/19, 2020/21, 2022/23, 2024/25 (national-team revenue,
  distributions to member associations, Nations League payouts). Per-league fees are derived:
  A 2.25m, B 1.5m, C 1.125m, D 0.75m (group winners get the fee again) reproduce UEFA's totals exactly.
- results.csv: international results 1872-2026 (martj42/international_results on GitHub);
  unl_matches.json made from it by unl_analysis.py.
"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
src = root / 'data' / 'unl'
M = json.loads((src / 'money.json').read_text())
G = json.loads((src / 'unl_matches.json').read_text())
y = G['years']; pt = G['per_team']
avg = lambda xs: sum(xs) / len(xs)
before = [i for i, yy in enumerate(y) if yy <= 2017]
after = [i for i, yy in enumerate(y) if yy >= 2019]
fr_uu_before = avg([G['uefa_v_uefa']['friendly'][i] for i in before])
fr_uu_after = avg([G['uefa_v_uefa']['friendly'][i] for i in after])
summary = dict(
  per_season=[round(c['total'] / c['seasons']) for c in M['cycles']],
  share_paid=[round(100 * a['distributed'] / a['revenue']) for a in M['annual'] if a['season'] in ('2018/19', '2022/23')],
  friendlies_uu=[round(fr_uu_before), round(fr_uu_after), round(100 * (fr_uu_after / fr_uu_before - 1))],
  games_per_team=[round(avg([G['per_team_total'][i] for i, yy in enumerate(y) if 2014 <= yy <= 2017]), 1), round(avg([G['per_team_total'][i] for i, yy in enumerate(y) if 2022 <= yy <= 2025]), 1)],  # same 4-year cycle position, after COVID
  friendly_share=[round(100 * avg([pt['friendly'][i] for i in before]) / avg([G['per_team_total'][i] for i in before])),
                  round(100 * avg([pt['friendly'][i] for i in after]) / avg([G['per_team_total'][i] for i in after]))],
)
print(summary)
data = dict(money=M, games=G, s=summary)
html = (root / 'scripts' / 'unl_template.html').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
out = root / 'follow-the-money'; out.mkdir(exist_ok=True); (out / 'index.html').write_text(html)

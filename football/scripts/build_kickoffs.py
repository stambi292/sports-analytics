"""Build football/kick-off-for-whom/index.html from kickoffs_template.html and data/laliga_kickoffs.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((root / 'data' / 'laliga_kickoffs.json').read_text())
B, L, dist = d['bigVsRest'], d['last'], d['distance']
d['recs'] = [
    {'tag': 'Distance', 'h': 'Match the slot to the trip',
     'p': f"Weeknight games are no shorter: the median Monday or Friday away trip is {dist['monfriMedian']} km. When choosing which game goes to Monday 21:00, prefer local matches and derbies, and keep long trips (over 500 km) for weekend afternoons. In 2025/26 that rule would have touched {L['tough']} matches."},
    {'tag': 'Fairness', 'h': 'Share the awkward slots',
     'p': f"Clubs outside the big three play {B['restMonfri']}% of their games on a Monday or Friday, against {B['bigMonfri']}% for matches with the big three. A simple cap, such as no club hosting more than three Monday games a season, would spread the burden without changing the TV grid."},
    {'tag': 'Families', 'h': 'Keep earlier slots for family audiences',
     'p': f"{d['trend'][-2]['late']}% of games now start at 20:45 or later. Protecting a 16:15 or 18:30 slot on Sundays for clubs with a large local and family crowd would help the next generation of match-goers, which is where the league says it is losing young fans."},
    {'tag': 'Measure it', 'h': 'Track the effect on the stands',
     'p': "LALIGA has the attendance and audience data that public sources lack. Joining it with this slot data would show exactly what a Monday 21:00 costs in empty seats for each club, and turn the debate into a number both fans and broadcasters can accept."},
]
html = (root / 'scripts' / 'kickoffs_template.html').read_text().replace('/*__DATA__*/null', json.dumps(d, separators=(',', ':'), ensure_ascii=False))
out = root / 'kick-off-for-whom'; out.mkdir(exist_ok=True)
(out / 'index.html').write_text(html)
print('ok', len(html))

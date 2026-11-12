"""Insert a 'How it was built' section (tools + pipeline) into each project template, once."""
import pathlib
here = pathlib.Path(__file__).parent

CSS = """
.build { display: grid; gap: 16px; }
.build .chips { display: flex; flex-wrap: wrap; gap: 8px; }
.build .chip { font: 600 14px var(--font-body); padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel); }
.build .chip b { color: var(--tool-acc); font-weight: 700; }
.build .steps { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; counter-reset: s; }
.build .step { background: var(--panel); border: 1px solid var(--line); border-top: 4px solid var(--tool-acc); border-radius: 8px; padding: 12px 14px; min-width: 0; }
.build .step h3 { font: 600 18px var(--font-display); margin: 0 0 4px; }
.build .step h3::before { counter-increment: s; content: counter(s) ". "; color: var(--tool-acc); }
.build .step p { margin: 0; font-size: 14px; color: var(--ink-2); line-height: 1.45; }
@media (max-width: 760px) { .build .steps { grid-template-columns: minmax(0, 1fr); } }
"""

def section(chips, steps):
    c = ''.join(f'<span class="chip"><b>{k}</b> · {v}</span>' for k, v in chips)
    s = ''.join(f'<div class="step"><h3>{h}</h3><p>{p}</p></div>' for h, p in steps)
    return f"""  <section class="build" id="how-it-was-built">
    <h2>How it was built</h2>
    <p class="intro">The tools and steps behind this page, from raw data to the published analysis.</p>
    <div class="chips">{c}</div>
    <div class="steps">{s}</div>
  </section>
"""

P = {
 'talent_template.html': ('var(--ger-ink)', section(
   [('Python', 'pandas, NumPy'), ('Parquet', 'PyArrow'), ('Git', 'sparse clones of open-data repos'), ('Data', '144,882 player ratings, 1,000+ World Cup squad rows'),
    ('JavaScript', 'hand-built SVG charts'), ('Playwright', 'desktop and phone checks'), ('GitHub Pages', 'hosting')],
   [('Collect', 'Pulled 9 seasons of FIFA / EA FC ratings and the World Cup database from public GitHub repos, only the files needed.'),
    ('Clean', 'Matched league names across game versions, kept the top five leagues and grouped 15 positions into 6.'),
    ('Analyse', 'Counted future stars, world-class players and local starters by nation, position and season with pandas.'),
    ('Visualise', 'Interactive line charts with country toggles, a World Cup timeline and position comparisons, all in plain JavaScript and SVG.'),
    ('Recommend', 'Turned each finding into a fix with a measurable target from Germany\'s own best years.')])),
 'poacher_template.html': ('var(--green-ink)', section(
   [('Python', 'pandas, json'), ('xG data', 'Understat season totals'), ('Event data', 'StatsBomb open data'), ('Statistics', 'Poisson model, goals vs xG'),
    ('JavaScript', 'SVG shot map and charts'), ('Playwright', 'desktop and phone checks'), ('GitHub Pages', 'hosting')],
   [('Collect', 'Season xG, shots and minutes from Understat; every shot from StatsBomb event files for 10 matches.'),
    ('Clean', 'Parsed match events to rebuild his minutes from line-ups and substitutions, and mapped shot locations to the pitch.'),
    ('Analyse', 'Goals minus xG per season, xG per 90, shots per 90 and xG per shot, in Germany and abroad.'),
    ('Model', 'A Poisson model turns xG per 90 and finishing ratio into the chance he scores in a match.'),
    ('Visualise', 'Interactive shot map with filters, season charts and a match calculator.')])),
 'kickoffs_template.html': ('var(--red-ink)', section(
   [('Python', 'pandas, json'), ('Data', '4,270 LALIGA matches, openfootball'), ('Geo', 'haversine distances between 30+ stadiums'), ('Fairness metrics', 'slot share by club'),
    ('JavaScript', 'heatmap, charts and trip planner'), ('Playwright', 'desktop and phone checks'), ('GitHub Pages', 'hosting')],
   [('Collect', 'Twelve seasons of LALIGA fixtures with dates and kick-off times from openfootball.'),
    ('Clean', 'Unified club names across seasons and attached stadium coordinates.'),
    ('Analyse', 'Late and weeknight share by season and club, and away-trip distance for every match.'),
    ('Visualise', 'A week-by-hour heatmap, trend chart, fairness ranking and an away-fan trip planner.'),
    ('Recommend', 'Scheduling fixes for the league, each tied to a number from the data.')])),
}
for f, (acc, sec) in P.items():
    p = here / f; s = p.read_text()
    if 'id="how-it-was-built"' in s:
        print('skip', f); continue
    s = s.replace('</style>', f':root {{ --tool-acc: {acc}; }}' + CSS + '</style>', 1)
    i = s.rfind('  <section>\n    <h2>Method')
    if i == -1: i = s.index('</main>')
    s = s[:i] + sec + s[i:]
    p.write_text(s); print('ok', f)

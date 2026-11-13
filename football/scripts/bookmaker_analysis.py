"""Can data beat the bookmaker? Walk-forward test of two models against Bet365 on the Premier League.

Data: football/data/bookmaker/pl_matches_odds.csv (Premier League 2000/01-2026/27 from
Football-Data.co.uk via xgabora/Club-Football-Match-Data, MIT). OddHome/Draw/Away = Bet365,
Max* = best price across ~17 European bookmakers.

Models (each match is predicted using ONLY matches played before that date):
  * Goals model: Poisson attack/defence ratings + home advantage, refit every match date,
    time-decayed (half-life 240 days), L2-regularised so promoted teams start near average.
  * Elo: eloratings-style rating (K=20, home +60), turned into H/D/A with an ordered logit fitted
    on the seasons before each test season.
Test window: 2006/07-2025/26 (20 seasons, 7,600 matches; best-price odds exist from 2005/06).
"""
import json, pathlib, numpy as np, pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize
from sklearn.linear_model import PoissonRegressor

root = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(root / 'data/bookmaker/pl_matches_odds.csv', parse_dates=['MatchDate'])
d = d.dropna(subset=['FTHome', 'FTAway', 'OddHome', 'OddDraw', 'OddAway']).sort_values('MatchDate').reset_index(drop=True)
d['season'] = d.MatchDate.apply(lambda t: t.year if t.month >= 7 else t.year - 1)
d['res'] = d.FTResult.map({'H': 0, 'D': 1, 'A': 2})

# ---- bookmaker probabilities: remove the margin proportionally
inv = 1 / d[['OddHome', 'OddDraw', 'OddAway']].values
d['margin'] = inv.sum(1) - 1
bk = inv / inv.sum(1, keepdims=True)
d[['bH', 'bD', 'bA']] = bk

# ---- Goals model, walk-forward by match date
HL = 240.0
teams = sorted(set(d.HomeTeam) | set(d.AwayTeam)); ti = {t: i for i, t in enumerate(teams)}; nT = len(teams)
gH = np.full(len(d), np.nan); gD = gH.copy(); gA = gH.copy(); lamH = gH.copy(); lamA = gH.copy()
start = pd.Timestamp('2005-07-01')
dates = d.MatchDate[d.MatchDate >= start].unique()
G = np.arange(11)
for dt in dates:
    past = d[(d.MatchDate < dt) & (d.MatchDate >= dt - pd.Timedelta(days=3 * 365))]
    w = 0.5 ** ((dt - past.MatchDate).dt.days.values / HL)
    n = len(past)
    X = np.zeros((2 * n, 2 * nT + 1)); y = np.concatenate([past.FTHome.values, past.FTAway.values]); ww = np.concatenate([w, w])
    h = past.HomeTeam.map(ti).values; a = past.AwayTeam.map(ti).values; r = np.arange(n)
    X[r, h] = 1; X[r, nT + a] = 1; X[r, 2 * nT] = 1          # home goals: attack(home) + defence(away) + home adv
    X[n + r, a] = 1; X[n + r, nT + h] = 1                    # away goals
    m = PoissonRegressor(alpha=0.002, max_iter=300).fit(X, y, sample_weight=ww)
    idx = np.where(d.MatchDate.values == dt)[0]
    for i in idx:
        hh, aa = ti[d.HomeTeam[i]], ti[d.AwayTeam[i]]
        x1 = np.zeros(2 * nT + 1); x1[hh] = 1; x1[nT + aa] = 1; x1[2 * nT] = 1
        x2 = np.zeros(2 * nT + 1); x2[aa] = 1; x2[nT + hh] = 1
        l1, l2 = m.predict(np.vstack([x1, x2]))
        M = np.outer(poisson.pmf(G, l1), poisson.pmf(G, l2)); M /= M.sum()
        gH[i], gD[i], gA[i] = np.tril(M, -1).sum(), np.trace(M), np.triu(M, 1).sum()
        lamH[i], lamA[i] = l1, l2
d['gH'], d['gD'], d['gA'], d['lamH'], d['lamA'] = gH, gD, gA, lamH, lamA

# ---- Elo
R = {}; eD = np.zeros(len(d)); prev_season = None
for i, row in d.iterrows():
    if row.season != prev_season:                             # regress 20% to the mean each summer
        R = {k: 1500 + .8 * (v - 1500) for k, v in R.items()}; prev_season = row.season
    rh, ra = R.get(row.HomeTeam, 1420), R.get(row.AwayTeam, 1420)   # new teams start below average
    eD[i] = rh + 60 - ra
    exp = 1 / (1 + 10 ** (-eD[i] / 400)); s = [1, .5, 0][row.res]
    gd = abs(row.FTHome - row.FTAway); k = 20 * (1 if gd <= 1 else 1.5 if gd == 2 else (11 + gd) / 8)
    R[row.HomeTeam] = rh + k * (s - exp); R[row.AwayTeam] = ra - k * (s - exp)
d['eloD'] = eD

def ologit(x, c1, c2, b):
    pA = 1 / (1 + np.exp(-(c1 - b * x))); pAD = 1 / (1 + np.exp(-(c2 - b * x)))
    return np.c_[1 - pAD, pAD - pA, pA]
eP = np.full((len(d), 3), np.nan)
for s in range(2006, d.season.max() + 1):
    tr = d[(d.season < s) & (d.season >= 2001)]
    def nll(p): P = ologit(tr.eloD.values, *p); return -np.log(np.clip(P[np.arange(len(tr)), tr.res.values], 1e-9, 1)).sum()
    c = minimize(nll, [-1, .2, .005], method='Nelder-Mead', options={'maxiter': 4000}).x
    ix = d.index[d.season == s]; eP[ix] = ologit(d.eloD.values[ix], *c)
d[['eH', 'eD', 'eA']] = eP

# ---- evaluation on test window
T = d[(d.season >= 2006) & (d.season <= 2025)].copy()
Y = np.eye(3)[T.res.values]
def scores(P):
    return dict(brier=float(((P - Y) ** 2).sum(1).mean()), logloss=float(-np.log(P[np.arange(len(P)), T.res.values]).mean()),
                acc=float((P.argmax(1) == T.res.values).mean()))
models = {'Bookmaker (Bet365)': T[['bH', 'bD', 'bA']].values, 'Goals model': T[['gH', 'gD', 'gA']].values,
          'Elo model': T[['eH', 'eD', 'eA']].values, 'Coin flip (home/draw/away rates)': np.tile(np.bincount(d[d.season < 2006].res, minlength=3) / len(d[d.season < 2006]), (len(T), 1))}
S = {k: scores(v) for k, v in models.items()}
for k, v in S.items(): print(f'{k:35s}', {a: round(b, 4) for a, b in v.items()})

# per-season Brier, bookmaker vs goals model
per = []
for s, g in T.groupby('season'):
    y = np.eye(3)[g.res.values]
    b = ((g[['bH', 'bD', 'bA']].values - y) ** 2).sum(1).mean(); m = ((g[['gH', 'gD', 'gA']].values - y) ** 2).sum(1).mean()
    e = ((g[['eH', 'eD', 'eA']].values - y) ** 2).sum(1).mean()
    per.append(dict(season=f'{s}/{str(s + 1)[2:]}', book=round(b, 4), model=round(m, 4), elo=round(e, 4), margin=round(g.margin.mean() * 100, 2),
                    fav=round(float((g[['bH', 'bD', 'bA']].values.argmax(1) == g.res.values).mean() * 100), 1)))
wins = sum(p['model'] < p['book'] for p in per)
print('model beat book in', wins, 'of', len(per), 'seasons')

# calibration of the bookmaker and the model (home-win probability, all three outcomes pooled)
def calib(P):
    p = P.ravel(); y = Y.ravel(); bins = np.arange(0, 1.01, .1); out = []
    for lo in bins[:-1]:
        mk = (p >= lo) & (p < lo + .1)
        if mk.sum() >= 40: out.append(dict(lo=round(lo, 1), n=int(mk.sum()), pred=round(float(p[mk].mean()) * 100, 1), act=round(float(y[mk].mean()) * 100, 1)))
    return out
cal = dict(book=calib(models['Bookmaker (Bet365)']), model=calib(models['Goals model']))

# ---- betting simulation: £10 flat stake whenever model says the price has value
def sim(P, odds, edge, label):
    o = odds; ev = P * o - 1; bets = []
    for j in range(len(P)):
        k = int(ev[j].argmax())
        if ev[j, k] > edge: bets.append((T.MatchDate.values[j], 10 * (o[j, k] - 1) if T.res.values[j] == k else -10, k, o[j, k]))
    n = len(bets); profit = sum(b[1] for b in bets)
    return dict(label=label, bets=n, staked=10 * n, profit=round(profit), roi=round(profit / (10 * n) * 100, 1) if n else 0,
                hit=round(sum(b[1] > 0 for b in bets) / n * 100, 1) if n else 0, curve=np.cumsum([b[1] for b in bets])[::25].round().tolist()), bets
b365 = T[['OddHome', 'OddDraw', 'OddAway']].values; best = T[['MaxHome', 'MaxDraw', 'MaxAway']].values
okbest = ~np.isnan(best).any(1); best = np.where(np.isnan(best), b365, best)
sims = {}
for nm, P in [('model', models['Goals model']), ('elo', models['Elo model'])]:
    for on, o in [('b365', b365), ('best', best)]:
        for e in (0.0, 0.05, 0.10):
            r, _ = sim(P, o, e, f'{nm} {on} edge{int(e*100)}'); sims[r['label']] = r
            print(r['label'], r['bets'], r['profit'], r['roi'], r['hit'])

# simple strategies at Bet365 prices
def strat(pick, odds, label):
    k = pick; won = T.res.values == k; pr = np.where(won, 10 * (odds[np.arange(len(k)), k] - 1), -10)
    return dict(label=label, bets=len(k), profit=round(float(pr.sum())), roi=round(float(pr.sum() / (10 * len(k)) * 100), 1),
                hit=round(float(won.mean() * 100), 1), curve=np.cumsum(pr)[::20].round().tolist())
simple = [strat(np.zeros(len(T), int), b365, 'Back every home team'), strat(np.ones(len(T), int), b365, 'Back every draw'),
          strat(b365.argmin(1), b365, 'Back every favourite'), strat(b365.argmax(1), b365, 'Back every underdog')]
for s in simple: print(s['label'], s['profit'], s['roi'], s['hit'])

# favourite-longshot: return per £1 by bookmaker probability bucket (Bet365 price)
fl = []
po = 1 / b365
for lo, hi, nm in [(0, .2, 'Long shots (under 20%)'), (.2, .4, '20–40%'), (.4, .6, '40–60%'), (.6, .8, '60–80%'), (.8, 1.01, 'Big favourites (80%+)')]:
    mk = (po >= lo) & (po < hi); won = (np.arange(3)[None, :] == T.res.values[:, None]) & mk
    ret = (b365 * won).sum() / mk.sum() - 1
    fl.append(dict(bucket=nm, n=int(mk.sum()), roi=round(float(ret) * 100, 1)))
print(fl)

# biggest model-vs-book disagreements that came true / failed (goals model, best-price value bets)
_, mb = sim(models['Goals model'], best, 0.10, 'x')

# the margin per season, and Hull v Man United 2026 example of a shock
ex = d[(d.HomeTeam == 'Hull') & (d.AwayTeam == 'Man United') & (d.season == 2026)].iloc[0]
example = dict(date=str(ex.MatchDate.date()), home='Hull', away='Man United', score=f'{int(ex.FTHome)}–{int(ex.FTAway)}', odds=[ex.OddHome, ex.OddDraw, ex.OddAway],
               book=[round(ex.bH * 100, 1), round(ex.bD * 100, 1), round(ex.bA * 100, 1)], margin=round(ex.margin * 100, 1))

out = dict(n=len(T), seasons=len(per), first=per[0]['season'], last=per[-1]['season'], scores=S, per=per, wins=wins, cal=cal,
           sims=sims, simple=simple, fl=fl, example=example,
           margin_first=per[0]['margin'], margin_last=per[-1]['margin'],
           fav_rate=round(float((models['Bookmaker (Bet365)'].argmax(1) == T.res.values).mean() * 100), 1),
           draws=round(float((T.res == 1).mean() * 100), 1))
(root / 'data/bookmaker/results.json').write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
print('saved')

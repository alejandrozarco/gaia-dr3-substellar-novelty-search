"""ZTF24abfojgu: is the ZTF 76.34-min signal (or its 1-day aliases 72.49 / 80.63 min) present in ATLAS high-state photometry
(MJD >= 60582)? (2026-09-30.) Cleaning as atlas_outbursts.py; flux minus a leave-one-out running median over +-3 d per filter (>= 3
neighbours), o and c combined. Observed statistic: maximum Lomb-Scargle power within +-0.01 c/d of 17.8592, 18.8619, 19.8647 c/d.
Null: the same statistic for 1000 random triplets of windows spaced by 1.0027 c/d (the alias spacing) centred at 5-60 c/d, avoiding
+-0.1 c/d of the three test frequencies and of integers. Output: atlas_period_abfojgu.txt."""
import os, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
H = os.path.dirname(os.path.abspath(__file__)); g = "5182404743053707904"; rng = np.random.default_rng(11)
L = [l for l in open(os.path.join(H, "atlas", g + ".txt")).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
R = R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]; R = R[(R.duJy < 3 * R.duJy.median()) & (R.MJD >= 60582)]
parts = []
for f in "oc":
    x = R[R.F == f].sort_values("MJD"); t = x.MJD.values; y = x.uJy.values; res = np.full(len(x), np.nan)
    for i in range(len(x)):
        nb = np.abs(t - t[i]) <= 3; nb[i] = False
        if nb.sum() >= 3: res[i] = y[i] - np.median(y[nb])
    parts.append(x.assign(res=res).dropna(subset=["res"]))
D = pd.concat(parts); ls = LombScargle(D.MJD.values, D.res.values, D.duJy.values)
def trip(f0): return max(ls.power(np.linspace(f - 0.01, f + 0.01, 201)).max() for f in (f0 - 1.0027, f0, f0 + 1.0027))
obs = trip(18.8619); test = (17.8592, 18.8619, 19.8647); per = {f: float(ls.power(np.linspace(f - 0.01, f + 0.01, 201)).max()) for f in test}; null = []
while len(null) < 1000:
    c = rng.uniform(5, 60)
    if min(abs(c - f) for f in (17.8592 - 1, 17.8592, 18.8619, 19.8647, 19.8647 + 1)) > 0.1 and abs(c - round(c)) > 0.1: null.append(trip(c))
p = (np.sum(np.array(null) >= obs) + 1) / 1001
txt = f"ATLAS high state (MJD >= 60582): {len(D)} points (o {int((D.F == 'o').sum())}, c {int((D.F == 'c').sum())})\nmax power per test window: " + ", ".join(f"{k} c/d {v:.4f}" for k, v in per.items()) + f"\nalias-triplet statistic {obs:.4f}; random-triplet median {np.median(null):.4f}; empirical p = {p:.4f}\n"
open(os.path.join(H, "atlas_period_abfojgu.txt"), "w").write(txt); print(txt)
# Refinement (added 2026-09-30): best frequency near 18.8619 c/d, bootstrap error (300 resamples), semi-amplitude of a sinusoid
# in uJy and as a fraction of the high-state median difference flux plus the quiescent flux (ZTF g 20.25 ~ 29 uJy is not in the
# difference flux, so the fraction is quoted against the high-state difference flux only, an upper bound).
fr = np.linspace(18.80, 18.92, 12001); pw = ls.power(fr); fb = fr[np.argmax(pw)]; bs = []
t, y, e = D.MJD.values, D.res.values, D.duJy.values
for k in range(300):
    i = rng.integers(0, len(t), len(t)); l2 = LombScargle(t[i], y[i], e[i]); bs.append(fr[np.argmax(l2.power(fr))])
mdl = ls.model(np.linspace(0, 1 / fb, 200) + t[0], fb); amp = np.ptp(mdl) / 2; med = float(np.median(R.uJy))
txt2 = f"best frequency {fb:.5f} c/d = {1440 / fb:.3f} min; bootstrap sigma {np.std(bs):.5f} c/d ({1440 / fb**2 * np.std(bs) * 60:.1f} s); semi-amplitude {amp:.1f} uJy = {amp / med:.2f} of the high-state median difference flux ({med:.0f} uJy)\n"
open(os.path.join(H, "atlas_period_abfojgu.txt"), "a").write(txt2); print(txt2)

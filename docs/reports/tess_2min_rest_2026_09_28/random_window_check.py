"""Empirical false-alarm check for ATLAS window folds (2026-09-30).
fold_at2.py reports the maximum Lomb-Scargle power within +-0.01 c/d of the TESS frequency f (and 2f, f/2) with an analytic
white-noise FAP. Excess low-frequency or systematic power can make every window 'significant' (seen as equal power at f, 2f and f/2).
Here, per star and band, the maximum power in the +-0.01 c/d window around f is compared with the maxima of 500 windows of the same
width centred on random frequencies in 0.5-20 c/d (avoiding +-0.05 c/d around f, 2f, f/2 and integer c/d). Empirical p = fraction of
random windows with power >= the window at f. Uses the same cleaning as fold_at2.py (err 0, chi/N < 10, duJy < 3x median, uJy).
Usage: python random_window_check.py <atlas dir> <gaia:f> [...]"""
import sys, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
rng = np.random.default_rng(1)
def load(fn):
    L = [l for l in open(fn).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R.dropna(subset=["MJD", "uJy", "duJy"]); return R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]
d = sys.argv[1]
for arg in sys.argv[2:]:
    g, f = arg.split(":"); f = float(f); R = load(f"{d}/{g}.txt"); out = [g, f"{f:.5f}"]
    for b in ("o", "c"):
        x = R[R.F == b]; x = x[x.duJy < 3 * x.duJy.median()]
        if len(x) < 50: out.append(f"{b}: n<50"); continue
        ls = LombScargle(x.MJD.values, x.uJy.values - np.median(x.uJy.values), x.duJy.values)
        def wmax(c): fr = np.linspace(c - 0.01, c + 0.01, 401); return ls.power(fr).max()
        obs = wmax(f); cents = []
        while len(cents) < 500:
            c = rng.uniform(0.5, 20)
            if min(abs(c - f), abs(c - 2 * f), abs(c - f / 2)) > 0.05 and abs(c - round(c)) > 0.05: cents.append(c)
        rnd = np.array([wmax(c) for c in cents]); p = (np.sum(rnd >= obs) + 1) / 501
        out.append(f"{b}: power {obs:.4f}, random-window median {np.median(rnd):.4f}, p = {p:.3f}")
    print(" | ".join(out), flush=True)

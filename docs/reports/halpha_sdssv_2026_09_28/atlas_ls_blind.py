"""Blind ATLAS period search for the two H-alpha-emission white dwarfs (batch 9, 2026-09-30).
Cleaning as fold_at2.py (err 0, chi/N < 10, duJy > 0, duJy < 3x median per filter; flux uJy). Per filter, a nightly-median is NOT removed
(to keep hour-scale signals) but each filter's median is subtracted; o and c combined with per-filter error weights.
Lomb-Scargle 0.05-50 c/d. FAP: 200 shuffles of flux within filter and 5-d blocks (keeps slow trends and window, destroys phase)."""
import sys, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
rng = np.random.default_rng(3)
def load(fn):
    L = [l for l in open(fn).read().splitlines() if l.strip()]; h = L[0].lstrip("#").split(); R = pd.DataFrame([dict(zip(h, l.split())) for l in L[1:]])
    for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
    R = R.dropna(subset=["MJD", "uJy", "duJy"]); return R[(R.err == 0) & (R["chi/N"] < 10) & (R.duJy > 0)]
fr = np.linspace(0.05, 50, 300000)
for g in sys.argv[1:]:
    R = load(f"atlas/{g}.txt"); parts = []
    for b in ("o", "c"):
        x = R[R.F == b]; x = x[x.duJy < 3 * x.duJy.median()].copy(); x["y"] = x.uJy - x.uJy.median(); parts.append(x)
        print(g, b, "n", len(x), "median uJy %.1f  median err %.1f  rms %.1f" % (x.uJy.median(), x.duJy.median(), x.y.std()))
    D = pd.concat(parts); t, y, e = D.MJD.values, D.y.values, D.duJy.values
    p = LombScargle(t, y, e).power(fr); top = np.argsort(p)[::-1]; seen = []
    for i in top:
        if all(abs(fr[i] - s) > 0.02 for s in seen): seen.append(fr[i])
        if len(seen) == 6: break
    mx = []
    for s in range(200):
        yy = y.copy()
        for b in ("o", "c"):
            idx = np.where(D.F.values == b)[0]; blk = np.floor(t[idx] / 5)
            for k in np.unique(blk): ii = idx[blk == k]; yy[ii] = rng.permutation(yy[ii])
        mx.append(LombScargle(t, yy, e).power(fr[::3]).max())
    mx = np.array(mx)
    for f in seen:
        pw = p[np.argmin(abs(fr - f))]; print("  f %.5f c/d  P %.4f h  power %.4f  FAP %.3f" % (f, 24 / f, pw, (np.sum(mx >= pw) + 1) / 201))

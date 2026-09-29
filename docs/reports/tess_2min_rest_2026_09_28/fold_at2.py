"""ATLAS attribution test at a known frequency, corrected (2026-09-29). The TESS single-sector frequency is uncertain by
~0.001 c/d, which over a 10-year ATLAS baseline drifts by several cycles, so folding at the exact value averages a real signal
away. Here each of f, 2f and f/2 is searched in a +-0.01 c/d window (step 0.00002), and the false-alarm probability is computed
over that window only (the frequency is known in advance). Same cuts and season detrending as fold_at.py.
Usage: python fold_at2.py <atlas.txt> <f_cd> <G>   Output: one line per band with window-best f, FAP and amplitude for f, 2f, f/2."""
import sys, numpy as np, warnings; warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
p, f0, G = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); flux = 3631e6 * 10 ** (-0.4 * G); W = 0.01
L = [l for l in open(p).read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["chi/N"]) < 3 and float(x["mag5sig"]) > 17.5]
print(f"{p.split('/')[-1]} f={f0:.5f} c/d; star flux {flux:.0f} uJy")
for b in ("c", "o"):
    x = [r for r in ok if r["F"] == b]
    if len(x) < 50: print(f"  {b}: only {len(x)} points"); continue
    t = np.array([float(r["MJD"]) for r in x]); f = np.array([float(r["uJy"]) for r in x]); e = np.array([float(r["duJy"]) for r in x])
    season = np.floor((t - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); t, f, e = t[clip], f[clip], e[clip]; ls = LombScargle(t, f, e)
    out = f"  {b}: n {len(t)}"
    for lab, fq in (("f", f0), ("2f", 2 * f0), ("f/2", f0 / 2)):
        FR = np.arange(fq - W, fq + W, 0.00002); P = ls.power(FR); k = P.argmax(); fb = FR[k]
        fap = ls.false_alarm_probability(P[k], minimum_frequency=FR[0], maximum_frequency=FR[-1])
        X = np.vstack([np.sin(2*np.pi*fb*t), np.cos(2*np.pi*fb*t), np.ones_like(t)]).T; c = np.linalg.lstsq(X / e[:, None], f / e, rcond=None)[0]
        cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None])); a = np.hypot(c[0], c[1]); ea = np.sqrt((cov[0,0] + cov[1,1]) / 2)
        out += f"; {lab}: best {fb:.5f} FAP {fap:.2g} amp {a:.1f}+-{ea:.1f} uJy ({100*a/flux:.2f}%)"
    print(out)

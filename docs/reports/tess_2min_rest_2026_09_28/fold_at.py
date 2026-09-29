"""Fold an ATLAS forced-photometry file at a given frequency: same cuts as fold_all.py. Usage: python fold_at.py <atlas.txt> <f_cd> <G>"""
import sys, numpy as np, warnings; warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
p, f0, G = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); flux = 3631e6 * 10 ** (-0.4 * G)
L = [l for l in open(p).read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["chi/N"]) < 3 and float(x["mag5sig"]) > 17.5]
print(f"{p.split('/')[-1]} f={f0:.5f} c/d (P {1440/f0:.2f} min); star flux {flux:.0f} uJy")
for b in ("c", "o"):
    x = [r for r in ok if r["F"] == b]
    if len(x) < 50: print(f"  {b}: only {len(x)} points"); continue
    t = np.array([float(r["MJD"]) for r in x]); f = np.array([float(r["uJy"]) for r in x]); e = np.array([float(r["duJy"]) for r in x])
    season = np.floor((t - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); t, f, e = t[clip], f[clip], e[clip]; ls = LombScargle(t, f, e)
    FR = np.arange(0.5, 72, 0.0001); P = ls.power(FR); m = np.ones_like(FR, bool)
    for n in range(1, 73): m &= np.abs(FR - n) > 0.03
    k = np.argmax(np.where(m, P, 0)); out = f"  {b}: n {len(t)}; top {FR[k]:.5f} (P {1440/FR[k]:.2f} min) FAP {ls.false_alarm_probability(P[k], minimum_frequency=0.5, maximum_frequency=72):.2g}"
    for lab, fq in (("f", f0), ("2f", 2 * f0), ("f/2", f0 / 2)):
        X = np.vstack([np.sin(2*np.pi*fq*t), np.cos(2*np.pi*fq*t), np.ones_like(t)]).T; c = np.linalg.lstsq(X / e[:, None], f / e, rcond=None)[0]; cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None])); a = np.hypot(c[0], c[1]); ea = np.sqrt((cov[0,0]+cov[1,1])/2)
        pw = float(ls.power(np.array([fq]))[0]); out += f"; {lab}: FAP {ls.false_alarm_probability(pw, minimum_frequency=0.5, maximum_frequency=72):.2g} amp {a:.1f}+-{ea:.1f} uJy ({100*a/flux:.2f}%)"
    print(out)

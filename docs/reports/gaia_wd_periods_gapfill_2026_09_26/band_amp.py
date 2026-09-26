"""Per-band (ATLAS c, o) sine + harmonic amplitudes at a given frequency, from atlas_<id>.txt (uJy fluxes; season medians removed;
same cuts as confirm.py). python band_amp.py <id> <freq> <G mag>"""
import sys, numpy as np
i, f0, G = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); REF = 3631e6 * 10 ** (-0.4 * G)
L = [l for l in open(f"atlas_{i}.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
for b in ("c", "o"):
    s = [x for x in ok if x["F"] == b]; med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
    t = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((t - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); t, f, e = t[clip], f[clip] / REF, e[clip] / REF
    ph = 2 * np.pi * f0 * (t - 58000); X = np.vstack([np.ones_like(t), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)]).T; W = 1 / e ** 2
    p = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * f)); C = np.linalg.inv(X.T @ (X * W[:, None])); c2 = max(np.sum(W * (f - X @ p) ** 2) / (len(t) - 5), 1)
    print(f"{i} {b}: n {len(t)}, A1 {100*np.hypot(p[1],p[2]):.2f} +- {100*np.sqrt(c2*(C[1,1]+C[2,2])/2):.2f}%, A2 {100*np.hypot(p[3],p[4]):.2f}%, phase1 {np.degrees(np.arctan2(p[2],p[1])):.0f}, phase2 {np.degrees(np.arctan2(p[4],p[3])):.0f}")

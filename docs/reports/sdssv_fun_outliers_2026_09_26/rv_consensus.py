"""Consensus velocities from rv_multi_all.csv: per visit, the median of the H-alpha, H-beta and H-gamma velocities where at least
two lines agree within max(3 sigma, 40 km/s) of that median (else the visit is dropped); error = max(inter-line scatter / sqrt(n),
median line error / sqrt(n), 10 km/s). Per star: chi2 of a constant velocity, largest pairwise difference and its significance.
Visits whose line velocities sit at the grid edge (|v| >= 690 km/s) are excluded. Output rv_consensus.csv."""
import numpy as np, pandas as pd
d = pd.read_csv("rv_multi_all.csv", dtype={"sdss_id": str}); d = d[d.rv.abs() < 690]
rows = []
for (sid, mjd), g in d.groupby(["sdss_id", "mjd"]):
    if len(g) < 2: continue
    med = g.rv.median(); tol = np.maximum(3 * g.e_rv.fillna(99), 40); ok = (g.rv - med).abs() <= tol
    if ok.sum() < 2: continue
    gg = g[ok]; n = len(gg); v = gg.rv.mean(); e = max(gg.rv.std(ddof=1) / np.sqrt(n) if n > 1 else 0, gg.e_rv.median() / np.sqrt(n), 10)
    rows.append(dict(sdss_id=sid, mjd=mjd, v=v, e=e, n_lines=n))
V = pd.DataFrame(rows); out = []
for sid, g in V.groupby("sdss_id"):
    if len(g) < 2: continue
    w = 1 / g.e ** 2; mu = np.sum(w * g.v) / np.sum(w); chi2 = float(np.sum(w * (g.v - mu) ** 2)); i, j = g.v.idxmax(), g.v.idxmin()
    out.append(dict(sdss_id=sid, n_vis=len(g), chi2r=round(chi2 / (len(g) - 1), 2), dv=round(g.v[i] - g.v[j], 1), dv_sig=round((g.v[i] - g.v[j]) / np.hypot(g.e[i], g.e[j]), 1),
                    vis=" ".join(f"{int(m)}:{x:+.0f}±{e:.0f}" for m, x, e in zip(g.mjd, g.v, g.e))))
O = pd.DataFrame(out); O.to_csv("rv_consensus.csv", index=False); print(len(O))

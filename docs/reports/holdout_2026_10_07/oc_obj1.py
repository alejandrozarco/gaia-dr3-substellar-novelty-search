"""Obj1: per-block eclipse times vs the ALL point-fit ephemeris (bootstrap errors), then weighted linear/quadratic O-C ephemeris."""
import sys, json; sys.argv = ["holdout.py", "4851800979770492544"]
import numpy as np, pandas as pd
import holdout as H
from astropy.time import Time
S = json.load(open("4851800979770492544_summary.json")); f = S["f_cd"]; T0 = S["T0_bjd_tdb"]; sigw = S["sigw_min"] / 1440; P = 1 / f
rows = []
for b, g in H.df.groupby("blk"):
    if len(g) < 30: continue
    sub = H.group(g); tc = np.median(g.t); n = np.round((tc - T0) * f); Tp = T0 + n * P
    sh, s_chi, _ = H.free_phase(sub, f, Tp, sigw, 3 / 1440, 361)
    nb = 200 if len(g) < 5000 else 60; bs = []
    for _ in range(nb):
        s2 = [(ds, (t[p], y[p], e[p])) for ds, (t, y, e) in sub for p in [H.rng.integers(0, len(y), len(y))]]
        bs.append(H.free_phase(s2, f, Tp + sh, sigw, 1.5 / 1440, 301)[0])
    sb = 1.4826 * np.median(np.abs(np.array(bs) - np.median(bs))); s = max(s_chi, sb, 0.5 / 1440 * 0.02)
    rows.append(dict(block=b, n_pts=len(g), cycle=int(n), T_obs=Tp + sh, sigma_min=s * 1440, oc_min=sh * 1440)); print(rows[-1], flush=True)
d = pd.DataFrame(rows).sort_values("cycle"); E = d.cycle.values.astype(float); T = d.T_obs.values; s = d.sigma_min.values / 1440
out = {}
for deg in (1, 2):
    A = np.vander(E, deg + 1)[:, ::-1]; w = 1 / s; c, *_ = np.linalg.lstsq(A * w[:, None], T * w, rcond=None); r = T - A @ c; chi = np.sum((r / s) ** 2); dof = len(T) - deg - 1
    cov = np.linalg.inv((A * w[:, None]).T @ (A * w[:, None])) * max(chi / dof, 1); out[deg] = (c, cov, chi, dof); d[f"res_deg{deg}_min"] = r * 1440
    print(f"deg {deg}: chi2 {chi:.2f} dof {dof}; coef {c}; sig {np.sqrt(np.diag(cov))}")
d.to_csv("4851800979770492544_block_times.csv", index=False)
# linear ephemeris re-referenced to cycle near weighted centre
c, cov, chi, dof = out[1]; w = 1 / s ** 2; nref = np.round(np.sum(w * E) / np.sum(w))
T0n = c[0] + nref * c[1]; sT0 = np.sqrt(cov[0, 0] + nref ** 2 * cov[1, 1] + 2 * nref * cov[0, 1]); cTP = cov[0, 1] + nref * cov[1, 1]; Pn, sP = c[1], np.sqrt(cov[1, 1])
t1, t2 = Time("2026-11-01T00:00:00", scale="utc").tdb.jd, Time("2027-04-01T00:00:00", scale="utc").tdb.jd
n = np.arange(np.ceil((t1 - T0n) / Pn), np.floor((t2 - T0n) / Pn) + 1); tp = T0n + n * Pn; st = np.sqrt(sT0 ** 2 + n ** 2 * sP ** 2 + 2 * n * cTP)
pr = pd.DataFrame(dict(cycle_from_T0=n.astype(int), bjd_tdb=np.round(tp, 6), sigma_min=np.round(st * 1440, 3), utc_label=Time(tp, format="jd", scale="tdb").utc.isot, event="mid_eclipse"))
with open("4851800979770492544_predictions_blocktiming.csv", "w") as fh:
    fh.write(f"# Gaia DR3 4851800979770492544 mid-eclipse predictions 2026-11-01..2027-03-31 from weighted linear fit to {len(T)} block eclipse times; BJD_TDB = {T0n:.6f} + {Pn:.10f} E; sigma T0 {sT0*1440:.3f} min, sigma P {sP:.2g} d, cov {cTP:.3g}; chi2 {chi:.1f}/{dof}; utc_label = BJD minus TDB-UTC only (no barycentric correction)\n")
    pr.to_csv(fh, index=False)
json.dump(dict(T0=T0n, sT0_d=sT0, P=Pn, sP_d=sP, cov=cTP, chi2=chi, dof=dof, quad=dict(coef=list(out[2][0]), sig=list(np.sqrt(np.diag(out[2][1]))), chi2=out[2][2])), open("4851800979770492544_blocktiming_ephem.json", "w"), indent=1)
print(d.round(4).to_string(index=False)); print(T0n, sT0 * 1440, Pn, sP); print(pr.head(3)); print(pr.tail(3))

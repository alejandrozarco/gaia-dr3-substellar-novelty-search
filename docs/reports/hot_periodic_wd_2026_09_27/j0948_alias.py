"""WDJ094809.07-280038.55 (Gaia DR3 5657176543986789248): Gaia G vs ZTF g/r at the two candidate frequencies 2.170 and 1.167 c/d (1 c/d aliases).
Common-phase fit (each data set scaled by its own amplitude and offset, shared sinusoid + harmonic); chi2 at each candidate refined on a fine grid.
Also lists TESS 120-s products."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia; from astroquery.mast import Observations; from astropy.timeseries import LombScargle
gid = "5657176543986789248"
t = Gaia.load_data(ids=[gid], retrieval_type="EPOCH_PHOTOMETRY", data_release="Gaia DR3", data_structure="INDIVIDUAL", format="csv"); t = list(t.values())[0][0].to_pandas()
m = np.isfinite(t.g_transit_time) & (t.g_transit_flux > 0) & (t.variability_flag_g_reject.astype(str).str.lower() != "true")
S = {"Gaia G": (t.g_transit_time[m].values + 2455197.5, t.g_transit_flux[m].values / np.median(t.g_transit_flux[m]) - 1, t.g_transit_flux_error[m].values / np.median(t.g_transit_flux[m]))}
for b in ("BP", "RP"):
    tc, fc, ec, rj = f"{b.lower()}_obs_time", f"{b.lower()}_flux", f"{b.lower()}_flux_error", f"variability_flag_{b.lower()}_reject"
    mm = np.isfinite(t[tc]) & (t[fc] > 0) & (t[rj].astype(str).str.lower() != "true"); S[f"Gaia {b}"] = (t[tc][mm].values + 2455197.5, t[fc][mm].values / np.median(t[fc][mm]) - 1, t[ec][mm].values / np.median(t[fc][mm]))
z = pd.read_csv(f"ztf_{gid}.csv")
for b in ("zg", "zr"):
    x = z[z.filtercode == b]; y = 10 ** (-0.4 * (x.mag - np.median(x.mag))) - 1; S[f"ZTF {b[1]}"] = (x.mjd.values + 2400000.5, y.values, (x.magerr * 0.921).values)
def harm(tt, f, t0=2459000.0): return np.vstack([fn(2 * np.pi * k * f * (tt - t0)) for k in (1, 2) for fn in (np.cos, np.sin)]).T
def chi_common(f, keys):
    T, Y, E, G = [], [], [], []
    for i, k in enumerate(keys):
        tt, y, e = S[k]; X = np.hstack([np.ones((len(tt), 1)), harm(tt, f)]); c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; a = np.hypot(c[1], c[2])
        T.append(tt); Y.append((y - c[0]) / a); E.append(e / a); G.append(np.full(len(tt), i))
    tt, y, e = map(np.concatenate, (T, Y, E)); X = harm(tt, f); c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; return np.sum(((y - X @ c) / e) ** 2)
for k, (tt, y, e) in S.items():
    ls = LombScargle(tt, y, e); FR = np.linspace(0.2, 5, 200000); p = ls.power(FR)
    print(k, len(tt), "peak", round(FR[np.argmax(p)], 5), "| power at 2.170:", round(p[np.abs(FR - 2.170) < 0.01].max(), 3), " at 1.167:", round(p[np.abs(FR - 1.167) < 0.01].max(), 3))
keys = ["Gaia G", "ZTF g", "ZTF r"]
for f0 in (2.170, 1.167, 3.173, 0.8330, 1.1695):
    g = np.linspace(f0 - 0.004, f0 + 0.004, 4001); ch = np.array([chi_common(f, keys) for f in g]); k = np.argmin(ch); print(f"candidate {f0}: best f {g[k]:.6f} c/d (P {24 / g[k]:.4f} h), chi2 {ch[k]:.1f}, N {sum(len(S[x][0]) for x in keys)}")
for k in ("Gaia BP", "Gaia RP", "Gaia G", "ZTF g", "ZTF r"):
    tt, y, e = S[k]; X = np.hstack([np.ones((len(tt), 1)), harm(tt, 2.16998)]); c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; r = y - X @ c
    cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None])) * max(np.sum((r / e) ** 2) / (len(tt) - 5), 1); print(k, "semi-amplitude %", round(100 * np.hypot(c[1], c[2]), 2), "+-", round(100 * np.sqrt(cov[1, 1]), 2))
o = Observations.query_criteria(target_name="875311151", obs_collection="TESS", dataproduct_type="timeseries"); print("TESS 2-min:", sorted(set(o["sequence_number"])) if len(o) else "none", set(o["t_exptime"]) if len(o) else "")

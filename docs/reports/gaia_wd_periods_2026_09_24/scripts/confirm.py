# ATLAS confirmation of Gaia DR3 GLS frequencies for the lane candidates. For each available atlas_<id>.txt:
# broad GLS 0.05-50 c/d (fractional flux vs Gaia G flux); narrow search at f_gaia +- 0.01 c/d (also f/2 and 2f); amplitude compared with
# 30 random control windows of the same width in 0.5-50 c/d; Gaia G fold at the ATLAS frequency: times of maximum compared (T0 = 2458000).
import sys, glob, numpy as np, pandas as pd
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.timeseries import LombScargle
import astropy.units as u
GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m"); T0 = 2458000.0
U = pd.read_csv("unconfirmed.csv", dtype={"source_id": str}).set_index("source_id")
def load(i):
    r = U.loc[i]; c0 = SkyCoord(r.ra * u.deg, r.dec * u.deg); REF = 3631e6 * 10 ** (-0.4 * r.phot_g_mean_mag)
    L = [l for l in open(f"atlas_{i}.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
    ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]; T, Y, E, B = [], [], [], []
    for b in ("c", "o"):
        s = [x for x in ok if x["F"] == b]
        if len(s) < 20: continue
        med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
        mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
        season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
        for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
        clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
        t = Time(mjd[clip], format="mjd", scale="utc", location=GEO); T += list((t.tdb + t.light_travel_time(c0)).jd); Y += list(f[clip] / REF); E += list(e[clip] / REF); B += [b] * clip.sum()
    return map(np.array, (T, Y, E, B))
def fit(t, y, e, f, B=None):
    cols = [np.ones_like(t)] + ([(B == "c").astype(float)] if B is not None and len(set(B)) > 1 else []); k = len(cols)
    X = np.vstack(cols + [np.sin(2*np.pi*f*(t-T0)), np.cos(2*np.pi*f*(t-T0))]).T; W = 1/e**2
    p = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*y)); C = np.linalg.inv(X.T @ (X*W[:, None])); c2 = max(np.sum(W*(y-X@p)**2)/(len(t)-len(p)), 1)
    a, b = p[k], p[k+1]; return 100*np.hypot(a, b), 100*np.sqrt(c2*(C[k,k]+C[k+1,k+1])/2), T0 + (np.arctan2(a, b) % (2*np.pi)) / (2*np.pi*f)
def narrow(t, y, e, B, lo, hi):
    fr = np.arange(lo, hi, 0.1 / (t.max() - t.min())); P = LombScargle(t, y, e).power(fr); k = np.argmax(P); a, ea, tm = fit(t, y, e, fr[k], B); return fr[k], P[k], a, ea, tm
rng = np.random.default_rng(7); rows = []
for fn in sorted(glob.glob("atlas_*.txt")):
    i = fn[6:-4]
    if i not in U.index: continue
    t, y, e, B = load(i); fg = U.loc[i, "gls_freq_g_fov"]
    fr = np.arange(0.05, 50, 0.2 / (t.max() - t.min())); ls = LombScargle(t, y, e); P = ls.power(fr); k = np.argmax(P)
    out = dict(source_id=i, n=len(t), f_gaia=round(fg, 5), atlas_top=round(fr[k], 5), atlas_top_fap=float(f"{ls.false_alarm_probability(P[k], minimum_frequency=0.05, maximum_frequency=50, method='baluev'):.2g}"))
    ctrl = np.array([narrow(t, y, e, B, lo, lo + 0.02)[2] for lo in rng.uniform(0.5, 49.5, 30)])
    for tag, ff in (("f", fg), ("2f", 2 * fg), ("f/2", fg / 2)):
        if ff < 0.06: continue
        fb, Pb, a, ea, tm = narrow(t, y, e, B, ff - 0.01, ff + 0.01); out[f"{tag}_atlas"] = round(fb, 6); out[f"{tag}_amp"] = round(a, 2); out[f"{tag}_eamp"] = round(ea, 2)
        out[f"{tag}_ctrl_pct"] = round(100 * np.mean(ctrl < a)); out[f"{tag}_tmax"] = round(tm, 4)
    out["ctrl_med"] = round(np.median(ctrl), 2); out["ctrl_max"] = round(ctrl.max(), 2)
    # Gaia fold at the ATLAS frequency
    try:
        g = pd.read_csv(f"epphot_{i}.csv"); g = g[(g.GrVFlag == 0) & np.isfinite(g.FG)]; tg = g.TimeG.values + 2455197.5; yg = g.FG.values / np.median(g.FG) - 1; eg = g.e_FG.values / np.median(g.FG)
        a, ea, tm = fit(tg, yg, eg, out["f_atlas"]) if "f_atlas" in out else (np.nan, np.nan, np.nan); out["gaia_amp_at_fatlas"] = round(a, 2); out["gaia_eamp"] = round(ea, 2); out["gaia_tmax"] = round(tm, 4)
    except Exception as ex: out["gaia_err"] = str(ex)[:40]
    rows.append(out); print(out, flush=True)
pd.DataFrame(rows).to_csv("confirm.csv", index=False)

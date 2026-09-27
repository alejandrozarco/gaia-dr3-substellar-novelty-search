"""Gaia DR3 epoch photometry of the short-timescale GF21 white dwarfs (vst_new.csv): G-band generalised Lomb-Scargle (5-100 c/d; Baluev FAP),
G/BP/RP semi-amplitudes at the G peak (sinusoid + harmonic), RP/BP ratio."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia; from astropy.timeseries import LombScargle
s = pd.read_csv("vst_new.csv", dtype={"GaiaDR3": str}); tabs = {}
for k0 in range(0, len(s), 50):
    dl = Gaia.load_data(ids=list(s.GaiaDR3[k0:k0 + 50]), retrieval_type="EPOCH_PHOTOMETRY", data_release="Gaia DR3", data_structure="INDIVIDUAL", format="csv")
    for k, v in dl.items():
        t = v[0].to_pandas() if hasattr(v[0], "to_pandas") else v[0]; tabs[str(t.source_id.iloc[0])] = t
def amp(t, f, fr):
    X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * fr * t) for k in (1, 2) for fn in (np.sin, np.cos)]).T
    c, *_ = np.linalg.lstsq(X, f, rcond=None); r = f - X @ c; cov = np.linalg.inv(X.T @ X) * np.var(r) * len(f) / max(len(f) - 5, 1)
    return np.hypot(c[1], c[2]) / c[0], np.sqrt(cov[1, 1]) / c[0]
rows = []; FR = np.linspace(5, 100, 400000)
for _, r in s.iterrows():
    t = tabs.get(r.GaiaDR3); d = dict(GaiaDR3=r.GaiaDR3)
    if t is None: rows.append(d); continue
    m = np.isfinite(t.g_transit_time) & (t.g_transit_flux > 0) & (t.variability_flag_g_reject.astype(str).str.lower() != "true")
    tg, fg, eg = t.g_transit_time[m].values, t.g_transit_flux[m].values, t.g_transit_flux_error[m].values
    ls = LombScargle(tg, fg, eg); p = ls.power(FR); k = np.argmax(p); f0 = FR[k]; d.update(f_gls=f0, P_gls_min=1440 / f0, fap=ls.false_alarm_probability(p[k], minimum_frequency=5, maximum_frequency=100))
    for b, tc, fc, rej in (("G", "g_transit_time", "g_transit_flux", "variability_flag_g_reject"), ("BP", "bp_obs_time", "bp_flux", "variability_flag_bp_reject"), ("RP", "rp_obs_time", "rp_flux", "variability_flag_rp_reject")):
        mm = np.isfinite(t[tc]) & np.isfinite(t[fc]) & (t[fc] > 0) & (t[rej].astype(str).str.lower() != "true")
        if mm.sum() >= 12: a, e = amp(t[tc][mm].values, t[fc][mm].values, f0); d[f"A_{b}"] = 100 * a; d[f"e_{b}"] = 100 * e
    rows.append(d)
A = pd.DataFrame(rows); s = s.merge(A, on="GaiaDR3", how="left"); s["RP_BP"] = s.A_RP / s.A_BP; s.to_csv("vst_gls.csv", index=False)
k = s[(s.fap < 1e-3) & (s.P_gls_min > 40) & (s.P_gls_min < 200) & (s.MG < 10.8)]
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
print(len(s), "measured;", (s.fap < 1e-3).sum(), "with FAP < 1e-3;", len(k), "with 40-200 min and M_G < 10.8")
print(k.sort_values("P_gls_min")[["GaiaDR3", "WDJname", "Gmag", "MG", "bprp", "TeffH", "P_gls_min", "fap", "A_G", "A_BP", "e_BP", "A_RP", "e_RP", "RP_BP"]].round(3).to_string(index=False))

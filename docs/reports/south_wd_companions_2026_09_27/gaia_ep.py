"""Gaia DR3 epoch photometry (DataLink EPOCH_PHOTOMETRY) for the southern short-period white dwarfs; sinusoid + harmonic at the
vari_spurious_signals GLS frequency in G, BP and RP (flux, rejected/flagged epochs removed); fractional semi-amplitudes and RP/BP ratio."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia
s = pd.read_csv("sample.csv", dtype={"source_id": str}); rows = []
dl = Gaia.load_data(ids=list(s.source_id), retrieval_type="EPOCH_PHOTOMETRY", data_release="Gaia DR3", data_structure="INDIVIDUAL", format="csv")
tabs = {}
for k, v in dl.items():
    t = v[0].to_pandas() if hasattr(v[0], "to_pandas") else v[0]; tabs[str(t.source_id.iloc[0])] = t
print(len(tabs), "epoch-photometry files")
def amp(t, f, fr):
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*fr*t), np.cos(2*np.pi*fr*t), np.sin(4*np.pi*fr*t), np.cos(4*np.pi*fr*t)]).T
    c, *_ = np.linalg.lstsq(X, f, rcond=None); r = f - X @ c; cov = np.linalg.inv(X.T @ X) * np.var(r) * len(f) / max(len(f) - 5, 1)
    return np.hypot(c[1], c[2]) / c[0], np.sqrt(cov[1, 1]) / c[0], len(f)
for _, r in s.iterrows():
    t = tabs.get(r.source_id); d = dict(source_id=r.source_id, f=r.gls_freq_g_fov)
    if t is None: d["status"] = "no epoch photometry"; rows.append(d); continue
    for b, tc, fc, rej in (("G", "g_transit_time", "g_transit_flux", "variability_flag_g_reject"), ("BP", "bp_obs_time", "bp_flux", "variability_flag_bp_reject"), ("RP", "rp_obs_time", "rp_flux", "variability_flag_rp_reject")):
        m = np.isfinite(t[tc]) & np.isfinite(t[fc]) & (t[fc] > 0) & (t[rej].astype(str).str.lower() != "true")
        if m.sum() < 12: continue
        a, e, n = amp(t[tc][m].values, t[fc][m].values, r.gls_freq_g_fov); d[f"A_{b}"] = 100 * a; d[f"e_{b}"] = 100 * e; d[f"n_{b}"] = n
    if "A_BP" in d and "A_RP" in d: d["RP_BP"] = d["A_RP"] / max(d["A_BP"], 1e-3)
    rows.append(d)
R = pd.DataFrame(rows).merge(s, on="source_id"); R.to_csv("south_amp.csv", index=False)
pd.set_option("display.width", 220)
print(R[["source_id", "phot_g_mean_mag", "bp_rp", "f", "TeffH", "MassH", "A_G", "A_BP", "e_BP", "A_RP", "e_RP", "RP_BP"]].sort_values("RP_BP", ascending=False).round(2).to_string(index=False))

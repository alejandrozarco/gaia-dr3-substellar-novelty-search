"""EB1 (Ranaivomanana+2025) short-period blue objects: Gaia DR3 epoch photometry G/BP/RP semi-amplitudes at the catalogue period (sinusoid +
harmonic, variability-rejected epochs removed), GF21 Teff/log g, CatWISE2020 W1/W2 excess vs Montreal pure-H G3-W colours, companion M_W1."""
import sys, numpy as np, pandas as pd, warnings, astropy.units as u; warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia; from astroquery.xmatch import XMatch; from astropy.table import Table
s = pd.read_csv(sys.argv[1], dtype={"GaiaDR3": str}); out = sys.argv[2]
dl = Gaia.load_data(ids=list(s.GaiaDR3), retrieval_type="EPOCH_PHOTOMETRY", data_release="Gaia DR3", data_structure="INDIVIDUAL", format="csv")
tabs = {}
for k, v in dl.items():
    t = v[0].to_pandas() if hasattr(v[0], "to_pandas") else v[0]; tabs[str(t.source_id.iloc[0])] = t
def amp(t, f, fr):
    X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * fr * t) for k in (1, 2) for fn in (np.sin, np.cos)]).T
    c, *_ = np.linalg.lstsq(X, f, rcond=None); r = f - X @ c; cov = np.linalg.inv(X.T @ X) * np.var(r) * len(f) / max(len(f) - 5, 1)
    return np.hypot(c[1], c[2]) / c[0], np.sqrt(cov[1, 1]) / c[0]
rows = []
for _, r in s.iterrows():
    t = tabs.get(r.GaiaDR3); d = dict(GaiaDR3=r.GaiaDR3, f=1 / r.Per)
    if t is None: rows.append(d); continue
    for b, tc, fc, rej in (("G", "g_transit_time", "g_transit_flux", "variability_flag_g_reject"), ("BP", "bp_obs_time", "bp_flux", "variability_flag_bp_reject"), ("RP", "rp_obs_time", "rp_flux", "variability_flag_rp_reject")):
        m = np.isfinite(t[tc]) & np.isfinite(t[fc]) & (t[fc] > 0) & (t[rej].astype(str).str.lower() != "true")
        if m.sum() >= 12: a, e = amp(t[tc][m].values, t[fc][m].values, 1 / r.Per); d[f"A_{b}"] = 100 * a; d[f"e_{b}"] = 100 * e
    rows.append(d)
A = pd.DataFrame(rows); s = s.merge(A, on="GaiaDR3", how="left"); s["RP_BP"] = s.A_RP / s.A_BP
T = Table.from_pandas(s[["GaiaDR3", "RA_ICRS", "DE_ICRS"]])
def xm(cat, r, cols):
    x = XMatch.query(cat1=T, cat2=cat, max_distance=r * u.arcsec, colRA1="RA_ICRS", colDec1="DE_ICRS").to_pandas(); x["GaiaDR3"] = x.GaiaDR3.astype(str)
    return x.sort_values("angDist").drop_duplicates("GaiaDR3")[["GaiaDR3"] + cols]
s = s.merge(xm("vizier:J/MNRAS/508/3877/maincat", 1.5, ["WDJname", "TeffH", "loggH", "MassH", "Plx"]), on="GaiaDR3", how="left")
s = s.merge(xm("vizier:II/365/catwise", 3, ["W1mproPM", "W2mproPM", "e_W1mproPM"]), on="GaiaDR3", how="left")
L = open("Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
M = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)]); iG, iW1 = hdr.index("G3"), hdr.index("W1")
def col(te, lg):
    if not (np.isfinite(te) and np.isfinite(lg)): return np.nan
    lg = min(max(lg, 7.0), 9.0); lo = min(np.floor(lg * 2) / 2, 8.5); v = []
    for l in (lo, lo + 0.5):
        q = M[np.isclose(M[:, 1], l)]; q = q[np.argsort(q[:, 0])]; v.append(np.interp(te, q[:, 0], q[:, iG] - q[:, iW1]))
    return float(np.interp(lg, [lo, lo + 0.5], v))
s["dW1"] = [(g - w) - col(te, lg) for g, w, te, lg in zip(s.Gmag, s.W1mproPM, s.TeffH, s.loggH)]
def mw1(r):
    if not (np.isfinite(r.dW1) and r.dW1 > 0.05 and np.isfinite(r.Plx) and r.Plx > 0): return np.nan
    wd = r.W1mproPM + r.dW1; return wd - 2.5 * np.log10(10 ** (0.4 * r.dW1) - 1) - 5 * np.log10(1000 / r.Plx / 10)
s["M_W1comp"] = s.apply(mw1, axis=1); s.to_csv(out, index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
print(s.sort_values("P_min")[["GaiaDR3", "WDJname", "Gmag", "GMAG", "BP-RP", "P_min", "TeffH", "MassH", "A_G", "A_BP", "e_BP", "A_RP", "e_RP", "RP_BP", "W1mproPM", "dW1", "M_W1comp", "LitClass"]].round(2).to_string(index=False))

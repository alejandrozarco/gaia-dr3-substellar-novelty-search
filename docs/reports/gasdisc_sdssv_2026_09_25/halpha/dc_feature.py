"""Feature search in SDSS-V white dwarfs classified without hydrogen lines (SnowWhite DC/DZ/DQ/DB families, 'nonH' group) on the
DAHe locus (0 < BP-RP < 0.6, 12 < M_G < 14.5, parallax/error > 3): chi2/dof of the stored 6400-6750 A coadd about a quadratic
continuum (3 rounds of 4-sigma clipping for the fit only), and the same for 4780-4940 A (H-beta). Featureless spectra give ~1."""
import numpy as np, pandas as pd
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
t = pd.read_csv("p2_final.csv", dtype={"sdss_id": str, "gaia": str})
s = t[t.plx_ok & (t.bprp > 0) & (t.bprp < 0.6) & (t.MG > 12) & (t.MG < 14.5) & (t.grp == "nonH")].copy()
def chi(f, iv, a, b):
    m = (GRID > a) & (GRID < b); w = GRID[m]; ok = (iv > 0) & np.isfinite(f)
    if ok.sum() < 50: return np.nan, np.nan
    x = (w - w.mean()) / (w.max() - w.min()); use = ok.copy()
    for _ in range(3):
        p = np.polyfit(x[use], f[use], 2, w=np.sqrt(iv[use])); r = (f - np.polyval(p, x)) * np.sqrt(iv); use = ok & (np.abs(r) < 4)
    return float(np.sum(r[ok] ** 2) / (ok.sum() - 3)), float(np.median(np.polyval(p, x) * np.sqrt(iv[ok])))
out = []
for r in s.itertuples():
    d = np.load(f"store/{r.sdss_id[-2:]}/{r.sdss_id}.npz")
    ca, sa = chi(d["f_6400"].astype(float), d["iv_6400"].astype(float), 6400, 6750); cb, sb = chi(d["f_4780"].astype(float), d["iv_4780"].astype(float), 4780, 4940)
    out.append(dict(sdss_id=r.sdss_id, gaia=r.gaia, cls=r.cls, G=r.G, bprp=r.bprp, MG=r.MG, chi_ha=round(ca, 2), snr_ha=round(sa, 1), chi_hb=round(cb, 2), snr_hb=round(sb, 1)))
o = pd.DataFrame(out); o.to_csv("dc_feature.csv", index=False)
print(len(o), o[["chi_ha", "chi_hb"]].quantile([.5, .9, .99]).round(2).to_string())
for sid in ("78995796", "61248548"):
    x = o[o.sdss_id == sid]; print(sid, x.to_string(index=False, header=False), "rank chi_ha", int((o.chi_ha > x.chi_ha.iloc[0]).sum()) + 1)
pd.set_option("display.width", 200); print(o.sort_values("chi_ha", ascending=False).head(30).to_string())

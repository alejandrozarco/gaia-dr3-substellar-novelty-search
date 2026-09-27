"""Southern red-rising Gaia WDs: CatWISE2020 W1/W2 and VHS DR5 J/Ks against Montreal pure-H photometry at GF21 Teff/log g, scaled at Gaia G;
TESS sector list."""
import numpy as np, pandas as pd, astropy.units as u, warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier; from astropy.coordinates import SkyCoord; from astroquery.mast import Tesscut
R = pd.read_csv("south_amp.csv", dtype={"source_id": str}); R = R[R.RP_BP > 1.7]
L = open("Table_DA.txt").readlines(); hdr = L[1].replace("log g", "logg").split()
D = np.array([[float(x) for x in l.split()] for l in L[2:] if len(l.split()) == len(hdr)]); ix = {k: hdr.index(k) for k in ("G3", "W1", "W2", "Ks")}; ix["J"] = hdr.index("J")
def mcol(te, lg, c):
    lg = min(max(lg, 7.0), 9.0); lo = np.floor(lg * 2) / 2; hi = min(lo + 0.5, 9.0); v = []
    for l in (lo, hi):
        q = D[np.isclose(D[:, 1], l)]; q = q[np.argsort(q[:, 0])]; v.append(np.interp(te, q[:, 0], q[:, ix["G3"]] - q[:, ix[c]]))
    return np.interp(lg, [lo, hi], v) if hi > lo else v[0]
V = Vizier(columns=["**"], row_limit=3); rows = []
for _, r in R.iterrows():
    c = SkyCoord(r.ra, r.dec, unit="deg"); d = dict(source_id=r.source_id, P_min=round(1440 / r.f, 1), G=r.phot_g_mean_mag, dist=round(1000 / r.parallax), Teff=r.TeffH, M=r.MassH, RP_BP=round(r.RP_BP, 2))
    try:
        w = V.query_region(c, radius=3 * u.arcsec, catalog="II/365/catwise")
        if len(w): d["W1"] = float(w[0]["W1mproPM"][0]); d["W2"] = float(w[0]["W2mproPM"][0])
        v = V.query_region(c, radius=2 * u.arcsec, catalog="II/367/vhs_dr5")
        if len(v): d["J"] = float(v[0]["Jpmag"][0]) if np.ma.is_masked(v[0]["Jpmag"][0]) is False else np.nan; d["Ks"] = float(v[0]["Kspmag"][0]) if not np.ma.is_masked(v[0]["Kspmag"][0]) else np.nan
    except Exception as ex: d["hole"] = str(ex)[:60]
    if np.isfinite(r.TeffH):
        for b in ("J", "Ks", "W1", "W2"):
            if b in d and np.isfinite(d[b]): d["d" + b] = round((r.phot_g_mean_mag - d[b]) - mcol(r.TeffH, r.loggH, b), 2)
        if "W1" in d and np.isfinite(d.get("dW1", np.nan)):
            wd = d["W1"] + d["dW1"]; comp = wd - 2.5 * np.log10(10 ** (0.4 * d["dW1"]) - 1) if d["dW1"] > 0 else np.nan; d["M_W1comp"] = round(comp - 5 * np.log10(1000 / r.parallax / 10), 2)
    try: d["tess_sectors"] = len(Tesscut.get_sectors(coordinates=c))
    except Exception: d["tess_sectors"] = -1
    rows.append(d)
O = pd.DataFrame(rows); O.to_csv("south_ir.csv", index=False); pd.set_option("display.width", 220); print(O.round(2).to_string(index=False))

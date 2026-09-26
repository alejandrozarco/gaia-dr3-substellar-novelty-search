# Local prior-art crossmatch for the SnowWhite CV selection (classification LIKE '%CV%' OR p_cv > 0.3; SDSS DR20
# snow_white_boss_star, Astra 0.8.1). Positions: Gaia DR3 (epoch 2016.0) propagated to J2000.0 with the Gaia proper motion.
# Catalogues (downloaded from VizieR 2026-09-23 into cat/):
#   Inight+2025 J/MNRAS/536/1057 (SDSS-V 2020-2023 ML CVs), Inight+2023b J/MNRAS/525/3597, Inight+2023a J/MNRAS/524/4867 (a1+a2),
#   Ritter&Kolb B/cb (cbdata, pcbdata, lmxbdata), Downes V/123A, Rodriguez+2025 J/PASP/137/A4201, Wang+2025 J/A+A/698/A321.
# Match: Gaia DR3 id where the catalogue carries one, else position within R arcsec of the J2000 (and of the 2016.0) position.
import numpy as np, pandas as pd, warnings, json
warnings.filterwarnings("ignore")
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u

sw = pd.read_csv("sw_cv_raw.csv", skiprows=1)
g = pd.read_csv("gaia_dr3_605.csv")
sw = sw.merge(g, left_on="gaia_dr3_source_id", right_on="source_id", how="left", suffixes=("", "_g"))
dt = 2000.0 - 2016.0
ra0 = np.where(np.isfinite(sw.ra_g), sw.ra_g, sw.ra); de0 = np.where(np.isfinite(sw.dec_g), sw.dec_g, sw.dec)
pmra = np.nan_to_num(sw.pmra_g.values); pmde = np.nan_to_num(sw.pmdec.values)
sw["ra2000"] = ra0 + pmra * dt / 3.6e6 / np.cos(np.radians(de0)); sw["de2000"] = de0 + pmde * dt / 3.6e6
sw["ra2016"] = ra0; sw["de2016"] = de0
c2000 = SkyCoord(sw.ra2000.values * u.deg, sw.de2000.values * u.deg); c2016 = SkyCoord(sw.ra2016.values * u.deg, sw.de2016.values * u.deg)

def load(f):
    # NOTE: Table.to_pandas() turns masked int64 Gaia ids into float -> precision loss (4707482485122305536 -> ...6048).
    # Fill masked integer columns with -1 first and keep them int64.
    t = Table.read("cat/" + f + ".ecsv")
    for c in t.colnames:
        if t[c].dtype.kind in "iu" and hasattr(t[c], "mask"):
            t[c] = t[c].astype("int64").filled(-1) if t[c].dtype.kind == "i" else t[c].filled(0)
    p = t.to_pandas()
    for c in p.columns:
        if "gaia" in c.lower(): assert p[c].dtype.kind in "iuO", (f, c, p[c].dtype)
    return p

def radec(t):
    for rc, dc in (("RAJ2000", "DEJ2000"), ("RA_ICRS", "DE_ICRS")):
        if rc in t.columns:
            if t[rc].dtype == object:  # sexagesimal
                c = SkyCoord(t[rc].astype(str).values, t[dc].astype(str).values, unit=(u.hourangle, u.deg))
                return c
            return SkyCoord(t[rc].values * u.deg, t[dc].values * u.deg)
    raise KeyError("no coords")

res = {k: [] for k in range(len(sw))}
cats = [("Inight2025", "J_MNRAS_536_1057_table1", "GaiaEDR3", 3, "Vtype"),
        ("Inight2023b", "J_MNRAS_525_3597_tablea1", "GaiaEDR3", 3, "VType"),
        ("Inight2023a", "J_MNRAS_524_4867_tablea1", "GaiaEDR3", 3, "VType"),
        ("RK_cb", "B_cb_cbdata", None, 10, "Type1"), ("RK_pcb", "B_cb_pcbdata", None, 10, "Type1"), ("RK_lmxb", "B_cb_lmxbdata", None, 10, "Type1"),
        ("Downes", "V_123A_cv", None, 10, "VarType"),
        ("Rodriguez2025_300", "J_PASP_137_A4201_cv_300", "GaiaDR3", 5, None), ("Rodriguez2025_1000", "J_PASP_137_A4201_cv_1000", "GaiaDR3", 5, None),
        ("Wang2025_cvs", "J_A+A_698_A321_cvs", "GaiaDR3", 5, "Name"), ("Wang2025_cand", "J_A+A_698_A321_cand", "GaiaDR3", 5, "Name")]
summary = {}
for lab, f, gcol, rad, tcol in cats:
    t = load(f); n = 0
    try:
        ct = radec(t)
    except Exception as e:
        ct = None
    for i in range(len(sw)):
        hit = None
        if gcol and gcol in t.columns and np.isfinite(sw.gaia_dr3_source_id[i]):
            m = t[t[gcol].astype(str) == str(int(sw.gaia_dr3_source_id[i]))]
            if len(m): hit = (m.index[0], "gaia_id")
        if hit is None and ct is not None:
            for cc in (c2000[i], c2016[i]):
                sep = cc.separation(ct).arcsec
                j = int(np.nanargmin(sep))
                if sep[j] < rad: hit = (t.index[j], f"pos {sep[j]:.1f}\""); break
        if hit is not None:
            row = t.loc[hit[0]]
            name = str(row.get("Name", row.get("SDSS", row.get("IAUName", ""))))
            typ = str(row.get(tcol, "")) if tcol else ""
            res[i].append(f"{lab}[{name}|{typ}|{hit[1]}]"); n += 1
    summary[lab] = n; print(lab, len(t), "matched", n, flush=True)
sw["local_hits"] = [";".join(res[i]) for i in range(len(sw))]
sw["n_local"] = [len(res[i]) for i in range(len(sw))]
sw.to_csv("sw_cv_xlocal.csv", index=False)
print(summary)
print("objects with any local hit:", (sw.n_local > 0).sum(), "of", len(sw))

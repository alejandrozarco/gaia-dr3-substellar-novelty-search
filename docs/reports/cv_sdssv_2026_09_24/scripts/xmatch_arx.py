# Crossmatch the SnowWhite CV selection with identifiers extracted from arXiv sources (cat/arxiv_ids.csv) and the Inight+2026
# DESI CV table (cat/Inight2026_DESI_tabledata.csv): exact Gaia DR3 id match, or J-name/table position within 3" of the J2000
# or 2016.0 position. Adds column arx_hits to sw_cv_xlocal.csv -> sw_cv_x2.csv
import pandas as pd, numpy as np
from astropy.coordinates import SkyCoord; import astropy.units as u
sw = pd.read_csv("sw_cv_xlocal.csv")
a = pd.read_csv("cat/arxiv_ids.csv", dtype=str)
de = pd.read_csv("cat/Inight2026_DESI_tabledata.csv", dtype={"EDR3_source_id": str})
gid = sw.gaia_dr3_source_id.astype("int64").astype(str)
c20 = SkyCoord(sw.ra2000.values * u.deg, sw.de2000.values * u.deg); c16 = SkyCoord(sw.ra2016.values * u.deg, sw.de2016.values * u.deg)
hits = [[] for _ in range(len(sw))]
ids = a[a.kind.str.startswith("gaia")]
for i, g in enumerate(gid):
    for _, r in ids[ids.token == g].iterrows(): hits[i].append(f"{r.label}[gaia_id]")
    for _, r in de[de.EDR3_source_id == g].iterrows(): hits[i].append(f"Inight2026DESI[{r.Name}|{r.Variable_type}|gaia_id]")
jn = a[a.kind.str.startswith("Jname")].copy(); jn["ra"] = jn.ra.astype(float); jn["dec"] = jn.dec.astype(float)
cj = SkyCoord(jn.ra.values * u.deg, jn.dec.values * u.deg); cd = SkyCoord(de.ra.values * u.deg, de.dec.values * u.deg)
for cc in (c20, c16):
    idx, sep, _ = cc.match_to_catalog_sky(cj)
    for i in np.where(sep.arcsec < 3)[0]:
        r = jn.iloc[idx[i]]; s = f"{r.label}[{r.token}|{sep[i].arcsec:.1f}\"]"
        if not any(r.label in h for h in hits[i]): hits[i].append(s)
    idx, sep, _ = cc.match_to_catalog_sky(cd)
    for i in np.where(sep.arcsec < 3)[0]:
        r = de.iloc[idx[i]]; s = f"Inight2026DESI[{r.Name}|{r.Variable_type}|{sep[i].arcsec:.1f}\"]"
        if not any("Inight2026DESI" in h for h in hits[i]): hits[i].append(s)
sw["arx_hits"] = [";".join(h) for h in hits]; sw["n_arx"] = [len(h) for h in hits]
sw.to_csv("sw_cv_x2.csv", index=False)
print("objects with arXiv/DESI hits:", (sw.n_arx > 0).sum(), " of which no local hit:", ((sw.n_arx > 0) & (sw.n_local == 0)).sum())
print("any prior hit:", ((sw.n_arx > 0) | (sw.n_local > 0)).sum())
for lab in ["Brink", "Inight2026DESI", "Schwope+2026", "Hernandez", "Galiullin", "Mendoza", "Kepler", "Dag", "Wang", "Rodriguez", "van Roestel", "Liu", "Zhao"]:
    print(lab, sum(lab in h for h in sw.arx_hits))

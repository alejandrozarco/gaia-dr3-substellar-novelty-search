"""DESI DR1 emission-line DA sample (Amorim+2026 classes DAe, DAE, DA+) with Gaia DR3 (1.5") and CatWISE2020 (3") via CDS XMatch."""
import pandas as pd, numpy as np, astropy.units as u, warnings; warnings.filterwarnings("ignore")
from astroquery.xmatch import XMatch; from astropy.table import Table
d = pd.read_csv("docs/reports/gasdisc_desi_dr1_2026_09_26/desi_pass2.csv.gz", dtype={"targetid": str})
s = d[d.cls.isin(["DAe", "DAE", "DA+"])].copy()
T = Table.from_pandas(s[["targetid", "name", "ra", "dec"]])
def xm(cat, r):
    x = XMatch.query(cat1=T, cat2=cat, max_distance=r * u.arcsec, colRA1="ra", colDec1="dec").to_pandas(); x["targetid"] = x.targetid.astype(str)
    return x.sort_values("angDist").drop_duplicates("targetid")
g = xm("vizier:I/355/gaiadr3", 1.5)[["targetid", "Source", "Gmag", "BP-RP", "Plx", "e_Plx"]].rename(columns={"Source": "gaia"}); g["gaia"] = g.gaia.astype("int64").astype(str)
w = xm("vizier:II/365/catwise", 3)[["targetid", "W1mproPM", "e_W1mproPM", "W2mproPM", "e_W2mproPM", "angDist"]].rename(columns={"angDist": "wsep"})
s = s.merge(g, on="targetid", how="left").merge(w, on="targetid", how="left"); s.to_csv("dae_sample.csv", index=False)
print(len(s), s.gaia.notna().sum(), s.W1mproPM.notna().sum())

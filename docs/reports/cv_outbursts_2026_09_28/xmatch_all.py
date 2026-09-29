"""Bulk front-filter of the ALeRCE CV/Nova list with the CDS XMatch service. Writes xm_<tag>.csv per catalogue
(oid + nearest match within the radius) and prints match counts. A failed catalogue is reported as HOLE."""
import pandas as pd, numpy as np, time, io
from astropy.table import Table
import astropy.units as u
from astroquery.xmatch import XMatch
A = pd.read_csv("alerce_cvnova.csv").sort_values("probability", ascending=False).drop_duplicates("oid")[["oid", "meanra", "meandec"]]
A.to_csv("objects.csv", index=False); T = Table.from_pandas(A)
CATS = [("vsx", "vizier:B/vsx/vsx", 5), ("simbad", "simbad", 5), ("gaia", "vizier:I/355/gaiadr3", 2), ("rk", "vizier:B/cb/cbdata", 5),
        ("szk1a", "vizier:J/AJ/159/198/table1", 5), ("szk1b", "vizier:J/AJ/159/198/table2", 5), ("szk1c", "vizier:J/AJ/159/198/table3", 5),
        ("szk2a", "vizier:J/AJ/162/94/table1", 5), ("szk2b", "vizier:J/AJ/162/94/table2", 5), ("inight", "vizier:J/MNRAS/524/4867/tablea1", 5),
        ("desi", "vizier:J/ApJS/282/26/table3", 5), ("canbay", "vizier:J/AJ/169/87/table1", 5), ("lamost", "vizier:J/AJ/165/148/table1", 5),
        ("inight21", "vizier:J/MNRAS/504/2420/tablea3", 5), ("pb", "vizier:J/A+A/687/A305/tableb2", 5), ("erosita_cv", "vizier:J/A+A/690/A243/tablea1", 5),
        ("allwise", "vizier:II/328/allwise", 3), ("erass1", "vizier:J/A+A/682/A34/erass1-m", 15), ("erass3", "vizier:J/A+A/712/A171/erass3-m", 15)]
for tag, cat, rad in CATS:
    for k in range(3):
        try:
            t0 = time.time(); R = XMatch.query(cat1=T, cat2=cat, max_distance=rad * u.arcsec, colRA1="meanra", colDec1="meandec").to_pandas()
            R = R.sort_values("angDist").drop_duplicates("oid"); R.to_csv(f"xm_{tag}.csv", index=False)
            print(f"{tag:11s} {cat:40s} r={rad:>2}\"  matched {len(R):6d} / {len(A)}  ({time.time()-t0:.0f}s)", flush=True); break
        except Exception as e:
            print(f"{tag:11s} attempt {k+1} failed: {type(e).__name__} {str(e)[:120]}", flush=True); time.sleep(20)
    else: print(f"{tag:11s} HOLE", flush=True)

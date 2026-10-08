import sys, os, numpy as np
os.environ["DRY"] = "1"; sys.argv = ["holdout2.py", sys.argv[1]]
try: exec(open("holdout2.py").read())
except SystemExit: pass
from astropy.time import Time
E = fit_ephem(df[df.blk.str.startswith("TESS")], "TESS only")
for d_ in ("2026-11-01", "2027-03-31"):
    tp, sT, n = predict(E, Time(d_, scale="utc").tdb.jd); print(d_, f"pred sigma {sT*1440:.1f} min = {sT*E['f']:.3f} cyc")

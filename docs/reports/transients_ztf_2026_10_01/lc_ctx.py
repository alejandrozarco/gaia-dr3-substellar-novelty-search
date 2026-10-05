"""ALeRCE detections, prior non-detections and a VizieR 4-arcsec context (PS1, Gaia DR3, 2MASS, unWISE) for one ZTF object
(2026-09-30). Usage: python lc_ctx.py <oid> <ra> <dec>"""
import sys, requests, pandas as pd
from astroquery.vizier import Vizier; import astropy.units as u, astropy.coordinates as c
o, ra, de = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); A = "https://api.alerce.online/ztf/v1"
d = pd.DataFrame(requests.get(f"{A}/objects/{o}/detections", timeout=60).json()).sort_values("mjd"); n = pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections", timeout=60).json())
print(d[["mjd", "fid", "magpsf", "sigmapsf", "drb", "isdiffpos", "distnr"]].to_string(index=False))
if len(n): print("non-detections: before first", n[n.mjd < d.mjd.min()].sort_values("mjd").tail(4)[["mjd", "fid", "diffmaglim"]].values.tolist(), "| after first", len(n[n.mjd > d.mjd.min()]), "e.g.", n[n.mjd > d.mjd.min()].sort_values("mjd").tail(4)[["mjd", "fid", "diffmaglim"]].values.tolist())
v = Vizier(columns=["**"], row_limit=10)
for cat in ("II/349/ps1", "I/355/gaiadr3", "II/246/out", "II/363/unwise"):
    try:
        t = v.query_region(c.SkyCoord(ra * u.deg, de * u.deg), radius=4 * u.arcsec, catalog=cat)
        if len(t):
            t = t[0]; keep = [k for k in t.colnames if k in ("_r", "gmag", "rmag", "imag", "zmag", "ymag", "Gmag", "BP-RP", "Plx", "Jmag", "Kmag", "FW1", "FW2")]; print(cat); print(t[keep])
        else: print(cat, "none within 4 arcsec")
    except Exception as ex: print(cat, "HOLE", repr(ex)[:80])

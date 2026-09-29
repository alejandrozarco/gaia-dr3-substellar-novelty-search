"""Catalogue fields for the two VSX drafts (2026-09-29): VSX live API (with a positive control), constellation, J2000 position
(Gaia DR3 moved to epoch 2000.0), aliases from SIMBAD and VizieR cones, ATLAS-REFCAT2 and Gaia magnitudes. Output: vsx_fields.json."""
import requests, json, numpy as np
from astropy.coordinates import SkyCoord, get_constellation
import astropy.units as u
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
STARS = {"WDJ1438-3051": dict(gaia="6217118886429978112", ra=219.6860257892086, dec=-30.863470766084053, pmra=-3.4456, pmdec=-16.3956),
         "WDJ1118-5442": dict(gaia="5346312514819760896", ra=169.5127880261117, dec=-54.705022753182064, pmra=-10.7120, pmdec=-2.8306)}
def vsx(ra, dec, r_deg):
    return requests.get(f"https://vsx.aavso.org/index.php?view=api.list&ra={ra}&dec={dec}&radius={r_deg}&format=json", timeout=60).json()
out = {}
for name, s in STARS.items():
    ra0 = s["ra"] - s["pmra"] * 16 / 3.6e6 / np.cos(np.radians(s["dec"])); de0 = s["dec"] - s["pmdec"] * 16 / 3.6e6
    c = SkyCoord(ra0 * u.deg, de0 * u.deg); r = dict(pos_j2000=c.to_string("hmsdms", sep=" ", precision=2), constellation=get_constellation(c))
    v = vsx(ra0, de0, 0.01); r["vsx_36arcsec"] = v; v2 = vsx(ra0, de0, 0.5); r["vsx_30arcmin_count"] = len((v2.get("VSXObjects") or {}).get("VSXObject", []) or [])
    try:
        ids = Simbad.query_objectids(f"Gaia DR3 {s['gaia']}"); r["simbad_ids"] = [str(x) for x in ids[ids.colnames[0]]]
    except Exception as e: r["simbad_ids"] = f"HOLE {e}"
    for cat, key in (("II/246/out", "2MASS"), ("II/328/allwise", "AllWISE"), ("J/ApJ/867/105/refcat2", "refcat2"), ("IV/39/tic82", "TIC")):
        try:
            t = Vizier(columns=["**"], row_limit=3).query_region(SkyCoord(s["ra"] * u.deg, s["dec"] * u.deg), radius=3 * u.arcsec, catalog=cat)
            r[key] = {k: str(t[0][k][0]) for k in t[0].colnames[:40]} if len(t) else "none within 3 arcsec"
        except Exception as e: r[key] = f"HOLE {e}"
    out[name] = r
# positive control: the API must return a known VSX star at its own position (AM Her)
ctrl = vsx(274.0555, 49.8678, 0.01); out["_control_AM_Her"] = len((ctrl.get("VSXObjects") or {}).get("VSXObject", []) or [])
json.dump(out, open("vsx_fields.json", "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str)[:6000])

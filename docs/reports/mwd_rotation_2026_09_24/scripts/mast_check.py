# Which targets have K2 / TESS short-cadence (SPOC/TESS-SPOC/QLP...) time series on MAST? (public, no account)
import json, sys, time
from astroquery.mast import Observations
from astropy.coordinates import SkyCoord
import astropy.units as u
T = json.load(open("data/targets.json")) + json.load(open("data/controls.json"))
out = {}
for rec in T:
    sid = rec["source_id"]; c = SkyCoord(float(rec["ra"]) * u.deg, float(rec["dec"]) * u.deg)
    try:
        obs = Observations.query_criteria(coordinates=c, radius=10 * u.arcsec, obs_collection=["K2", "TESS", "Kepler"], dataproduct_type="timeseries")
    except Exception as e:
        print(sid, "HOLE", repr(e)[:200]); out[sid] = "HOLE"; continue
    L = []
    for o in obs:
        L.append(dict(coll=str(o["obs_collection"]), target=str(o["target_name"]), prov=str(o["provenance_name"]), exp=float(o["t_exptime"]) if o["t_exptime"] else None,
                      seq=str(o["sequence_number"]), dist=float(o["distance"]) if "distance" in o.colnames else None, obsid=str(o["obs_id"])))
    out[sid] = L
    s = ", ".join(sorted(set(f"{x['coll']}/{x['prov']}/{x['exp']}s/{x['target']}" for x in L)))
    print(sid, rec.get("name", "")[:24].ljust(24), "G=%.2f" % float(rec["phot_g_mean_mag"]), "n=%d" % len(L), s[:300], flush=True)
    time.sleep(0.5)
json.dump(out, open("data/mast_timeseries.json", "w"), indent=1)

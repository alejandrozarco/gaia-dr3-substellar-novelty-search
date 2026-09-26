"""All-table VizieR cone (6") + Gaia DR3 neighbours (10") for the 8 pilot candidates.
Every table returned is listed; a failed query is written as a HOLE, never as 'nothing found'."""
import json, sys, time
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
R = [json.loads(l) for l in open(f"{A}/results.jsonl")]
C = [r for r in R if r.get("status") == "CANDIDATE"]
out = {}
for r in C:
    sid = r["source_id"]; c = SkyCoord(r["ra"], r["dec"], unit="deg")
    rec = dict(ra=r["ra"], dec=r["dec"], P=r["P"], tables=None, gaia=None)
    for attempt in range(3):
        try:
            v = Vizier(columns=["**", "_r"], row_limit=20); v.TIMEOUT = 900
            res = v.query_region(c, radius=6 * u.arcsec)
            tabs = []
            for name in res.keys():
                t = res[name]
                rmin = float(min(t["_r"])) if "_r" in t.colnames and len(t) else None
                cols = [x for x in t.colnames]
                first = {k: str(t[0][k]) for k in cols[:40]} if len(t) else {}
                tabs.append(dict(table=name, n=len(t), rmin=rmin, row=first))
            rec["tables"] = tabs; break
        except Exception as e:
            rec["tables_error"] = f"{type(e).__name__}: {e}"[:300]; time.sleep(20)
    try:
        g = Vizier(columns=["Source", "RA_ICRS", "DE_ICRS", "Gmag", "BP-RP", "Plx", "RUWE", "_r"], row_limit=50)
        g.TIMEOUT = 300
        gt = g.query_region(c, radius=10 * u.arcsec, catalog="I/355/gaiadr3")
        rec["gaia"] = [dict(src=str(x["Source"]), G=float(x["Gmag"]) if x["Gmag"] is not None else None,
                            bprp=str(x["BP-RP"]), plx=str(x["Plx"]), ruwe=str(x["RUWE"]), r=float(x["_r"]))
                       for x in gt[0]] if len(gt) else []
    except Exception as e:
        rec["gaia_error"] = f"{type(e).__name__}: {e}"[:300]
    out[sid] = rec
    nt = len(rec["tables"]) if rec["tables"] is not None else "HOLE"
    print(f"{sid}: tables={nt} gaia_neighbours={len(rec['gaia']) if rec['gaia'] is not None else 'HOLE'}", flush=True)
    json.dump(out, open(f"{A}/vet_cone.json", "w"), indent=1)
print("VET_CONE_DONE", flush=True)

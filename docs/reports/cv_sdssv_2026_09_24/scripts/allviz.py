# All-table VizieR cone (every VizieR table, 5" around the J2000-propagated Gaia DR3 position; also 2016.0 position when PM is
# large) + SIMBAD cone (5", by position, all otypes) for each candidate. Failed queries are recorded as HOLE, never as empty.
# Output: allviz.json {gaia: {vizier_tables: [...], vizier_rows: {table: [row dicts (first 3 rows, all columns)]}, simbad_cone: [...]}}
import json, time, sys, numpy as np, pandas as pd, requests, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
cand = pd.read_csv(sys.argv[1]); out_fn = sys.argv[2]
try: out = json.load(open(out_fn))
except Exception: out = {}
V = Vizier(columns=["**", "_r"], row_limit=20); V.TIMEOUT = 300
def simbad_cone(ra, de, r=5.0):
    q = (f"SELECT b.main_id, b.otype, b.ra, b.dec, DISTANCE(POINT('ICRS', b.ra, b.dec), POINT('ICRS', {ra}, {de}))*3600 AS sep, b.nbref "
         f"FROM basic AS b WHERE CONTAINS(POINT('ICRS', b.ra, b.dec), CIRCLE('ICRS', {ra}, {de}, {r/3600})) = 1")
    for k in range(3):
        try:
            rr = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=120)
            if rr.status_code == 200: return [dict(zip([c["name"] for c in rr.json()["metadata"]], x)) for x in rr.json()["data"]]
        except Exception: pass
        time.sleep(5)
    return "HOLE"
for _, r in cand.iterrows():
    g = str(int(r.gaia_dr3_source_id))
    if g in out and out[g].get("vizier_tables") not in (None, "HOLE"): continue
    dt = 2000.0 - 2016.0
    ra0, de0 = r.ra_g, r.dec_g
    c20 = SkyCoord((ra0 + r.pmra_g * dt / 3.6e6 / np.cos(np.radians(de0))) * u.deg, (de0 + r.pmdec * dt / 3.6e6) * u.deg)
    rec = dict(ra2000=c20.ra.deg, de2000=c20.dec.deg)
    tl = None
    for k in range(3):
        try:
            tl = V.query_region(c20, radius=5 * u.arcsec); break
        except Exception as e:
            time.sleep(15)
    if tl is None:
        rec["vizier_tables"] = "HOLE"
    else:
        rec["vizier_tables"] = [t.meta.get("name", "?") for t in tl]
        rows = {}
        for t in tl:
            nm = t.meta.get("name", "?"); rs = []
            for row in t[:3]:
                rs.append({c: str(row[c])[:40] for c in t.colnames if str(row[c]) not in ("--", "", "nan")})
            rows[nm] = dict(desc=str(t.meta.get("description", ""))[:120], rows=rs)
        rec["vizier_rows"] = rows
    # SIMBAD cone at both epochs (SIMBAD positions are J2000 at epoch 2000)
    rec["simbad_cone"] = simbad_cone(c20.ra.deg, c20.dec.deg)
    out[g] = rec
    print(g, "tables:", "HOLE" if tl is None else len(tl), "| simbad:", rec["simbad_cone"] if rec["simbad_cone"] == "HOLE" else [(x["main_id"], x["otype"], round(x["sep"], 1)) for x in rec["simbad_cone"]], flush=True)
    json.dump(out, open(out_fn, "w"), indent=1)
    time.sleep(1)
print("done")

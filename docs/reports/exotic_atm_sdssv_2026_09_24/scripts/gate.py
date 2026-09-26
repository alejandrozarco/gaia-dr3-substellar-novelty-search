# Prior-classification gate for the exotic-atmosphere candidates. Per object:
#  (1) SIMBAD TAP: identifiers, otype, sp_type, and all bibcodes with titles (failed query -> HOLE)
#  (2) VizieR all-table cone (every catalogue, row_limit 50) of radius 5" + half the 2000->2016 proper-motion offset around the midpoint
#      of the J2000 and Gaia-2016 positions; stores table names/descriptions and every value of class/type-like columns (HOLE on failure)
#  (3) DESI DR1 spectrum existence (Legacy Survey viewer desi-spec-dr1 layer, 6" boxes) and LAMOST DR10 v2.0 cone (9"), HOLE on failure
import json, sys, time, re, requests, numpy as np, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
C = json.load(open(sys.argv[1])); out_fn = sys.argv[2]
try: out = json.load(open(out_fn))
except Exception: out = {}
def tap(adql):
    err = None
    for k in range(3):
        try:
            r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=adql), timeout=90)
            if r.status_code == 200: return r.json()["data"]
            err = f"HTTP {r.status_code}"
        except Exception as e: err = str(e)[:100]
        time.sleep(3)
    return "HOLE " + str(err)
V = Vizier(columns=["**"], row_limit=50); V.TIMEOUT = 240
TYPECOL = re.compile(r"(sp|spt|sptype|spec|class|type|cl|otype|remark|note|comm|flag|obj|DQ|DA|DB|DZ|DC)", re.I)
for g, c in C.items():
    if g in out and not any(isinstance(v, str) and v.startswith("HOLE") for v in out[g].values()): continue
    rec = {}
    ids = tap(f"SELECT i2.id FROM ident AS i1 JOIN ident AS i2 ON i1.oidref = i2.oidref WHERE i1.id = 'Gaia DR3 {g}'")
    rec["simbad_ids"] = ids if isinstance(ids, str) else sorted(x[0] for x in ids)
    b = tap(f"SELECT b.otype, b.sp_type, b.main_id FROM ident AS i1 JOIN basic AS b ON b.oid = i1.oidref WHERE i1.id = 'Gaia DR3 {g}'")
    rec["simbad_basic"] = b
    refs = tap(f"SELECT r.bibcode, r.title FROM ident AS i1 JOIN has_ref AS h ON h.oidref = i1.oidref JOIN ref AS r ON r.oidbib = h.oidbibref WHERE i1.id = 'Gaia DR3 {g}'")
    rec["simbad_refs"] = refs if isinstance(refs, str) else sorted([x[0], x[1]] for x in refs)
    p0 = SkyCoord(c["ra2000"] * u.deg, c["dec2000"] * u.deg); p1 = SkyCoord(c["ra16"] * u.deg, c["dec16"] * u.deg)
    sep = p0.separation(p1).arcsec
    mid = SkyCoord((c["ra2000"] + c["ra16"]) / 2 * u.deg, (c["dec2000"] + c["dec16"]) / 2 * u.deg)
    rad = 5.0 + sep / 2
    tl = None
    for k in range(3):
        try: tl = V.query_region(mid, radius=rad * u.arcsec); break
        except Exception as e: tl = "HOLE " + str(e)[:100]; time.sleep(10)
    if isinstance(tl, str): rec["vizier"] = tl
    else:
        rec["vizier"] = []; rec["vizier_typecols"] = []
        for t in tl:
            name = t.meta.get("name", "?"); desc = t.meta.get("description", "")
            rec["vizier"].append([name, desc[:120], len(t)])
            for col in t.colnames:
                if TYPECOL.search(col):
                    vals = sorted({str(v) for v in t[col] if str(v) not in ("--", "", "nan")})
                    if vals: rec["vizier_typecols"].append(f"{name}:{col}={'|'.join(vals)[:120]}")
    rec["vizier_radius_arcsec"] = rad
    # DESI DR1 spectra
    try:
        d = 6 / 3600; dr = d / np.cos(np.radians(c["dec16"]))
        r = requests.get("https://www.legacysurvey.org/viewer/desi-spec-dr1/1/cat.json", params=dict(ralo=min(c["ra16"], c["ra2000"]) - dr, rahi=max(c["ra16"], c["ra2000"]) + dr,
                         declo=min(c["dec16"], c["dec2000"]) - d, dechi=max(c["dec16"], c["dec2000"]) + d), timeout=60)
        j = r.json(); rec["desi_dr1"] = list(zip(j.get("name", []), j.get("targetid", []))) if r.status_code == 200 else f"HOLE HTTP {r.status_code}"
    except Exception as e: rec["desi_dr1"] = "HOLE " + str(e)[:80]
    de = (c["dec16"] + c["dec2000"]) / 2; ra = (c["ra16"] + c["ra2000"]) / 2
    if de < -12: rec["lamost_dr10"] = "OUT_OF_LAMOST_DEC"
    else:
        try:
            x = requests.get("https://www.lamost.org/dr10/v2.0/voservice/conesearch", params=dict(ra=ra, dec=de, sr=0.0025), timeout=90).text
            names = re.findall(r'<FIELD[^>]*name="([^"]+)"', x); rows = re.findall(r"<TR>(.*?)</TR>", x, re.S)
            if not names: rec["lamost_dr10"] = "HOLE no VOTable fields"
            else: rec["lamost_dr10"] = [{k: dict(zip(names, re.findall(r"<TD>(.*?)</TD>", rr, re.S))).get(k) for k in ("obsid", "class", "subclass", "snrg")} for rr in rows]
        except Exception as e: rec["lamost_dr10"] = "HOLE " + str(e)[:80]
    out[g] = rec
    print(g, "simbad", (len(rec["simbad_ids"]) if not isinstance(rec["simbad_ids"], str) else rec["simbad_ids"]), "refs", (len(rec["simbad_refs"]) if not isinstance(rec["simbad_refs"], str) else rec["simbad_refs"]),
          "vizier", (len(rec["vizier"]) if not isinstance(rec["vizier"], str) else rec["vizier"]), "desi", rec["desi_dr1"], "lamost", rec["lamost_dr10"] if isinstance(rec["lamost_dr10"], str) else len(rec["lamost_dr10"]), flush=True)
    json.dump(out, open(out_fn, "w"), indent=1, default=str)
print("done")

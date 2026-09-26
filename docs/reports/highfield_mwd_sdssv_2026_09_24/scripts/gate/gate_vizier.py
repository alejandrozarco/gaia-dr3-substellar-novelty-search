# VizieR all-table cone (every table, 5" around the J2000-propagated AND the Gaia-2016 position), adapted from the
# 2026-09-23 novelty.py. Flags rows whose type/class/remark/field columns carry magnetic, DQ/DZ/DAH-type or CV/QSO hints, and
# ALSO lists every table name + description so that single-class catalogues without a type column are not missed.
# Failed queries -> HOLE.
import json, time, sys, numpy as np, warnings
warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
C = json.load(open(sys.argv[1])); outfn = sys.argv[2]
V = Vizier(columns=["**"], row_limit=50); V.TIMEOUT = 240
KEYS = ("DAH", "DAP", "DH", "DBH", "DQH", "DZH", "MWD", "magnet", "Magnet", "Zeeman", "DQ", "DZ", "DC", "DA", "DB", "CV", "QSO", "polar", "Polar")
out = {}
for g, c in C.items():
    rec = dict(tables={}, hits=[])
    for tag, (ra, de) in (("J2000", (c["ra2000"], c["dec2000"])), ("2016", (c["ra2016"], c["dec2016"]))):
        tl = None
        for k in range(3):
            try:
                tl = V.query_region(SkyCoord(ra * u.deg, de * u.deg), radius=5 * u.arcsec); break
            except Exception as e:
                time.sleep(10)
        if tl is None:
            rec["tables"][tag] = "HOLE"; continue
        rec["tables"][tag] = [t.meta.get("name", "?") for t in tl]
        for t in tl:
            name = t.meta.get("name", "?")
            for col in t.colnames:
                lc = col.lower()
                if any(k in lc for k in ("sptype", "sp", "spt", "class", "type", "mag_field", "bfield", "field", "b_mg", "remark", "note", "comment", "cl", "otype")):
                    for v in t[col]:
                        sv = str(v)
                        if any(k in sv for k in KEYS) and len(sv) < 40:
                            h = f"{name}:{col}={sv}"
                            if h not in rec["hits"]: rec["hits"].append(h)
        time.sleep(1)
    out[g] = rec
    t2 = rec["tables"].get("J2000"); t6 = rec["tables"].get("2016")
    print(g, "tables J2000:", t2 if t2 == "HOLE" else len(t2), "2016:", t6 if t6 == "HOLE" else len(t6), "| hits:", rec["hits"][:12], flush=True)
    json.dump(out, open(outfn, "w"), indent=1)

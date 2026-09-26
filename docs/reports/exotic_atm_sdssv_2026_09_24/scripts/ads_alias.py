# ADS full-text search on every alias: SIMBAD identifiers (minus Gaia), bare Gaia DR3 number, short names Jhhmm+ddmm and
# Jhhmmss+ddmmss (J2000 and Gaia-2016 positions), and the Gentile Fusillo WDJ name prefix. Failed query -> HOLE.
import json, sys, time, numpy as np
sys.path.insert(0, "/tmp/fanout"); from ads import search
from astropy.coordinates import SkyCoord; import astropy.units as u
C = json.load(open(sys.argv[1])); G = json.load(open(sys.argv[2])); out = {}
def short(ra, dec):
    c = SkyCoord(ra * u.deg, dec * u.deg); h, m, s = c.ra.hms; d, dm, ds = np.abs(c.dec.dms); sg = "+" if dec >= 0 else "-"
    return {f"J{int(h):02d}{int(m):02d}{sg}{int(d):02d}{int(abs(dm)):02d}", f"J{int(h):02d}{int(m):02d}{int(s):02d}{sg}{int(d):02d}{int(abs(dm)):02d}{int(abs(ds)):02d}"}
for g, c in C.items():
    al = set()
    ids = G.get(g, {}).get("simbad_ids", [])
    if isinstance(ids, list): al |= {i for i in ids if not i.startswith("Gaia")}
    al.add(g)
    for ra, de in ((c["ra2000"], c["dec2000"]), (c["ra16"], c["dec16"])): al |= short(ra, de)
    terms = sorted({f'full:"{a}"' for a in al})
    docs, n = search(" OR ".join(terms), rows=50)
    out[g] = dict(aliases=sorted(al), n=(n if docs is not None else f"HOLE HTTP {n}"), docs=docs)
    print(g, "HOLE" if docs is None else n, [(d["bibcode"], d.get("title", [""])[0][:60]) for d in (docs or [])][:8], flush=True)
    time.sleep(1)
json.dump(out, open(sys.argv[3], "w"), indent=1)

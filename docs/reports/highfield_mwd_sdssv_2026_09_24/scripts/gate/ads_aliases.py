# ADS full-text search on every alias of each target: SIMBAD identifiers, bare Gaia numbers, and short coordinate names
# (Jhhmm+ddmm and Jhhmmss+ddmmss, truncated, from both the J2000-epoch and the Gaia 2016.0 positions) -- papers such as
# Jewett+2024 name objects only by short J names (verified: the bare Gaia id finds nothing, "J0547+1501" finds the paper).
import json, sys, time, re, numpy as np
sys.path.insert(0, "."); from ads import search
from astropy.coordinates import SkyCoord; import astropy.units as u
S = json.load(open(sys.argv[1])); N = json.load(open(sys.argv[2])); outfn = sys.argv[3]
def short(ra, dec):
    c = SkyCoord(ra * u.deg, dec * u.deg); h, m, s = c.ra.hms; sg = "+" if dec >= 0 else "-"; d, dm, ds = np.abs(c.dec.dms)
    h, m, s, d, dm, ds = int(h), int(m), s, int(d), int(abs(dm)), abs(ds)
    return {f"J{h:02d}{m:02d}{sg}{d:02d}{dm:02d}", f"J{h:02d}{m:02d}{int(s):02d}{sg}{d:02d}{dm:02d}{int(ds):02d}"}
out = {}
for g, v in S.items():
    al = set(v["ids"] or []); n = N[g]; pm = n["pm"]
    ra16 = n["ra2000"] + pm[0] * 16 / 3.6e6 / np.cos(np.radians(n["dec2000"])); de16 = n["dec2000"] + pm[1] * 16 / 3.6e6
    for ra, de in ((n["ra2000"], n["dec2000"]), (ra16, de16)): al |= short(ra, de)
    terms = sorted({f'full:"{a.replace("Gaia DR3 ", "").replace("Gaia DR2 ", "")}"' for a in al})
    docs, nf = search(" OR ".join(terms), rows=80)
    out[g] = dict(aliases=sorted(al), n=nf if docs is not None else None, docs=docs)
    print(g, "HOLE" if docs is None else nf, [d["bibcode"] for d in (docs or [])][:12], flush=True)
    time.sleep(0.5)
json.dump(out, open(outfn, "w"), indent=1)

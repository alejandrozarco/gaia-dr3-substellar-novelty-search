# Grep downloaded arXiv sources (/tmp/mwd/arx and /tmp/fanout/exotic_atm/arx; all text-like files incl. machine-readable tables)
# for each candidate's Gaia DR3/DR2 id and short names (Jhhmm+ddmm, Jhhmmss+ddmmss, and LaTeX-style J1234$+$5678 / $-$ variants)
# at the J2000 and Gaia-2016 positions.
import json, glob, os, re, sys, numpy as np
from astropy.coordinates import SkyCoord; import astropy.units as u
C = json.load(open(sys.argv[1]))
files = [f for f in glob.glob("/tmp/mwd/arx/**/*", recursive=True) + glob.glob("/tmp/fanout/exotic_atm/arx/**/*", recursive=True)
         if os.path.isfile(f) and f.lower().endswith((".tex", ".txt", ".dat", ".csv", ".tab", ".mrt", ".bbl", ".ecsv", ".vot", ".xml"))]
texts = {}
for f in files:
    try: texts[f] = open(f, errors="ignore").read()
    except Exception: pass
papers = sorted({f.split("/arx/")[1].split("/")[0] for f in texts})
print("files", len(texts), "papers", len(papers), papers)
def names(c):
    out = set()
    for ra, de in ((c["ra2000"], c["dec2000"]), (c["ra16"], c["dec16"])):
        s = SkyCoord(ra * u.deg, de * u.deg); h, m, sec = s.ra.hms; d, dm, ds = np.abs(s.dec.dms); sg = "+" if de >= 0 else "-"
        h, m, d, dm = int(h), int(m), int(d), int(abs(dm))
        for sgt in (sg, "$" + sg + "$", "$" + ("-" if sg == "-" else "+") + "$", "{" + sg + "}", "−" if sg == "-" else "+"):
            out.add(f"J{h:02d}{m:02d}{sgt}{d:02d}{dm:02d}")
        out.add(f"J{h:02d}{m:02d}{int(sec):02d}")
    return out
res = {}
for g, c in C.items():
    hits = []
    pats = {g} | names(c)
    for f, t in texts.items():
        for p in pats:
            if p in t:
                i = t.find(p); hits.append((f.split("/arx/")[1], p, t[max(0, i - 80):i + 120].replace("\n", " ")))
    res[g] = hits
    print(g, len(hits), sorted({h[0].split("/")[0] + ":" + h[1] for h in hits})[:10])
json.dump(res, open(sys.argv[2], "w"), indent=1)

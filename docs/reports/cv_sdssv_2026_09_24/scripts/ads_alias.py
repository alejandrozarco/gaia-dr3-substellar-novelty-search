# ADS full-text search on all aliases per object: SIMBAD identifiers (TAP), bare Gaia DR3 id, short J names (Jhhmm+ddmm,
# Jhhmmss+ddmmss) from J2000 (epoch 2000) and 2016.0 positions, and the WDJ name. Failed searches -> HOLE.
import sys, json, time, requests, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/fanout"); from ads import search
from astropy.coordinates import SkyCoord; import astropy.units as u
k = pd.read_csv(sys.argv[1]); out_fn = sys.argv[2]
def simbad_ids(g):
    q = f"SELECT i2.id FROM ident AS i1 JOIN ident AS i2 ON i1.oidref = i2.oidref WHERE i1.id = 'Gaia DR3 {g}'"
    for kk in range(3):
        try:
            r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=90)
            if r.status_code == 200: return [x[0] for x in r.json()["data"]]
        except Exception: pass
        time.sleep(3)
    return None
def short(c):
    h, m, s = c.ra.hms; sg = "+" if c.dec.deg >= 0 else "-"; d, dm, ds = np.abs(c.dec.dms)
    return {f"J{int(h):02d}{int(m):02d}{sg}{int(d):02d}{int(abs(dm)):02d}", f"J{int(h):02d}{int(m):02d}{int(s):02d}{sg}{int(d):02d}{int(abs(dm)):02d}{int(abs(ds)):02d}"}
out = {}
for _, r in k.iterrows():
    g = str(int(r.gaia_dr3_source_id)); dt = -16.0
    c16 = SkyCoord(r.ra_g * u.deg, r.dec_g * u.deg)
    c00 = SkyCoord((r.ra_g + r.pmra_g * dt / 3.6e6 / np.cos(np.radians(r.dec_g))) * u.deg, (r.dec_g + r.pmdec * dt / 3.6e6) * u.deg)
    al = {g} | short(c16) | short(c00)
    ids = simbad_ids(g)
    if ids: al |= {i.replace("Gaia DR3 ", "").replace("Gaia DR2 ", "").strip() for i in ids}
    terms = sorted(f'full:"{a}"' for a in al if len(a) > 5)
    docs, nf = search(" OR ".join(terms), rows=60)
    out[g] = dict(aliases=sorted(al), simbad_ids=ids, n=None if docs is None else nf, docs=docs)
    print(g, "HOLE" if docs is None else nf, [(d["bibcode"], d.get("title", [""])[0][:60]) for d in (docs or [])][:8], flush=True)
    time.sleep(1)
json.dump(out, open(out_fn, "w"), indent=1)

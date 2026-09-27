import os, requests, warnings; warnings.filterwarnings("ignore")
from astroquery.vizier import Vizier; from astroquery.simbad import Simbad; import astropy.units as u; from astropy.coordinates import SkyCoord
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip()
T = {"3842377248804727168": (139.45087253940676, 0.1781952340723616), "3230486971974872192": (69.63651731568868, 0.5213442034983069)}
V = Vizier(columns=["**"], row_limit=3); V.TIMEOUT = 200
for gid, (ra, dec) in T.items():
    c = SkyCoord(ra, dec, unit="deg"); print("=====", gid)
    allt = V.query_region(c, radius=5 * u.arcsec); print(len(allt), " ".join(sorted(allt.keys())))
    for k in allt.keys():
        cols = [n for n in allt[k].colnames if any(s in n.lower() for s in ("per", "freq", "type", "class", "sp", "var", "name", "teff"))]
        if cols: print("  ", k, "|", "; ".join(f"{n}={allt[k][0][n]}" for n in cols[:10])[:300])
    r = Simbad.query_region(c, radius=5 * u.arcsec)
    if r is not None and len(r):
        mid = r[0]["main_id"]; print("SIMBAD", mid, "|", " | ".join(str(x) for x in Simbad.query_objectids(mid)["id"]))
        q = Simbad.query_tap(f"SELECT b.bibcode, b.title FROM ref b JOIN has_ref h ON h.oidbibref = b.oidbib JOIN ident i ON i.oidref = h.oidref WHERE i.id = '{mid}'")
        for x in q: print("  REF", x["bibcode"], str(x["title"])[:110])
    names = [f'"{gid}"'] + ([f'"{str(x)}"' for x in Simbad.query_objectids(mid)["id"] if not str(x).startswith("Gaia")] if r is not None and len(r) else [])
    for n in names:
        j = requests.get("https://api.adsabs.harvard.edu/v1/search/query", params={"q": f"full:{n}", "fl": "bibcode,title", "rows": 10}, headers={"Authorization": "Bearer " + tok}, timeout=60).json()
        print("ADS", n, j.get("response", {}).get("numFound"), [d["bibcode"] for d in j.get("response", {}).get("docs", [])])

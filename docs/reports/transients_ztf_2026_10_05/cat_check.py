"""VSX API (60 arcsec; control SS Cyg), SIMBAD (10 arcsec), CBAT TOCP page (RA/Dec string match) for positions (2026-09-30).
Usage: python cat_check.py name:ra:dec [...]"""
import sys, re, requests
from astropy.coordinates import SkyCoord; import astropy.units as u
t = requests.get("http://www.cbat.eps.harvard.edu/unconf/tocp.html", timeout=60).text
def vsx(a, d):
    r = requests.get("https://www.aavso.org/vsx/index.php", params=dict(view="api.list", ra=a, dec=d, radius=60 / 3600, format="json"), timeout=60).json()
    it = r.get("VSXObjects", {}).get("VSXObject", []) if isinstance(r.get("VSXObjects"), dict) else []; it = it if isinstance(it, list) else [it]
    return [x.get("Name") for x in it]
print("control SS Cyg VSX:", vsx(325.67854, 43.58617)[:1])
for arg in sys.argv[1:]:
    nm, a, d = arg.split(":"); a, d = float(a), float(d); s = SkyCoord(a * u.deg, d * u.deg).to_string("hmsdms", sep=" ", precision=0)
    hh, dd = s.split()[0:2], s.split()[3:5]; pat = f"{hh[0]} {hh[1]}"; hits = [l.strip()[:120] for l in t.splitlines() if pat + " " in l and f"{dd[0]} {dd[1]}"[1:] in l]
    q = f"SELECT main_id, otype FROM basic WHERE CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',{a},{d},0.00278))=1"
    sb = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(request="doQuery", lang="adql", format="csv", query=q), timeout=60).text.strip().splitlines()[1:]
    print(nm, "| VSX 60\":", vsx(a, d), "| SIMBAD 10\":", sb, "| TOCP:", hits)

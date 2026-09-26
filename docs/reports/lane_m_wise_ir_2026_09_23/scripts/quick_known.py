# Quick novelty check for a Gaia DR3 source: VSX API, SIMBAD, ADS full text on all designations incl. short forms, Li+2025 WDMS, VarWISE
import sys, os, json, subprocess, urllib.request, urllib.parse, warnings
warnings.filterwarnings("ignore")
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
sid = sys.argv[1]
g = Gaia.launch_job(f"SELECT ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id={sid}").get_results()[0]
ra, de = float(g["ra"]), float(g["dec"]); c = SkyCoord(ra*u.deg, de*u.deg)
hh = c.to_string("hmsdms", sep="", precision=1).replace(" ", "")
rs, ds = c.ra.to_string(unit=u.hourangle, sep="", precision=2, pad=True), c.dec.to_string(sep="", precision=1, alwayssign=True, pad=True)
short = [f"J{rs[:4]}{ds[:5]}", f"J{rs[:6]}{ds[:7]}", f"J{rs[:4]}{ds[:3]}"]
print(f"Gaia DR3 {sid}: RA {ra:.5f} Dec {de:+.5f} G {float(g['phot_g_mean_mag']):.2f} BP-RP {float(g['bp_rp']):.2f} plx {float(g['parallax']):.2f}; short forms {short}")
url = f"https://vsx.aavso.org/index.php?view=api.list&ra={ra}&dec={de}&radius=0.0042&format=json"
j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
v = j.get("VSXObjects") or {}; o = v.get("VSXObject", []) if isinstance(v, dict) else []; o = [o] if isinstance(o, dict) else o
print("VSX 15in:", [(x.get("Name"), x.get("VariabilityType"), x.get("Period")) for x in o] or "none")
names = [sid] + short
for cat, col in (("II/328/allwise", "AllWISE"), ("II/246/out", "2MASS"), ("IV/39/tic82", "TIC")):
    try:
        r = Vizier(columns=["**"], row_limit=1).query_region(c, radius=3*u.arcsec, catalog=cat)
        if r: names.append(("TIC " if col == "TIC" else "") + str(r[0][col][0]))
    except Exception as e: pass
s = Simbad(); s.add_votable_fields("otype", "ids")
try:
    r = s.query_region(c, radius=10*u.arcsec)
    for row in r:
        print("SIMBAD:", row["main_id"], f"[{row['otype']}]", "ids:", str(row["ids"])[:300])
        names += [i.strip() for i in str(row["ids"]).split("|") if i.strip() and not i.strip().startswith("Gaia DR2")]
    if not len(r): print("SIMBAD: none within 10in")
except Exception as e: print("SIMBAD ERR", e)
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip()
seen = set()
for n in dict.fromkeys(names):
    q = n.replace("Gaia DR3 ", "").replace("2MASS J", "").replace("WISEA ", "")
    if q in seen: continue
    seen.add(q)
    url = "https://api.adsabs.harvard.edu/v1/search/query?" + urllib.parse.urlencode(dict(q=f'full:"{q}"', fl="bibcode,title", rows=5))
    try:
        rr = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}), timeout=60).read())["response"]
        if rr["numFound"]: print(f"ADS full:{q!r}: {rr['numFound']}", [(d['bibcode'], d['title'][0][:70]) for d in rr['docs'][:5]])
    except Exception as e: print("ADS ERR", q, e)
print("ADS strings searched:", list(seen))
for f in ("CHI2_WDMS.csv", "FaintQC_WDMS.csv"):
    if os.path.exists(f): print(f, "listed" if sid in open(f).read() else "absent")
for T in ("varwisepure", "varwiseext"):
    Q = f"SELECT designation, vartype, confidence, period1, w1_amp FROM {T} WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{de},0.0025))=1"
    p = subprocess.run(["curl", "-s", "--max-time", "300", "--data-urlencode", f"QUERY={Q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL", "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
    print(T, p.stdout.strip().splitlines()[1:] or "none")
# van Roestel ZTF eclipsing white dwarf catalogue (Zenodo 15007293, April 2026): not in ADS/VizieR; public explorer table
try:
    import re as _re, numpy as _np
    _s = urllib.request.urlopen(urllib.request.Request("https://janvanroestel.github.io/eclipsingWD-explorer/data.js", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
    _d = json.loads(_re.search(r"const SAMPLE_DATA = (\{.*?\});", _s, _re.S).group(1))
    _sep = _np.hypot((_np.array(_d["ra"], float) - ra)*_np.cos(_np.radians(de)), _np.array(_d["dec"], float) - de)*3600
    _j = int(_np.argmin(_sep))
    print(f"van Roestel eclipsing-WD catalogue ({len(_d['ztfname'])} rows): nearest {_d['ztfname'][_j]} at {_sep[_j]:.1f}in, P {_d['period'][_j]}, tags {_d['tags'][_j]}" + ("  <-- LISTED" if _sep[_j] < 5 else ""))
except Exception as _e:
    print("van Roestel catalogue check: HOLE", _e)

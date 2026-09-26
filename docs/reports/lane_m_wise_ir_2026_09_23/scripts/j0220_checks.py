import io, csv, json, os, subprocess, urllib.request, urllib.parse, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
E = json.load(open("j0220_ephem.json")); P, T0 = E["P"], E["T0"]
RA0, DE0, PMRA, PMDE = 35.01897808991266, 63.06656439951715, -11.742487691862992, 38.93010342285144
c = SkyCoord(RA0*u.deg, DE0*u.deg)
q = f"SELECT mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},{5/3600}))=1"
p = subprocess.run(["curl", "-s", "--max-time", "600", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL", "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
T = []
for x in csv.DictReader(io.StringIO(p.stdout)):
    try:
        yr = (float(x["mjd"]) - 57388.0)/365.25; rap = RA0 + PMRA*yr/3.6e6/np.cos(np.radians(DE0)); dep = DE0 + PMDE*yr/3.6e6
        if np.hypot((float(x["ra"]) - rap)*np.cos(np.radians(DE0)), float(x["dec"]) - dep)*3600 > 3: continue
        if not (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"): continue
        T.append((float(x["mjd"]), float(x["w1mpro"]), float(x["w1sigmpro"])))
    except ValueError: pass
T = np.array(T); mjd, w1, e1 = T.T
t = Time(mjd, format="mjd", scale="utc"); bjd = (t.tdb + t.light_travel_time(c, kind="barycentric", location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))).jd
ph = ((bjd - T0)/P) % 1
visit = np.cumsum(np.r_[0, np.diff(np.sort(mjd)) > 20]); order = np.argsort(mjd); vis = np.empty_like(visit); vis[order] = visit
hump = (ph > 0.68) & (ph < 0.9); base = (ph > 0.1) & (ph < 0.6)
print(f"visits: {vis.max()+1}; hump-phase points {hump.sum()} from {len(set(vis[hump]))} visits; baseline points {base.sum()}")
per = []
for v in sorted(set(vis)):
    s = vis == v
    if (hump & s).sum() >= 2 and (base & s).sum() >= 2:
        per.append((int(round(np.median(mjd[s]))), (hump & s).sum(), float(np.median(w1[base & s]) - np.median(w1[hump & s]))))
print("per-visit hump height (baseline minus hump median, mag):", [(a, n, round(h, 2)) for a, n, h in per])
hh = np.array([h for _, _, h in per]); print(f"visits with both: {len(hh)}; hump height median {np.median(hh):.2f}, >0.1 mag in {np.sum(hh > 0.1)}/{len(hh)}")
for lab, s in (("2014-2019", mjd < 58500), ("2019-2024", mjd >= 58500)):
    print(f"{lab}: hump median {np.median(w1[hump & s]):.2f} (n={np.sum(hump & s)}), baseline {np.median(w1[base & s]):.2f} (n={np.sum(base & s)})")
# literature and catalogue checks
tok = open(os.path.expanduser("~/.config/ads/token")).read().strip()
def ads(qs, rows=8):
    url = "https://api.adsabs.harvard.edu/v1/search/query?" + urllib.parse.urlencode(dict(q=qs, fl="bibcode,title", rows=rows))
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}), timeout=60).read())["response"]
for n in ("J0220+6303", "J022004+630359", "J022004.5+630359", "J022004.54+630359", "J022004.55+630359", "0220+6303", "J022004", "513958743252720768", "423456613"):
    r = ads(f'full:"{n}"'); print(f"ADS full:{n!r}: {r['numFound']}", [(d["bibcode"], d["title"][0][:60]) for d in r["docs"][:5]])
from astroquery.simbad import Simbad
s = Simbad(); s.add_votable_fields("otype", "ids")
r = s.query_region(c, radius=15*u.arcsec)
for row in r: print("SIMBAD:", row["main_id"], row["otype"], "| ids:", row["ids"])
from astroquery.gaia import Gaia
eb = Gaia.launch_job("SELECT * FROM gaiadr3.vari_eclipsing_binary WHERE source_id=513958743252720768").get_results()
print("Gaia DR3 vari_eclipsing_binary rows:", len(eb), {n: eb[n][0] for n in eb.colnames if n in ("frequency", "reference_time", "model_type", "global_ranking", "derived_primary_ecl_depth_g", "derived_secondary_ecl_depth_g", "derived_primary_ecl_duration_g")} if len(eb) else "")
cls = Gaia.launch_job("SELECT * FROM gaiadr3.vari_classifier_result WHERE source_id=513958743252720768").get_results()
print("Gaia DR3 classifier:", [(n, cls[n][0]) for n in cls.colnames if n in ("best_class_name", "best_class_score", "classifier_name")] if len(cls) else "none")
from astroquery.vizier import Vizier
for cat, rad in (("II/321/iphas2", 3), ("II/362/uvex", 3), ("V/164/dr5", 5), ("J/ApJS/245/34", 5), ("V/156/dr7lrs", 5)):
    try:
        rr = Vizier(columns=["**"], row_limit=3).query_region(c, radius=rad*u.arcsec, catalog=cat)
        if not rr: print(f"{cat}: none within {rad}in"); continue
        tb = rr[0]; print(f"{cat}: " + ", ".join(f"{k}={tb[k][0]}" for k in tb.colnames if any(z in k for z in ("mag", "Ha", "r-", "U", "He", "class", "Class", "subclass", "SubClass", "_r", "snr", "Name")))[:600])
    except Exception as ex: print(cat, "ERR", str(ex)[:120])

import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
E = json.load(open("j0220_ephem.json")); P, T0 = E["P"], E["T0"]
RA0, DE0, PMRA, PMDE = 35.01897808991266, 63.06656439951715, -11.742487691862992, 38.93010342285144
c = SkyCoord(RA0*u.deg, DE0*u.deg)
q = f"SELECT mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},{5/3600}))=1"
p = subprocess.run(["curl", "-s", "--max-time", "600", "--data-urlencode", f"QUERY={q}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL", "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
rows = list(csv.DictReader(io.StringIO(p.stdout)))
T = []
for x in rows:
    try:
        yr = (float(x["mjd"]) - 57388.0)/365.25; rap = RA0 + PMRA*yr/3.6e6/np.cos(np.radians(DE0)); dep = DE0 + PMDE*yr/3.6e6
        if np.hypot((float(x["ra"]) - rap)*np.cos(np.radians(DE0)), float(x["dec"]) - dep)*3600 > 3: continue
        if not (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"): continue
        T.append((float(x["mjd"]), float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["w2mpro"]) if x["w2mpro"] else np.nan, float(x["w2sigmpro"]) if x["w2sigmpro"] else np.nan))
    except ValueError: pass
T = np.array(T); mjd, w1, e1, w2, e2 = T.T
t = Time(mjd, format="mjd", scale="utc"); bjd = (t.tdb + t.light_travel_time(c, kind="barycentric", location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))).jd
ph = ((bjd - T0)/P) % 1
print(f"WISE epochs {len(T)}")
for lab, m in (("W1", w1), ("W2", w2)):
    ok = np.isfinite(m)
    bins = np.linspace(0, 1, 13); md = [np.median(m[ok][(ph[ok] >= bins[j]) & (ph[ok] < bins[j+1])]) for j in range(12)]; nn = [int(((ph[ok] >= bins[j]) & (ph[ok] < bins[j+1])).sum()) for j in range(12)]
    print(f"{lab} fold on eclipse ephemeris (12 bins, phase 0 = mid-eclipse): {' '.join(f'{v:.2f}' for v in md)}; n per bin {nn}; range {max(md)-min(md):.2f}")
    near = ok & ((np.abs(((bjd - T0)/P + 0.5) % 1 - 0.5))*P*1440 < 4)
    print(f"   {lab} points within +-4 min of mid-eclipse: {near.sum()} values {np.round(m[near], 2).tolist()}")
# ZTF for the figure
ra, de = RA0 - 11.74*5/3.6e6/np.cos(np.radians(DE0)), DE0 + 38.93*5/3.6e6
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r&FORMAT=CSV"
qq = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(qq)) if x["catflags"] == "0" and float(x["mag"]) < float(x["limitmag"]) - 0.1]
pal = EarthLocation.of_site("Palomar")
fig, ax = plt.subplots(4, 1, figsize=(6.4, 10), sharex=True)
for a, b, col in ((ax[0], "zg", "C2"), (ax[1], "zr", "C3")):
    X = [x for x in Z if x["filtercode"] == b]; tt = Time(np.array([float(x["mjd"]) for x in X]), format="mjd", scale="utc", location=pal)
    bj = (tt.tdb + tt.light_travel_time(c, kind="barycentric")).jd; mm = np.array([float(x["mag"]) for x in X]); pz = (((bj - T0)/P) + 0.25) % 1 - 0.25
    a.plot(np.r_[pz, pz+1], np.r_[mm, mm], ".", ms=2.5, color=col, alpha=0.6); a.invert_yaxis(); a.set_ylabel(f"ZTF {b[1]} (mag)")
for a, m, lab, col in ((ax[2], w1, "W1", "C1"), (ax[3], w2, "W2", "C4")):
    ok = np.isfinite(m); pz = (ph + 0.25) % 1 - 0.25
    a.plot(np.r_[pz[ok], pz[ok]+1], np.r_[m[ok], m[ok]], ".", ms=3, color=col, alpha=0.5)
    bins = np.linspace(-0.25, 0.75, 13); md = [np.median(m[ok][(pz[ok] >= bins[j]) & (pz[ok] < bins[j+1])]) for j in range(12)]
    a.plot(np.r_[bins[:-1], bins[:-1]+1] + 1/24, np.r_[md, md], "ks-", ms=4); a.invert_yaxis(); a.set_ylabel(f"NEOWISE {lab} (mag)")
ax[3].set_xlabel(f"orbital phase (mid-eclipse BJD_TDB {T0:.5f}, P = {P:.9f} d)"); ax[0].set_title("Gaia DR3 513958743252720768 (WISE J022004.54+630359.3), 90 pc", fontsize=10)
plt.tight_layout(); plt.savefig("j0220_fold.png", dpi=130); print("figure written")

import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RA0, DE0, PMRA, PMDE = 168.6333385103172, 13.274448259501675, -59.19223093922503, 2.766154914444853
c = SkyCoord(RA0*u.deg, DE0*u.deg)
ra, de = RA0 + PMRA*5/3.6e6/np.cos(np.radians(DE0)), DE0 + PMDE*5/3.6e6
q = subprocess.run(["curl", "-sL", "--max-time", "600", f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5 and float(x["mag"]) < float(x["limitmag"]) - 0.2]
pal = EarthLocation.of_site("Palomar")
def bj(mjd, loc):
    t = Time(mjd, format="mjd", scale="utc", location=loc) if loc is not None else Time(mjd, format="mjd", scale="utc")
    return (t.tdb + t.light_travel_time(c, kind="barycentric", location=loc if loc is not None else EarthLocation.from_geocentric(0, 0, 0, unit=u.m))).jd
S = {}
for b in ("zg", "zr", "zi"):
    X = [x for x in Z if x["filtercode"] == b]
    if len(X) < 30: continue
    t = bj(np.array([float(x["mjd"]) for x in X]), pal); m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X]); o = np.array([x["oid"] for x in X])
    for oo in set(o): m[o == oo] -= np.median(m[o == oo])
    S[b] = (t, m, e)
    yrs = (t - 2458000)/365.25
    print(f"{b}: n={len(t)}, robust sd {1.4826*np.median(np.abs(m)):.3f}, median err {np.median(e):.3f}; yearly medians: " + " ".join(f"{int(2017+y)}:{np.median(m[(yrs>=y-0.5)&(yrs<y+0.5)]):+.2f}" for y in range(1, 9) if ((yrs>=y-0.5)&(yrs<y+0.5)).sum() > 5))
    ls = LombScargle(t, m, e); f, p = ls.autopower(minimum_frequency=0.5, maximum_frequency=48, samples_per_peak=10)
    top = np.argsort(p)[::-1]; seen = []
    for j in top:
        if all(abs(f[j]-s) > 0.02 for s in seen): seen.append(f[j])
        if len(seen) == 5: break
    print(f"   LS top peaks: {[(round(1/s, 7), round(float(ls.power(np.array([s]))[0]), 3)) for s in seen]}; power at 0.0691687: {ls.power(np.array([1/0.0691687]))[0]:.3f}, at 2x: {ls.power(np.array([1/0.1383374]))[0]:.3f}")
# WISE
qq = f"SELECT mjd, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, qual_frame, qi_fact, saa_sep, moon_masked, cc_flags, nb, na FROM neowiser_p1bs_psd WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA0},{DE0},{5/3600}))=1"
p = subprocess.run(["curl", "-s", "--max-time", "600", "--data-urlencode", f"QUERY={qq}", "--data-urlencode", "FORMAT=csv", "--data-urlencode", "LANG=ADQL", "--data-urlencode", "REQUEST=doQuery", "https://irsa.ipac.caltech.edu/TAP/sync"], capture_output=True, text=True)
W = []
for x in csv.DictReader(io.StringIO(p.stdout)):
    try:
        yr = (float(x["mjd"]) - 57388.0)/365.25; rap = RA0 + PMRA*yr/3.6e6/np.cos(np.radians(DE0)); dep = DE0 + PMDE*yr/3.6e6
        if np.hypot((float(x["ra"]) - rap)*np.cos(np.radians(DE0)), float(x["dec"]) - dep)*3600 > 3: continue
        if not (float(x["qual_frame"]) > 0 and float(x["qi_fact"]) > 0 and float(x["saa_sep"]) > 0 and x["moon_masked"][0] == "0" and x["cc_flags"][0] == "0" and x["nb"] == "1" and x["na"] == "0"): continue
        W.append((float(x["mjd"]), float(x["w1mpro"]), float(x["w1sigmpro"]), float(x["w2mpro"]) if x["w2mpro"] else np.nan, float(x["w2sigmpro"]) if x["w2sigmpro"] else np.nan))
    except ValueError: pass
W = np.array(W); wt = bj(W[:, 0], None); w1, e1, w2, e2 = W[:, 1], W[:, 2], W[:, 3], W[:, 4]; w1 = w1 - np.median(w1)
# joint frequency scan (2-harmonic per dataset)
def chi(t, m, e, f, nh=2):
    X = [np.ones_like(t)]
    for k in range(1, nh+1): X += [np.sin(2*np.pi*k*f*(t-2459000)), np.cos(2*np.pi*k*f*(t-2459000))]
    X = np.column_stack(X); w = 1/e**2; pp = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (m*w)); return float(np.sum((m - X @ pp)**2*w)), pp
f0 = 1/0.0691687
fr = f0 + np.linspace(-0.05, 0.05, 20001)
sets = [S[b] for b in S] + [(wt, w1, e1)]
C = np.array([sum(chi(t, m, e, f)[0] for t, m, e in sets) for f in fr])
C0 = sum(chi(t, m, e, f0*0 + 1e-6, 0)[0] for t, m, e in sets)
k = np.argmin(C); fb = fr[k]
order = np.argsort(C); alts = []
for j in order:
    if all(abs(fr[j]-a) > 0.002 for a in alts): alts.append(fr[j])
    if len(alts) == 5: break
print(f"joint ZTF+WISE best P = {1/fb:.8f} d ({24/fb:.4f} h); chi2 {C[k]:.1f} vs constant {C0:.1f}; next minima: {[(round(1/a, 8), round(float(C[np.argmin(np.abs(fr-a))]-C[k]), 1)) for a in alts[1:]]}")
for lab, (t, m, e) in list(S.items()) + [("W1", (wt, w1, e1))]:
    ch, pp = chi(t, m, e, fb, 2); ph = np.linspace(0, 1, 400); M = pp[0] + pp[1]*np.sin(2*np.pi*ph) + pp[2]*np.cos(2*np.pi*ph) + pp[3]*np.sin(4*np.pi*ph) + pp[4]*np.cos(4*np.pi*ph)
    print(f"  {lab}: 2-harmonic peak-to-peak {M.max()-M.min():.3f} mag, max light at phase {ph[np.argmin(M)]:.2f}")
fig, ax = plt.subplots(len(S)+2, 1, figsize=(6.4, 2.3*(len(S)+2)), sharex=True)
for a, (lab, (t, m, e)) in zip(ax, list(S.items()) + [("W1", (wt, w1, e1)), ("W2", (wt, w2 - np.nanmedian(w2), e2))]):
    ph = ((t - 2459000)*fb) % 1; ok = np.isfinite(m)
    a.plot(np.r_[ph[ok], ph[ok]+1], np.r_[m[ok], m[ok]], ".", ms=2.5, alpha=0.4)
    bb = np.linspace(0, 1, 11); md = [np.nanmedian(m[ok][(ph[ok] >= bb[j]) & (ph[ok] < bb[j+1])]) for j in range(10)]
    a.plot(np.r_[bb[:-1]+0.05, bb[:-1]+1.05], np.r_[md, md], "ks-", ms=4); a.invert_yaxis(); a.set_ylabel(f"{lab} (rel. mag)"); a.set_ylim(0.8, -0.8)
ax[-1].set_xlabel(f"phase (P = {1/fb:.8f} d, T0 = BJD 2459000)"); ax[0].set_title("Gaia DR3 3965186104852552448 (3eRASS J111431.9+131627)", fontsize=10)
plt.tight_layout(); plt.savefig("j1114_fold.png", dpi=120)
json.dump(dict(P=1/fb), open("j1114_ephem.json", "w")); print("figure written")

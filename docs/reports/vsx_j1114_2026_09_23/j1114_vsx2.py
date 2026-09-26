import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RA0, DE0, PMRA, PMDE = 168.6333385103172, 13.274448259501675, -59.19223093922503, 2.766154914444853
c = SkyCoord(RA0*u.deg, DE0*u.deg)
ra, de = RA0 + PMRA*5/3.6e6/np.cos(np.radians(DE0)), DE0 + PMDE*5/3.6e6
q = subprocess.run(["curl", "-sL", "--max-time", "600", f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=r,i&FORMAT=CSV"], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5 and float(x["mag"]) < float(x["limitmag"]) - 0.2]
pal = EarthLocation.of_site("Palomar")
D = {}
for b in ("zi", "zr"):
    X = [x for x in Z if x["filtercode"] == b]
    t = Time(np.array([float(x["mjd"]) for x in X]), format="mjd", scale="utc", location=pal)
    bj = (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
    m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X]); oid = np.array([x["oid"] for x in X])
    for o in set(oid): m[oid == o] -= np.median(m[oid == o])
    D[b] = (bj, m, e)
def design(t, f): return np.column_stack([np.ones_like(t)] + [fn(2*np.pi*k*f*(t - 2459000.0)) for k in (1, 2) for fn in (np.sin, np.cos)])
def chi(f):
    tot = 0.0
    for t, m, e in D.values():
        X = design(t, f); w = 1/e**2; p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (m*w)); tot += np.sum((m - X @ p)**2*w)
    return tot
f0 = 1/0.06914240; fr = f0 + np.linspace(-4e-5, 4e-5, 801); C = np.array([chi(f) for f in fr])
k = np.argmin(C); n = sum(len(v[0]) for v in D.values()); red = C[k]/(n - 10)
ok = fr[(C - C[k])/red <= 1.0]
fb = fr[k]; Pb = 1/fb; eP = (1/ok.min() - 1/ok.max())/2
print(f"ZTF r+i joint: P = {Pb:.8f} +- {eP:.8f} d (reduced chi2 {red:.2f}, n = {n})")
# epoch of maximum (i band) with bootstrap uncertainty
t, m, e = D["zi"]; rng = np.random.default_rng(3); phs = []
ph = np.linspace(0, 1, 4000, endpoint=False)
def phmax(tt, mm, ee):
    X = design(tt, fb); w = 1/ee**2; p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (mm*w))
    M = p[1]*np.sin(2*np.pi*ph) + p[2]*np.cos(2*np.pi*ph) + p[3]*np.sin(4*np.pi*ph) + p[4]*np.cos(4*np.pi*ph); return ph[np.argmin(M)]
p0 = phmax(t, m, e)
for i in range(300):
    j = rng.integers(0, len(t), len(t)); phs.append(phmax(t[j], m[j], e[j]))
dphi = np.std(((np.array(phs) - p0 + 0.5) % 1) - 0.5)
E = np.round((2459700.0 - 2459000.0)*fb); Tm = 2459000.0 + (E + p0)/fb
print(f"epoch of maximum (i): BJD_TDB {Tm:.4f} +- {dphi/fb:.4f} d")
fig, ax = plt.subplots(2, 1, figsize=(6.4, 5.6), sharex=True)
for a, b, col in zip(ax, ("zi", "zr"), ("C3", "C1")):
    tt, mm, ee = D[b]; phd = ((tt - Tm)*fb) % 1
    a.errorbar(np.r_[phd, phd+1], np.r_[mm, mm], np.r_[ee, ee], fmt=".", ms=2.5, color=col, alpha=0.35, elinewidth=0.4)
    bb = np.linspace(0, 1, 13); md = [np.median(mm[(phd >= bb[j]) & (phd < bb[j+1])]) for j in range(12)]
    a.plot(np.r_[bb[:-1], bb[:-1]+1] + 1/24, np.r_[md, md], "ks-", ms=4); a.invert_yaxis(); a.set_ylabel(f"ZTF {b[1]} (relative mag)")
ax[0].set_title(f"2MASS J11143206+1316279, P = {Pb:.7f} d, phase 0 = max (BJD_TDB {Tm:.4f})", fontsize=8)
ax[1].set_xlabel("phase")
plt.tight_layout(); plt.savefig("2MASS_J11143206+1316279_ZTF_phase.png", dpi=110)
json.dump(dict(P=Pb, eP=eP, T_max=Tm, eT=dphi/fb), open("j1114_vsx_values.json", "w"))

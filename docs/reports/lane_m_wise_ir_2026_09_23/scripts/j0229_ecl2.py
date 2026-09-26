import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
RA, DE = 37.45358, 75.52392
c = SkyCoord(RA*u.deg, DE*u.deg)
ra, de = RA + 28.6*5/3.6e6/np.cos(np.radians(DE)), DE - 14.1*5/3.6e6
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r&FORMAT=CSV"
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] in ("0",) and float(x["mag"]) < float(x["limitmag"]) - 0.1]
pal = EarthLocation.of_site("Palomar")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=pal); return (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
D = {}
for b in ("zg", "zr"):
    X = [x for x in Z if x["filtercode"] == b]
    t = bjd(np.array([float(x["mjd"]) for x in X])); m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X])
    D[b] = (t, m, e)
# in-eclipse points: > 0.4 mag below the median in either band
tin = []; 
for b, (t, m, e) in D.items():
    med = np.median(m); s = (m - med) > 0.4
    tin += list(zip(t[s], [b]*s.sum(), (m - med)[s]))
tin.sort(); T = np.array([x[0] for x in tin])
print(f"in-eclipse points (>0.4 mag deep, flag 0): {len(T)} spanning BJD {T.min():.1f}-{T.max():.1f}")
# refine P: minimise the circular phase spread of in-eclipse points
P0 = 0.150207767
grid = P0 + np.linspace(-1e-6, 1e-6, 40001)
R = np.array([np.abs(np.mean(np.exp(2j*np.pi*T/P))) for P in grid])
k = np.argmax(R); P = grid[k]
# uncertainty: half-width where R drops by 1/sqrt(N)-ish: use bootstrap
rng = np.random.default_rng(1); boots = []
for i in range(200):
    Tb = rng.choice(T, len(T), replace=True)
    boots.append(grid[np.argmax([np.abs(np.mean(np.exp(2j*np.pi*Tb/p))) for p in grid[::20]]) * 20])
print(f"refined P = {P:.9f} d (bootstrap sd {np.std(boots):.1e} d); phase concentration R = {R[k]:.4f}")
ph = np.angle(np.mean(np.exp(2j*np.pi*T/P)))/(2*np.pi)
n0 = np.round(np.median(T)/P - ph); T0 = (n0 + ph) * P
print(f"mid-eclipse ephemeris: BJD_TDB {T0:.6f} + {P:.9f} E")
dph = ((T - T0)/P + 0.5) % 1 - 0.5
print(f"in-eclipse phase offsets (min): {np.round(np.sort(dph*P*1440), 1).tolist()}")
for b, (t, m, e) in D.items():
    med = np.median(m); ph2 = ((t - T0)/P + 0.5) % 1 - 0.5
    ine = np.abs(ph2*P*1440) < 1.5
    print(f"{b}: out-of-eclipse median {med:.3f}; points within +-1.5 min of mid-eclipse: {ine.sum()}, depths {np.round(np.sort(m[ine]-med), 2).tolist()}")
    oot = np.abs(ph2*P*1440) > 8
    tt = t[oot]; mm = m[oot]; ee = e[oot]
    for nh, lab in ((1, "P"), (2, "P/2")):
        X = np.column_stack([np.ones_like(tt), np.sin(2*np.pi*nh*(tt-T0)/P), np.cos(2*np.pi*nh*(tt-T0)/P)]); w = 1/ee**2
        p = np.linalg.solve(X.T @ (X*w[:, None]), X.T @ (mm*w)); print(f"    out-of-eclipse sinusoid at {lab}: full amplitude {2*np.hypot(p[1], p[2]):.3f} mag")
    bins = np.linspace(-0.5, 0.5, 21); md = [np.median(m[(ph2 >= bins[j]) & (ph2 < bins[j+1])]) - med for j in range(20)]
    print(f"    binned (20) fold rel. median: {' '.join(f'{v:+.2f}' for v in md)}")
json.dump(dict(P=P, T0=T0), open("j0229_ephem.json", "w"))

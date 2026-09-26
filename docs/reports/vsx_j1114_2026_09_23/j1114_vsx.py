# J1114+1316 VSX values re-derived from the ZTF data: magnitude range per band from the phased light curve, epoch of maximum (BJD_TDB)
import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RA0, DE0, PMRA, PMDE = 168.6333385103172, 13.274448259501675, -59.19223093922503, 2.766154914444853
P = 0.06914240
c = SkyCoord(RA0*u.deg, DE0*u.deg)
ra, de = RA0 + PMRA*5/3.6e6/np.cos(np.radians(DE0)), DE0 + PMDE*5/3.6e6
q = subprocess.run(["curl", "-sL", "--max-time", "600", f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5 and float(x["mag"]) < float(x["limitmag"]) - 0.2]
pal = EarthLocation.of_site("Palomar")
out = {}
fig, ax = plt.subplots(3, 1, figsize=(6.4, 7.6), sharex=True)
for a, b, col in zip(ax, ("zi", "zr", "zg"), ("C3", "C1", "C2")):
    X = [x for x in Z if x["filtercode"] == b]
    t = Time(np.array([float(x["mjd"]) for x in X]), format="mjd", scale="utc", location=pal)
    bj = (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
    m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X]); oid = np.array([x["oid"] for x in X])
    # use the field/oid with most points to avoid inter-field offsets in absolute magnitudes
    main = max(set(oid), key=lambda o: (oid == o).sum()); s = oid == main
    tt, mm, ee = bj[s], m[s], e[s]
    X2 = np.column_stack([np.ones_like(tt)] + [f(2*np.pi*k*(tt - 2459000.0)/P) for k in (1, 2) for f in (np.sin, np.cos)])
    w = 1/ee**2; p = np.linalg.solve(X2.T @ (X2*w[:, None]), X2.T @ (mm*w))
    ph = np.linspace(0, 1, 2000, endpoint=False)
    M = p[0] + sum(p[2*k-1]*np.sin(2*np.pi*k*ph) + p[2*k]*np.cos(2*np.pi*k*ph) for k in (1, 2))
    phmax = ph[np.argmin(M)]
    out[b] = dict(n=int(s.sum()), oid=str(main), max=round(float(M.min()), 2), min=round(float(M.max()), 2), amp=round(float(M.max() - M.min()), 3), phase_max=round(float(phmax), 4))
    phd = ((tt - 2459000.0)/P) % 1
    a.errorbar(np.r_[phd, phd+1], np.r_[mm, mm], np.r_[ee, ee], fmt=".", ms=2.5, color=col, alpha=0.35, elinewidth=0.4)
    a.plot(np.r_[ph, ph+1], np.r_[M, M], "k-", lw=1.2); a.invert_yaxis(); a.set_ylabel(f"ZTF {b[1]} (mag)")
# epoch of maximum: use the i band (highest S/N), cycle nearest the middle of the data
E = np.round((2459700.0 - 2459000.0)/P)
T_max = 2459000.0 + (E + out["zi"]["phase_max"])*P
out["epoch_max_BJD_TDB_i"] = round(float(T_max), 4); out["P"] = P
ax[0].set_title(f"2MASS J11143206+1316279 (Gaia DR3 3965186104852552448)  P = {P} d", fontsize=9)
ax[2].set_xlabel("phase (T0 = BJD_TDB 2459000.0)")
plt.tight_layout(); plt.savefig("J1114_ZTF_phase.png", dpi=110)
print(json.dumps(out, indent=1))

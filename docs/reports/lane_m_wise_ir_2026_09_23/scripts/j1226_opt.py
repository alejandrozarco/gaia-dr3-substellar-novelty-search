import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
RA0, DE0 = 186.6576601770502, -23.070649744994668
P = json.load(open("j1226_wise.json"))["P"]; f0 = 1 / P
# ZTF all bands, 3 arcsec (PM small: 0.05"/yr)
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{RA0-0.00006}%20{DE0}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = list(csv.DictReader(io.StringIO(q)))
print("ZTF rows:", len(Z), {b: sum(1 for x in Z if x["filtercode"] == b) for b in ("zg", "zr", "zi")}, "catflags==0:", sum(1 for x in Z if x["catflags"] == "0"))
def ampfit(t, m, e, f, nh=2):
    cols = [np.ones_like(t)]
    for k in range(1, nh+1): cols += [np.sin(2*np.pi*k*f*t), np.cos(2*np.pi*k*f*t)]
    X = np.column_stack(cols); w = 1/e**2; C = np.linalg.inv(X.T @ (X*w[:, None])); p = C @ (X.T @ (m*w))
    r = m - X @ p; chi2 = float(np.sum(r**2*w)); s2 = chi2 / max(1, len(t) - X.shape[1])
    # amplitude of the first harmonic and its error (scaled by reduced chi2)
    a1 = np.hypot(p[1], p[2]); ea1 = np.sqrt(s2 * (C[1,1]*p[1]**2 + C[2,2]*p[2]**2) / max(a1**2, 1e-12))
    ph = np.linspace(0, 1, 400, endpoint=False); M = p[0] + sum(p[2*k-1]*np.sin(2*np.pi*k*ph) + p[2*k]*np.cos(2*np.pi*k*ph) for k in range(1, nh+1))
    return 2*a1, 2*ea1, M.max()-M.min(), ph[np.argmin(M)]
for b in ("zg", "zr", "zi"):
    X = [x for x in Z if x["filtercode"] == b and x["catflags"] == "0" and float(x["mag"]) < float(x["limitmag"]) - 0.2]
    if len(X) < 10: print(b, "n", len(X)); continue
    t = np.array([float(x["hjd"]) for x in X]); m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X])
    a, ea, pp, phmax = ampfit(t - 2459000, m, e, f0, 1)
    ls = LombScargle(t, m, e); pw = float(ls.power(np.array([f0]))[0])
    print(f"  {b}: n={len(t)}, median {np.median(m):.2f}, robust sd {1.4826*np.median(np.abs(m-np.median(m))):.3f}, median err {np.median(e):.3f}; "
          f"sinusoid full amplitude at WISE period {a:.3f} +- {ea:.3f} mag; LS power at f0 {pw:.3f}")
# same for W1 (1 harmonic) for a like-for-like ratio
W = json.load(open("j1226_wise.json")); t = np.array(W["t"]); m = np.array(W["w1"]); e = np.array(W["e1"])
a, ea, pp, phmax = ampfit(t - 2459000, m, e, f0, 1); print(f"  W1: sinusoid full amplitude {a:.3f} +- {ea:.3f} mag (max light phase {phmax:.2f})")
m2 = np.array(W["w2"]); e2 = np.array(W["e2"]); ok = np.isfinite(m2) & np.isfinite(e2)
a, ea, pp, phmax = ampfit(t[ok] - 2459000, m2[ok], e2[ok], f0, 1); print(f"  W2: sinusoid full amplitude {a:.3f} +- {ea:.3f} mag")
# SkyMapper DR4 photometry
c = SkyCoord(RA0*u.deg, DE0*u.deg)
r = Vizier(columns=["**"], row_limit=2).query_region(c, radius=3*u.arcsec, catalog="II/379/smssdr4")
if r:
    tb = r[0]; print("SkyMapper DR4:", {n: str(tb[n][0]) for n in tb.colnames if n.endswith("PSF") or n.startswith("e_") and n.endswith("PSF") or n in ("ObjectId", "flags", "ClassStar", "Ngood")})

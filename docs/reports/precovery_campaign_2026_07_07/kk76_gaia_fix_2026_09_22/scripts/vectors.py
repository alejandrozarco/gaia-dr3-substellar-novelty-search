import sys, pickle; sys.path.insert(0, "/tmp/kk76_fix")
from common import *
from astropy.io import fits
ROOTS = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq",
         "ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"]
T = {}
for r in ROOTS:
    fn = f"{DATA}/{r}_flc.fits" if os.path.exists(f"{DATA}/{r}_flc.fits") else f"{DATA}/{r}_flt.fits"
    h = fits.getheader(fn, 0)
    T[r] = Time((h["EXPSTART"] + h["EXPEND"]) / 2, format="mjd", scale="utc")
V = horizons_hst_vectors([T[r].jd for r in ROOTS])
out = {}
for r, v in zip(ROOTS, V):
    assert abs(v[0] - T[r].jd) < 1e-6, (r, v[0], T[r].jd)
    out[r] = dict(isot=T[r].isot, jd=T[r].jd, X=v[1], Y=v[2], Z=v[3])
    print(f"{r} {T[r].isot}  HST geocentric (km) {v[1]:+11.4f} {v[2]:+11.4f} {v[3]:+11.4f}  |r|={np.sqrt(v[1]**2+v[2]**2+v[3]**2):.1f}")
pickle.dump(out, open("hst_vectors.pkl", "wb"))

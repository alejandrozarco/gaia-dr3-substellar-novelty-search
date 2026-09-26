import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
RA, DE = 37.45358, 75.52392; c = SkyCoord(RA*u.deg, DE*u.deg)
ra, de = RA + 28.6*5/3.6e6/np.cos(np.radians(DE)), DE - 14.1*5/3.6e6
q = subprocess.run(["curl", "-sL", "--max-time", "600", f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r&FORMAT=CSV"], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and float(x["mag"]) < float(x["limitmag"]) - 0.1]
pal = EarthLocation.of_site("Palomar")
t = Time(np.array([float(x["mjd"]) for x in Z]), format="mjd", scale="utc", location=pal); bjd = (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
m = np.array([float(x["mag"]) for x in Z]); b = np.array([x["filtercode"] for x in Z]); e = np.array([float(x["magerr"]) for x in Z]); expt = np.array([float(x["exptime"]) for x in Z])
med = {bb: np.median(m[b == bb]) for bb in ("zg", "zr")}
dm = np.array([mm - med[bb] for mm, bb in zip(m, b)])
deep = ((b == "zg") & (dm > 0.8)) | ((b == "zr") & (dm > 0.35))
print(f"deep points: {deep.sum()} (g {np.sum(deep & (b=='zg'))}, r {np.sum(deep & (b=='zr'))}); exposure times: {sorted(set(expt))}")
E = json.load(open("j0229_ephem.json")); P, T0 = E["P"], E["T0"]
# per season: best phase shift of deep points and the fraction of points near that phase that are deep
yr = (bjd - 2458000)/365.25
for y in range(0, 9):
    s = (yr >= y + 0.5) & (yr < y + 1.5)
    if (deep & s).sum() < 2: continue
    off = (((bjd[deep & s] - T0)/P + 0.5) % 1 - 0.5) * P * 1440
    print(f"  season {2018 + y}: n_deep {(deep & s).sum():2d}, deep offsets (min) {np.round(np.sort(off), 1).tolist()}")
# grid search: which P maximises (deep points concentrated) AND (non-deep points avoid the eclipse window)?
def score(Pt, T0t, half=3.0):
    off = (((bjd - T0t)/Pt + 0.5) % 1 - 0.5) * Pt * 1440
    inw = np.abs(off) < half
    return (deep & inw).sum() - 2*((~deep) & inw).sum()
best = (-1e9, None, None)
for Pt in P + np.linspace(-2e-6, 2e-6, 2001):
    ph = (bjd[deep] / Pt) % 1; ang = np.angle(np.mean(np.exp(2j*np.pi*ph)))/(2*np.pi)
    T0t = (np.round(np.median(bjd[deep])/Pt - ang) + ang) * Pt
    sc = score(Pt, T0t)
    if sc > best[0]: best = (sc, Pt, T0t)
sc, Pb, T0b = best
off = (((bjd - T0b)/Pb + 0.5) % 1 - 0.5) * Pb * 1440
print(f"best window score {sc}: P = {Pb:.9f}, T0 = {T0b:.6f}; within +-3 min: deep {np.sum(deep & (np.abs(off) < 3))}, non-deep {np.sum(~deep & (np.abs(off) < 3))}; deep outside +-3 min: {np.sum(deep & (np.abs(off) >= 3))}")
print("deep offsets at best P (min):", np.round(np.sort(off[deep]), 1).tolist())
print("non-deep points within +-4 min (offset, band, dm):", [(round(o, 1), bb, round(d, 2)) for o, bb, d in sorted(zip(off[~deep & (np.abs(off) < 4)], b[~deep & (np.abs(off) < 4)], dm[~deep & (np.abs(off) < 4)]))])
json.dump(dict(P=Pb, T0=T0b, note="J0229+7531 eclipse ephemeris (window score)"), open("j0229_ephem2.json", "w"))

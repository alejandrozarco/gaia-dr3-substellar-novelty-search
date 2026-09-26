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
m = np.array([float(x["mag"]) for x in Z]); b = np.array([x["filtercode"] for x in Z])
med = {bb: np.median(m[b == bb]) for bb in ("zg", "zr")}; dm = np.array([mm - med[bb] for mm, bb in zip(m, b)])
deep = ((b == "zg") & (dm > 0.8)) | ((b == "zr") & (dm > 0.35)); nd = ~deep
td, tn = bjd[deep], bjd[nd]
print(f"deep {deep.sum()}, normal {nd.sum()}, baseline {bjd.max()-bjd.min():.0f} d")
# For each trial P: phase of deep points -> circular mean; score = (deep within +-w) - (normal within +-w), w = 0.035 phase
f0 = 1/0.0751039
freqs = np.arange(f0 - 0.02, f0 + 0.02, 2e-7)
w = 0.03
best = []
for f in freqs:
    ph = (td * f) % 1; ang = np.angle(np.mean(np.exp(2j*np.pi*ph)))/(2*np.pi)
    dd = ((td * f - ang + 0.5) % 1) - 0.5; dn = ((tn * f - ang + 0.5) % 1) - 0.5
    sc = np.sum(np.abs(dd) < w) - 3*np.sum(np.abs(dn) < w)
    best.append(sc)
best = np.array(best); k = np.argsort(best)[::-1]
seen = []
for j in k:
    if all(abs(freqs[j] - s) > 2e-4 for s in seen): seen.append(freqs[j])
    if len(seen) == 8: break
for f in seen:
    ph = (td * f) % 1; ang = np.angle(np.mean(np.exp(2j*np.pi*ph)))/(2*np.pi)
    dd = ((td * f - ang + 0.5) % 1) - 0.5; dn = ((tn * f - ang + 0.5) % 1) - 0.5
    print(f"P = {1/f:.9f} d: score {best[np.argmin(np.abs(freqs-f))]}, deep within +-{w}: {np.sum(np.abs(dd) < w)}/{len(dd)}, normal within: {np.sum(np.abs(dn) < w)}; deep phase spread (min) {np.std(dd)*1440/f:.1f}")

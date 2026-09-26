import io, csv, json, subprocess, warnings, numpy as np
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
RA, DE = 37.45358, 75.52392; c = SkyCoord(RA*u.deg, DE*u.deg)
ra, de = RA + 28.6*5/3.6e6/np.cos(np.radians(DE)), DE - 14.1*5/3.6e6
q = subprocess.run(["curl", "-sL", "--max-time", "600", f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r&FORMAT=CSV"], capture_output=True, text=True).stdout
Z = [x for x in csv.DictReader(io.StringIO(q)) if float(x["mag"]) < float(x["limitmag"]) - 0.1]
pal = EarthLocation.of_site("Palomar")
t = Time(np.array([float(x["mjd"]) for x in Z]), format="mjd", scale="utc", location=pal); bjd = (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
m = np.array([float(x["mag"]) for x in Z]); b = np.array([x["filtercode"] for x in Z]); fl = np.array([int(x["catflags"]) for x in Z]); oid = np.array([x["oid"] for x in Z]); fid = np.array([x["field"] if "field" in x else "" for x in Z])
print("columns:", list(Z[0].keys()))
med = {bb: np.median(m[(b == bb) & (fl == 0)]) for bb in ("zg", "zr")}
dm = np.array([mm - med[bb] for mm, bb in zip(m, b)])
deep = ((b == "zg") & (dm > 0.8)) | ((b == "zr") & (dm > 0.35))
print("oids:", {o: int((oid == o).sum()) for o in set(oid)})
print("deep points per oid:", {o: int((deep & (oid == o)).sum()) for o in set(oid)})
order = np.argsort(bjd); nights = np.floor(bjd[order] - 0.5)
# nights with >=4 exposures and at least one deep point
for n in sorted(set(nights)):
    s = order[nights == n]
    if len(s) >= 3 and deep[s].any():
        print(f"night BJD {n+0.5:.0f}: " + " | ".join(f"{(bjd[i]-bjd[s[0]])*1440:6.1f}m {b[i][1]} {dm[i]:+.2f}{'*' if deep[i] else ''} f{fl[i]} {oid[i][-4:]}" for i in s))

import io, csv, subprocess, numpy as np
from astropy.timeseries import LombScargle, BoxLeastSquares
ra, de = 35.01897808991266 - 11.74*5/3.6e6/np.cos(np.radians(63.0666)), 63.06656439951715 + 38.93*5/3.6e6
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra}%20{de}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
Z = list(csv.DictReader(io.StringIO(q)))
print("rows", len(Z), {b: sum(1 for x in Z if x["filtercode"] == b) for b in ("zg", "zr", "zi")}, "flags:", {f: sum(1 for x in Z if x["catflags"] == f) for f in set(x["catflags"] for x in Z)})
for b in ("zg", "zr", "zi"):
    X = [x for x in Z if x["filtercode"] == b and float(x["mag"]) < float(x["limitmag"]) - 0.1]
    t = np.array([float(x["hjd"]) for x in X]); m = np.array([float(x["mag"]) for x in X]); e = np.array([float(x["magerr"]) for x in X]); fl = np.array([int(x["catflags"]) for x in X])
    if len(t) < 20: continue
    med = np.median(m[fl == 0]); rs = 1.4826*np.median(np.abs(m[fl == 0] - med))
    faint = (m - med) > np.maximum(5*e, 0.3)
    print(f"{b}: n={len(t)} (flag0 {np.sum(fl==0)}), median {med:.3f}, robust sd {rs:.3f}, points >max(5sig,0.3 mag) fainter: {faint.sum()}")
    for P in (0.0495421, 0.0990842):
        ph = ((t - 2459000.0)/P) % 1
        if faint.sum(): print(f"   P={P}: faint-point phases {np.round(np.sort(ph[faint]), 3).tolist()[:30]}; depths {np.round(np.sort(m[faint]-med)[::-1], 2).tolist()[:15]}; flags {fl[faint].tolist()[:30]}")
    # BLS on flag-0 points for narrow eclipses (durations 3-15 min) over 0.03-0.5 d
    s = fl == 0
    bls = BoxLeastSquares(t[s], m[s], e[s]); periods = np.exp(np.linspace(np.log(0.03), np.log(0.5), 200000))
    r = bls.power(periods, [0.002, 0.004, 0.007, 0.01], objective="snr")
    k = np.argmax(r.power); print(f"   BLS best P={r.period[k]:.7f} d depth {r.depth[k]:.3f} dur {r.duration[k]*1440:.1f} min snr {r.power[k]:.1f}; power at 0.0990842: {r.power[np.argmin(np.abs(r.period-0.0990842))]:.1f}")

# Tasks 4+5: He limits and automated inventory of absorption features with identification against NIST lists at +93 km/s.
import sys, json, numpy as np
sys.path.insert(0, "/tmp/hotdq/review2/spec_agent")
from common import *
from scipy.ndimage import percentile_filter, gaussian_filter1d
from scipy.signal import find_peaks
L = json.load(open("/tmp/hotdq/review2/data/nist_vacuum_lines.json"))
L["Ca II"] = [(3934.78, 1000), (3969.59, 1000), (8500.36, 500), (8544.44, 500), (8664.52, 500)]
L["Na I"] = [(5891.58, 1000), (5897.56, 1000)]
L["He II"] = [(4687.02, 1000), (5413.03, 300), (6562.0, 300), (4542.86, 200), (3204.0, 100)]
VT = 93.0
t = load_visits(TARGET)[0]
w, f, iv = t["w"], t["f"], t["iv"]
m = (w > 3750) & (w < 8900) & (iv > 0)
w, f, iv = w[m], f[m], iv[m]
cont = gaussian_filter1d(percentile_filter(f, 90, size=161), 30)
n = f / cont; en = 1 / np.sqrt(iv) / cont
# ---------- Task 4: He limits (EW within +-7 A, local linear continuum from +-(9..20) A sidebands) ----------
print("He limits (EW in mA; positive = absorption), window +-7 A at +93 km/s:")
for nm, lam in [("He I 4472", 4472.735), ("He I 4923", 4923.30), ("He I 5017", 5017.08), ("He I 5877", 5877.25), ("He I 6680", 6679.99), ("He I 7067", 7067.20), ("He II 4687", 4687.02), ("He II 5413", 5413.03)]:
    E, eE, cd, n2, cc = ew(t["w"], t["f"], t["iv"], lam, 7.0, [(-20, -9), (9, 20)], vel=VT)
    print(f"  {nm:10s}: EW {1000*E:+6.0f} +- {1000*eE:4.0f} mA -> 3-sigma upper limit {1000*max(E,0)+3000*eE:5.0f} mA; core depth {cd:+.3f}")
# ---------- Task 5: feature inventory ----------
sm = gaussian_filter1d(1 - n, 1.0)
esm = np.sqrt(gaussian_filter1d(en ** 2, 1.0) / 2.5)
pk, pr = find_peaks(sm, height=0.04, distance=3)
sig = sm / esm
keep = pk[sig[pk] > 5]
def nearest(lam_obs, sp, vel, tol):
    rest = lam_obs / (1 + vel / C)
    c = [(abs(x[0] - rest), x[0], x[1]) for x in L.get(sp, [])]
    c = [x for x in c if x[0] < tol]
    return sorted(c, key=lambda x: -x[2])[:2]
print("\nAbsorption features (smoothed depth > 0.04 and > 5 sigma):  lam_obs  depth  sigma  | C II(+93) | other IDs within 2.5 A (rest at +93 km/s; Na/Ca at 0) ")
for k in keep:
    lo = w[k]
    ids = []
    for sp in ["C II", "C I", "H I", "He I", "He II", "O I", "O II", "C III", "Mg II", "Si II"]:
        nb = nearest(lo, sp, VT, 2.5)
        if nb:
            ids.append(f"{sp} " + ",".join(f"{x[1]:.1f}({x[2]:g})" for x in nb))
    for sp in ["Na I", "Ca II"]:
        nb = nearest(lo, sp, 0.0, 2.5)
        if nb: ids.append(f"{sp}(v=0) {nb[0][1]:.1f}")
    sky = [s for s in [5578.89, 5891.58, 5897.56, 6302.05, 6365.54] if abs(lo - s) < 3]
    tel = "TELLURIC" if (6860 < lo < 6960) or (7160 < lo < 7340) or (7590 < lo < 7720) or (8100 < lo < 8400) else ""
    print(f"  {lo:8.1f}  {sm[k]:.3f}  {sig[k]:5.1f}  | {'; '.join(ids) if ids else 'UNIDENTIFIED'} {'SKY' if sky else ''} {tel}")

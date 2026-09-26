# Task 2: C II equivalent widths, target vs published hot DQs (SDSS DR17) and SDSS-V carbon-line WDs, identical method.
# Per spectrum: C II template CCF -> velocity; per feature: EW = integral(1-F/Fc) over [lo,hi] (rest, shifted to star velocity),
# Fc = straight line through the medians of 12-A sidebands just outside the window. Errors from ivar.
import sys, json, numpy as np
sys.path.insert(0, "/tmp/hotdq/review2/spec_agent")
from common import *
from astropy.io import fits
L = json.load(open("/tmp/hotdq/review2/data/nist_vacuum_lines.json"))
FEATS = {  # name: (lo, hi) rest vacuum window; sidebands placed at [lo-14,lo-2] and [hi+2,hi+14] unless given
    "3921": (3915, 3928, None),
    "4076": (4070, 4083, None),
    "4268": (4260, 4276, None),
    "4374": (4366, 4381, [(4352, 4360), (4388, 4400)]),
    "4412": (4406, 4418, None),
    "4620": (4614, 4627, None),
    "5145": (5129, 5158, [(5110, 5125), (5162, 5175)]),
    "5892": (5886, 5898, None),
    "6580+6585": (6574, 6591, [(6594, 6606), (6608, 6620)]),
    "7236": (7228, 7244, None),
    "7115-7122": (7108, 7127, [(7090, 7102), (7130, 7142)]),
}
def load_sdss(path):
    d = fits.open(path)[1].data
    w = 10 ** d["loglam"]; return dict(w=w, f=np.array(d["flux"], float), iv=np.array(d["ivar"], float), snr=np.nan)
def cii_velocity(v):
    w, f, iv = v["w"], v["f"], v["iv"]
    m = (w > 3850) & (w < 7400) & (iv > 0)
    from scipy.ndimage import percentile_filter, gaussian_filter1d
    ww, ff = w[m], f[m]
    cont = gaussian_filter1d(percentile_filter(ff, 85, size=121), 30)
    dep = 1 - ff / cont
    lines = [3921.8, 4077.0, 4268.4, 4620.5, 5146.6, 6579.9, 6584.7, 7233.3, 7238.4, 4375.5, 4412.7]
    vels = np.arange(-1000, 1001, 5.0); cc = []
    for vel in vels:
        t = np.zeros_like(ww)
        for l in lines:
            t += np.exp(-0.5 * ((ww - l * (1 + vel / C)) / 1.7) ** 2)
        cc.append(np.corrcoef(dep, t)[0, 1])
    cc = np.array(cc); return float(vels[np.argmax(cc)]), float(cc.max())
def measure(v, vel):
    out = {}
    for nm, (lo, hi, sb) in FEATS.items():
        s = 1 + vel / C
        sbw = sb if sb else [(lo - 14, lo - 2), (hi + 2, hi + 14)]
        wins = [(a * s, b * s) for a, b in sbw]
        w, f, iv = v["w"], v["f"], v["iv"]
        try:
            cont = linear_cont(w, f, iv, wins)
        except Exception:
            out[nm] = (np.nan, np.nan); continue
        sel = (w > lo * s) & (w < hi * s) & (iv > 0)
        if sel.sum() < 4:
            out[nm] = (np.nan, np.nan); continue
        dw = np.gradient(w)
        E = np.sum((1 - f[sel] / cont[sel]) * dw[sel]); eE = np.sqrt(np.sum((dw[sel] / np.sqrt(iv[sel]) / cont[sel]) ** 2))
        out[nm] = (E, eE)
    return out
if __name__ == "__main__":
    specs = [("TARGET 5208047381438507520 (SDSS-V LCO 1 visit)", load_visits(TARGET)[0])]
    for n in ["J1426+5752", "J0106+1513", "J2348-0942", "J1337-0026", "PHL657", "PB7043"]:
        specs.append((f"hot DQ {n} (SDSS DR17)", load_sdss(f"{SPEC}/sdss_{n}.fits")))
    for sid, lab in [(79068566, "DQA warm 17.6kK (MWDD) coadd"), (89905789, "DQA warm 16.2kK coadd"), (82182126, "DQ: 15.2kK coadd"), (61206487, "SW DA: 120kK?"), (95489940, "SW DA/hotDQ"), (70916622, "SW hotDQ/DC")]:
        c = coadd(f"{SPEC}/mwmVisit-0.8.1-{sid}.fits")
        specs.append((f"{sid} {lab}", c))
    print("name | v_CII (km/s), ccf | EW (A) per feature")
    print("feature: " + " ".join(f"{k:>10s}" for k in FEATS))
    res = {}
    for nm, v in specs:
        vel, ccm = cii_velocity(v)
        m = measure(v, vel)
        res[nm] = dict(v=vel, ccf=ccm, ew={k: m[k] for k in m})
        print(f"{nm[:52]:52s} v={vel:+5.0f} cc={ccm:.2f}")
        print("   EW " + " ".join(f"{m[k][0]:6.2f}+-{m[k][1]:.2f}" for k in FEATS))
    json.dump(res, open("/tmp/hotdq/review2/spec_agent/carbon_ew.json", "w"), indent=1, default=float)

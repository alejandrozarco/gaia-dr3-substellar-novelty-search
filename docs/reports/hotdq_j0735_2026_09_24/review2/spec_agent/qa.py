# Task 3: data-quality checks. (a) shift-undo convention verified on a multi-visit carbon WD with in_stack True/False visits;
# (b) target velocity with/without undo; (c) sky-line/telluric positions; (d) flags at each C II feature; (e) barycentric correction.
import sys, json, numpy as np
sys.path.insert(0, "/tmp/hotdq/review2/spec_agent")
from common import *
from carbon import cii_velocity, FEATS
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from scipy.ndimage import gaussian_filter1d, percentile_filter
print("(a) convention test: per-visit C II CCF velocity after undo (lambda = grid*(1+v/c) only if in_stack) vs raw grid")
for sid in [79068566]:
    for v in load_visits(f"{SPEC}/mwmVisit-0.8.1-{sid}.fits"):
        vu, cu = cii_velocity(v)
        raw = dict(v); raw["w"] = v["wg"]; vr, cr = cii_velocity(raw)
        print(f"  {sid} MJD {v['mjd']} in_stack={v['in_stack']} xcsao={v['xv']:+6.0f} snr={v['snr']:.1f} -> v(undo rule)={vu:+5.0f} (cc {cu:.2f}); v(raw grid)={vr:+5.0f}")
print("(a2) Balmer-line centroid per visit for a bright multi-visit DA (57579772, xcsao -81..+178): H-beta/H-alpha core Gaussian centre")
from scipy.optimize import curve_fit
def g(x, a, mu, s, c0, c1): return c0 + c1 * (x - mu) - a * np.exp(-0.5 * ((x - mu) / s) ** 2)
for v in load_visits(f"{SPEC}/mwmVisit-0.8.1-57579772.fits"):
    if v["snr"] < 20: continue
    outs = []
    for lam in [6564.61, 4862.68]:
        for key in ["w", "wg"]:
            w = v[key]; s = np.abs(w - lam) < 12
            try:
                p, _ = curve_fit(g, w[s], v["f"][s] / np.median(v["f"][s]), p0=[0.3, lam, 4, 1, 0])
                outs.append((p[1] / lam - 1) * C)
            except Exception:
                outs.append(np.nan)
    print(f"  MJD {v['mjd']} xcsao {v['xv']:+5.0f}: Halpha core v undo {outs[0]:+5.0f} raw {outs[1]:+5.0f} | Hbeta undo {outs[2]:+5.0f} raw {outs[3]:+5.0f}")
t = load_visits(TARGET)[0]
print(f"(b) target: in_stack={t['in_stack']}, xcsao_v_rad={t['xv']:+.1f}, nexp={t['nexp']}")
vu, cu = cii_velocity(t); raw = dict(t); raw["w"] = t["wg"]; vr, cr = cii_velocity(raw)
print(f"    C II CCF velocity: shift undone {vu:+.0f} km/s (cc {cu:.2f}); NOT undone {vr:+.0f} km/s (cc {cr:.2f})")
# barycentric correction
lco = EarthLocation.of_site("Las Campanas Observatory")
tm = Time(60695.0 + (5244061289 + 450) / 86400.0 - 60695 * 0 - 5244061289 / 86400.0 + 5244061289 / 86400.0 - 60695.0, format="mjd") if False else Time((5244061289 + 450) / 86400.0, format="mjd", scale="tai")
co = SkyCoord(113.7671 * u.deg, -79.73634 * u.deg)
bc = co.radial_velocity_correction(kind="barycentric", obstime=tm, location=lco).to(u.km / u.s).value
print(f"    obs time {tm.utc.iso} UTC; barycentric correction {bc:+.2f} km/s (sky/telluric features appear at v_bary ~ {bc:+.1f} km/s after correct undo; at {bc - t['xv']:+.1f} if the undo were wrong)")
# (c) sky/telluric tests: telluric O2 A/B band and water residuals cross-correlated with a DA control's (convention-independent zero point = control's own undo)
def norm(w, f):
    cont = gaussian_filter1d(percentile_filter(f, 90, size=151), 25); return f / cont
for lab, (lo, hi) in {"O2 B band 6860-6960": (6855, 6960), "O2 A band 7590-7720": (7585, 7720), "H2O 8130-8350": (8120, 8350)}.items():
    # template: mean normalised residual of all LCO/APO control visits with snr>10, in their barycentric frame
    stack = []; wref = np.arange(lo, hi, 0.5)
    import glob
    for fn in glob.glob(SPEC + "/mwmVisit-0.8.1-*.fits"):
        for v in load_visits(fn):
            if v["snr"] < 12: continue
            n = norm(v["w"], v["f"]); stack.append(np.interp(wref, v["w"], n))
    tmpl = np.median(stack, 0)
    nt = np.interp(wref, t["w"], norm(t["w"], t["f"]))
    vels = np.arange(-400, 401, 5.0); cc = []
    for vel in vels:
        cc.append(np.corrcoef(np.interp(wref, wref * (1 + vel / C), nt), tmpl)[0, 1])
    cc = np.array(cc)
    print(f"    telluric-residual CCF target(undo) vs control stack, {lab}: peak {vels[np.argmax(cc)]:+.0f} km/s (r={cc.max():.2f}); r at 0: {cc[vels==0][0]:.2f}; r at -178: {cc[vels==-180][0]:.2f}; r at +178: {cc[vels==180][0]:.2f}")
# sky emission 5578.89 / 6302.05 / 6365.54 / NaD: local residual profile
for sl in [5578.89, 6302.05, 6365.54, 5891.58, 5897.56]:
    for key, lab in [("w", "undo"), ("wg", "raw")]:
        w = t[key]; s = np.abs(w - sl) < 10
        n = t["f"][s] / np.median(t["f"][s]); k = np.argmax(np.abs(n - 1))
    w = t["w"]; s = np.abs(w - sl) < 8
    n = t["f"][s] / np.median(t["f"][s]); fl = t["flags"][s].astype(np.int64)
    print(f"    sky {sl:.2f}: pixels within 8 A (undo frame): " + " ".join(f"{a:.1f}:{b:.2f}{'*' if c else ''}" for a, b, c in zip(w[s], n, fl != 0)))
print("(d) flags within each C II feature window at +93 km/s (fraction of pixels with any flag; bits other than the ubiquitous 17/22/24/26):")
UBQ = (1 << 17) | (1 << 22) | (1 << 24) | (1 << 26)
for nm, (lo, hi, sb) in FEATS.items():
    s = (t["w"] > lo * (1 + 93 / C)) & (t["w"] < hi * (1 + 93 / C))
    fl = t["flags"][s].astype(np.int64)
    other = fl & ~UBQ
    bits = sorted(set(b for x in other for b in range(32) if (x >> b) & 1))
    print(f"    {nm:10s}: n={s.sum()}, any flag {np.mean(fl != 0):.2f}, non-ubiquitous flag {np.mean(other != 0):.2f} bits {bits}, min ivar>0: {np.all(t['iv'][s] > 0)}")

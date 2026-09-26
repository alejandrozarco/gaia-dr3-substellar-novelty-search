# Generalised line test for SDSS-V white-dwarf spectra: python spec_lines_gen.py <sdss_id> <label>
# Visits from the mwmVisit file; the XCSAO rest-frame shift is undone only for in_stack visits (lambda = grid (1 + v/c));
# inverse-variance coadd on a common log-lambda grid; continuum = running 85th percentile over 120 A (smoothed); depth = 1 - f/cont.
# Template cross-correlation with NIST vacuum lines (15 strongest per species, Gaussian FWHM 4 A), for the coadd and for each
# visit separately; the "contrast" is (peak - median)/(1.4826 MAD) off-peak (not a calibrated false-alarm probability).
# Gaussian fits to the C II features used for 5208047381438507520; H/He depths at the C II velocity against a baseline of
# 400 random windows free of C II lines.
import sys, json, numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.ndimage import percentile_filter, gaussian_filter1d
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sid, label = sys.argv[1], sys.argv[2]; C = 299792.458
L = json.load(open("/tmp/hotdq/dd/nist_vacuum_lines.json")); L["He II"] = [(4687.02, 100.0), (5413.03, 50.0), (6562.0, 40.0), (4542.9, 20.0)]
grid = 10 ** np.arange(np.log10(3700), np.log10(9300), 6e-5)
visits = []
with fits.open(f"/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-{sid}.fits") as h:
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        hd = h[i].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
        for r in h[i].data:
            v = float(r["xcsao_v_rad"]); ins = bool(r["in_stack"])
            w = wg * (1 + v / C) if ins else wg
            f = np.array(r["flux"], float); iv = np.array(r["ivar"], float); ok = (iv > 0) & np.isfinite(f)
            visits.append(dict(mjd=int(r["mjd"]), v=v, in_stack=ins, snr=float(r["snr"]), f=np.interp(grid, w[ok], f[ok], left=np.nan, right=np.nan),
                               iv=np.interp(grid, w[ok], iv[ok], left=0, right=0)))
def prep(f, iv):
    m = np.isfinite(f) & (iv > 0); w, f, iv = grid[m], f[m], iv[m]
    npix = int(round(np.log10(1 + 120 / 5000) / 6e-5)); cont = gaussian_filter1d(percentile_filter(f, 85, size=npix), npix / 4)
    return w, f, iv, cont, 1 - f / cont, 1 / np.sqrt(iv) / cont
num = np.nansum([v["f"] * v["iv"] for v in visits], axis=0); den = np.sum([v["iv"] for v in visits], axis=0)
co = dict(f=np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), iv=den)
def strongest(sp, n=15, lo=3850, hi=9200, merge=1.5):
    rows = sorted([x for x in L[sp] if lo < x[0] < hi], key=lambda x: -x[1]); out = []
    for lam, I in rows:
        if all(abs(lam - q) > merge for q in out): out.append(lam)
        if len(out) == n: break
    return out
def ccf(w, depth, species, vels=np.arange(-3000, 3001, 10.0)):
    res = {}
    for sp in species:
        lines = strongest(sp)
        if not lines: continue
        cc = []
        for vv in vels:
            t = np.zeros_like(w)
            for lam in lines: t += np.exp(-0.5 * ((w - lam * (1 + vv / C)) / 1.7) ** 2)
            cc.append(np.corrcoef(depth, t)[0, 1])
        cc = np.array(cc); k = np.argmax(cc); far = np.abs(vels - vels[k]) > 1000; mad = 1.4826 * np.median(np.abs(cc[far] - np.median(cc[far])))
        res[sp] = dict(v=float(vels[k]), r=float(cc[k]), contrast=float((cc[k] - np.median(cc[far])) / mad), cc=cc)
    return vels, res
SPEC = ["C II", "He I", "H I", "C I", "O I", "O II", "C III", "He II", "Mg II", "Si II"]
w, f, iv, cont, depth, edep = prep(co["f"], co["iv"])
vels, R = ccf(w, depth, SPEC)
print(f"== {label} (sdss_id {sid}); visits: " + "; ".join(f"MJD {v['mjd']} S/N {v['snr']:.1f} xcsao {v['v']:+.0f} in_stack {v['in_stack']}" for v in visits))
for sp in SPEC:
    if sp in R: print(f"  coadd {sp:6s}: contrast {R[sp]['contrast']:5.1f} at {R[sp]['v']:+5.0f} km/s (r {R[sp]['r']:.3f})")
for v in visits:
    wv, fv, ivv, cv, dv, ev = prep(v["f"], v["iv"]); _, Rv = ccf(wv, dv, ["C II", "He I", "H I"])
    print(f"  visit MJD {v['mjd']}: C II contrast {Rv['C II']['contrast']:.1f} at {Rv['C II']['v']:+.0f} km/s; He I {Rv['He I']['contrast']:.1f}; H I {Rv['H I']['contrast']:.1f}")
feats = [(3918, 3924), (4074, 4079), (4266, 4271), (4371, 4378), (4618, 4623), (5889, 5895), (6577, 6587), (6780, 6787), (7230, 7241)]
def g(x, a, mu, s, c0, c1): return c0 + c1 * (x - mu) - a * np.exp(-0.5 * ((x - mu) / s) ** 2)
vg = R["C II"]["v"]; rows = []
for lo, hi in feats:
    comps = [x for x in L["C II"] if lo <= x[0] <= hi]; lab = sum(a * b for a, b in comps) / sum(b for a, b in comps)
    mu0 = lab * (1 + vg / C); sel = np.abs(w - mu0) < 25
    try:
        p, cv = curve_fit(g, w[sel], f[sel] / cont[sel], p0=[0.1, mu0, 3.0, 1, 0], sigma=edep[sel], absolute_sigma=True, bounds=([0, mu0 - 8, 0.8, 0.5, -1], [1, mu0 + 8, 15, 1.5, 1]), maxfev=20000)
        e = np.sqrt(np.diag(cv)); rows.append(dict(lab=round(lab, 2), v=round((p[1] / lab - 1) * C), e_v=round(e[1] / lab * C), depth=round(p[0], 3), snr=round(p[0] / e[0], 1), sigma=round(p[2], 2)))
    except Exception as ex: rows.append(dict(lab=round(lab, 2), fail=str(ex)[:60]))
for r in rows: print("   C II", r)
good = [r for r in rows if r.get("snr", 0) > 4 and r.get("e_v", 1e9) < 200]
if good:
    vv = np.array([r["v"] for r in good]); ev = np.array([r["e_v"] for r in good]); wt = 1 / ev ** 2; vm = np.sum(vv * wt) / np.sum(wt)
    print(f"  {len(good)} C II features with depth > 4 sigma: weighted mean v {vm:+.0f} km/s, scatter {np.std(vv):.0f} km/s")
else: vm = vg
rng = np.random.default_rng(1); cii = np.array([x[0] for x in L["C II"] if x[1] >= 30])
base = []
for mu in [x for x in rng.uniform(3900, 7400, 4000) if np.min(np.abs(cii * (1 + vm / C) - x)) > 8][:400]:
    s = np.abs(w - mu) < 3; base.append(np.sum(depth[s] / edep[s] ** 2) / np.sum(1 / edep[s] ** 2))
print(f"  baseline depth (random C II-free windows): median {np.median(base):+.3f}, 99% {np.percentile(base, 99):+.3f}")
for nm, lam in [("H-alpha", 6564.632), ("H-beta", 4862.691), ("He I 4472", 4472.735), ("He I 5877", 5877.25), ("He I 6680", 6679.99), ("He II 4687", 4687.02)]:
    s = np.abs(w - lam * (1 + vm / C)) < 3; d = np.sum(depth[s] / edep[s] ** 2) / np.sum(1 / edep[s] ** 2)
    print(f"   {nm:10s}: depth {d:+.3f} (baseline 99% {np.percentile(base, 99):+.3f})")
fig, ax = plt.subplots(3, 1, figsize=(15, 10), gridspec_kw=dict(height_ratios=[1.2, 1.2, 1]))
for a, (lo, hi) in zip(ax[:2], [(3800, 5500), (5500, 7450)]):
    s = (w > lo) & (w < hi); a.plot(w[s], gaussian_filter1d(f[s] / cont[s], 1.0), "k", lw=0.7)
    for lam, I in L["C II"]:
        if lo < lam < hi and I >= 100: a.axvline(lam * (1 + vm / C), color="m", lw=0.6, alpha=0.5)
    for lam in [6564.632, 4862.691, 4341.691]:
        if lo < lam < hi: a.axvline(lam * (1 + vm / C), color="b", ls="--", lw=0.8)
    for lam in [4472.735, 5877.25, 6679.99, 4027.3, 4923.3, 5017.1]:
        if lo < lam < hi: a.axvline(lam * (1 + vm / C), color="g", ls=":", lw=0.9)
    a.set_xlim(lo, hi); a.set_ylim(0.5, 1.15)
ax[0].set_title(f"{label} (sdss_id {sid}), {len(visits)}-visit coadd. magenta C II, blue Balmer, green He I, all at {vm:+.0f} km/s", fontsize=9)
for sp, col in [("C II", "m"), ("He I", "g"), ("H I", "b"), ("C I", "orange")]:
    ax[2].plot(vels, R[sp]["cc"], color=col, label=f"{sp} (contrast {R[sp]['contrast']:.1f})")
ax[2].legend(fontsize=8); ax[2].set_xlabel("velocity (km/s)")
plt.tight_layout(); plt.savefig(f"/tmp/hotdq/dd/fig_lines_{label}.png", dpi=85)
json.dump(dict(sid=sid, label=label, visits=[{k: v[k] for k in ("mjd", "v", "in_stack", "snr")} for v in visits],
               ccf={k: {kk: vv for kk, vv in v.items() if kk != "cc"} for k, v in R.items()}, cii=rows, v_mean=float(vm)), open(f"/tmp/hotdq/dd/lines_{label}.json", "w"), indent=1)

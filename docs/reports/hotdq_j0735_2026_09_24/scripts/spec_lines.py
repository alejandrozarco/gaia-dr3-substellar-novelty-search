# Line identification for Gaia DR3 5208047381438507520 (SDSS-V DR20 sdss_id 95077848; one LCO BOSS visit, MJD 60695).
# 1) Visit spectrum with the XCSAO rest-frame shift undone (in_stack visit: lambda_bary = lambda_grid (1 + v_xcsao/c)).
# 2) Continuum: running 85th percentile over 120 A, smoothed; depth = 1 - flux/continuum.
# 3) Template cross-correlation per species (NIST vacuum wavelengths): binary template of the N strongest lines of each species
#    in 3850-9200 A (Gaussian FWHM 4 A), Pearson correlation with the depth spectrum vs velocity (-3000..+3000 km/s);
#    significance = (peak - median) / (1.4826 MAD) over |v| > 1000 km/s from the peak.
# 4) Gaussian fits to the individual C II features; centroids vs intensity-weighted NIST vacuum centroids -> velocities.
import json, numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.ndimage import percentile_filter, gaussian_filter1d
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
C = 299792.458
L = json.load(open("nist_vacuum_lines.json"))
L["He II"] = [(4687.02, 100.0), (5413.03, 50.0), (6562.0, 40.0), (4542.9, 20.0)]
with fits.open("/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-95077848.fits") as h:
    hd = h[2].header; r = h[2].data[0]
    wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"])); v0 = float(r["xcsao_v_rad"])
    w = wg * (1 + v0 / C); f = np.array(r["flux"], float); iv = np.array(r["ivar"], float)
m = (w > 3700) & (w < 9300) & (iv > 0) & np.isfinite(f)
w, f, iv = w[m], f[m], iv[m]
dlog = np.median(np.diff(np.log10(w))); npix = int(round(np.log10(1 + 120 / 5000) / dlog))
cont = gaussian_filter1d(percentile_filter(f, 85, size=npix), npix / 4)
depth = 1 - f / cont; edep = 1 / np.sqrt(iv) / cont
def template(lines, vel, fwhm=4.0):
    s = fwhm / 2.3548; t = np.zeros_like(w)
    for lam in lines:
        lo = lam * (1 + vel / C); t += np.exp(-0.5 * ((w - lo) / s) ** 2)
    return t
def strongest(sp, n=15, lo=3850, hi=9200, merge=1.5):
    rows = sorted([x for x in L[sp] if lo < x[0] < hi], key=lambda x: -x[1]); out = []
    for lam, I in rows:
        if all(abs(lam - q) > merge for q in out): out.append(lam)
        if len(out) == n: break
    return out
vels = np.arange(-3000, 3001, 10.0); res = {}
for sp in ["C II", "He I", "H I", "C I", "O I", "O II", "C III", "He II", "Mg II", "Si II"]:
    lines = strongest(sp)
    if not lines: continue
    cc = np.array([np.corrcoef(depth, template(lines, v))[0, 1] for v in vels]); k = np.argmax(cc)
    far = np.abs(vels - vels[k]) > 1000; mad = 1.4826 * np.median(np.abs(cc[far] - np.median(cc[far])))
    res[sp] = dict(n_lines=len(lines), v_peak=float(vels[k]), cc_peak=float(cc[k]), z=float((cc[k] - np.median(cc[far])) / mad), cc=cc.tolist())
    print(f"{sp:6s} {len(lines):2d} lines: CCF peak r = {cc[k]:.3f} at {vels[k]:+.0f} km/s, significance {res[sp]['z']:.1f} sigma")
# individual C II features
feats = [(3918, 3924), (4074, 4079), (4266, 4271), (4371, 4378), (4618, 4623), (4737, 4750), (5134, 5155), (5889, 5895), (6577, 6587), (6780, 6787), (7230, 7241)]
def g(x, a, mu, s, c0, c1): return c0 + c1 * (x - mu) - a * np.exp(-0.5 * ((x - mu) / s) ** 2)
rows = []
for lo, hi in feats:
    comps = [x for x in L["C II"] if lo <= x[0] <= hi]
    if not comps: continue
    lab = sum(a * b for a, b in comps) / sum(b for a, b in comps)
    vg = res["C II"]["v_peak"]; mu0 = lab * (1 + vg / C)
    sel = np.abs(w - mu0) < 18
    try:
        p, cv = curve_fit(g, w[sel], f[sel] / cont[sel], p0=[0.1, mu0, 2.5, 1, 0], sigma=edep[sel], absolute_sigma=True, maxfev=20000)
        e = np.sqrt(np.diag(cv)); vel = (p[1] / lab - 1) * C; evel = e[1] / lab * C
        ew = p[0] * abs(p[2]) * np.sqrt(2 * np.pi)
        rows.append(dict(window=[lo, hi], lab_vac=round(lab, 2), n_comp=len(comps), center=round(float(p[1]), 2), e_center=round(float(e[1]), 2),
                         v=round(float(vel), 0), e_v=round(float(evel), 0), depth=round(float(p[0]), 3), sigma_A=round(float(abs(p[2])), 2), EW_A=round(float(ew), 2), depth_snr=round(float(p[0] / e[0]), 1)))
        print(f"  C II {lab:8.2f}: center {p[1]:8.2f} +- {e[1]:.2f} -> v {vel:+6.0f} +- {evel:4.0f} km/s; depth {p[0]:.3f} ({p[0]/e[0]:.1f} sigma), sigma {abs(p[2]):.2f} A, EW {ew:.2f} A")
    except Exception as ex:
        print("  fit failed", lo, hi, ex)
good = [x for x in rows if x["depth_snr"] > 5 and x["e_v"] < 150]
vv = np.array([x["v"] for x in good]); ev = np.array([x["e_v"] for x in good]); wts = 1 / ev ** 2
vm = np.sum(vv * wts) / np.sum(wts); evm = 1 / np.sqrt(np.sum(wts)); chi2 = np.sum(((vv - vm) / ev) ** 2)
print(f"weighted mean C II velocity {vm:.0f} +- {evm:.0f} km/s from {len(good)} features; chi2 {chi2:.1f} for {len(good)-1} dof; scatter {np.std(vv):.0f} km/s")
# hydrogen and helium checks at the C II velocity
for nm, lam in [("H-alpha", 6564.632), ("H-beta", 4862.691), ("H-gamma", 4341.691), ("He I 4472", 4472.735), ("He I 5877", 5877.25), ("He I 6680", 6679.99), ("He II 4687", 4687.02), ("C I 9097", 9097.33), ("O I 7774", 7774.08)]:
    mu = lam * (1 + vm / C); sel = np.abs(w - mu) < 3
    d = np.sum(depth[sel] / edep[sel] ** 2) / np.sum(1 / edep[sel] ** 2); ed = 1 / np.sqrt(np.sum(1 / edep[sel] ** 2))
    print(f"  {nm:11s} at {mu:8.2f}: mean depth {d:+.3f} +- {ed:.3f} ({d/ed:+.1f} sigma)")
json.dump(dict(xcsao_v=v0, ccf={k: {kk: vv2 for kk, vv2 in v.items() if kk != "cc"} for k, v in res.items()}, features=rows, v_mean=vm, e_v_mean=evm, chi2=chi2), open("spec_lines.json", "w"), indent=1)
fig, ax = plt.subplots(3, 1, figsize=(15, 11), gridspec_kw=dict(height_ratios=[1.2, 1.2, 1]))
for a, (lo, hi) in zip(ax[:2], [(3800, 5500), (5500, 7450)]):
    s = (w > lo) & (w < hi); a.plot(w[s], f[s] / cont[s], "k", lw=0.7)
    for lam, I in L["C II"]:
        if lo < lam < hi and I >= 100: a.axvline(lam * (1 + vm / C), color="m", lw=0.6, alpha=0.6)
    for lam in [6564.632, 4862.691, 4341.691, 4102.899]:
        if lo < lam < hi: a.axvline(lam, color="b", ls="--", lw=0.8)
    for lam in [4472.735, 5877.25, 6679.99, 4027.3, 4923.3, 5017.1, 7067.1]:
        if lo < lam < hi: a.axvline(lam, color="g", ls=":", lw=0.9)
    a.set_ylim(0.55, 1.12); a.set_xlim(lo, hi); a.set_ylabel("normalised flux")
ax[0].set_title(f"Gaia DR3 5208047381438507520, SDSS-V BOSS visit MJD 60695 (XCSAO shift undone). Magenta: NIST C II (rel. int. >= 100) at {vm:+.0f} km/s; blue dashed: Balmer (rest); green dotted: He I (rest)", fontsize=9)
for sp, col in [("C II", "m"), ("He I", "g"), ("H I", "b"), ("C I", "orange"), ("O II", "c"), ("He II", "r")]:
    if sp in res: ax[2].plot(vels, res[sp]["cc"], color=col, label=f"{sp} ({res[sp]['z']:.1f} sigma at {res[sp]['v_peak']:+.0f})")
ax[2].set_xlabel("velocity (km/s)"); ax[2].set_ylabel("template correlation"); ax[2].legend(fontsize=8)
plt.tight_layout(); plt.savefig("fig_lines_ccf.png", dpi=90)

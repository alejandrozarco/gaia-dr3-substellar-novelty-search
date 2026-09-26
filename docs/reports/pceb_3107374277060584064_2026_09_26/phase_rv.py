"""Hot WD Gaia DR3 3107374277060584064 (SDSS-V sdss_id 74709777): ZTF sine ephemeris (g and r, shared frequency and phase, separate
amplitudes/offsets; frequency grid 1.6860-1.6873 c/d) and the photometric phase of each SDSS-V visit (mid-exposure from tai_beg/tai_end,
no barycentric correction: < 0.01 in phase). Per visit: Gaussian fits (quadratic baseline) to H-alpha and the Ca II triplet (common
velocity and width, three amplitudes) on the visit spectrum with the XCSAO shift undone for in_stack visits (sdssv.visits)."""
import os
import sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import sdssv
from astropy.io import fits
from scipy.optimize import curve_fit
C = 299792.458
z = pd.read_csv("ztf_WD.csv"); z = z[z.filtercode.isin(["zg", "zr"])]
t = z.hjd.values - 2400000.5; fl = np.zeros(len(z)); e = np.zeros(len(z)); band = (z.filtercode == "zr").values.astype(int)
for b in (0, 1):
    m = band == b; fl[m] = 10 ** (-0.4 * (z.mag.values[m] - np.median(z.mag.values[m]))); e[m] = 0.921 * z.magerr.values[m] * fl[m]
best = None
for f in np.arange(1.6860, 1.6873, 2e-6):
    X = np.vstack([band == 0, band == 1, (band == 0) * np.cos(2*np.pi*f*t), (band == 0) * np.sin(2*np.pi*f*t)]).T.astype(float)
    # shared phase: fit g and r cos/sin separately then require same phase via r-band only
    Xr = np.vstack([band == 0, band == 1, np.cos(2*np.pi*f*t) * np.where(band == 1, 1, 0.5), np.sin(2*np.pi*f*t) * np.where(band == 1, 1, 0.5)]).T.astype(float)
    c, *_ = np.linalg.lstsq(Xr / e[:, None], fl / e, rcond=None); chi = np.sum(((fl - Xr @ c) / e) ** 2)
    if best is None or chi < best[0]: best = (chi, f, c)
chi, f0, c = best; amp = np.hypot(c[2], c[3]); phi = np.arctan2(c[3], c[2])
# flux = a cos(2 pi f t - phi)  -> maximum at t = phi / (2 pi f) + k/f
T0 = phi / (2*np.pi*f0); T0 += np.round((59300 - T0) * f0) / f0
print(f"ZTF: f = {f0:.6f} c/d (P = {24/f0:.4f} h), r semi-amplitude {100*amp:.1f}% (g fixed at half of r), chi2/dof {chi/(len(t)-4):.2f}, max light at MJD {T0:.4f}")
# frequency error from chi2 + 1 (scaled)
def g(x, *p): return p[0] + p[1]*(x - x.mean()) + p[2]*(x - x.mean())**2 + sum(p[3+k] * np.exp(-0.5*((x - L[k]*(1+p[-2]/C)) / (L[k]*p[-1]/C))**2) for k in range(len(L)))
rows = []
h = fits.open(sdssv.fetch(74709777, "visit"))
tv = {int(r["mjd"]): ((r["tai_beg"] + r["tai_end"]) / 2 / 86400) for i in (1, 2) if h[i].data is not None and len(h[i].data) for r in h[i].data}
for v in sdssv.visits(74709777):
    tm = tv[v["mjd"]]; ph = ((tm - T0) * f0) % 1; row = dict(mjd=v["mjd"], t_mid=round(tm, 4), phase_from_max=round(ph, 3), snr=round(v["snr"], 1), in_stack=v["in_stack"], xcsao=round(v["xcsao_v"], 1))
    for name, Ls, win in (("Ha", [6564.61], 1800), ("CaT", [8500.35, 8544.44, 8664.52], 1200)):
        L = Ls; m = np.zeros(len(v["wave"]), bool)
        for l in L: m |= np.abs(v["wave"]/l - 1) * C < win
        x, y, iv = v["wave"][m], v["flux"][m], v["ivar"][m]; ok = (iv > 0) & np.isfinite(y); x, y, iv = x[ok], y[ok], iv[ok]
        med = np.median(y); p0 = [med, 0, 0] + [0.3*med]*len(L) + [0, 150]
        try:
            p, cv = curve_fit(g, x, y, p0=p0, sigma=1/np.sqrt(iv), absolute_sigma=True, maxfev=20000,
                              bounds=([-np.inf]*3 + [-np.inf]*len(L) + [-600, 30], [np.inf]*3 + [np.inf]*len(L) + [600, 800]))
            pe = np.sqrt(np.diag(cv)); a = p[3:3+len(L)]; ea = pe[3:3+len(L)]
            snr_line = np.sum(a) / np.sqrt(np.sum(ea**2))
            row.update({f"{name}_v": round(p[-2], 0), f"{name}_ev": round(pe[-2], 0), f"{name}_sigma": round(p[-1], 0), f"{name}_amp_snr": round(snr_line, 1)})
        except Exception as ex:
            row[f"{name}_v"] = f"fail {type(ex).__name__}"
    rows.append(row)
out = pd.DataFrame(rows); print(out.to_string(index=False)); out.to_csv("visit_phase_rv.csv", index=False)

"""H-alpha velocities of GALEX J142443.0+110123 from three public ESO FORS2 1200R spectra (programme 0101.D-0384(A), 2018 April;
ESO Phase-3 ADP products) (2026-09-30). Same line model as rv_fit.py (two Gaussians + linear continuum, common centre) over
+-40 A. The ADP wavelength frame (SPECSYS keyword) is reported; if TOPOCENT, a barycentric correction for Paranal is applied.
Wavelength zero point checked on the sky [O I] 6300.30 and 6363.78 A (air) lines in BGFLUX. Output: fors2_rv.txt."""
import glob, numpy as np
from astropy.io import fits; from astropy.time import Time; from astropy.coordinates import SkyCoord, EarthLocation; import astropy.units as u
from scipy.optimize import least_squares
C = 299792.458; pos = SkyCoord(216.17895 * u.deg, 11.02292 * u.deg); paranal = EarthLocation.of_site("paranal")
def model(p, x):
    mu, c0, c1, a1, s1, a2, s2 = p; d = x - mu; return c0 + c1 * d - a1 * np.exp(-d**2 / (2 * s1**2)) - a2 * np.exp(-d**2 / (2 * s2**2))
def fit(x, y, e, l0, W, narrow=False):
    m = (x > l0 - W) & (x < l0 + W) & np.isfinite(y) & (e > 0); x, y, e = x[m], y[m], e[m]; c = np.median(np.r_[y[:5], y[-5:]]); y, e = y / c, e / c
    if narrow:   # sky emission line: Gaussian + constant
        f = lambda p: (p[1] + p[2] * np.exp(-(x - p[0])**2 / (2 * p[3]**2)) - y) / e; r = least_squares(f, [l0, 1, 1, 1.5])
    else:
        lo = [l0 - 15, 0.2, -1, 0, 0.5, 0, 2]; hi = [l0 + 15, 3, 1, 2, 15, 2, 3 * W]; p0 = np.clip([x[np.argmin(y)], 1, 0, 0.3, 3, 0.3, W / 3], lo, hi)
        r = least_squares(lambda p: (model(p, x) - y) / e, p0, bounds=(lo, hi))
    red = 2 * r.cost / max(len(x) - len(r.x), 1); cov = np.linalg.inv(r.jac.T @ r.jac) * max(1, red); return r.x[0], np.sqrt(cov[0, 0])
out = []
for f in sorted(glob.glob("ADP*.fits")):
    h = fits.open(f); H0 = h[0].header; d = h[1].data; w = d["WAVE"][0]; fl = d["FLUX"][0]; er = d["ERR"][0]; bg = d["BGFLUX"][0]
    mjd = H0["MJD-OBS"] + H0["EXPTIME"] / 2 / 86400; spec = H0.get("SPECSYS", "?")
    bc = pos.radial_velocity_correction(kind="barycentric", obstime=Time(mjd, format="mjd"), location=paranal).to(u.km / u.s).value
    mu, emu = fit(w, fl, er, 6562.80, 40)
    sky = [fit(w, bg, np.sqrt(np.abs(bg)) + 1, l, 6, narrow=True) for l in (6300.304, 6363.776)]
    dz = np.mean([C * (s[0] / l - 1) for s, l in zip(sky, (6300.304, 6363.776))])
    v = C * (mu / 6562.80 - 1); vb = v - dz + (bc if spec != "BARYCENT" else 0)
    out.append(f"{f} MJD(mid) {mjd:.4f} SPECSYS {spec} S/N {H0.get('SNR', 0):.0f}: H-alpha centre {mu:.3f} +- {emu:.3f} A -> {v:.1f} +- {C * emu / 6562.8:.1f} km/s (frame); sky [O I] offset {dz:.1f} km/s; barycentric corr {bc:.1f}; v_bary (sky-corrected) {vb:.1f} km/s")
open("fors2_rv.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))

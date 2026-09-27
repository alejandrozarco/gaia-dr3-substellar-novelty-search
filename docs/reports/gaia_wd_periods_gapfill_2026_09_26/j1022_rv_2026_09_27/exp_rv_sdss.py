"""Per-exposure Balmer-line velocities of SDSS J1022+1611 from the full SDSS (2589-54174-0043) and BOSS (5337-55987-0142) spec files.
Template: the COADD of the same visit. Each exposure (camera b1: H-beta, H-gamma, H-delta, H-epsilon; camera r1: H-alpha) is continuum-normalised
(linear, 2500-3500 km/s from the line) and shifted against the template over -500..+500 km/s (2 km/s); chi2 over |v| < 1500 km/s; parabola refinement;
error from delta chi2 = 1 after scaling chi2_min to dof. Per exposure: weighted mean over lines. Times: TAI-BEG + EXPTIME/2 (MJD, TAI; heliocentric
correction not applied - identical within a visit to < 1 km/s)."""
import sys, numpy as np
from astropy.io import fits
C = 299792.458; S = np.arange(-500, 501, 2.0)
LB = {"Hb": 4862.68, "Hg": 4341.69, "Hd": 4102.89, "He": 3971.20}; LR = {"Ha": 6564.61}
def seg(w, f, iv, l):
    v = (w / l - 1) * C; m = (np.abs(v) < 3500) & (iv > 0) & np.isfinite(f); v, f, iv = v[m], f[m], iv[m]; c = np.abs(v) > 2500
    if c.sum() < 6: return None
    p = np.polyfit(v[c], f[c], 1, w=np.sqrt(iv[c])); cc = np.polyval(p, v); return (v, f / cc, iv * cc ** 2) if np.median(cc) > 0 else None
def shift(X, T):
    xv, xf, xi = X; tv, tf, _ = T; m = np.abs(xv) < 1500
    chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tf)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi))
    if not 0 < i < len(S) - 1: return np.nan, np.nan
    a, b, _ = np.polyfit(S[i - 1:i + 2], chi[i - 1:i + 2], 2); red = max(chi[i] / (m.sum() - 1), 1)
    return (-b / (2 * a), np.sqrt(red / a)) if a > 0 else (np.nan, np.nan)
for fn in sys.argv[1:]:
    h = fits.open(fn); co = h["COADD"].data; wc = 10 ** co["loglam"]; fc = co["flux"]; ic = co["ivar"] * (co["and_mask"] == 0)
    T = {n: seg(wc, fc, ic, l) for n, l in {**LB, **LR}.items()}
    exps = {}
    for x in h[4:]:
        cam, e = x.name.split("-")[0], x.name.split("-")[1]; d = x.data; w = 10 ** d["loglam"]; iv = d["ivar"] * (d["mask"] == 0)
        t = (x.header["TAI-BEG"] + x.header["EXPTIME"] / 2) / 86400.0
        for n, l in (LB if cam.startswith("B") else LR).items():
            X = seg(w, d["flux"], iv, l)
            if X is None or T[n] is None: continue
            v, s = shift(X, T[n]); exps.setdefault(e, dict(t=t))[n] = (v, s)
    print("==", fn)
    for e, dd in sorted(exps.items(), key=lambda z: z[1]["t"]):
        vals = [dd[k] for k in dd if k != "t" and np.isfinite(dd[k][0]) and dd[k][1] < 60]
        if not vals: continue
        v = np.array(vals); w_ = 1 / v[:, 1] ** 2; mu = np.sum(w_ * v[:, 0]) / w_.sum(); er = 1 / np.sqrt(w_.sum())
        per = "  ".join(f"{k}:{dd[k][0]:+6.1f}±{dd[k][1]:4.1f}" for k in ("Ha", "Hb", "Hg", "Hd", "He") if k in dd)
        print(f"  exp {e} MJD {dd['t']:.5f}: mean {mu:+6.1f} ± {er:4.1f} km/s | {per}")

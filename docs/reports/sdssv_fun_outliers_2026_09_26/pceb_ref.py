"""Gaia DR3 3107374277060584064: velocity of the white dwarf's own absorption lines per SDSS-V visit (He II 4686, H-gamma, H-delta),
against the coadd of the in-stack visits, as a check of each visit's velocity zero point."""
import os
import sys, numpy as np
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
C = 299792.458; S = np.arange(-500, 501, 5.0)
vs = sdssv.visits("74709777"); w, f, iv = sdssv.coadd([v for v in vs if v["in_stack"]])[:3]
def seg(w, f, iv, l, half=2500, core=1200):
    v = (w / l - 1) * C; m = (np.abs(v) < half) & (iv > 0) & np.isfinite(f); v, f, iv = v[m], f[m], iv[m]; c = np.abs(v) > core
    p = np.polyfit(v[c], f[c], 1, w=np.sqrt(iv[c])); cc = np.polyval(p, v); return v, f / cc, iv * cc ** 2
for name, l in (("He II 4686", 4687.02), ("H-gamma", 4341.69), ("H-delta", 4102.89)):
    tv, tf, _ = seg(w, f, iv, l); out = []
    for v in vs:
        xv, xf, xi = seg(v["wave"], v["flux"], v["ivar"], l); m = np.abs(xv) < 900
        chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tf)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi))
        a, b, _ = np.polyfit(S[max(i-1,0):i + 2], chi[max(i-1,0):i + 2], 2) if 0 < i < len(S) - 1 else (np.nan, np.nan, 0)
        best = -b / (2 * a) if a > 0 else S[i]; e = np.sqrt(max(chi[i] / (m.sum() - 1), 1) / a) if a > 0 else np.nan
        out.append(f"{v['mjd']}({'S' if v['in_stack'] else 'n'},x{v['xcsao_v']:+.0f}): {best:+.0f}±{e:.0f}")
    print(name, " | ".join(out))

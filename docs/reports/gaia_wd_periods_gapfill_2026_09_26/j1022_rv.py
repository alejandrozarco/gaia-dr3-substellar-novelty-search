"""Relative radial velocities of SDSS J1022+1611 from its SDSS (2007), BOSS (2012) and LAMOST DR11 (2021, ObsID 892505193) spectra:
each spectrum continuum-normalised around H-beta, H-gamma, H-delta (+-4000 km/s, linear continuum from the window edges);
chi2 shift against the BOSS spectrum (template) over -400..+400 km/s in 2 km/s steps, line cores (+-1500 km/s) only;
error from delta chi2 = 1 after scaling chi2_min to dof."""
import os
import sys, io, gzip, time, requests, numpy as np
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
from astropy.io import fits
C = 299792.458; LINES = [4862.7, 4341.7, 4102.9]
for k in range(5):
    try: sp = GE.sparcl_spectra(155.71509, 16.19768); break
    except Exception: time.sleep(20)
raw = b""
for rel in ("v1.1", "v2.0"):
    raw = requests.get(f"https://www.lamost.org/dr11/{rel}/spectrum/fits/892505193", timeout=120).content
    if len(raw) > 5000: break
if len(raw) > 5000:
    d = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw))[1].data[0]
    sp.append(dict(dataset="LAMOST DR11", date="2021-02-13", w=np.asarray(d["WAVELENGTH"], float), f=np.asarray(d["FLUX"], float), iv=np.asarray(d["IVAR"], float) * (d["ANDMASK"] == 0)))
else: print("LAMOST HOLE")
def seg(s, l):
    v = (s["w"] / l - 1) * C; m = (np.abs(v) < 4000) & (s["iv"] > 0) & np.isfinite(s["f"]); v, f, iv = v[m], s["f"][m], s["iv"][m]
    e = np.abs(v) > 3000; p = np.polyfit(v[e], f[e], 1); c = np.polyval(p, v); return v, f / c, iv * c ** 2
tmpl = [s for s in sp if s["dataset"].startswith("BOSS")][0]
T = [seg(tmpl, l) for l in LINES]
for s in sp:
    S = [seg(s, l) for l in LINES]; shifts = np.arange(-400, 401, 2.0); chi = []
    for dv in shifts:
        c2 = 0; n = 0
        for (vt, ft, _), (v, f, iv) in zip(T, S):
            m = np.abs(v) < 1500; ftm = np.interp(v[m] - dv, vt, ft); c2 += np.sum((f[m] - ftm) ** 2 * iv[m]); n += m.sum()
        chi.append(c2)
    chi = np.array(chi); k = np.argmin(chi); red = max(chi[k] / (n - 1), 1e-9); ok = chi <= chi[k] + red
    print(f"{s['dataset']:<14} {s['date']}: dv = {shifts[k]:+.0f} km/s (+-{(shifts[ok].max() - shifts[ok].min()) / 2:.0f}), chi2r {red:.2f}")

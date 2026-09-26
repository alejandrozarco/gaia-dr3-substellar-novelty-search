"""Joint ephemeris: CoRoT IRa01, LRa01, LRa06 (detrended as corot_lc.py, binned to 30 min) and ZTF g, r (flux).
Model per data set k: a_k + b_k cos(2 pi f (t - T0)) ... fitted linearly as a_k + c_k cos(2 pi f t) + s_k sin(2 pi f t) with a common
phase enforced by fitting c, s jointly with per-set scale: two-step - for each f, per-set amplitude A_k from separate fits, then
a common (c, s) with weights A_k / A_ref. Times: CoRoT DATEBARTT + 51544.5 -> BMJD(TT); ZTF hjd - 2400000.5 (HJD; differences
< 1 min are negligible). Scans f over 1.6862-1.6872 c/d, step 2e-7. Prints the best f, chi2 differences of the neighbouring aliases."""
import glob, numpy as np, pandas as pd
from astropy.io import fits
from scipy.ndimage import median_filter
sets = []
for f in sorted(glob.glob("corot/*.fits")):
    d = fits.open(f)["BAR"].data; ok = (d["STATUS"] == 0) & (d["WHITEFLUX"] > 0)
    t = d["DATEBARTT"][ok].astype(float) + 51544.5; y = d["WHITEFLUX"][ok].astype(float); o = np.argsort(t); t, y = t[o], y[o]; y = y / np.median(y) - 1
    w = int(3 / np.median(np.diff(t))) | 1; r = y - median_filter(y, size=w, mode="nearest"); s = 1.4826 * np.median(np.abs(r)); k = np.abs(r) < 5 * s; t, r = t[k], r[k]
    b = np.floor((t - t.min()) * 48); g = pd.DataFrame(dict(t=t, r=r, b=b)).groupby("b").agg(t=("t", "mean"), r=("r", "mean"), n=("r", "size"), sd=("r", "std"))
    g = g[g.n >= 3]; sets.append((f.split("_")[3][:8], g.t.values, g.r.values, (g.sd / np.sqrt(g.n)).values))
z = pd.read_csv("ztf_WD.csv")
for b in ("zg", "zr"):
    s = z[z.filtercode == b]; fl = 10 ** (-0.4 * (s.mag - s.mag.median())) - 1; sets.append((b, s.hjd.values - 2400000.5, fl.values, 0.921 * s.magerr.values * (fl.values + 1)))
names = ["CoRoT 2007a", "CoRoT 2007b", "CoRoT 2012", "ZTF g", "ZTF r"]
def chi(f, ret=False):
    # per set: fit a + c cos + s sin; then shared phase: rotate to common phase using amplitude-weighted combination
    tot = 0; phis = []; A = []
    for _, t, y, e in sets:
        X = np.vstack([np.ones_like(t), np.cos(2*np.pi*f*t), np.sin(2*np.pi*f*t)]).T
        c, *_ = np.linalg.lstsq(X / e[:, None], y / e, rcond=None); A.append(np.hypot(c[1], c[2])); phis.append(np.arctan2(c[2], c[1]))
    # common phase: weighted circular mean
    W = np.array([np.sum((a / e) ** 2) for a, (_, t, y, e) in zip(A, sets)])
    phi = np.angle(np.sum(W * np.exp(1j * np.array(phis))))
    for a, (_, t, y, e) in zip(A, sets):
        X = np.vstack([np.ones_like(t), np.cos(2*np.pi*f*t - phi)]).T
        c, *_ = np.linalg.lstsq(X / e[:, None], y / e, rcond=None); tot += np.sum(((y - X @ c) / e) ** 2)
    return (tot, phi, A, phis) if ret else tot
fr = np.arange(1.6862, 1.6872, 2e-7); cs = np.array([chi(f) for f in fr])
k = np.argmin(cs); f0 = fr[k]; tot, phi, A, phis = chi(f0, True)
print(f"best f = {f0:.7f} c/d, P = {1/f0:.8f} d = {24/f0:.5f} h; chi2 = {tot:.1f}")
# local minima (aliases)
mins = [i for i in range(1, len(cs) - 1) if cs[i] < cs[i-1] and cs[i] < cs[i+1]]
mins = sorted(mins, key=lambda i: cs[i])[:5]
for i in mins: print(f"  alias f = {fr[i]:.7f}: delta chi2 = {cs[i]-tot:.1f}")
for n, a, p in zip(names, A, phis): print(f"  {n}: semi-amplitude {100*a:.2f}%, phase offset from common {np.degrees(np.angle(np.exp(1j*(p-phi)))):+.1f} deg")
T0 = phi / (2*np.pi*f0); T0 += np.round((59300 - T0) * f0) / f0
print(f"max light: BMJD {T0:.5f} + {1/f0:.8f} E")

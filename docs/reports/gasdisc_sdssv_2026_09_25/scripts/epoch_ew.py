"""Shape-free check: summed equivalent width of the three Ca II lines (+-900 km/s windows, vs quadratic continuum) per epoch."""
import sys, glob, numpy as np
from epoch_amp import norm, W, CAT, C
sid, lab = sys.argv[1], sys.argv[2]; d = np.load(f"store/{sid[-2:]}/{sid}.npz"); dl = np.gradient(W)
win = np.zeros(len(W), bool)
for l in CAT: win |= np.abs(W / l - 1) * C < 900
rows = [("SDSS-V coadd",) + norm(W, d["f_8250"], d["iv_8250"])] + [(f"SDSS-V {d['mjd'][k]}",) + norm(W, d["vf_8250"][k], d["viv_8250"][k]) for k in range(len(d["mjd"]))]
for fn in sorted(glob.glob(f"desi_{lab}_*.npz")): rows.append((fn,) + norm(*[np.load(fn)[x] for x in ("w", "f", "iv")]))
for name, n, v in rows:
    ok = win & (v > 0) & np.isfinite(n); ew = np.sum(((n - 1) * dl)[ok]); e = np.sqrt(np.sum((dl ** 2 / v)[ok])); cov = ok.sum() / win.sum()
    print(f"{name:26s} EW(emission, 3 lines) = {ew:6.2f} +- {e:4.2f} A  coverage {cov:.2f}")

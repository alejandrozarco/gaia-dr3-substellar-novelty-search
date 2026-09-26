# Per-visit line-centroid velocities (barycentric frame, XCSAO shift undone) for emission lines, by Gaussian fit to the
# continuum-subtracted profile. Usage: python line_rv.py <sdss_id> [line ...]
import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
from scipy.optimize import curve_fit
sys.path.insert(0, "/tmp/fanout/cv")
from cvspec import load_visits, LINES
C = 299792.458
sid = int(sys.argv[1]); lines = sys.argv[2:] or ["Ha", "Hb"]
def g(x, a, mu, sig, c0, c1): return a * np.exp(-0.5 * ((x - mu) / sig) ** 2) + c0 + c1 * x
for v in load_visits(sid):
    out = [f"MJD {v['mjd']} tai_beg={v['tai_beg']:.0f} S/N={v['snr']:.1f} v_xcsao={v['v_xcsao']:.0f}"]
    for ln in lines:
        l0 = LINES[ln]; s = (v["lam"] > l0 - 60) & (v["lam"] < l0 + 60) & (v["ivar"] > 0)
        x = v["lam"][s] - l0; y = v["flux"][s]; e = 1 / np.sqrt(v["ivar"][s])
        try:
            p, cov = curve_fit(g, x, y, p0=[np.nanmax(y) - np.nanmedian(y), 0, 5, np.nanmedian(y), 0], sigma=e, maxfev=20000)
            out.append(f"{ln}: v={p[1]/l0*C:+.0f}+-{np.sqrt(cov[1,1])/l0*C:.0f} km/s sigma={abs(p[2])/l0*C:.0f} km/s amp={p[0]:.2f}")
        except Exception as ex:
            out.append(f"{ln}: fit failed")
    print(" | ".join(out))

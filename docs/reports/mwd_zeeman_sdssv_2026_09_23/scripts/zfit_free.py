# Model-light field estimate: fit H-alpha and H-beta each with three absorption components of FREE centre, width and depth
# (pi, sigma-, sigma+) plus one broad concentric wing, on a linear continuum; B from the sigma+/sigma- half-separation:
# B_Ha = (l+ - l-)/2 / 20.13 A/MG and B_Hb = (l+ - l-)/2 / 11.04 A/MG (linear Zeeman, mean surface field). The two lines give
# independent estimates; agreement is the Zeeman test (lambda^2 scaling). Usage: python zfit_free.py <gaia_id> [<gaia_id> ...]
import sys, csv, json, numpy as np, warnings
warnings.filterwarnings("ignore")
from astropy.io import fits
from scipy.optimize import least_squares
rows = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
L0 = {"Ha": 6564.61, "Hb": 4862.68}; K = {"Ha": 4.67e-13 * 6564.61 ** 2 * 1e6, "Hb": 4.67e-13 * 4862.68 ** 2 * 1e6}
WIN = {"Ha": (6300, 6830), "Hb": (4660, 5060)}
def load(g):
    r = rows[g]; h = fits.open(f"spec/mwmStar-{r['v_astra']}-{r['sdss_id']}.fits"); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]
        if best is None or d["snr"] > best[3]: best = (np.array(d["wavelength"], float), np.array(d["flux"], float), np.array(d["ivar"], float), float(d["snr"]))
    return best
def model(p, x, l0):
    c0, c1, dw, sw, d0, s0, dm, sm, dp, sp, lm, lp, sh = p
    g = lambda mu, s: np.exp(-0.5 * ((x - mu) / s) ** 2)
    cont = c0 + c1 * (x - l0) / 100
    return cont * (1 - dw * g(l0 + sh, sw) - d0 * g(l0 + sh, s0) - dm * g(l0 + sh - lm, sm) - dp * g(l0 + sh + lp, sp))
def fit(x, y, iv, l0, dl0):
    m = (iv > 0) & np.isfinite(y); x, y, w = x[m], y[m], np.sqrt(iv[m])
    med = np.median(y[(np.abs(x - l0) > 0.8 * (x.max() - l0))])
    best = None
    for dl in dl0 * np.array([0.6, 0.8, 1.0, 1.25, 1.6]):
        for sw_ in (40, 80):
            p0 = [med, 0, 0.15, sw_, 0.2, 6, 0.15, 8, 0.15, 8, dl, dl, 0]
            lo = [0, -np.inf, 0, 15, 0, 1.5, 0, 1.5, 0, 1.5, 5, 5, -15]; hi = [np.inf, np.inf, 1, 300, 1, 40, 1, 60, 1, 60, 400, 400, 15]
            try:
                r = least_squares(lambda p: (model(p, x, l0) - y) * w, p0, bounds=(lo, hi), max_nfev=4000)
            except Exception: continue
            if best is None or r.cost < best.cost: best = r
    J = best.jac; chi2r = 2 * best.cost / (len(x) - len(best.x))
    try: C = np.linalg.inv(J.T @ J) * max(chi2r, 1)
    except np.linalg.LinAlgError: C = np.full((len(best.x),) * 2, np.nan)
    return best.x, C, chi2r, x, y
if __name__ == "__main__":      # guard: importing this module (visits.py) must not overwrite the results file
    out = {}
    for g in sys.argv[1:]:
        lam, f, iv, snr = load(g); res = {}
        for k in ("Ha", "Hb"):
            m = (lam > WIN[k][0]) & (lam < WIN[k][1])
            p, C, chi2r, x, y = fit(lam[m], f[m], iv[m], L0[k], 6.0 * K[k])
            half = (p[10] + p[11]) / 2; e_half = 0.5 * np.sqrt(C[10, 10] + C[11, 11] + 2 * C[10, 11])
            res[k] = dict(B=half / K[k], eB=e_half / K[k], asym=(p[11] - p[10]) / K[k], depths=[p[6], p[4], p[8]], widths=[p[7], p[5], p[9]], chi2r=chi2r)
        out[g] = dict(snr=snr, **res)
        print(f"{g} S/N {snr:5.1f} | B(Ha) {res['Ha']['B']:5.2f} +- {res['Ha']['eB']:4.2f} MG (sigma depths {res['Ha']['depths'][0]:.2f}/{res['Ha']['depths'][2]:.2f}, pi {res['Ha']['depths'][1]:.2f}; asym {res['Ha']['asym']:+.2f}) "
              f"| B(Hb) {res['Hb']['B']:5.2f} +- {res['Hb']['eB']:4.2f} MG (depths {res['Hb']['depths'][0]:.2f}/{res['Hb']['depths'][2]:.2f}, pi {res['Hb']['depths'][1]:.2f}) | chi2r {res['Ha']['chi2r']:.2f}/{res['Hb']['chi2r']:.2f}", flush=True)
    json.dump(out, open("zfit_free_" + ("_".join(sys.argv[1:2]) if len(sys.argv) == 2 else "batch") + ".json", "w"), indent=1, default=float)

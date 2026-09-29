"""Fine period pass (2026-09-29). eclipse_fit.py scans the period on a grid whose step can be many times the period error,
so its parabola error is unreliable. Here the eclipse shape (duration, flat fraction) is held at the eclipse_fit values and
chi2 is minimised over the eclipse centre (0.0002-phase steps) for 81 periods spanning +-0.4 of the eclipse width in
accumulated phase over the data span. P and its error come from a parabola to chi2(P) within delta chi2 < 25 of the minimum,
after scaling chi2_r to 1. Output: period_refine.json."""
import numpy as np, json, os
H = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(H, "eclipse_fit.py")).read().split("CEN = ")[0].replace('os.environ.get("STARS", "WDJ1438-3051,WDJ1118-5442")', '"WDJ1438-3051,WDJ1118-5442,J0353-5502"'))
FITS = {}
for fn in ("eclipse_fit.json", "eclipse_fit_J0353-5502.json"): FITS.update(json.load(open(os.path.join(H, fn))))
def chi_at(P, Tref, D, T, fr, cens):
    best = np.inf; bc = None
    for c in cens:
        chi = 0
        for d in D.values():
            ph = ((d["t"] - Tref) / P + 0.5) % 1 - 0.5; w = 1 / d["e"]; A = design(ph, trap(ph - c, T, fr))
            coef = np.linalg.lstsq(A * w[:, None], d["f"] * w, rcond=None)[0]; chi += np.sum(((d["f"] - A @ coef) * w) ** 2)
        if chi < best: best, bc = chi, c
    return best, bc
out = {}
for name, s in STARS.items():
    r = FITS[name]; D, _ = load(s); T, fr, P0 = r["dur_phase"], r["flat_fraction"], r["P"]
    tm = np.median(np.concatenate([d["t"] for d in D.values()])); Tref = r["T0_BJD_TDB"] + round((tm - r["T0_BJD_TDB"]) / P0) * P0
    span = max(d["t"].max() for d in D.values()) - min(d["t"].min() for d in D.values())
    w = 0.4 * T * P0 * P0 / span; Ps = P0 + np.linspace(-w, w, 81); cens = np.arange(-0.01, 0.01001, 0.0002)
    res = [chi_at(P, Tref, D, T, fr, cens) for P in Ps]; chis = np.array([x[0] for x in res]); j = int(np.argmin(chis))
    n = sum(len(d["t"]) for d in D.values()); s2 = chis[j] / (n - 13); z = (chis - chis[j]) / s2; m = z < 25
    a, b, _ = np.polyfit(Ps[m] - Ps[j], z[m], 2); P = Ps[j] - b / (2 * a); sP = np.sqrt(1 / a)
    out[name] = dict(P=P, sigP=sP, chi2r=s2, grid_halfwidth=w, n_in_fit=int(m.sum()), Tref=Tref, centre_at_best=res[j][1],
                     T0_BJD_TDB=Tref + res[j][1] * Ps[j], P_eclipse_fit=P0, sigP_eclipse_fit=r["sigP"])
    print(f"{name}: P = {P:.9f} +- {sP:.9f} d (eclipse_fit {P0:.9f} +- {r['sigP']:.9f}); parabola over {int(m.sum())} of 81 grid points; "
          f"mid-eclipse near the data median BJD_TDB {out[name]['T0_BJD_TDB']:.5f}", flush=True)
json.dump(out, open(os.path.join(H, "period_refine.json"), "w"), indent=1, default=float)

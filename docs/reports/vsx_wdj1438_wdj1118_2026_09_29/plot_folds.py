"""Fold figures for the VSX files on the refined ephemerides (period_refine.json) with the eclipse shape from eclipse_fit.json;
harmonic and depth coefficients refitted at that ephemeris (2026-09-29)."""
import numpy as np, json, os, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(H, "eclipse_fit.py")).read().split("CEN = ")[0])
F = json.load(open(os.path.join(H, "eclipse_fit.json"))); R = json.load(open(os.path.join(H, "period_refine.json")))
for name, s in STARS.items():
    D, _ = load(s); P, T0 = R[name]["P"], R[name]["T0_BJD_TDB"]; T, fr = F[name]["dur_phase"], F[name]["flat_fraction"]
    fig, axs = plt.subplots(2, 2, figsize=(11, 6), gridspec_kw=dict(width_ratios=[2, 1]))
    for k, b in enumerate(("o", "c")):
        d = D[b]; ph = ((d["t"] - T0) / P + 0.5) % 1 - 0.5; w = 1 / d["e"] ** 2
        A = design(ph, trap(ph, T, fr)); coef = np.linalg.lstsq(A * np.sqrt(w)[:, None], d["f"] * np.sqrt(w), rcond=None)[0]
        for col, (xl, nb) in enumerate(((0.5, 50), (0.15, 30))):
            ed = np.linspace(-xl, xl, nb + 1); cen = (ed[:-1] + ed[1:]) / 2; mb, er = [], []
            for i in range(nb):
                m = (ph >= ed[i]) & (ph < ed[i + 1]); mb.append(np.sum(d["f"][m] * w[m]) / np.sum(w[m]) if m.any() else np.nan); er.append(1 / np.sqrt(np.sum(w[m])) if m.any() else np.nan)
            ax = axs[k, col]; ax.errorbar(cen, mb, er, fmt="o", ms=3, color="k"); x = np.linspace(-xl, xl, 1000)
            ax.plot(x, design(x, trap(x, T, fr)) @ coef, color="tab:red", lw=1); ax.set_xlim(-xl, xl); ax.set_xlabel("orbital phase"); ax.set_ylabel("ATLAS difference flux (uJy)")
            ax.set_title(f"{name} ATLAS {b} (n={len(d['t'])}), P = {P:.8f} d, phase 0 = BJD_TDB {T0:.5f}", fontsize=7)
    plt.tight_layout(); plt.savefig(os.path.join(H, f"{name}_fold.png"), dpi=100); plt.close(); print(name, "figure P", round(P, 8), "T0", round(T0, 5))

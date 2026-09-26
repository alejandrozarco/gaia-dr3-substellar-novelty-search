# J0753 = Gaia DR3 3082614748370926848: SED decomposition figure (observed Gaia/PS1/VHS/WISE; M-dwarf template + 4206 K blackbody fit at 367 pc).
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
exec(open("j0753_sed_fit.py").read().split("res = {}")[0].replace('bands = ["G", "BP", "RP", "g", "r", "i", "z", "y", "J", "Ks"]', 'bands = ["g", "r", "i", "z", "y", "J", "Ks"]'))
d = 367.0; dm = 5 * np.log10(d / 10); MJ, T, R = 9.68, 4367, 0.0531
tm = mtempl(MJ); FM = np.array([mag2jy(b, tm[b] + dm) for b in bands]); FB = np.array([bb_jy(b, T, R, d) for b in bands])
lw = np.array([lam[b] for b in bands]); o = np.argsort(lw)
fig, ax = plt.subplots(figsize=(7.5, 5))
ax.errorbar(lw[o], Fobs[o] * 1e6, eF[o] * 1e6, fmt="ko", label="observed (PS1 means, VHS 2011)")
ax.plot(lw[o], FM[o] * 1e6, "s--", color="tab:red", label=f"empirical M dwarf, M_J = {MJ} (~M5.5) at {d:.0f} pc")
ax.plot(lw[o], FB[o] * 1e6, "^--", color="tab:blue", label=f"extra component: blackbody {T} K, R = {R} Rsun")
ax.plot(lw[o], (FM + FB)[o] * 1e6, "-", color="0.4", label="sum")
# WISE (not fitted): AllWISE 2010 and CatWISE 2010-18 means, W1 plateau/dip
for lab, w1, w2, mk in (("AllWISE 2010", 15.406, 14.957, "D"), ("CatWISE 2010-18", 14.998, 14.575, "v")):
    ax.plot([3.35, 4.60], [309.54 * 10 ** (-0.4 * w1) * 1e6, 171.787 * 10 ** (-0.4 * w2) * 1e6], mk, color="tab:purple", label=f"{lab} (not fitted)")
ax.vlines(3.35, 309.54 * 10 ** (-0.4 * 15.7) * 1e6, 309.54 * 10 ** (-0.4 * 14.5) * 1e6, color="tab:purple", lw=3, alpha=0.5, label="W1 range over the 2.53-h cycle")
tmW = [309.54 * 10 ** (-0.4 * (tm["Ks"] + dm - 0.22)) * 1e6]
ax.plot([3.35], tmW, "x", color="tab:red", ms=9, label="M-dwarf photosphere expected in W1")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("wavelength (micron)"); ax.set_ylabel("flux density (micro-Jy)")
ax.set_title("J0753-0042: M dwarf + an extra component that is neither a star nor a hot white dwarf", fontsize=9); ax.legend(fontsize=6.5, loc="lower right")
plt.tight_layout(); plt.savefig("../figures/j0753_sed.png", dpi=120); print("saved")

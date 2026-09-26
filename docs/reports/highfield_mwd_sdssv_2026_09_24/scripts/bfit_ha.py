# H-alpha-only variant of the field estimator (for cool stars where only H-alpha is expected): ln F = poly - A_a * tau_Ha
import sys, numpy as np, spec as S, bfit as BF, pandas as pd, json
from scipy.optimize import nnls
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
sid = int(sys.argv[1]); B1, B2 = float(sys.argv[2]), float(sys.argv[3])
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id"); teff = float(d.loc[sid].teff_phot)
V = [v for v in S.load_visits(sid) if v["snr"] >= 8]
lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
for v in V:
    cv = S.continuum(v["lam"], v["flux"], v["ivar"]); okv = (v["ivar"] > 0) & np.isfinite(cv) & (cv > 0)
    fnv = np.where(okv, v["flux"] / np.where(okv, cv, 1), 0); ivn = np.where(okv, v["ivar"] * cv**2, 0); w = np.interp(lam, v["lam"], okv.astype(float)) > 0.99
    num += np.interp(lam, v["lam"], fnv) * np.interp(lam, v["lam"], ivn) * w; den += np.interp(lam, v["lam"], ivn) * w
fn = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); er = np.where(den > 0, 1 / np.sqrt(np.where(den > 0, den, 1)), np.nan)
m = (lam > 5400) & (lam < 8200) & np.isfinite(fn) & (fn > 0.05) & (den > 0)
for a, b in S.MASK: m &= ~((lam > a) & (lam < b))
x = lam[m]; y = np.log(fn[m]); W = fn[m] / er[m]; P = np.vstack([((x - 6800) / 1400) ** k for k in range(4)]).T
Bps = np.logspace(np.log10(B1), np.log10(B2), 70); incs = (0, 15, 30, 45, 60, 75, 90); sigs = (8, 16, 30)
grid = np.full((len(Bps), len(incs), len(sigs)), np.nan); best = (np.inf,)
for i, Bp in enumerate(Bps):
    for j, inc in enumerate(incs):
        for k, sg in enumerate(sigs):
            T = BF.templates(Bp, inc, sg, teff)[0]; Ti = np.interp(x, BF.LG, T)
            A = np.hstack([-Ti[:, None], P, -P]); c, rn = nnls(A * W[:, None], y * W); grid[i, j, k] = rn**2
            if rn**2 < best[0]: best = (rn**2, Bp, inc, sg, c)
cp, *_ = np.linalg.lstsq(P * W[:, None], y * W, rcond=None); chi0 = np.sum(((y - P @ cp) * W) ** 2)
chi2, Bp, inc, sg, c = best; sc = max(chi2 / m.sum(), 1); g = np.nanmin(grid, axis=(1, 2))
ok = (g - chi2) / sc < 9; low = np.nanmin(g[Bps < 3]) if (Bps < 3).any() else np.nan
print(f"{sid} Ha-only 5400-8200 A | best Bp {Bp:.1f} MG i {inc} sig {sg} | A_a {c[0]:.3f} | chi2_red {chi2/m.sum():.2f} | no-field worse by {(chi0-chi2)/sc:.0f} (rescaled) | range {Bps[ok].min():.1f}-{Bps[ok].max():.1f} MG")
T = BF.templates(Bp, inc, sg, teff)[0]; Pl = np.vstack([((lam - 6800) / 1400) ** k for k in range(4)]).T
model = np.exp(-c[0] * np.interp(lam, BF.LG, T) + Pl @ (c[1:5] - c[5:9]))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 6.5), gridspec_kw=dict(height_ratios=[2, 1]))
mm = (lam > 5400) & (lam < 8200) & np.isfinite(fn)
a1.plot(lam[mm], gaussian_filter1d(np.nan_to_num(fn), 2)[mm], "k", lw=0.6); a1.plot(lam[mm], model[mm], "r", lw=1, label=f"H-alpha only, centred dipole Bp={Bp:.0f} MG i={inc}")
a1.axvline(6564.6, ls=":", color="tab:blue"); a1.legend(fontsize=8); a1.set_ylim(0.6, 1.2); a1.set_title(f"sdss_id {sid} (Teff_phot {teff:.0f} K)", fontsize=9, loc="left")
for j, inc_ in enumerate(incs): a2.plot(Bps, (np.nanmin(grid[:, j, :], axis=1) - chi2) / sc, label=f"i={inc_}")
a2.set_xscale("log"); a2.set_ylim(-2, 200); a2.axhline(9, ls="--", color="0.5"); a2.legend(fontsize=7, ncol=4); a2.set_xlabel("Bp [MG]")
plt.tight_layout(); plt.savefig(f"plots/bfit_ha_{sid}.png", dpi=85)
json.dump(dict(sid=sid, Bp=Bp, inc=inc, sig=sg, A_a=float(c[0]), chi2_red=chi2 / m.sum(), dchi_nofield=(chi0 - chi2) / sc, range=[float(Bps[ok].min()), float(Bps[ok].max())]), open(f"bfit_ha_{sid}.json", "w"))

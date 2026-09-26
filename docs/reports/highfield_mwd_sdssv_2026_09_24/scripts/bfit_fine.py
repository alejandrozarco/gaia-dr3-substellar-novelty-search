# Finer field grid for a single star (visit coadd), reporting the chi2 curve and the acceptable range.
import sys, numpy as np, json, spec as S, bfit as BF, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
sid = int(sys.argv[1]); B1, B2 = float(sys.argv[2]), float(sys.argv[3])
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id"); teff = float(d.loc[sid].teff_phot)
V = [v for v in S.load_visits(sid) if v["snr"] >= 8] or sorted(S.load_visits(sid), key=lambda v: -v["snr"])[:1]
lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
for v in V:
    cv = S.continuum(v["lam"], v["flux"], v["ivar"]); okv = (v["ivar"] > 0) & np.isfinite(cv) & (cv > 0)
    fnv = np.where(okv, v["flux"] / np.where(okv, cv, 1), 0); ivn = np.where(okv, v["ivar"] * cv**2, 0)
    num += np.interp(lam, v["lam"], fnv) * np.interp(lam, v["lam"], ivn) * (np.interp(lam, v["lam"], okv.astype(float)) > 0.99)
    den += np.interp(lam, v["lam"], ivn) * (np.interp(lam, v["lam"], okv.astype(float)) > 0.99)
fn = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); er = np.where(den > 0, 1 / np.sqrt(np.where(den > 0, den, 1)), np.nan)
mask = np.ones_like(lam, bool)
for a, b in S.MASK: mask &= ~((lam > a) & (lam < b))
Bps = np.logspace(np.log10(B1), np.log10(B2), 60)
r = BF.fit(lam, fn, er, teff, Bps=Bps, incs=(0, 15, 30, 45, 60, 75, 90), sigs=(8, 12, 16, 24, 30), mask=mask)
g = np.nanmin(r["grid"], axis=(1, 2)); sc = max(r["chi2"] / r["npix"], 1)
ok = (g - r["chi2"]) / sc < 9
print(sid, f"Teff {teff:.0f} visits {len(V)} | best Bp {r['Bp']:.1f} MG i {r['inc']} sig {r['sig']} | chi2_red {r['chi2']/r['npix']:.2f} | Bp range (resc. dchi2<9): {Bps[ok].min():.1f}-{Bps[ok].max():.1f} MG | A {np.round(r['A'],3)}")
json.dump(dict(sid=sid, Bp=r["Bp"], inc=r["inc"], sig=r["sig"], chi2_red=r["chi2"] / r["npix"], Bp_range=[Bps[ok].min(), Bps[ok].max()], A=list(map(float, r["A"])), teff=teff),
          open(f"bfit_fine_{sid}.json", "w"), indent=1)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(14, 7.5), gridspec_kw=dict(height_ratios=[2.2, 1]))
m = np.isfinite(fn) & (lam > 3700) & (lam < 9300)
a1.plot(lam[m], gaussian_filter1d(np.nan_to_num(fn), 2)[m], "k", lw=0.5, label=f"visit coadd ({len(V)} visits, XCSAO undone, per-visit normalised)")
a1.plot(lam[m], r["model"][m], "r", lw=0.9, label=f"centred dipole Bp={r['Bp']:.0f} MG, i={r['inc']}, sigma={r['sig']} A (Schimeczek & Wunner H data)")
for l0 in (6564.61, 4862.68, 4341.69, 4102.89): a1.axvline(l0, color="tab:blue", ls=":", lw=0.6)
a1.set_ylim(0.55, 1.2); a1.legend(fontsize=7, loc="lower right"); a1.set_title(f"sdss_id {sid} Gaia DR3 {int(d.loc[sid].gaia_dr3_source_id)} | Teff_phot {teff:.0f} K", fontsize=9, loc="left")
for k, inc in enumerate(r["incs"]): a2.plot(Bps, (np.nanmin(r["grid"][:, k, :], axis=1) - r["chi2"]) / sc, label=f"i={inc}")
a2.set_xscale("log"); a2.set_ylim(-2, 300); a2.axhline(9, color="0.5", ls="--"); a2.set_xlabel("Bp [MG]"); a2.set_ylabel("rescaled dchi2"); a2.legend(fontsize=7, ncol=4)
plt.tight_layout(); plt.savefig(f"plots/bfit_fine_{sid}.png", dpi=85)

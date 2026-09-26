# Annotated spectra (visit coadd, XCSAO undone, per-visit normalised) with line lists for non-hydrogen interpretations.
import sys, numpy as np, spec as S
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
AIR2VAC = lambda l: l * 1.000276
LINES = {"CII (hot DQ)": [4267.3, 4372.5, 5133.1, 5145.2, 5151.1, 6578.1, 6582.9, 7231.3, 7236.4],
         "CI": [4771.7, 4932.0, 5052.1, 5380.3, 6013.2, 6587.6, 7115.2, 8335.1, 9078.3, 9094.8, 9111.8, 9405.7],
         "C2 Swan heads": [4382.5, 4737.1, 5165.2, 5635.5, 6122.0],
         "HeI": [4471.5, 4713.1, 4921.9, 5015.7, 5875.6, 6678.2, 7065.2],
         "metals (Ca II, Ca I, Mg I, Na I, Fe I)": [3933.7, 3968.5, 4226.7, 5167.3, 5172.7, 5183.6, 5889.9, 5895.9, 4045.8, 4383.5, 4404.8, 5269.5, 8498.0, 8542.1, 8662.1],
         "Balmer": [6562.8, 4861.3, 4340.5, 4101.7, 3970.1]}
COL = dict(zip(LINES, ["tab:red", "tab:orange", "tab:brown", "tab:green", "tab:purple", "tab:blue"]))
for sid in map(int, sys.argv[1:]):
    V = [v for v in S.load_visits(sid) if v["snr"] >= 6]
    lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
    for v in V:
        cv = S.continuum(v["lam"], v["flux"], v["ivar"]); okv = (v["ivar"] > 0) & np.isfinite(cv) & (cv > 0)
        fnv = np.where(okv, v["flux"] / np.where(okv, cv, 1), 0); ivn = np.where(okv, v["ivar"] * cv**2, 0)
        num += np.interp(lam, v["lam"], fnv) * np.interp(lam, v["lam"], ivn); den += np.interp(lam, v["lam"], ivn)
    fn = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    fig, axs = plt.subplots(len(LINES), 1, figsize=(14, 2.0 * len(LINES)), sharex=True)
    for a, (k, ls) in zip(axs, LINES.items()):
        m = np.isfinite(fn) & (lam > 3700) & (lam < 9400)
        a.plot(lam[m], gaussian_filter1d(np.nan_to_num(fn), 2)[m], "k", lw=0.5)
        for l in ls: a.axvline(AIR2VAC(l), color=COL[k], lw=0.8, alpha=0.8)
        a.set_ylim(0.55, 1.2); a.set_ylabel(k, fontsize=7, rotation=0, ha="right"); a.axhline(1, color="0.7", lw=0.5)
    axs[0].set_title(f"sdss_id {sid}: visit coadd ({len(V)} visits with S/N>=6, XCSAO undone), line lists (vacuum)", fontsize=9, loc="left")
    plt.tight_layout(); plt.savefig(f"plots/lines_{sid}.png", dpi=75); plt.close(fig); print("ok", sid)

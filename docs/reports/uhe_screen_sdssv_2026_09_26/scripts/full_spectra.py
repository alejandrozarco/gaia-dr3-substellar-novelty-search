import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d, median_filter
U = os.path.dirname(os.path.abspath(__file__))
S = [("100568930", "WDJ0958-1758"), ("92169356", "EC 01395-6452"), ("93074954", "GALEX J0412-3754"), ("111789298", "GALEX J1913-5330"), ("78658917", "PG 1201-049"),
     ("93205750", "Gaia DR3 4866851575967878144"), ("59101580", "WDJ0706+6133 (known DA UHE)"), ("63039439", "HS 2115+1148 (known DAO UHE)")]
fig, ax = plt.subplots(len(S), 1, figsize=(15, 2.1 * len(S)))
for a, (sid, lab) in zip(ax, S):
    vs = sdssv.visits(sid); use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; ok = (iv > 0) & np.isfinite(f) & (w > 3700) & (w < 9000)
    w, f = w[ok], f[ok]; c = median_filter(f, 601, mode="nearest"); a.plot(w, gaussian_filter1d(f / c, 1.5), "k", lw=.5); a.set_ylim(0.6, 1.15); a.set_xlim(3700, 9000)
    for l, n in [(3890.2, ""), (3971.2, ""), (4102.9, "Hd"), (4341.7, "Hg"), (4687.0, "HeII"), (4862.7, "Hb"), (5413.0, "HeII"), (6564.6, "Ha"), (4543.0, ""), (4201, ""), (5280, "UHE"), (4658, "CIV"), (5801.3, "CIV"), (6068, "UHE")]:
        a.axvline(l, color="r" if "UHE" in n else "b", lw=.4, alpha=.5)
    a.text(3720, 0.65, f"{lab} ({sid}), {len(use)} visit(s)", fontsize=8); a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig(f"{U}/full_spectra.png", dpi=65)

# Multi-object inspection pages: per object a row of 4 panels (full 3700-9200 A, 3800-4550, 4550-5450, 5450-7250) of the
# mwmStar coadd (best-S/N HDU), lightly smoothed, with line markers (vacuum wavelengths). Title carries Gaia id, SnowWhite class,
# MWDD type, G, BP-RP, M_G, S/N.
import sys, numpy as np
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import fetch, best_star
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
AV = 1.000277  # air -> vacuum (approx.)
LINES = {  # label: (wavelengths vacuum, colour)
    "H": ([6564.61, 4862.68, 4341.69, 4102.89, 3971.19, 3890.15], "tab:blue"),
    "HeI": ([x * AV for x in (4026.2, 4387.9, 4471.5, 4713.1, 4921.9, 5015.7, 5875.6, 6678.2, 7065.2)], "tab:green"),
    "HeII": ([4685.7 * AV], "lime"),
    "CI": ([x * AV for x in (4771.7, 4932.0, 5052.1, 5380.3, 6014.8, 6587.6, 7115.2, 8335.1, 9094.8)], "tab:red"),
    "CII": ([x * AV for x in (4267.0, 5145.2, 6578.0, 6582.9, 7231.3, 7236.4, 3919.0, 3920.7)], "magenta"),
    "C2": ([x * AV for x in (4382.0, 4737.0, 5165.2, 5635.5, 6122.0)], "brown"),
    "CaII": ([3934.8, 3969.6, 8500.4, 8544.4, 8664.5], "tab:orange"),
    "MgI": ([x * AV for x in (5167.3, 5172.7, 5183.6)], "olive"), "NaI": ([5891.6, 5897.6], "gold"), "MgII": ([4482.6], "olive"),
}
def smooth(f, k=3): return np.convolve(np.nan_to_num(f), np.ones(k) / k, mode="same")
def page(items, out, k=3):
    n = len(items); fig, axs = plt.subplots(n, 4, figsize=(22, 2.9 * n), gridspec_kw=dict(width_ratios=[2.2, 1, 1, 1.6]))
    axs = np.atleast_2d(axs)
    for row, it in zip(axs, items):
        fn = fetch(it["sdss_id"])
        if fn is None: row[0].set_title(f"HOLE download {it['sdss_id']}"); continue
        b = best_star(fn)
        if b is None: row[0].set_title(f"empty {it['sdss_id']}"); continue
        hdu, w, f, iv, snr = b; fs = smooth(f, k)
        for a, (lo, hi) in zip(row, [(3700, 9200), (3800, 4550), (4550, 5450), (5450, 7250)]):
            m = (w > lo) & (w < hi) & np.isfinite(fs)
            if m.sum() < 10: continue
            a.plot(w[m], fs[m], lw=0.6, color="k")
            y = fs[m]; lo_y, hi_y = np.percentile(y, 1), np.percentile(y, 99.5); pad = 0.08 * (hi_y - lo_y)
            a.set_ylim(lo_y - pad, hi_y + pad); a.set_xlim(lo, hi)
            if lo > 3700 or True:
                for nm, (ls, col) in LINES.items():
                    for l0 in ls:
                        if lo < l0 < hi: a.axvline(l0, color=col, lw=0.6, ls=":", alpha=0.8)
            a.tick_params(labelsize=7)
        row[0].set_title(f"{it.get('tag','')} Gaia DR3 {it['gid']} sdss_id {it['sdss_id']} | SW {it.get('cls','')} | MWDD {it.get('mwdd','')} | G {it.get('G',0):.2f} BP-RP {it.get('bprp',0):.2f} MG {it.get('MG',0):.2f} | S/N {snr:.0f} hdu{hdu}", fontsize=8, loc="left")
        row[1].set_title(it.get("note", ""), fontsize=7)
    handles = [plt.Line2D([], [], color=c, ls=":", label=nm) for nm, (l, c) in LINES.items()]
    axs[0, 3].legend(handles=handles, fontsize=6, ncol=4, loc="upper right")
    plt.tight_layout(); plt.savefig(out, dpi=55); plt.close()

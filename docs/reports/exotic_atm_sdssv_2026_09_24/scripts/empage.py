# Emission-screen inspection pages: per object a row with full spectrum (3700-9200), H-gamma zoom (4200-4500), H-beta zoom
# (4600-5150) and H-alpha zoom (6250-6900); mwmStar (best HDU) lightly smoothed; nebular/sky line positions dashed grey.
import sys, numpy as np
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import fetch, best_star
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
NEB = [6549.9, 6564.6, 6585.3, 6718.3, 6732.7, 6302.0, 6365.5, 4960.3, 5008.2, 4862.7, 4341.7, 5578.9]
BAL = [6564.61, 4862.68, 4341.69]
def page(items, out):
    n = len(items); fig, axs = plt.subplots(n, 4, figsize=(22, 2.2 * n), gridspec_kw=dict(width_ratios=[2, 0.8, 1.2, 1.4]))
    axs = np.atleast_2d(axs)
    for row, it in zip(axs, items):
        b = best_star(fetch(it["sdss_id"])); hdu, w, f, iv, snr = b; fs = gaussian_filter1d(np.nan_to_num(f), 2)
        for a, (lo, hi) in zip(row, [(3700, 9200), (4200, 4500), (4600, 5150), (6250, 6900)]):
            m = (w > lo) & (w < hi)
            a.plot(w[m], fs[m], lw=0.6, color="k"); y = fs[m]
            p1, p2 = np.percentile(y, 1), np.percentile(y, 99.5); a.set_ylim(p1 - 0.1 * (p2 - p1), p2 + 0.1 * (p2 - p1)); a.set_xlim(lo, hi)
            for l0 in BAL:
                if lo < l0 < hi: a.axvline(l0, color="tab:blue", ls=":", lw=0.8)
            if lo > 3700:
                for l0 in NEB:
                    if lo < l0 < hi: a.axvline(l0, color="0.6", ls="--", lw=0.5)
            a.tick_params(labelsize=6)
        row[0].set_title(f"#{it.get('rank','')} Gaia {it['gid']} | SW {it['cls']} | MWDD {it['mwdd']} | DESI {it.get('desi','')} | G {it['G']:.2f} BP-RP {it['bprp']:.2f} MG {it['MG']:.2f} S/N {snr:.0f}", fontsize=7, loc="left")
        row[2].set_title(it.get("note", ""), fontsize=6)
    plt.tight_layout(); plt.savefig(out, dpi=55); plt.close()

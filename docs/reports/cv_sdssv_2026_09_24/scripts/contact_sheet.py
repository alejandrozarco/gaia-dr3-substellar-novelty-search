# Contact sheets: 8 objects per PNG, each = barycentric coadd (smoothed) over 3600-9800 A + inset zoom 4250-4950 and 6450-6700.
# Usage: python contact_sheet.py <csv with sdss_id column> <prefix>
import sys, numpy as np, pandas as pd, warnings, json
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/tmp/fanout/cv")
from cvspec import load_visits, coadd, LINES
lst = pd.read_csv(sys.argv[1]); pre = sys.argv[2]
m = pd.read_csv("/tmp/fanout/cv/master.csv").set_index("sdss_id")
def smooth(y, k):
    yy = np.where(np.isfinite(y), y, 0.0); w = np.isfinite(y).astype(float); ker = np.ones(k)
    return np.convolve(yy, ker, "same") / np.maximum(np.convolve(w, ker, "same"), 1e-9)
ids = list(lst.sdss_id)
for p in range(0, len(ids), 8):
    fig, axes = plt.subplots(4, 2, figsize=(17, 13))
    for ax, sid in zip(axes.flat, ids[p:p + 8]):
        r = m.loc[sid]
        vis = load_visits(sid)
        lam, fl, iv, n = coadd(vis, use=[i for i, v in enumerate(vis) if v["snr"] > 1] or None)
        fs = smooth(fl, 5); g = np.isfinite(fl) & (lam > 3700) & (lam < 9800)
        lo, hi = np.nanpercentile(fs[g], [1, 99.5])
        ax.plot(lam, fs, "k-", lw=0.6)
        ax.set_xlim(3600, 9800); ax.set_ylim(min(lo, 0) - 0.05 * (hi - lo), hi + 0.3 * (hi - lo))
        for k in ("Ha", "Hb", "Hg", "Hd", "HeI5876", "HeI6678", "HeII4686", "HeI4472"):
            ax.axvline(LINES[k], color="tab:red" if "HeII" in k else ("tab:green" if "HeI" in k else "tab:blue"), lw=0.5, ls=":", alpha=0.7)
        ttl = (f"G{int(r.gaia_dr3_source_id)} sid{sid} {r.classification} pcv={r.p_cv:.2f} G={r.g_mag:.1f} SN={r.snr_coadd:.0f}\n"
               f"Ha EW={r.Ha_ew:.0f} FWHM={r.Ha_fwhm:.0f} HeI5876={r.HeI5876_ew:.1f}({r.HeI5876_sig:.0f}s) HeII={r.HeII4686_ew:.1f}({r.HeII4686_sig:.0f}s) "
               f"HeII/Hb={r.heii_hb:.2f} vx={r.max_abs_vx:.0f} SIMBAD={str(r.simbad)[:28]}")
        ax.set_title(ttl, fontsize=7)
        for (a, b), pos in (((4250, 4950), [0.03, 0.55, 0.3, 0.4]), ((6450, 6700), [0.67, 0.55, 0.3, 0.4])):
            ins = ax.inset_axes(pos); s = (lam > a) & (lam < b) & np.isfinite(fl)
            if s.sum() > 5:
                ins.plot(lam[s], smooth(fl, 2)[s], "k-", lw=0.5)
                for k, l0 in LINES.items():
                    if a < l0 < b: ins.axvline(l0, color="tab:red" if "HeII" in k else "tab:blue", lw=0.4, ls=":")
            ins.tick_params(labelsize=5)
    for ax in axes.flat[len(ids[p:p + 8]):]: ax.axis("off")
    fig.tight_layout(); fn = f"/tmp/fanout/cv/plots/{pre}_{p // 8:02d}.png"; fig.savefig(fn, dpi=85); plt.close(fig); print(fn, flush=True)

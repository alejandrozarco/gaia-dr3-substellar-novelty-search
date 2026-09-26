# Detailed diagnostic figure for one object: mwmStar coadd vs own XCSAO-undone visit coadd (full range), per-visit spectra
# (XCSAO shift undone, offset vertically, with MJD and xcsao_v_rad), and zooms with line markers.
import sys, numpy as np
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts")
from common import fetch, best_star, load_visits, coadd_visits
from plotpage import LINES
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
def detail(sid, gid, title, out, zooms=((3800, 4500), (4500, 5400), (5400, 6300), (6300, 7300)), sm=2, extra_lines=None):
    fn = fetch(sid); fv = fetch(sid, "visit")
    fig = plt.figure(figsize=(18, 14)); gs = fig.add_gridspec(3, 4, height_ratios=[1, 1.4, 1])
    a0 = fig.add_subplot(gs[0, :]); a1 = fig.add_subplot(gs[1, :]); az = [fig.add_subplot(gs[2, i]) for i in range(4)]
    b = best_star(fn); hdu, w, f, iv, snr = b
    m = (w > 3650) & (w < 9300)
    a0.plot(w[m], gaussian_filter1d(np.nan_to_num(f), sm)[m], color="k", lw=0.6, label=f"mwmStar hdu{hdu} S/N {snr:.0f}")
    info = []
    if fv:
        wc, fc, ic, used = coadd_visits(fv)
        mc = np.isfinite(fc)
        a0.plot(wc[mc], gaussian_filter1d(np.nan_to_num(fc), sm)[mc], color="tab:red", lw=0.5, alpha=0.7, label=f"own coadd of {len(used)} visits (XCSAO undone)")
        vs = load_visits(fv); off = 0
        med = np.nanmedian([np.nanmedian(v["flux"][(v["wave_bary"] > 5000) & (v["wave_bary"] < 6000)]) for v in vs if v["snr"] > 1] or [1])
        for v in sorted(vs, key=lambda v: v["mjd"]):
            mm = (v["wave_bary"] > 3650) & (v["wave_bary"] < 7400) & np.isfinite(v["flux"])
            a1.plot(v["wave_bary"][mm], gaussian_filter1d(np.nan_to_num(v["flux"]), sm + 1)[mm] + off, lw=0.5)
            a1.text(7420, off + med, f"MJD {v['mjd']} v={v['v']:.0f} S/N {v['snr']:.1f} {'LCO' if v['hdu']==2 else 'APO'}", fontsize=7, va="center")
            info.append((v["mjd"], round(v["v"], 1), round(v["snr"], 1), v["hdu"], v["in_stack"]))
            off += 1.2 * med
        a1.set_xlim(3650, 8100)
    for nm, (ls, col) in LINES.items():
        for l0 in ls:
            a0.axvline(l0, color=col, lw=0.5, ls=":")
            a1.axvline(l0, color=col, lw=0.4, ls=":")
    a0.set_xlim(3650, 9300); a0.legend(fontsize=8); a0.set_title(title, fontsize=10, loc="left")
    src = (wc, fc) if fv else (w, f)
    for a, (lo, hi) in zip(az, zooms):
        for (ww, ff, c, lab) in ((w, f, "k", "mwmStar"), (src[0], src[1], "tab:red", "own coadd")):
            mm = (ww > lo) & (ww < hi) & np.isfinite(ff)
            if mm.sum() < 5: continue
            a.plot(ww[mm], gaussian_filter1d(np.nan_to_num(ff), sm)[mm], color=c, lw=0.7)
        for nm, (ls, col) in LINES.items():
            for l0 in ls:
                if lo < l0 < hi: a.axvline(l0, color=col, lw=0.6, ls=":"); a.text(l0, a.get_ylim()[1] if False else 0, "", fontsize=6)
        if extra_lines:
            for l0, lab in extra_lines:
                if lo < l0 < hi: a.axvline(l0, color="c", lw=0.8, ls="--")
        a.set_xlim(lo, hi)
    handles = [plt.Line2D([], [], color=c, ls=":", label=nm) for nm, (l, c) in LINES.items()]
    a0.legend(handles=a0.get_legend_handles_labels()[0] + handles, fontsize=7, ncol=6)
    plt.tight_layout(); plt.savefig(out, dpi=65); plt.close()
    return info
if __name__ == "__main__":
    sid, gid, out = sys.argv[1], sys.argv[2], sys.argv[3]
    print(detail(sid, gid, " ".join(sys.argv[4:]), out))

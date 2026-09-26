# Full-spectrum plot for one object: barycentric re-coadd (XCSAO shift undone), per-visit spectra, zooms on H-beta/He II
# and H-alpha. Usage: python plot_spec.py <sdss_id> <label> [smooth_pix]
import sys, numpy as np, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/tmp/fanout/cv")
from cvspec import load_visits, load_star, coadd, LINES

sid = int(sys.argv[1]); label = sys.argv[2] if len(sys.argv) > 2 else str(sid); sm = int(sys.argv[3]) if len(sys.argv) > 3 else 3
vis = load_visits(sid)
lam, fl, iv, n = coadd(vis, use=[i for i, v in enumerate(vis) if v["snr"] > 1] or None)
def smooth(y, k):
    if k <= 1: return y
    yy = np.where(np.isfinite(y), y, 0.0); w = np.isfinite(y).astype(float); ker = np.ones(k)
    return np.convolve(yy, ker, "same") / np.maximum(np.convolve(w, ker, "same"), 1e-9)
fig = plt.figure(figsize=(15, 10))
ax = fig.add_axes([0.06, 0.55, 0.9, 0.4])
ax.plot(lam, smooth(fl, sm), "k-", lw=0.7, label=f"barycentric coadd of {n} visits (XCSAO shift undone)")
try:
    st = load_star(sid)[0]
    ax.plot(st["lam"], smooth(st["flux"], sm), color="tab:orange", lw=0.5, alpha=0.6, label=f"pipeline mwmStar coadd (v_rad={st['v_rad']:.0f})")
except Exception:
    pass
good = np.isfinite(fl)
lo, hi = np.nanpercentile(smooth(fl, sm)[good & (lam > 3800) & (lam < 9500)], [0.5, 99.7])
ax.set_ylim(min(0, lo) - 0.05 * (hi - lo), hi + 0.25 * (hi - lo)); ax.set_xlim(3600, 10300)
for k, l0 in LINES.items():
    if k in ("NaD", "OI7774", "FeII5169"): continue
    c = "tab:blue" if k.startswith("H") and not k.startswith("He") else ("tab:red" if k.startswith("HeII") else "tab:green")
    ax.axvline(l0, color=c, lw=0.6, alpha=0.5, ls=":")
    ax.text(l0, hi + 0.15 * (hi - lo), k, rotation=90, fontsize=7, color=c, ha="center", va="bottom")
ax.set_title(f"{label}  sdss_id {sid}  (visits: " + ", ".join(f"{v['mjd']} v_x={v['v_xcsao']:.0f} S/N={v['snr']:.1f}" for v in vis)[:230] + ")", fontsize=8)
ax.set_xlabel("vacuum wavelength (A, barycentric)"); ax.set_ylabel("flux (1e-17 erg/s/cm2/A)"); ax.legend(fontsize=7, loc="upper right")
# per-visit
ax2 = fig.add_axes([0.06, 0.07, 0.42, 0.4])
off = 0; stp = np.nanpercentile(fl[good], 95) * 0.8 if good.sum() else 1
for i, v in enumerate(sorted(vis, key=lambda x: x["mjd"] + x["tai_beg"] / 86400 / 1e5)):
    g = v["ivar"] > 0
    ax2.plot(v["lam"][g], smooth(v["flux"][g], sm) + off, lw=0.5)
    ax2.text(10000, off + 0.2 * stp, f"MJD {v['mjd']} S/N {v['snr']:.1f}", fontsize=6)
    off += stp
ax2.set_xlim(3600, 10300); ax2.set_title("individual visits (barycentric, offset)", fontsize=8)
for k in ("Ha", "Hb", "HeII4686", "HeI5876"):
    ax2.axvline(LINES[k], lw=0.5, ls=":", color="grey")
# zooms
for j, (a, b, ttl) in enumerate(((4250, 4950, "H-gamma .. H-beta, He II 4686"), (5800, 6750, "He I 5876, H-alpha, He I 6678"))):
    axz = fig.add_axes([0.55, 0.07 + 0.21 * (1 - j), 0.41, 0.17])
    s = (lam > a) & (lam < b)
    axz.plot(lam[s], smooth(fl[s], max(1, sm - 1)), "k-", lw=0.7)
    e = 1 / np.sqrt(np.where(iv[s] > 0, iv[s], np.nan))
    axz.fill_between(lam[s], fl[s] - e, fl[s] + e, color="grey", alpha=0.3, lw=0)
    for k, l0 in LINES.items():
        if a < l0 < b: axz.axvline(l0, color="tab:red" if "HeII" in k else "tab:blue", lw=0.6, ls=":")
    axz.set_title(ttl, fontsize=8)
fn = f"/tmp/fanout/cv/plots/spec_{sid}.png"
fig.savefig(fn, dpi=110); print(fn)

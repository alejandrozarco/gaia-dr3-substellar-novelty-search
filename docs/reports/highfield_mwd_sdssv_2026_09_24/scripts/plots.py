# Plotting helpers: (1) screening grid of continuum-normalised spectra; (2) per-star trumpet diagram (Balmer wavelengths vs B
# from the Schimeczek & Wunner database) under the normalised spectrum.
import numpy as np, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import spec as S, hfield as H
BALMER = (6564.61, 4862.68, 4341.69, 4102.89, 3971.2)

def grid(entries, out, ncol=2, title=""):
    """entries: list of (label, lam, flux, ivar)."""
    n = len(entries); nrow = int(np.ceil(n / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(9 * ncol, 2.1 * nrow), squeeze=False)
    for a, (lab, lam, f, iv) in zip(axs.flat, entries):
        mt = S.metrics(lam, f, iv); c = mt["cont"]; m = (lam > 3650) & (lam < 9500) & np.isfinite(c)
        a.plot(lam[m], gaussian_filter1d(f / c, 2)[m], "k", lw=0.5)
        for l0 in BALMER: a.axvline(l0, color="tab:blue", ls=":", lw=0.7)
        a.set_xlim(3650, 9500); a.set_ylim(0.35, 1.35); a.axhline(1, color="0.7", lw=0.5)
        a.set_title(lab + f" | exc {mt['excess']*100:.1f}% ndip {len(mt['dips'])}", fontsize=7.5, loc="left")
        a.tick_params(labelsize=7)
    for a in list(axs.flat)[n:]: a.axis("off")
    fig.suptitle(title, fontsize=9); plt.tight_layout(); plt.savefig(out, dpi=75); plt.close(fig)

_TR = None
def trumpet(lam, f, iv, out, title="", Bmax=1000.0, fmin=0.05, visits=None, logB=True, xr=(3650, 9300), mark=None, Bmin=None):
    """Top: normalised spectrum (+ per-visit spectra if given). Bottom: B vs lambda of Balmer components with relative
    oscillator strength (dE*S) >= fmin * max, alpha scaled by strength. mark: list of (lam, label) to annotate."""
    global _TR
    if _TR is None: _TR = H.load_balmer()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 8.5), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.6]))
    mt = S.metrics(lam, f, iv); c = mt["cont"]; m = np.isfinite(c) & (lam > xr[0]) & (lam < xr[1])
    a1.plot(lam[m], gaussian_filter1d(f / c, 2)[m], "k", lw=0.6, label="mwmStar coadd")
    if visits:
        for k, v in enumerate(visits):
            cv = S.continuum(v["lam"], v["flux"], v["ivar"]); mm = np.isfinite(cv) & (v["lam"] > xr[0]) & (v["lam"] < xr[1])
            a1.plot(v["lam"][mm], gaussian_filter1d(v["flux"] / cv, 3)[mm] - 0.35 * (k + 1), lw=0.5,
                    label=f"MJD {v['mjd']} v_xcsao {v['v']:+.0f} undone, S/N {v['snr']:.0f}")
    for l0 in BALMER: a1.axvline(l0, color="tab:blue", ls=":", lw=0.7); a2.axvline(l0, color="tab:blue", ls=":", lw=0.7)
    if mark:
        for l, s in mark: a1.annotate(s, (l, 1.12), fontsize=7, ha="center", color="tab:red"); a2.axvline(l, color="tab:red", lw=0.5, alpha=0.5)
    a1.set_ylim(0.2 - 0.35 * (len(visits) if visits else 0), 1.3); a1.axhline(1, color="0.7", lw=0.5)
    a1.legend(fontsize=6.5, loc="lower right"); a1.set_title(title, fontsize=8.5, loc="left")
    def ser(l0):
        for n, col in ((3, "tab:red"), (4, "tab:blue"), (5, "tab:green"), (6, "tab:orange")):
            if abs(l0 - H.LAM_RY / (0.25 - 1 / n**2)) < 40: return n, col
        return 9, "0.5"
    fser = {}
    for t in _TR:
        n, _ = ser(t["lam0"]); fser[n] = max(fser.get(n, 0), np.nanmax(t["f"]))
    for t in _TR:
        ok = np.isfinite(t["lam"]) & (t["B_MG"] <= Bmax) & (t["B_MG"] >= (0.5 if logB else 0))
        if ok.sum() < 2: continue
        n, col = ser(t["lam0"])
        if n > 6: continue
        fr = t["f"][ok] / fser[n]
        if fr.max() < fmin: continue
        pts = np.array([t["lam"][ok], t["B_MG"][ok]]).T
        # draw segments with alpha by strength
        from matplotlib.collections import LineCollection
        segs = np.stack([pts[:-1], pts[1:]], axis=1)
        al = np.clip(np.sqrt(fr[:-1]), 0.05, 1.0)
        lc = LineCollection(segs, colors=[matplotlib.colors.to_rgba(col, a) for a in al], linewidths=0.9); a2.add_collection(lc)
    a2.set_ylim(Bmin if Bmin is not None else (0.5 if logB else 0), Bmax); a2.set_yscale("log" if logB else "linear"); a2.set_xlim(*xr)
    a2.set_ylabel("B [MG]"); a2.set_xlabel("vacuum wavelength [A]")
    a2.set_title("Balmer components vs B (Schimeczek & Wunner H database, DaRUS-2118); alpha ~ sqrt(rel. osc. strength); red Ha, blue Hb, green Hg, orange Hd", fontsize=8)
    plt.tight_layout(); plt.savefig(out, dpi=85); plt.close(fig)
    return mt

"""Comparison figure for LP 133-754 (Gaia DR3 1609392862209121664, SDSS-V sdss_id 62246246) (2026-10-01).
(a) CH G-band region: LP 133-754 SDSS-V coadd, a median of SDSS-V DA white dwarfs with similar absolute magnitude and colour and a
    normal CH index (control), and G 99-37 (He-atmosphere magnetic DQ with known CH; sdss_id 75854318).
(b) the four individual SDSS-V visits and the DESI DR1 spectrum of LP 133-754, offset.
(c) 3800-5700 A: LP 133-754 vs G 99-37 (C2 Swan bands in G 99-37, none in LP 133-754).
(d) CH-index distribution of SDSS-V DA white dwarfs with M_G > 14 and S/N >= 6 (results/ch_index.csv).
SDSS-V visits: mwmVisit 0.8.1 BOSS spectra from the local store; the Astra XCSAO velocity is undone for in-stack visits (the stored
wavelengths of those visits are shifted by it); coadd = inverse-variance mean on a 1e-4 dex grid. Wavelengths vacuum, observed
frame. Normalisation: (a),(b) median of 4235-4262 and 4322-4332 A (the CH-index continuum); (c) median of 4500-5500 A. Display
smoothing: 5-pixel boxcar. Control: same-temperature DAs (0.45 < BP-RP < 0.65, as LP 133-754 at 0.54; M_G > 12.5; S/N >= 10; |CH-index z_pop| < 2; up to 40 stars). Ultramassive analogues of similar M_G are too few at usable S/N in SDSS-V (1 star with S/N >= 12).
Output: lp133_comparison.png, lp133_comparison.pdf."""
import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store"); C = 299792.458
G = 10 ** np.arange(np.log10(3650), np.log10(9000), 1e-4)
def vpath(sid): return os.path.join(ST, "sdssv_dr20", "visit", sid[-4:-2], sid[-2:], f"mwmVisit-0.8.1-{sid}.fits")
def visits(sid):
    out = []
    with fits.open(vpath(sid)) as h:
        for i in (1, 2):
            if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
            hd = h[i].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
            for r in h[i].data:
                v = float(r["xcsao_v_rad"]); w = wg * (1 + v / C) if (bool(r["in_stack"]) and np.isfinite(v)) else wg
                f = np.array(r["flux"], float); iv = np.array(r["ivar"], float); ok = (iv > 0) & np.isfinite(f)
                if ok.sum() < 500: continue
                out.append(dict(mjd=int(r["mjd"]), snr=float(r["snr"]), f=np.interp(G, w[ok], f[ok], left=np.nan, right=np.nan), iv=np.interp(G, w[ok], iv[ok], left=0, right=0)))
    return out
def coadd(vs):
    F = np.array([v["f"] for v in vs]); I = np.array([v["iv"] for v in vs]); F = np.nan_to_num(F)
    w = I.sum(0); return np.where(w > 0, (F * I).sum(0) / np.where(w > 0, w, 1), np.nan)
def norm(w, f, win):
    m = np.zeros_like(w, bool)
    for a, b in win: m |= (w > a) & (w < b)
    return f / np.nanmedian(f[m])
def sm(f, k=5): return np.convolve(np.nan_to_num(f, nan=np.nanmedian(f)), np.ones(k) / k, "same")
CHWIN = [(4235, 4262), (4322, 4332)]; WIDE = [(4500, 5500)]
lp_v = visits("62246246"); lp = coadd(lp_v); g99 = coadd(visits("75854318"))
T = pd.read_csv(os.path.join(H, "..", "results", "ch_index.csv"), dtype={"sdss_id": str})
ctl = T[(T.cls == "DA") & T.bprp.between(0.45, 0.65) & (T.MG > 12.5) & (T.snr >= 10) & (T.zpop.abs() < 2) & (T.sdss_id != "62246246")].head(40)
cs = []
for s in ctl.sdss_id:
    try: cs.append(norm(G, coadd(visits(s)), CHWIN))
    except Exception: pass
ctl_med = np.nanmedian(np.array(cs), 0); print("control stars:", len(cs))
d = np.load(os.path.join(ST, "desi_dr1_wd", "full", "spec_39633325647727762.npz")); dw, df = d["w"], np.where(d["iv"] > 0, d["f"], np.nan)
head = 4315.4 * (1 + 175 / C)   # CH A-X (0,0) head, vacuum, at the measured gravitational redshift (~ +175 km/s)
fig, ax = plt.subplots(2, 2, figsize=(13, 9)); a, b, c, e = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]
m = (G > 4150) & (G < 4480)
a.plot(G[m], sm(ctl_med)[m], color="0.5", lw=1.2, label=f"median of {len(cs)} SDSS-V DAs of the same colour (control)")
a.plot(G[m], sm(norm(G, g99, CHWIN))[m], color="tab:red", lw=1, label="G 99-37 (He-atmosphere magnetic DQ, known CH)")
a.plot(G[m], sm(norm(G, lp, CHWIN))[m], color="tab:blue", lw=1.3, label="LP 133-754 (SDSS-V coadd, 4 visits)")
a.axvline(head, color="k", ls=":", lw=0.8); a.text(head + 2, 1.28, "CH G-band head\n(redshifted)", fontsize=8)
for x, t in ((4341.7, "H$\\gamma$"), (4227.9, "Ca I")): a.axvline(x, color="0.7", lw=0.6); a.text(x + 1, 0.25, t, fontsize=8, color="0.4")
a.set_ylim(0.2, 1.45); a.set_xlim(4150, 4480); a.set_title("(a) CH G band: LP 133-754 vs control DAs and G 99-37", fontsize=10); a.legend(fontsize=8, loc="lower left"); a.set_ylabel("normalised flux")
for k, v in enumerate(sorted(lp_v, key=lambda v: v["mjd"])):
    b.plot(G[m], sm(norm(G, v["f"], CHWIN), 7)[m] + 0.6 * k, lw=0.9, label=f"SDSS-V visit MJD {v['mjd']} (S/N {v['snr']:.0f})")
dm = (dw > 4150) & (dw < 4480); b.plot(dw[dm], sm(norm(dw, df, CHWIN), 7)[dm] + 0.6 * len(lp_v), color="k", lw=0.9, label="DESI DR1 (independent)")
b.axvline(head, color="k", ls=":", lw=0.8); b.set_xlim(4150, 4480); b.set_title("(b) band present in every epoch (offset by 0.6)", fontsize=10); b.legend(fontsize=7, loc="upper left", ncol=1)
m2 = (G > 3800) & (G < 5700)
c.plot(G[m2], sm(norm(G, g99, WIDE), 7)[m2] + 0.8, color="tab:red", lw=0.9, label="G 99-37 (+0.8)")
c.plot(G[m2], sm(norm(G, lp, WIDE), 7)[m2], color="tab:blue", lw=0.9, label="LP 133-754")
for x in (4738.9, 5166.6, 5637.1): c.axvline(x, color="tab:red", lw=0.5, ls="--")
c.text(4745, 2.55, "C$_2$ Swan heads", fontsize=8, color="tab:red"); c.axvline(head, color="k", ls=":", lw=0.8)
for x, t in ((4862.7, "H$\\beta$"), (4341.7, "H$\\gamma$"), (4102.9, "H$\\delta$")): c.axvline(x, color="0.7", lw=0.6); c.text(x + 3, 0.15, t, fontsize=8, color="0.4")
c.set_xlim(3800, 5700); c.set_ylim(0, 2.8); c.set_xlabel("vacuum wavelength (A, observed)"); c.set_ylabel("normalised flux"); c.legend(fontsize=8, loc="upper right")
c.set_title("(c) no C$_2$ Swan bands in LP 133-754 (present in G 99-37)", fontsize=10)
P = T[(T.cls == "DA") & (T.MG > 14) & (T.snr >= 6)]; lpv = float(T.loc[T.sdss_id == "62246246", "ch_index"].iloc[0])
e.hist(P.ch_index.clip(-0.3, 0.45), bins=60, color="0.6"); e.axvline(lpv, color="tab:blue", lw=2); e.text(lpv - 0.01, e.get_ylim()[1] * 0.8, f"LP 133-754\n{lpv:.3f}", ha="right", fontsize=9, color="tab:blue")
e.set_yscale("log"); e.set_xlabel("CH G-band index (1 - band / continuum)"); e.set_ylabel("number of white dwarfs")
e.set_title(f"(d) CH index of {len(P)} cool SDSS-V DA white dwarfs (M$_G$ > 14, S/N $\\geq$ 6)", fontsize=10); b.set_xlabel("vacuum wavelength (A, observed)")
fig.suptitle("LP 133-754 (Gaia DR3 1609392862209121664): cool (6,700 K) ultramassive (1.25 M$_\\odot$) hydrogen-atmosphere white dwarf with CH absorption", fontsize=11)
plt.tight_layout(rect=(0, 0, 1, 0.96)); plt.savefig(os.path.join(H, "lp133_comparison.png"), dpi=110); plt.savefig(os.path.join(H, "lp133_comparison.pdf")); print("saved")

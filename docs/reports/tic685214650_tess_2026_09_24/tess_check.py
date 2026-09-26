# TIC 685214650 = Gaia DR3 4771958598593101184 (cool DC white dwarf, 75 pc, G 19.0): Huang+2026 (arXiv:2605.03323) list a
# 787.464 c/d (109.7 s), 69 ppt signal in TESS Sector 87 20-s data. (1) Reproduce it in the SPOC 20-s PDCSAP light curves of
# Sectors 87 and 94; crowding keywords. (2) Pixel test: in each 20-s TPF, fit a sinusoid at the best frequency to every pixel's
# flux (e-/s) and map the amplitude; compare the amplitude-weighted centroid and the peak pixel with the Gaia positions of the
# target and its neighbours at the TESS epoch. A source at the WD position puts the amplitude peak on the WD's pixel; the G = 15.99
# star 28" away (1.3 TESS pixels) or the G = 16.53 RUWE-10 M-dwarf binary 43" away would move it.
import numpy as np, glob, json
from astropy.io import fits
from astropy.wcs import WCS
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
field = json.load(open("gaia_field.json"))["field"]
out = {}
def fit_sin(t, y, f):
    X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t)]).T
    b, *_ = np.linalg.lstsq(X, y, rcond=None); r = y - X @ b; s = np.sqrt(np.sum(r ** 2) / (len(y) - 3))
    C = np.linalg.inv(X.T @ X) * s ** 2; A = np.hypot(b[1], b[2]); eA = np.sqrt((C[1, 1] + C[2, 2]) / 2)
    return A, eA, np.arctan2(b[2], b[1]), b[0]
for sec, lcf, tpf in (("87", glob.glob("mastDownload/TESS/*s0087*/*fast-lc.fits")[0], glob.glob("mastDownload/TESS/*s0087*/*fast-tp.fits")[0]),
                      ("94", glob.glob("mastDownload/TESS/*s0094*/*fast-lc.fits")[0], glob.glob("mastDownload/TESS/*s0094*/*fast-tp.fits")[0])):
    h = fits.open(lcf); d = h[1].data; hd = h[1].header
    m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]) & np.isfinite(d["TIME"])
    t = d["TIME"][m]; f = d["PDCSAP_FLUX"][m]; e = d["PDCSAP_FLUX_ERR"][m]; sap = d["SAP_FLUX"][m]
    med = np.median(f); y = f / med - 1; ok = np.abs(y - np.median(y)) < 5 * 1.4826 * np.median(np.abs(y - np.median(y))); t, y, e2 = t[ok], y[ok], (e / med)[ok]
    fr = np.arange(50, 2159, 0.002); ls = LombScargle(t, y); p = ls.power(fr, method="fast"); i = np.argmax(p)
    near = np.abs(fr - 787.464) < 0.5; j = np.argmax(np.where(near, p, 0))
    fine = np.arange(fr[j] - 0.01, fr[j] + 0.01, 1e-5); pf = ls.power(fine); fb = fine[np.argmax(pf)]
    A, eA, ph, _ = fit_sin(t, y, fb)
    top = np.argsort(p)[::-1]; pk = []
    for k in top:
        if all(abs(fr[k] - q) > 0.05 for q in pk): pk.append(fr[k])
        if len(pk) == 5: break
    fap = ls.false_alarm_probability(p[j], minimum_frequency=50, maximum_frequency=2159, method="baluev")
    res = dict(n=int(len(t)), span_d=float(t.max() - t.min()), CROWDSAP=hd.get("CROWDSAP"), FLFRCSAP=hd.get("FLFRCSAP"), median_pdcsap=float(med), median_sap=float(np.median(sap)),
               best_global_freq=float(fr[i]), top5=[float(x) for x in pk], freq_near_787=float(fb), power=float(p[j]), fap=float(fap), amp_ppt=float(A * 1e3), e_amp_ppt=float(eA * 1e3))
    print(f"S{sec}: n {len(t)}, CROWDSAP {hd.get('CROWDSAP')}, FLFRCSAP {hd.get('FLFRCSAP')}, median PDCSAP {med:.1f} e/s (SAP {np.median(sap):.1f}); "
          f"peak near 787.464: {fb:.4f} c/d ({86400/fb:.3f} s), power {p[j]:.4f}, FAP {fap:.1e}, amplitude {A*1e3:.1f} +- {eA*1e3:.1f} ppt; top peaks {[round(x,3) for x in pk]}")
    # pixel test
    th = fits.open(tpf); T = th[1].data; wcs = WCS(th[2].header); ap = th[2].data
    q = (T["QUALITY"] == 0) & np.isfinite(T["TIME"]); tt = T["TIME"][q]; FL = T["FLUX"][q]          # background-subtracted e-/s
    good = np.all(np.isfinite(FL), axis=(1, 2)); tt, FL = tt[good], FL[good]
    ny, nx = FL.shape[1:]; Amap = np.zeros((ny, nx)); Emap = np.zeros((ny, nx)); Pmap = np.zeros((ny, nx)); mean = np.nanmedian(FL, axis=0)
    for yy in range(ny):
        for xx in range(nx):
            yv = FL[:, yy, xx] - np.median(FL[:, yy, xx]); A_, eA_, ph_, _ = fit_sin(tt, yv, fb); Amap[yy, xx], Emap[yy, xx], Pmap[yy, xx] = A_, eA_, ph_
    S = Amap / Emap; pk_y, pk_x = np.unravel_index(np.argmax(S), S.shape)
    # amplitude-weighted centroid using pixels with S/N > 3 and in-phase with the peak pixel
    inph = (np.cos(Pmap - Pmap[pk_y, pk_x]) > 0.5) & (S > 3); yy, xx = np.mgrid[0:ny, 0:nx]
    cy = np.sum(yy * Amap * inph) / np.sum(Amap * inph); cx = np.sum(xx * Amap * inph) / np.sum(Amap * inph)
    tmid = 2457000 + np.median(tt); yr = 2016.0 + (tmid - 2457389.0) / 365.25
    stars = []
    for s in field[:8]:
        ra = float(s["ra"]) + (float(s["pmra"] or 0) * (yr - 2016.0) / 3.6e6) / np.cos(np.radians(float(s["dec"]))); de = float(s["dec"]) + float(s["pmdec"] or 0) * (yr - 2016.0) / 3.6e6
        px, py = wcs.all_world2pix([[ra, de]], 0)[0]; stars.append((str(s["source_id"]), float(s["phot_g_mean_mag"]), float(s["sep"]), float(px), float(py)))
    tgt = stars[0]
    print(f"   pixel test S{sec}: peak-S/N pixel (x,y)=({pk_x},{pk_y}) S/N {S.max():.1f}, amp {Amap[pk_y,pk_x]:.2f} e/s; in-phase amplitude centroid ({cx:.2f},{cy:.2f}); "
          f"target at ({tgt[3]:.2f},{tgt[4]:.2f}); offsets: " + "; ".join(f"{sid[-6:]} G{G:.1f} d={np.hypot(cx-px, cy-py):.2f} px" for sid, G, sep, px, py in stars))
    res["pixel"] = dict(peak=[int(pk_x), int(pk_y)], peak_snr=float(S.max()), centroid=[float(cx), float(cy)], stars=stars, epoch=float(yr))
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
    for a, img, ttl in ((axs[0], mean, "median flux (e/s)"), (axs[1], Amap, f"amplitude at {fb:.3f} c/d (e/s)"), (axs[2], S, "amplitude S/N")):
        im = a.imshow(img, origin="lower", cmap="viridis"); plt.colorbar(im, ax=a, fraction=0.046)
        for sid, G, sep, px, py in stars:
            a.plot(px, py, "r*" if sid == tgt[0] else "wo", ms=9 if sid == tgt[0] else 5, mfc="none" if sid != tgt[0] else "r")
            if G < 17.5 or sid == tgt[0]: a.annotate(f"G{G:.1f}", (px, py), color="w", fontsize=7, xytext=(3, 3), textcoords="offset points")
        a.contour(ap & 2 > 0, levels=[0.5], colors="orange", linewidths=0.8); a.plot(cx, cy, "m+", ms=12); a.set_title(f"S{sec} {ttl}", fontsize=9)
    plt.tight_layout(); plt.savefig(f"pixel_S{sec}.png", dpi=90); plt.close()
    out[sec] = res
json.dump(out, open("tess_check.json", "w"), indent=1, default=float)

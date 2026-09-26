# Full-range (3700-9200 A) SDSS-V spectra of a list of Gaia DR3 ids from sw_magnetic.csv, each against a non-magnetic DA of similar
# SnowWhite temperature, to look for high-field (>15 MG) or complex Zeeman patterns missed by the H-alpha/H-beta triplet inspection.
import sys, csv, numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
SW = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
ids = sys.argv[2:]; out = sys.argv[1]
def load(sid, v="0.8.1"):
    h = fits.open(f"spec/mwmStar-{v}-{sid}.fits"); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]
        if best is None or d["snr"] > best[3]: best = (np.array(d["wavelength"]), np.array(d["flux"]), np.array(d["ivar"]), float(d["snr"]))
    return best
lc, fc, _, _ = load(54797138)       # non-magnetic DA, Teff 11,150 K (Gaia DR3 458685159848886528)
fig, axs = plt.subplots(len(ids), 1, figsize=(13, 2.6 * len(ids)))
for a, g in zip(np.atleast_1d(axs), ids):
    r = SW[g]; lam, f, iv, snr = load(r["sdss_id"]); sm = np.convolve(f, np.ones(5) / 5, mode="same"); m = (lam > 3700) & (lam < 9200)
    n = np.median(sm[(lam > 5200) & (lam < 5400)]); nc = np.median(fc[(lc > 5200) & (lc < 5400)])
    a.plot(lc[(lc > 3700) & (lc < 9200)], np.convolve(fc, np.ones(5) / 5, mode="same")[(lc > 3700) & (lc < 9200)] / nc + 0.7, color="0.6", lw=0.5)
    a.plot(lam[m], sm[m] / n, color="k", lw=0.6)
    for l0 in (6564.61, 4862.68, 4341.69, 4102.9): a.axvline(l0, color="tab:blue", ls=":", lw=0.7)
    a.set_xlim(3700, 9200); a.set_ylim(0, 2.3)
    a.set_title(f"Gaia DR3 {g} | SW {r['classification']} p_dah {float(r['p_dah']):.2f} p_mwd {float(r['p_mwd']):.2f} | Teff_SW {r['teff']} logg_SW {r['logg']} | S/N {snr:.0f} | grey: non-magnetic DA 11,150 K (+0.7)", fontsize=8)
plt.tight_layout(); plt.savefig(out, dpi=80); print("ok")

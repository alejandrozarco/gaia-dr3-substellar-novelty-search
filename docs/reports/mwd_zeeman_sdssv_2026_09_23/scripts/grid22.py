# Figure: H-beta and H-alpha of the 22 SDSS-V DR20 white dwarfs with Zeeman-split Balmer lines and no magnetic classification found,
# sorted by S/N, with linear-Zeeman pi and sigma positions for the field measured independently from each line.
import csv, numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [r for r in csv.DictReader(open("report/novelty_summary.csv")) if r["verdict"] == "NO_MAGNETIC_LABEL"]
SW = {r["gaia_dr3_source_id"]: r for r in csv.DictReader(open("sw_magnetic.csv"))}
R.sort(key=lambda r: -float(r["sdssv_snr"]))
L0 = {"Hb": 4862.68, "Ha": 6564.61}
def load(g):
    s = SW[g]; h = fits.open(f"spec/mwmStar-{s['v_astra']}-{s['sdss_id']}.fits"); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]
        if best is None or d["snr"] > best[3]: best = (np.array(d["wavelength"]), np.array(d["flux"]), np.array(d["ivar"]), float(d["snr"]))
    return best
fig, axs = plt.subplots(11, 4, figsize=(15, 30))
for n, r in enumerate(R):
    lam, f, iv, snr = load(r["gaia_dr3"]); sm = np.convolve(f, np.ones(3) / 3, mode="same")
    for c, k in enumerate(("Hb", "Ha")):
        a = axs[n // 2, (n % 2) * 2 + c]; l0 = L0[k]; w = (lam > l0 - 250) & (lam < l0 + 250)
        norm = np.median(sm[w][np.abs(lam[w] - l0) > 210]); a.plot(lam[w], sm[w] / norm, color="k", lw=0.6)
        B = float(r["B_Ha_MG"] if k == "Ha" else r["B_Hb_MG"]); dl = 4.67e-13 * l0 ** 2 * B * 1e6
        for off, col in ((-dl, "tab:red"), (0, "tab:blue"), (dl, "tab:red")): a.axvline(l0 + off, color=col, ls=":", lw=0.9)
        a.set_xlim(l0 - 250, l0 + 250); a.set_ylim(0.3, 1.35); a.tick_params(labelsize=6)
        a.set_title(f"{r['gaia_dr3']} {k}: B={B:.2f} MG | G {r['G']} {r['dist_pc'][:-2]} pc | S/N {r['sdssv_snr']} | SW {r['snowwhite_class']}", fontsize=6.5)
for m in range(len(R), 22 + (22 % 2)):
    for c in range(2): axs[m // 2, (m % 2) * 2 + c].axis("off")
plt.tight_layout(); plt.savefig("report/no_label_22_grid.png", dpi=72); print("ok", len(R))

# Amplitude spectra (PDCSAP, 120-s) per TESS sector for the four new ZZ Ceti candidates, with 5x mean-amplitude lines.
import json, glob, numpy as np
from astropy.io import fits
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = [json.loads(l) for l in open("lane1_lc_results.jsonl")]
surv = {"6492083311194727168": "[OHD2001] WD J2324-595", "6558472750993181568": "GALEX J214927.5-515827",
        "2908195134345338496": "GALEX J054243.4-261011", "4729763229265811328": "GALEX J033619.1-564435"}
for g, nm in surv.items():
    rows = sorted([r for r in R if r["gaia"] == g and r["status"] == "OK"], key=lambda r: r["sector"])
    fig, axs = plt.subplots(len(rows), 1, figsize=(10, 1.9 * len(rows) + 0.6), squeeze=False)
    for a, r in zip(axs[:, 0], rows):
        d = fits.open(glob.glob(f"lc/{r['file']}")[0])[1].data; m = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"])
        t = d["TIME"][m]; y = d["PDCSAP_FLUX"][m] / np.median(d["PDCSAP_FLUX"][m]) - 1; ok = np.abs(y - np.median(y)) < 5 * 1.4826 * np.median(np.abs(y - np.median(y))); t, y = t[ok], y[ok]
        fr = np.arange(40, 359, 0.002); A = np.sqrt(4 * LombScargle(t, y, normalization="psd").power(fr, method="fast") / len(t)) * 1e3
        a.plot(fr, A, color="k", lw=0.5); a.axhline(5 * A.mean(), color="tab:red", ls="--", lw=0.8); a.axhline(4 * A.mean(), color="tab:orange", ls=":", lw=0.8)
        a.set_xlim(40, 359); a.set_ylabel("ppt", fontsize=7); a.tick_params(labelsize=7)
        a.text(0.99, 0.85, f"S{r['sector']} (CROWDSAP {r['crowdsap']:.2f})", transform=a.transAxes, ha="right", fontsize=7)
        for P in (1049.3, 881.6, 947.5, 472.6, 692.1, 971.4):
            if g == "6492083311194727168" and P in (1049.3, 881.6) or g == "6558472750993181568" and P in (947.5, 472.6) or g == "2908195134345338496" and P == 692.1 or g == "4729763229265811328" and P == 971.4:
                a.axvline(86400 / P, color="tab:blue", lw=0.6, alpha=0.5)
    axs[-1, 0].set_xlabel("frequency (c/d)"); fig.suptitle(f"Gaia DR3 {g} = {nm}: TESS 120-s amplitude spectra (red: 5x mean, orange: 4x mean; blue: detected periods)", fontsize=8)
    plt.tight_layout(); plt.savefig(f"fig_{g}.png", dpi=90); plt.close()
print("ok")

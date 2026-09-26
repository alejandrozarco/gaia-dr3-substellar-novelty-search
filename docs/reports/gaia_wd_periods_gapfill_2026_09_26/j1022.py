"""SDSS J1022+1611 (Gaia DR3 3890059941364406144): SPARCL SDSS/BOSS spectra, full range and Balmer zooms; Gaia parameters."""
import os
import sys, numpy as np, requests, io, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, time
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
from scipy.ndimage import gaussian_filter1d
q = "SELECT source_id, ra, dec, parallax, parallax_error, phot_g_mean_mag, bp_rp, ruwe, phot_bp_rp_excess_factor FROM gaiadr3.gaia_source WHERE source_id=3890059941364406144"
print(requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=120).text)
for k in range(5):
    try: sp = GE.sparcl_spectra(155.71509, 16.19768); break
    except Exception: time.sleep(20)
fig, ax = plt.subplots(2, 1, figsize=(13, 8))
for k, s in enumerate(sp):
    m = (s["iv"] > 0) & np.isfinite(s["f"]); w, f = s["w"][m], s["f"][m]
    ax[0].plot(w, gaussian_filter1d(f, 2) + 10 * k, lw=.6, label=f"{s['dataset']} {s['date']}")
    for j, l in enumerate([4102.9, 4341.7, 4862.7, 6564.6]):
        mm = np.abs(w / l - 1) * 3e5 < 6000
        ax[1].plot((w[mm] / l - 1) * 3e5, gaussian_filter1d(f[mm] / np.median(f[mm]), 2) + 0.6 * j + 0.25 * k, lw=.7)
for l in [3889, 3970.1, 4102.9, 4341.7, 4471.5, 4686, 4862.7, 5877, 6564.6]: ax[0].axvline(l, color="r", lw=.3)
ax[0].legend(fontsize=7); ax[0].set_xlim(3800, 9200); ax[1].set_title("Hd, Hg, Hb, Ha (bottom to top)"); ax[1].set_xlabel("km/s")
plt.tight_layout(); plt.savefig("j1022_spec.png", dpi=80)

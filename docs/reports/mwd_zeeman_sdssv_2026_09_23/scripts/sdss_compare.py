# Compare SDSS-I/II and eBOSS spectra (DR17) with the SDSS-V DR20 coadd for two white dwarfs whose SDSS-V spectra show strongly
# shifted Balmer features: WD 0745+365 (Gaia DR3 894999926685547520) and SDSS J085704.64+122226.5 (Gaia DR3 604881311110788864).
# SDSS DR17 lite spectra are in air wavelengths? No: SDSS spec 'loglam' is vacuum. Both sets are plotted in vacuum wavelength.
import numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def sdss(fn):
    d = fits.open(fn)[1].data; return 10 ** d["loglam"], d["flux"], d["ivar"]
def sdssv(sid):
    h = fits.open(f"/tmp/mwd/spec/mwmStar-0.8.1-{sid}.fits"); d = h[1].data[0] if len(h[1].data) else h[2].data[0]
    return np.array(d["wavelength"]), np.array(d["flux"]), np.array(d["ivar"])
sets = {"WD 0745+365 = Gaia DR3 894999926685547520": [("SDSS 0543-52017-0272 (2001-04)", sdss("spec-0543-52017-0272.fits")), ("eBOSS 9354-57806-0631 (2017-02)", sdss("spec-9354-57806-0631.fits")), ("SDSS-V DR20 (MJD 60675, 2024-12)", sdssv(57740866))],
        "SDSS J085704.64+122226.5 = Gaia DR3 604881311110788864": [("SDSS 2433-53820-0224 (2006-03)", sdss("spec-2433-53820-0224.fits")), ("BOSS 5293-55953-0236 (2012-01)", sdss("spec-5293-55953-0236.fits")), ("SDSS-V DR20 (MJD 60382-60399, 2024-03)", sdssv(55938113))]}
fig, axs = plt.subplots(2, 1, figsize=(13, 8))
for a, (title, sp) in zip(axs, sets.items()):
    for k, (lab, (l, f, iv)) in enumerate(sp):
        m = (l > 3800) & (l < 9000); sm = np.convolve(f, np.ones(5) / 5, mode="same"); n = np.median(sm[(l > 5200) & (l < 5400)])
        a.plot(l[m], sm[m] / n + 0.7 * k, lw=0.6, label=lab)
    for l0 in (6564.61, 4862.68, 4341.69, 4102.89): a.axvline(l0, color="0.5", ls=":", lw=0.7)
    a.set_title(title, fontsize=9); a.legend(fontsize=7, loc="upper right"); a.set_xlim(3800, 9000); a.set_ylim(0, 3.2)
axs[-1].set_xlabel("vacuum wavelength (Å)"); plt.tight_layout(); plt.savefig("/tmp/mwd/sdss/compare.png", dpi=90); print("ok")

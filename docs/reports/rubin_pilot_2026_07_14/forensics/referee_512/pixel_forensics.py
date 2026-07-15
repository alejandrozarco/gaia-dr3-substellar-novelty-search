#!/usr/bin/env python
"""Referee pixel forensics: independent aperture photometry on freshly-fetched PS1 warp
cutouts at the transient position. WCS-keyed (not positional). For each warp:
- fraction of masked (NaN) pixels in a r=3px core aperture
- aperture flux, background, noise -> SNR
- predicted SNR for a real i=21.15/21.59 source given the frame zeropoint/exptime
"""
import math
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

RA, DEC = 313.2265057, -14.8404352
CASES = {
    "55089_30380": ("partner", None),
    "55089_31126": ("catalog-detection", 21.591),
    "56472_50426": ("catalog-detection", 21.15),
    "56472_51576": ("partner", None),
}

for tag, (role, cat_mag) in CASES.items():
    fn = f"/tmp/rubin_pilot/forensics/referee_512/ref_{tag}.fits"
    with fits.open(fn) as hdul:
        h = hdul[0].header if hdul[0].data is not None else hdul[1].header
        d = hdul[0].data if hdul[0].data is not None else hdul[1].data
        w = WCS(h)
        zp = h.get("HIERARCH FPA.ZP", h.get("FPA.ZP", h.get("ZPT_OBS")))
        expt = h.get("EXPTIME")
        mjd = h.get("MJD-OBS")
    x, y = w.all_world2pix([[RA, DEC]], 0)[0]
    ny, nx = d.shape
    assert 5 < x < nx - 5 and 5 < y < ny - 5, f"{tag}: target off cutout ({x:.1f},{y:.1f})"
    yy, xx = np.mgrid[0:ny, 0:nx]
    rr = np.hypot(xx - x, yy - y)
    core = rr <= 3.0
    ann = (rr > 8) & (rr <= 20)
    core_vals = d[core]
    n_masked = int(np.sum(~np.isfinite(core_vals)))
    bg_vals = d[ann][np.isfinite(d[ann])]
    bg = np.median(bg_vals)
    sig = 1.4826 * np.median(np.abs(bg_vals - bg))
    good = core_vals[np.isfinite(core_vals)]
    flux = float(np.sum(good - bg))
    npix = len(good)
    snr = flux / (sig * math.sqrt(npix)) if npix else float("nan")
    # predicted counts for cat_mag: PS1 warps in units where m = zp - 2.5log10(counts/exptime)?
    # PS1 warp pixels: counts; m = ZP + 2.5*log10(exptime)?? -> report relative statement instead:
    line = (f"{tag} [{role}] MJD-OBS={mjd} exptime={expt} zp={zp} target@({x:.1f},{y:.1f}) "
            f"masked_core_px={n_masked}/{core.sum()} bg={bg:.2f} sig={sig:.2f} "
            f"apflux={flux:.1f} SNR={snr:.1f}")
    print(line)

# cross-check: measure a bright comparison? Instead, empirical calibration:
# use the two catalog-detection warps: catalog claims i=21.59 (flux 8.39e-6 Jy) and i=21.15.
# If those were real, the SAME source appears in partner warps at identical mag.
# So compare SNR(partner) directly with SNR(detection warp) measured the same way.

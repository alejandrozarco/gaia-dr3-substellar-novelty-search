#!/usr/bin/env python
"""Calibrate PS1 warp counts with the real i=17.013 star, predict SNR of a real i=21.15/21.59
source at the transient position, and compare with measured aperture fluxes."""
import math, urllib.request
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

STAR = (313.2253749938317, -14.836904295504986, 17.013)  # PS1 iMeanPSFMag, nDet=87
TGT = (313.2265057, -14.8404352)
WARPS = ["55089_30380", "55089_31126", "56472_50426", "56472_51576"]

def cutout(warp, ra, dec, tag):
    fn = f"/tmp/rubin_pilot/forensics/referee_512/star_{warp}.fits" if tag == "star" else \
         f"/tmp/rubin_pilot/forensics/referee_512/ref_{warp}.fits"
    if tag == "star":
        url = ("https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
               f"red=/rings.v3.skycell/1043/029/rings.v3.skycell.1043.029.wrp.i.{warp}.fits"
               f"&ra={ra}&dec={dec}&size=60&format=fits")
        urllib.request.urlretrieve(url, fn)
    return fn

def measure(fn, ra, dec, rad=3.0):
    with fits.open(fn) as hdul:
        h = hdul[0].header; d = hdul[0].data
        w = WCS(h)
    x, y = w.all_world2pix([[ra, dec]], 0)[0]
    ny, nx = d.shape
    yy, xx = np.mgrid[0:ny, 0:nx]
    rr = np.hypot(xx - x, yy - y)
    core = rr <= rad
    ann = (rr > 8) & (rr <= 20)
    bg_vals = d[ann][np.isfinite(d[ann])]
    bg = np.median(bg_vals)
    sig = 1.4826 * np.median(np.abs(bg_vals - bg))
    good = d[core][np.isfinite(d[core])]
    flux = float(np.sum(good - bg))
    return flux, sig, len(good), int(np.sum(~np.isfinite(d[core])))

print("warp        star_apflux  ->counts per i=21.15 source | tgt_apflux tgt_SNR pred_SNR(21.15) pred_SNR(21.59)")
for wp in WARPS:
    sfn = cutout(wp, STAR[0], STAR[1], "star")
    sflux, ssig, sn, smask = measure(sfn, STAR[0], STAR[1], rad=4.0)
    tflux, tsig, tn, tmask = measure(f"/tmp/rubin_pilot/forensics/referee_512/ref_{wp}.fits", TGT[0], TGT[1])
    # counts scale: star flux corresponds to i=17.013 (aperture rad 4 px ~ most of PSF)
    for m in (21.15, 21.591):
        pred = sflux * 10 ** (-0.4 * (m - STAR[2]))
        snr_pred = pred / (tsig * math.sqrt(tn))
        print(f"{wp}: star={sflux:8.0f} (masked {smask})  pred_counts(i={m})={pred:6.1f} "
              f"pred_SNR={snr_pred:4.1f} | tgt_flux={tflux:6.1f} tgt_SNR={tflux/(tsig*math.sqrt(tn)):4.1f} tgt_masked={tmask}")

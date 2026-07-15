#!/usr/bin/env python
"""Referee: compare LIVE Fink LSST diaSources to the report's lsst_photometry_mjd.csv,
keyed strictly by diaSourceId (no positional/order alignment)."""
import json, pandas as pd, numpy as np

base = "/tmp/rubin_pilot/forensics/170635519425249637/"
live = json.load(open(base + "referee3/fink_sources_live.json"))
print("live diaSources:", len(live))
rep = pd.read_csv(base + "lsst_photometry_mjd.csv")
print("report diaSources:", len(rep))

lm = {}
for s in live:
    did = int(s["i:diaSourceId"])
    lm[did] = s

assert set(lm.keys()) == set(rep["diaSourceId"].astype(int)), "diaSourceId sets differ!"

for _, r in rep.iterrows():
    did = int(r["diaSourceId"])
    s = lm[did]
    mjd_live = float(s["i:midpointMjdTai"])
    flux_live = float(s["i:psfFlux"])
    err_live = float(s["i:psfFluxErr"])
    band_live = s["i:band"]
    ra_live, dec_live = float(s["i:ra"]), float(s["i:dec"])
    assert abs(mjd_live - r["mjd_tai"]) < 1e-6, (did, mjd_live, r["mjd_tai"])
    assert abs(r["jd_tai"] - (r["mjd_tai"] + 2400000.5)) < 1e-5, ("JD/MJD offset wrong", did)
    assert band_live == r["band"], (did, band_live, r["band"])
    assert abs(flux_live - r["psf_diff_flux_nJy"]) < 0.5, (did, flux_live, r["psf_diff_flux_nJy"])
    assert abs(err_live - r["psf_diff_flux_err_nJy"]) < 0.5
    assert abs(ra_live - r["ra_deg"]) * 3600 < 0.01 and abs(dec_live - r["dec_deg"]) * 3600 < 0.01
    mag_live = 31.4 - 2.5 * np.log10(flux_live)
    assert abs(mag_live - r["diff_mag_AB"]) < 0.01, (did, mag_live, r["diff_mag_AB"])
    snr = flux_live / err_live
    rel = s.get("i:reliability")
    print("OK id=%d mjd=%.5f %s diffmag=%.3f snr=%.1f rel=%s ext=%s" %
          (did, mjd_live, band_live, mag_live, snr, rel, s.get("i:extendedness")))

# position stability from live data
ras = np.array([float(s["i:ra"]) for s in live])
decs = np.array([float(s["i:dec"]) for s in live])
mjds = np.array([float(s["i:midpointMjdTai"]) for s in live])
dra = (ras - ras.mean()) * np.cos(np.radians(decs.mean())) * 3600
ddec = (decs - decs.mean()) * 3600
sep = np.sqrt(dra**2 + ddec**2)
print("\nposition: max offset from mean = %.3f arcsec over %.2f d (mjd %.3f-%.3f)" %
      (sep.max(), mjds.max() - mjds.min(), mjds.min(), mjds.max()))
# linear motion fit (arcsec/day) to bound solar-system motion
pra = np.polyfit(mjds, dra, 1)[0]; pdec = np.polyfit(mjds, ddec, 1)[0]
print("fitted motion: %.4f arcsec/d RA, %.4f arcsec/d Dec" % (pra, pdec))
# flags
for s in live:
    for k in ("i:isDipole", "i:centroid_flag", "i:pixelFlags_saturated", "i:pixelFlags_cr"):
        v = s.get(k)
        if v not in (None, False, 0, "false", "False"):
            print("FLAG", s["i:diaSourceId"], k, v)
print("\nkeys sample:", sorted([k for k in live[0].keys() if k.startswith("i:")])[:60])

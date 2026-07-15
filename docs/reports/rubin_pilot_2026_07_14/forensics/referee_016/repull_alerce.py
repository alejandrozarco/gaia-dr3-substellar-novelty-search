#!/usr/bin/env python
"""Adversarial referee re-pull (2026-07-14/15): ALeRCE multisurvey LSST for 170591519677875016.
All comparisons MJD-keyed with asserts."""
import math, json
import numpy as np
import pandas as pd
from alerce.ms_search import AlerceSearchMultiSurvey

OUT = "/tmp/rubin_pilot/forensics/referee_016/"
oid = 170591519677875016
c = AlerceSearchMultiSurvey()
det = c.query_detections(oid=oid, survey="lsst", format="pandas")
det.to_csv(OUT + "ref_alerce_det.csv", index=False)
obj = c.query_object(oid=oid, survey="lsst", format="json")
json.dump(obj, open(OUT + "ref_alerce_obj.json", "w"), indent=1, default=str)
print("n_det:", len(det))

def njy2ab(f):
    return -2.5 * math.log10(f * 1e-9) + 8.90

# Claims from REPORT.md keyed by MJD
claims = {
    61218.31581: dict(band="i", mag=20.815, err=0.018, tflux=1085.4, tfluxerr=110.4),
    61228.32884: dict(band="i", mag=21.198, err=0.020, tflux=948.5, tfluxerr=122.3),
    61231.23473: dict(band="i", mag=21.135, err=0.043, tflux=1106.8, tfluxerr=110.7),
    61233.30790: dict(band="r", mag=21.122, err=0.016, tflux=943.8, tfluxerr=45.9),
}
assert len(det) == 4, f"expected 4 diaSources, got {len(det)}"
for mjd_c, cl in claims.items():
    m = det[np.abs(det["mjd"].astype(float) - mjd_c) < 2e-4]
    assert len(m) == 1, f"MJD {mjd_c}: {len(m)} rows matched"
    r = m.iloc[0]
    band = r["band_name"] if "band_name" in det.columns else r["band"]
    mag = njy2ab(float(r["psfFlux"]))
    magerr = 2.5 / math.log(10) * float(r["psfFluxErr"]) / float(r["psfFlux"])
    assert band == cl["band"], f"MJD {mjd_c}: band {band} != {cl['band']}"
    assert abs(mag - cl["mag"]) < 0.02, f"MJD {mjd_c}: mag {mag:.3f} vs claim {cl['mag']}"
    tf, tfe = float(r["templateFlux"]), float(r["templateFluxErr"])
    assert abs(tf - cl["tflux"]) < 5, f"MJD {mjd_c}: tflux {tf} vs {cl['tflux']}"
    print(f"MJD {mjd_c}: {band} {mag:.3f}+/-{magerr:.3f} | template {tf:.0f}+/-{tfe:.0f} nJy "
          f"= {njy2ab(tf):.2f} AB ({tf/tfe:.1f} sig) | rel={r.get('reliability')} "
          f"ext={r.get('extendedness')} sso={r.get('ssObjectId')}")
# positional scatter
ra = det["ra"].astype(float).values
dec = det["dec"].astype(float).values
dra = (ra - ra.mean()) * math.cos(math.radians(dec.mean())) * 3600e3
ddec = (dec - dec.mean()) * 3600e3
print(f"pos scatter (mas): RA rms {dra.std():.1f}, Dec rms {ddec.std():.1f}; "
      f"span {ra.max()-ra.min():.2e} deg over {det['mjd'].astype(float).max()-det['mjd'].astype(float).min():.2f} d")
print("ALL ALERCE ASSERTS PASSED")

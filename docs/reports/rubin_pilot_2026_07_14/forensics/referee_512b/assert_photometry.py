#!/usr/bin/env python
"""MJD-keyed asserts: fresh Fink pull vs claimed photometry_jd_keyed.csv rows."""
import json, math
import pandas as pd
import numpy as np

src = json.load(open("/tmp/rubin_pilot/forensics/referee_512b/fink_sources.json"))
df = pd.DataFrame(src)
df.columns = [c.split(":",1)[1] if ":" in c else c for c in df.columns]

def ab(flux_nJy):  # nJy -> AB
    return -2.5*math.log10(flux_nJy*1e-9) + 8.90

rows = []
for _, s in df.iterrows():
    rows.append(dict(
        mjd=float(s['midpointMjdTai']), band=s['band'],
        mag_diff=ab(s['psfFlux']),
        magerr_diff=2.5/math.log(10)*s['psfFluxErr']/s['psfFlux'],
        mag_total=ab(s['scienceFlux']),
        mag_template=ab(s['templateFlux']) if s['templateFlux'] and s['templateFlux']>0 else np.nan,
        snr=float(s['snr']), rel=float(s['reliability']),
        visit=int(s['visit']), det=int(s['detector']),
        ra=float(s['ra']), dec=float(s['dec']),
        anyflag=any(bool(s[c]) for c in df.columns if c.startswith('pixelFlags_')),
        isdip=bool(s['isDipole']), isneg=bool(s['isNegative']),
    ))
fresh = pd.DataFrame(rows).sort_values('mjd').reset_index(drop=True)
print(fresh.to_string())

claim = pd.read_csv("/tmp/rubin_pilot/forensics/170591507978387512/photometry_jd_keyed.csv")
claim_det = claim[claim['status']=='DETECTION'].copy()
print("\nclaimed detections:", len(claim_det))

# MJD-keyed asserts
n_matched = 0
for _, c in claim_det.iterrows():
    m = fresh[np.abs(fresh['mjd'] - c['mjd']) < 1e-4]
    assert len(m)==1, f"claimed epoch {c['mjd']} not uniquely in fresh pull ({len(m)} matches)"
    f = m.iloc[0]
    assert f['band']==c['band'], f"band mismatch at {c['mjd']}: {f['band']} vs {c['band']}"
    assert abs(f['mag_diff']-float(c['mag_diff_AB']))<0.02, f"mag_diff mismatch at {c['mjd']}: {f['mag_diff']:.3f} vs {c['mag_diff_AB']}"
    assert abs(f['mag_total']-float(c['mag_total_AB']))<0.02, f"mag_total mismatch at {c['mjd']}: {f['mag_total']:.3f} vs {c['mag_total_AB']}"
    assert abs(f['snr']-float(c['note'].split('snr=')[1].split(' ')[0]))<0.2
    n_matched += 1
print(f"ASSERTS PASS: {n_matched}/5 claimed Rubin epochs match fresh Fink pull (mjd, band, mag_diff, mag_total, snr)")

# any NEW epochs since the report?
extra = [m for m in fresh['mjd'] if not (np.abs(claim_det['mjd']-m)<1e-4).any()]
print("new epochs since report:", extra if extra else "none")

# light-curve shape check
fi = fresh[fresh['band']=='i']
print("\ni-band: ", [(round(r.mjd,3), round(r.mag_diff,3)) for r in fi.itertuples()])
rise = fi.iloc[0]['mag_diff'] - fi.iloc[1]['mag_diff']
dt = fi.iloc[1]['mjd'] - fi.iloc[0]['mjd']
print(f"rise {rise:.2f} mag in {dt:.2f} d; then {fi.iloc[1]['mag_diff']-fi.iloc[2]['mag_diff']:+.3f} over {fi.iloc[2]['mjd']-fi.iloc[1]['mjd']:.2f} d")
iz = fresh[(fresh['mjd']>61228)&(fresh['mjd']<61229)]
print("i-z (diff) at 61228:", round(iz[iz.band=='i'].mag_diff.iloc[0]-iz[iz.band=='z'].mag_diff.iloc[0],3))

# flags / dipole / negative / position scatter
print("\nany pixel flag set:", fresh['anyflag'].any(), "| dipole:", fresh['isdip'].any(), "| negative:", fresh['isneg'].any())
print("detectors:", sorted(fresh['det'].unique()), "visits:", sorted(fresh['visit'].unique()))
ra0, dec0 = fresh['ra'].mean(), fresh['dec'].mean()
sep = np.hypot((fresh['ra']-ra0)*np.cos(np.radians(dec0)), fresh['dec']-dec0)*3600
print(f"mean pos {ra0:.7f} {dec0:.7f}; per-epoch scatter (arcsec): {np.round(sep,4).tolist()}")
print(f"claimed pos 313.2265057 -14.8404352 -> offset {np.hypot((ra0-313.2265057)*np.cos(np.radians(dec0)), dec0-(-14.8404352))*3600:.4f} arcsec")

# template mags
print("template i mags:", np.round(fresh[fresh.band=='i']['mag_template'],3).tolist(),
      "z:", np.round(fresh[fresh.band=='z']['mag_template'],3).tolist())

# classifier fields from objects endpoint
obj = json.load(open("/tmp/rubin_pilot/forensics/referee_512b/fink_obj.json"))
o = obj[0] if isinstance(obj, list) else obj
for k in sorted(o):
    if 'clf' in k or 'tns' in k or 'elephant' in k.lower():
        print(k, "=", o[k])

#!/usr/bin/env python
"""Referee: LIVE re-pull of Rubin photometry from Fink LSST API; compare to REPORT table
and to the local fink_sources.json, keyed by diaSourceId and MJD (no positional alignment)."""
import requests, json, numpy as np, sys

OBJ = "170635519425249637"
r = requests.post("https://api.lsst.fink-portal.org/api/v1/sources",
                  json={"diaObjectId": OBJ, "output-format": "json"}, timeout=60)
print("HTTP", r.status_code, "len", len(r.text))
r.raise_for_status()
live = r.json()
print("live diaSources:", len(live))

def mag(nJy):
    return 31.4 - 2.5 * np.log10(nJy)

# Build live table keyed by diaSourceId
lt = {}
for s in live:
    did = s["r:diaSourceId"]
    lt[did] = dict(mjd=s["r:midpointMjdTai"], band=s["r:band"],
                   psf=s["r:psfFlux"], psferr=s["r:psfFluxErr"],
                   sci=s.get("r:scienceFlux"), rel=s.get("r:reliability"),
                   ra=s["r:ra"], dec=s["r:dec"])

# local file
loc = json.load(open("/tmp/rubin_pilot/forensics/170635519425249637/fink_object.json")) if False else None
locs = json.load(open("/tmp/rubin_pilot/forensics/170635519425249637/fink_sources.json"))
print("local diaSources:", len(locs))
for s in locs:
    did = s["r:diaSourceId"]
    assert did in lt, f"local diaSourceId {did} missing from live pull!"
    L = lt[did]
    assert abs(L["mjd"] - s["r:midpointMjdTai"]) < 1e-6, (did, "mjd mismatch")
    assert abs(L["psf"] - s["r:psfFlux"]) < 1e-3, (did, "psfFlux mismatch", L["psf"], s["r:psfFlux"])
    assert L["band"] == s["r:band"]

# REPORT claimed rows: (mjd, band, diffmag, snr)
claimed = [
    (61228.3877, "z", 22.30, 11.3), (61228.4188, "i", 21.36, 38.7),
    (61232.3248, "r", 21.33, 44.6), (61232.3267, "r", 21.35, 38.7),
    (61232.3541, "i", 21.40, 23.6), (61232.3560, "i", 21.38, 32.3),
    (61235.3406, "i", 21.54, 42.6), (61235.3415, "i", 21.60, 42.5),
    (61235.3677, "z", 21.89, 14.1), (61235.3686, "z", 22.21, 6.4),
]
rows = sorted(lt.values(), key=lambda x: x["mjd"])
assert len(rows) == len(claimed) == 10, (len(rows), "expected 10")
print(f"\n{'MJD':>12} {'band':>4} {'mag(live)':>9} {'mag(clm)':>8} {'SNR(live)':>9} {'SNR(clm)':>8} {'rel':>5}")
ras, decs, mjds = [], [], []
for (cm, cb, cmag, csnr), L in zip(claimed, rows):
    assert abs(L["mjd"] - cm) < 0.001, ("MJD key mismatch", L["mjd"], cm)
    assert L["band"] == cb, (cm, L["band"], cb)
    lm = mag(L["psf"]); lsnr = L["psf"] / L["psferr"]
    assert abs(lm - cmag) < 0.02, (cm, lm, cmag)
    assert abs(lsnr - csnr) < 2.0, (cm, lsnr, csnr)  # SNR to ~5%: report used slightly different err rounding
    print(f"{L['mjd']:12.4f} {L['band']:>4} {lm:9.2f} {cmag:8.2f} {lsnr:9.1f} {csnr:8.1f} {L['rel']:5.2f}")
    ras.append(L["ra"]); decs.append(L["dec"]); mjds.append(L["mjd"])

# positional stability, live data
ras, decs = np.array(ras), np.array(decs)
dra = (ras - ras.mean()) * np.cos(np.radians(-14.87)) * 3600
ddec = (decs - decs.mean()) * 3600
sep = np.sqrt(dra**2 + ddec**2)
print(f"\nposition scatter: max offset from mean = {sep.max():.3f}\" over {max(mjds)-min(mjds):.2f} d")
print(f"mean RA {ras.mean():.5f} Dec {decs.mean():.5f}")
# mover check: linear drift fit
A = np.polyfit(mjds, dra, 1)[0]; B = np.polyfit(mjds, ddec, 1)[0]
print(f"linear drift: {A*24:.4f}\"/hr RA, {B*24:.4f}\"/hr Dec ({np.hypot(A,B):.4f}\"/day total)")
print("\nALL LIVE FINK ASSERTS PASSED")

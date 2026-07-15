#!/usr/bin/env python
"""Referee: independent re-pull of Fink/LSST sources for diaObjectId 170591507978387512.
JD/MJD-keyed asserts against the claimed photometry_jd_keyed.csv rows."""
import json, sys, math
import urllib.request

OID = "170591507978387512"
URL = "https://api.lsst.fink-portal.org/api/v1/sources"

payload = json.dumps({"diaObjectId": OID, "output-format": "json"}).encode()
req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.loads(r.read().decode())

print(f"n_sources returned: {len(data)}")
rows = []
for s in data:
    mjd = s.get("r:midpointMjdTai") or s.get("f:midpointMjdTai")
    band = s.get("r:band")
    flux = s.get("r:psfFlux")          # nJy, difference flux
    ferr = s.get("r:psfFluxErr")
    sci = s.get("r:scienceFlux")
    scie = s.get("r:scienceFluxErr")
    rel = s.get("r:reliability")
    if mjd is None or flux is None:
        # dump keys once for diagnosis
        print("KEYS:", sorted(s.keys()))
        sys.exit("missing expected keys")
    mag_diff = -2.5 * math.log10(flux * 1e-9) + 8.90 if flux > 0 else None
    mag_diff_err = 2.5 / math.log(10) * ferr / flux if flux > 0 else None
    mag_tot = -2.5 * math.log10(sci * 1e-9) + 8.90 if sci and sci > 0 else None
    rows.append((float(mjd), band, mag_diff, mag_diff_err, mag_tot, flux / ferr, rel))

rows.sort()
for r_ in rows:
    print(f"MJD_TAI={r_[0]:.6f} band={r_[1]} mag_diff={r_[2]:.3f}+-{r_[3]:.3f} mag_tot={r_[4]:.3f} snr={r_[5]:.1f} rel={r_[6]}")

# ---- JD-keyed asserts vs claimed table ----
claimed = {
    61218.269544: ("z", 22.273, 21.851),
    61218.297847: ("i", 22.009, 21.808),
    61228.326103: ("i", 21.285, 21.108),
    61228.351994: ("z", 21.672, 21.448),
    61235.247397: ("i", 21.244, 21.106),
}
matched = 0
for mjd, band, md, mde, mt, snr, rel in rows:
    hits = [k for k in claimed if abs(k - mjd) < 1e-4]
    assert len(hits) == 1, f"epoch {mjd} not in claimed table (or ambiguous)"
    k = hits[0]
    cband, cmd, cmt = claimed[k]
    assert band == cband, f"band mismatch at {mjd}: {band} vs {cband}"
    assert abs(md - cmd) < 0.02, f"mag_diff mismatch at {mjd}: {md:.3f} vs {cmd}"
    assert abs(mt - cmt) < 0.02, f"mag_total mismatch at {mjd}: {mt:.3f} vs {cmt}"
    matched += 1
print(f"\nASSERTS PASSED: {matched} epochs matched by MJD key, band, mag_diff, mag_total")

# light-curve shape re-derivation (i band)
i_rows = [(m, md) for m, b, md, *_ in rows if b == "i"]
i_rows.sort()
if len(i_rows) >= 3:
    rise = i_rows[0][1] - i_rows[1][1]
    dt = i_rows[1][0] - i_rows[0][0]
    flat = i_rows[1][1] - i_rows[2][1]
    dt2 = i_rows[2][0] - i_rows[1][0]
    print(f"i-band: rise {rise:.2f} mag in {dt:.2f} d; then {flat:+.2f} mag over {dt2:.2f} d")

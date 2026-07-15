#!/usr/bin/env python
"""Referee: independent LS DR10 host check at Rubin position via Data Lab TAP sync."""
import urllib.request, urllib.parse, math

RA, DEC = 313.2265057, -14.8404352

adql = f"""SELECT ls_id, ra, dec, type, flux_g, flux_ivar_g, flux_r, flux_ivar_r,
flux_i, flux_ivar_i, flux_z, flux_ivar_z, nobs_g, nobs_r, nobs_i, nobs_z,
flux_w1, flux_w2, ebv
FROM ls_dr10.tractor
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, 10.0/3600.0)"""

url = "https://datalab.noirlab.edu/tap/sync?" + urllib.parse.urlencode({
    "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
with urllib.request.urlopen(url, timeout=120) as r:
    txt = r.read().decode()
print(txt)

import csv, io
rd = list(csv.DictReader(io.StringIO(txt)))
print(f"n sources within 10 arcsec: {len(rd)}")
for row in rd:
    ra2, dec2 = float(row["ra"]), float(row["dec"])
    dra = (ra2 - RA) * math.cos(math.radians(DEC)) * 3600
    ddec = (dec2 - DEC) * 3600
    sep = math.hypot(dra, ddec)
    def mag(f, iv):
        f = float(f); iv = float(iv)
        if f <= 0: return None, None
        m = 22.5 - 2.5 * math.log10(f)
        err = 2.5 / math.log(10) / (f * math.sqrt(iv)) if iv > 0 else None
        return m, err
    g, ge = mag(row["flux_g"], row["flux_ivar_g"])
    rr, re_ = mag(row["flux_r"], row["flux_ivar_r"])
    print(f"ls_id={row['ls_id']} type={row['type']} sep={sep:.3f}\" "
          f"g={g and round(g,2)}+-{ge and round(ge,2)} r={rr and round(rr,2)}+-{re_ and round(re_,2)} "
          f"nobs g/r/i/z={row['nobs_g']}/{row['nobs_r']}/{row['nobs_i']}/{row['nobs_z']} "
          f"W1flux={row['flux_w1']} W2flux={row['flux_w2']} ebv={row['ebv']}")

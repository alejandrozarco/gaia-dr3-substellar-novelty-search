#!/usr/bin/env python
"""Parse LS DR10 SCS VOTable, verify claimed counterpart independently."""
import math
from astropy.io.votable import parse_single_table

RA, DEC = 313.2265057, -14.8404352
t = parse_single_table("/tmp/rubin_pilot/forensics/referee_512/ls_scs.vot").to_table()
cols = t.colnames
print(f"n rows in 10\" cone: {len(t)}")
want = [c for c in ["ls_id","ra","dec","type","mag_g","mag_r","mag_i","mag_z",
                    "flux_g","flux_r","flux_ivar_g","flux_ivar_r",
                    "nobs_g","nobs_r","nobs_i","nobs_z","flux_w1","flux_w2","ebv"] if c in cols]
print("available wanted cols:", want)
for row in t:
    ra2, dec2 = float(row["ra"]), float(row["dec"])
    sep = math.hypot((ra2-RA)*math.cos(math.radians(DEC))*3600, (dec2-DEC)*3600)
    out = {c: row[c] for c in want}
    print(f"sep={sep:.3f}\"  " + "  ".join(f"{c}={out[c]}" for c in want))
    # derive mags from fluxes if present
    for b in ("g","r"):
        fc, ic = f"flux_{b}", f"flux_ivar_{b}"
        if fc in cols and ic in cols:
            f, iv = float(row[fc]), float(row[ic])
            if f > 0:
                m = 22.5 - 2.5*math.log10(f)
                e = 2.5/math.log(10)/(f*math.sqrt(iv)) if iv > 0 else float("nan")
                print(f"   derived {b} = {m:.2f} +- {e:.2f}  (SNR {f*math.sqrt(iv):.1f})")

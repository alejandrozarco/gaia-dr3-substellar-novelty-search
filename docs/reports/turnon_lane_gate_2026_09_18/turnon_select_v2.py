#!/usr/bin/env python3
"""Turn-on lane SELECTION v2 — dated nsc_dr2.meas instead of object-table averages.

The v1 selection used `mjd + deltamjd/2 < 58119` on nsc_dr2.object. Both columns are
aggregates over ALL bands, so the cut used a multi-band epoch aggregate to test a
single-band temporal condition. Measured on a 0.2x0.2 deg test box it discarded
58% of otherwise-valid objects (97 -> 41) while producing ZERO false positives.

v2 states the condition directly on dated r-band measurements.
"""
import subprocess, urllib.parse, csv, io, json, sys, time

TILES = [(118.3,10.4),(119.3,6.1),(120.0,8.0),(118.5,0.0),(116.0,12.0),(84.0,0.1),(83.0,-3.9)]
HALF = 0.6
def tap(q, t=280, tries=3):
    for k in range(tries):
        u = "https://datalab.noirlab.edu/tap/sync?" + urllib.parse.urlencode(
            {"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q})
        p = subprocess.run(["curl","-sL","--max-time",str(t),u],capture_output=True,text=True)
        if p.returncode == 0 and "," in p.stdout and "ERROR" not in p.stdout[:400]:
            return p.stdout
        time.sleep(4*(k+1))
    raise SystemExit("TAP failed — not returning a partial selection")

def sel(ra0, dec0, half):
    return f"""SELECT o.id, o.ra, o.dec, o.gmag, o.rmag, o.class_star,
       COUNT(m.mjd) AS n_r_pre, AVG(m.mag_auto) AS r_pre,
       MIN(m.mjd) AS first_pre, MAX(m.mjd) AS last_pre
FROM nsc_dr2.object o JOIN nsc_dr2.meas m ON m.objectid = o.id
WHERE o.ra BETWEEN {ra0-half} AND {ra0+half}
  AND o.dec BETWEEN {dec0-half} AND {dec0+half}
  AND o.class_star > 0.5 AND o.gmag > 0 AND o.gmag - o.rmag < 0.6
  AND m.filter = 'r' AND m.mjd < 58119
GROUP BY o.id, o.ra, o.dec, o.gmag, o.rmag, o.class_star
HAVING COUNT(m.mjd) >= 2 AND AVG(m.mag_auto) BETWEEN 22 AND 24"""

print("Turn-on selection v2 (dated meas). Comparing against v1 counts per tile.\n")
print(f"{'tile':>14} {'v2 (dated)':>11} {'v1 (object)':>12} {'ratio':>7}")
V1 = {"118.3_10.4":959,"119.3_6.1":1287,"120.0_8.0":434,"118.5_0.0":1672,
      "116.0_12.0":26,"84.0_0.1":9,"83.0_-3.9":16}
tot2 = 0
rows_all = []
for ra0, dec0 in TILES:
    key = f"{ra0}_{dec0}"
    body = tap(sel(ra0, dec0, HALF))
    rows = list(csv.DictReader(io.StringIO(body)))
    rows_all += rows
    n2 = len(rows); n1 = V1.get(key, 0); tot2 += n2
    print(f"{key:>14} {n2:11d} {n1:12d} {(n2/n1 if n1 else 0):7.2f}")
print(f"{'TOTAL':>14} {tot2:11d} {sum(V1.values()):12d} {tot2/sum(V1.values()):7.2f}")
json.dump(rows_all, open("turnon_out/candidates_v2_dated.json","w"))
print(f"\nwrote turnon_out/candidates_v2_dated.json ({len(rows_all)} objects)")

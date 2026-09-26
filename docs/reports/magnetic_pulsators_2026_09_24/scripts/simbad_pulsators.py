# SIMBAD: every object whose otype list contains Pu* or Pu? AND WD* or WD? (SIMBAD no longer has a ZZ* type; pulsating WDs are WD* + Pu*).
# Output lists/puls_simbad.csv with Gaia DR3 id (from ident) where available.
import sys, csv, json; sys.path.insert(0, 'scripts')
from simbad_tap import tap
q = ("SELECT b.oid, b.main_id, b.ra, b.dec, b.pmra, b.pmdec, b.otype, b.sp_type, i.id FROM basic AS b "
     "LEFT JOIN ident AS i ON i.oidref = b.oid AND i.id LIKE 'Gaia DR3 %' "
     "WHERE b.oid IN (SELECT oidref FROM otypes WHERE otype IN ('Pu*','Pu?')) AND b.oid IN (SELECT oidref FROM otypes WHERE otype IN ('WD*','WD?'))")
cols, rows = tap(q)
print("rows", len(rows))
with open('lists/puls_simbad.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['source', 'oid', 'name', 'ra', 'dec', 'pmra', 'pmdec', 'otype', 'sp_type', 'gaia_dr3'])
    for r in rows:
        g = r[8].replace('Gaia DR3 ', '') if r[8] else ''
        w.writerow(['SIMBAD_WD+Pu'] + r[:8] + [g])
import collections
print(collections.Counter(r[6] for r in rows)); print(sum(1 for r in rows if r[8]), 'with Gaia DR3 id')
sp = collections.Counter((r[7] or '')[:3] for r in rows); print(sp.most_common(30))

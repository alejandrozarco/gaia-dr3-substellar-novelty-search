# SIMBAD classification of the 154 good matches (pany>0.5): ident join on 'Gaia DR3 <id>' plus a 5" cone fallback. Probe: HD 49798 must resolve.
import pyvo, numpy as np
from astropy.table import Table, join
t=Table.read('s01_culpan_x_dr2mg.ecsv'); g=t[(t['pany']>0.5)]
k=Table.read('s03_knownhsd_x_dr2mg.ecsv'); k=k[k['pany']>0.5]
ids=list(map(int,g['GaiaEDR3']))+list(map(int,k['GaiaEDR3']))
sim=pyvo.dal.TAPService('https://simbad.cds.unistra.fr/simbad/sim-tap')
probe=sim.run_sync("SELECT b.main_id,b.otype FROM ident i JOIN basic b ON i.oidref=b.oid WHERE i.id='Gaia DR3 5562023884304074240'").to_table()
print('probe',probe); assert len(probe)==1
up=Table({'gid':np.array(['Gaia DR3 %d'%i for i in ids])})
r=sim.run_sync("""SELECT u.gid, b.main_id, b.otype, b.sp_type, b.ra, b.dec, b.oid
 FROM TAP_UPLOAD.u AS u JOIN ident i ON i.id=u.gid JOIN basic b ON i.oidref=b.oid""",uploads={'u':up}).to_table()
print('ident hits',len(r),'of',len(ids))
r['GaiaEDR3']=[int(s.split()[-1]) for s in r['gid']]
# all otypes
ot=sim.run_sync("""SELECT u.gid, o.otype FROM TAP_UPLOAD.u AS u JOIN ident i ON i.id=u.gid JOIN otypes o ON o.oidref=i.oidref""",uploads={'u':up}).to_table()
d={}
for row in ot: d.setdefault(int(row['gid'].split()[-1]),set()).add(str(row['otype']))
r['all_otypes']=[','.join(sorted(d.get(i,[]))) for i in r['GaiaEDR3']]
nr=sim.run_sync("SELECT u.gid, COUNT(*) AS nref FROM TAP_UPLOAD.u AS u JOIN ident i ON i.id=u.gid JOIN has_ref h ON h.oidref=i.oidref GROUP BY u.gid",uploads={'u':up}).to_table()
dn={int(x['gid'].split()[-1]):int(x['nref']) for x in nr}
r['nref']=[dn.get(i,0) for i in r['GaiaEDR3']]
r.write('s04_simbad.ecsv',overwrite=True)
gg=join(g,r,keys='GaiaEDR3',join_type='left')
from collections import Counter
print(Counter([str(x) for x in gg['otype'].filled('NONE')]).most_common())
gg.write('s04_good154_simbad.ecsv',overwrite=True)

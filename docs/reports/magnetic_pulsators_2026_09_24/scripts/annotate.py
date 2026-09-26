# Assign a pulsation-claim strength to every pulsator-list row and rebuild lists/puls_master.csv
#   strong = explicit time-series pulsation detection published for that star (or curated compilation of such detections)
#   weak   = candidate / catalogue-derived variability label (Vincent+2020 table-1 candidates via SIMBAD, GCVS/ATLAS/ZTF-RRL/Gaia labels,
#            Guidry cZZ, Jestin ZTF classes, MWDD 'VAR' without periods, 'possible' detections)
#   none   = NOV / non-pulsating variable (spotted, EB, ZTF periods flagged as non-pulsators)
import re, os, sys, json, numpy as np, pandas as pd
os.chdir('/tmp/fanout/magpuls')
d = pd.read_csv('lists/puls_long.csv', dtype=str).fillna('')
# SIMBAD otype origins
so = pd.read_csv('raw/simbad_pu_origins.csv', dtype=str).fillna('')
ps = pd.read_csv('lists/puls_simbad.csv', dtype=str).fillna('')
orig = so.groupby('oidref')['bib'].apply(lambda x: ';'.join(sorted(set(v for v in x if v)))).to_dict()
name2oid = dict(zip(ps['name'], ps['oid']))
WEAK_SIMBAD = {'2020AJ....160..252V', '2017ARep...61...80S', '2003AstL...29..468S', '2018AJ....156..241H', '2022MNRAS.510.3575H', '2022yCat.1355....0G',
               '2022yCat.1358....0G', '2012A&A...548A..79A', '2009yCat....1.2025S', '2019MNRAS.486.4574R'}
# Guidry t6 rows whose weighted-mean period is the non-pulsator dagger
gt6 = pd.read_csv('raw/viz_J_ApJ_912_125_table6.csv', dtype=str).fillna('')
g6_nonpuls = set('WD ' + w for w, wmp in zip(gt6['WD'], gt6['WMP']) if wmp.strip() == '')
def strength(r):
    s, st = r.source, r.status.lower()
    if 'nov' in st or s.endswith('_NOV'): return 'none'
    if s == 'Guidry2021_t6' and r['name'] in g6_nonpuls: return 'none'
    if s == 'Guidry2021_t5': return {'zz ceti': 'strong', 'candidate zz ceti': 'weak'}.get(st, 'none')
    if s == 'Jestin2026': return 'none' if 'spotted' in st else 'weak'
    if s == 'SIMBAD_WD+Pu':
        bibs = set(orig.get(name2oid.get(r['name'], ''), '').split(';')) - {''}
        r['note'] = (r['note'] + ' origin=' + ';'.join(sorted(bibs)))
        return 'strong' if (bibs - WEAK_SIMBAD) else 'weak'
    if s == 'MWDD': return 'strong' if re.search(r'periods=[1-9]', r.status) else 'weak'
    if s == 'Vincent2020': return 'weak' if st == 'possible' else 'strong'
    if s == 'Romero2019' and 'possible' in st: return 'weak'
    if s == 'Huang2026': return 'strong'
    return 'strong'
notes = []
d['claim'] = ''
for i in d.index:
    r = d.loc[i].copy()
    d.at[i, 'claim'] = strength(r); d.at[i, 'note'] = r['note']
d.loc[(d.source == 'Guidry2021_t6') & (d.claim == 'none'), 'status'] = 'ZTF period, flagged non-pulsator (WMP dagger)'
d.to_csv('lists/puls_long.csv', index=False)
rank = {'strong': 2, 'weak': 1, 'none': 0}
g = d[d.gaia_dr3 != ''].groupby('gaia_dr3')
master = pd.DataFrame(dict(
    n_rows=g.size(), sources=g['source'].apply(lambda x: ';'.join(sorted(set(x)))),
    strong_sources=g.apply(lambda x: ';'.join(sorted(set(x.loc[x.claim == 'strong', 'source'])))),
    names=g['name'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:300]),
    pclass=g['pclass'].apply(lambda x: ';'.join(sorted(set(map(str, x))))),
    status=g['status'].apply(lambda x: ';'.join(sorted(set(map(str, x))))[:400]),
    notes=g['note'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:500]),
    claim=g['claim'].apply(lambda x: max(x, key=lambda v: rank[v]))))
master['pulsator_claim'] = master.claim != 'none'
master.to_csv('lists/puls_master.csv')
print(master.claim.value_counts().to_string())
print(d.groupby(['source', 'claim']).size().unstack(fill_value=0).to_string())

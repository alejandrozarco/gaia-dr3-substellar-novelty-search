# Stage 3: resolve every pulsator-list row to a Gaia DR3 source_id. Writes lists/puls_long.csv, lists/puls_master.csv, out/puls_unresolved.csv
import re, sys, os, io, json, time, requests, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
os.chdir('/tmp/fanout/magpuls')
import mwdd_local
from resolve import resolve_names, coord_to_gaia
from gaia_cone import gaia_q, cone
rows = json.load(open('raw/puls_rows_stage2.json'))
d = pd.DataFrame(rows)
d['gaia_dr3'] = ''; d['how'] = ''; d['sep'] = np.nan
log = open('out/resolve_puls.log', 'w')
# --- gaia3 direct
m = d.id_type == 'gaia3'
d.loc[m, 'gaia_dr3'] = d.loc[m, 'id_value']; d.loc[m, 'how'] = 'gaia3_given'
# --- TIC -> DR2 (TIC v8.2 via VizieR TAP) ; also keep TIC coordinates as fallback
tics = sorted(set(d.loc[d.id_type == 'tic', 'id_value']))
ticmap = {}
for k in range(0, len(tics), 300):
    q = 'SELECT TIC, GAIA, RAJ2000, DEJ2000, pmRA, pmDE FROM "IV/39/tic82" WHERE TIC IN (' + ','.join(tics[k:k + 300]) + ')'
    r = requests.post('https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync', data=dict(REQUEST='doQuery', LANG='ADQL', FORMAT='csv', QUERY=q), timeout=300)
    if r.status_code != 200: print('HOLE TIC query', r.status_code, file=log); continue
    t = pd.read_csv(io.StringIO(r.text), dtype=str)
    for _, x in t.iterrows(): ticmap[x['TIC']] = x
print('TIC resolved', len(ticmap), 'of', len(tics), file=log, flush=True)
for i in d.index[d.id_type == 'tic']:
    x = ticmap.get(d.at[i, 'id_value'])
    if x is None: d.at[i, 'how'] = 'TIC_not_found'; continue
    if isinstance(x['GAIA'], str) and x['GAIA'].strip():
        d.at[i, 'id_type'] = 'gaia2'; d.at[i, 'id_value'] = x['GAIA'].strip(); d.at[i, 'how'] = 'tic->'
    else:
        d.at[i, 'id_type'] = 'coord'; d.at[i, 'ra'] = float(x['RAJ2000']); d.at[i, 'dec'] = float(x['DEJ2000']); d.at[i, 'epoch'] = 2000.0; d.at[i, 'how'] = 'tic(noGaia)->'
# --- DR2 -> DR3
dr2 = sorted(set(d.loc[d.id_type == 'gaia2', 'id_value']) - {'', 'nan'})
map23 = {}
for k in range(0, len(dr2), 400):
    q = ('SELECT dr2_source_id, dr3_source_id, angular_distance, magnitude_difference FROM gaiadr3.dr2_neighbourhood WHERE dr2_source_id IN ('
         + ','.join(dr2[k:k + 400]) + ')')
    try:
        cols, rr = gaia_q(q, timeout=300)
    except Exception as e:
        print('HOLE dr2_neighbourhood', e, file=log); continue
    for a, b, ang, dm in rr:
        a = str(a); b = str(b)
        sc = ang + (0 if dm is None else 500 * abs(dm))
        if a not in map23 or sc < map23[a][1]: map23[a] = (b, sc, ang)
print('DR2->DR3 mapped', len(map23), 'of', len(dr2), file=log, flush=True)
for i in d.index[d.id_type == 'gaia2']:
    x = map23.get(d.at[i, 'id_value'])
    if x: d.at[i, 'gaia_dr3'] = x[0]; d.at[i, 'how'] += 'dr2->dr3'; d.at[i, 'sep'] = x[2]
    else: d.at[i, 'how'] += 'dr2_unmapped'
# --- coordinates
for i in d.index[d.id_type == 'coord']:
    ra, dec, ep = d.at[i, 'ra'], d.at[i, 'dec'], d.at[i, 'epoch']
    if ra is None or (isinstance(ra, float) and np.isnan(ra)): d.at[i, 'how'] += 'no_coords'; continue
    maxsep = 3.0 if d.at[i, 'source'] in ('VSX', 'Gianninas2005', 'Gianninas2011') else 2.0
    g, how, s = coord_to_gaia(float(ra), float(dec), float(ep), maxsep)
    d.at[i, 'gaia_dr3'] = g or ''; d.at[i, 'how'] += how; d.at[i, 'sep'] = s if s is not None else np.nan
print('coords done', file=log, flush=True)
# --- short J names (Jhhmm+ddmm): MWDD allnames token match
mw = mwdd_local.load()
tok = {}
for j, an in zip(mw.index, mw['allnames'].fillna('')):
    for t in an.split(';'):
        t = t.strip()
        if re.fullmatch(r'J\d{4}[+\-]\d{4}', t): tok.setdefault(t, []).append(j)
for i in d.index[d.id_type == 'shortJ']:
    n = d.at[i, 'id_value'].replace('−', '-')
    if not re.fullmatch(r'J\d{4}[+\-]\d{4}', n): d.at[i, 'how'] = 'junk_name'; continue
    c = tok.get(n, [])
    if len(c) == 1: d.at[i, 'gaia_dr3'] = mw.at[c[0], 'gaia']; d.at[i, 'how'] = 'mwdd_shortname'
    else: d.at[i, 'how'] = f'shortname_ambiguous({len(c)})'
# --- names
def cleanname(n):
    n = n.strip().strip('()').replace('WDJ ', 'WD J').replace('SDSSJ', 'SDSS J').replace('WDJ', 'WD J')
    n = re.sub(r'\(\*\)$', '', n).strip(); n = n.split('=')[0].split('/')[0].strip()
    n = n.replace('HL Tau76', 'HL Tau 76').replace('SDSS 124949', 'SDSS J124949')
    return n
nm = d.index[d.id_type == 'name']
names = sorted({cleanname(x) for x in d.loc[nm, 'id_value'] if not x.startswith('\\') and len(x) < 60})
res = resolve_names(names)
json.dump(res, open('raw/puls_name_resolution.json', 'w'), default=str, indent=0)
for i in nm:
    n = d.at[i, 'id_value']
    if n.startswith('\\') or len(n) >= 60: d.at[i, 'how'] = 'junk_name'; continue
    r = res.get(cleanname(n), {})
    d.at[i, 'gaia_dr3'] = r.get('gaia') or ''; d.at[i, 'how'] = 'name:' + str(r.get('how')); d.at[i, 'sep'] = r.get('sep') if r.get('sep') is not None else np.nan
d['gaia_dr3'] = d['gaia_dr3'].fillna('').astype(str).replace({'nan': '', 'None': ''})
d.to_csv('lists/puls_long.csv', index=False)
un = d[(d.gaia_dr3 == '') & (d.how != 'junk_name')]
un.to_csv('out/puls_unresolved.csv', index=False)
print('rows', len(d), 'resolved', (d.gaia_dr3 != '').sum(), 'unresolved(non-junk)', len(un), file=log)
print(un.groupby('source').size().to_string(), file=log)
# --- master per Gaia DR3 id
g = d[d.gaia_dr3 != ''].groupby('gaia_dr3')
master = pd.DataFrame(dict(
    n_rows=g.size(), sources=g['source'].apply(lambda x: ';'.join(sorted(set(x)))),
    names=g['name'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:300]),
    pclass=g['pclass'].apply(lambda x: ';'.join(sorted(set(map(str, x))))),
    status=g['status'].apply(lambda x: ';'.join(sorted(set(map(str, x))))[:300]),
    notes=g['note'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:300])))
# a row counts as "pulsator claim" unless all its rows are NOV/non-variable/other-variable/spotted
def is_puls(sts, srcs):
    s = sts.lower()
    parts = [p for p in sts.split(';')]
    nonpuls = all(('nov' in p.lower()) or ('other variable' in p.lower()) or ('spotted' in p.lower()) for p in parts)
    return not nonpuls
master['pulsator_claim'] = [is_puls(s, r) for s, r in zip(master.status, master.sources)]
master.to_csv('lists/puls_master.csv')
print('master objects', len(master), 'with pulsator claim', master.pulsator_claim.sum(), file=log)
log.close()
print(open('out/resolve_puls.log').read())

# Second pass for unresolved pulsator rows: approximate coordinates (Bognar&Sodor 2016 1-arcsec/1-s precision, Gaia cone 25"),
# alias fixes, J-name typos, Jewett short names (pick the massive one among the MWDD candidates), extras (Antunes Amaral+2025, Yang 2026).
import re, sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts'); os.chdir('/tmp/fanout/magpuls')
from astropy.coordinates import SkyCoord; import astropy.units as u
import mwdd_local
from gaia_cone import cone, gaia_q
from resolve import resolve_names
d = pd.read_csv('lists/puls_long.csv', dtype=str).fillna('')
log = open('out/fix_unresolved.log', 'w')
def approx(rastr, destr, G=None, rad=25.0):
    c = SkyCoord(rastr, destr, unit=(u.hourangle, u.deg))
    q = (f"SELECT source_id, ra, dec, phot_g_mean_mag, parallax, bp_rp FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec), "
         f"CIRCLE('ICRS',{c.ra.deg},{c.dec.deg},{rad/3600.})) AND parallax > 2 AND bp_rp < 0.6")
    cols, rows = gaia_q(q)
    return rows
approx_coords = {'WD 0507+045': ('05 10 14', '+04 38 55'), 'HS 0507+0435': ('05 10 14', '+04 38 55'), 'PG 1149+057': ('11 51 54', '+05 28 40'),
                 '(J1218+0042)': ('12 18 31', '+00 42 16'), 'WD J1218+0042': ('12 18 31', '+00 42 16'), '(1310-0159)': ('13 10 08', '-01 59 56'),
                 'WD 1310-0159': ('13 10 08', '-01 59 56'), '(J1337+0104)': ('13 37 14', '+01 04 44'), 'WD J1337+0104': ('13 37 14', '+01 04 44'),
                 'PG 1541+650': ('15 41 45', '+64 53 53'), '(KISJ1945+4455)': ('19 45 42', '+44 55 11'), 'KIS J1945+4455': ('19 45 42', '+44 55 11')}
fixed = 0
for i in d.index[(d.gaia_dr3 == '') & (d.how != 'junk_name')]:
    n = d.at[i, 'name'].strip(); idv = d.at[i, 'id_value'].strip()
    key = n if n in approx_coords else (idv if idv in approx_coords else None)
    if key:
        rows = approx(*approx_coords[key])
        print(n, 'approx cone candidates', rows, file=log)
        if len(rows) == 1:
            d.at[i, 'gaia_dr3'] = str(rows[0][0]); d.at[i, 'how'] = 'approx_coord_unique(25")'; fixed += 1
        continue
print('approx fixed', fixed, file=log, flush=True)
# name aliases
alias = {'HE 1429-037': 'HE 1429-0343', 'WD 1345-0055': 'SDSS J134550.93-005536.5', 'WD 0232-097A': 'SDSS J023520.02-093456.3', '0232-097A': 'SDSS J023520.02-093456.3',
         'PSR J1738+0333': 'PSR J1738+0333', 'PSR J173853.96+033310.8': 'PSR J1738+0333', 'KIC 9164561(*)': 'KIC 9164561',
         'SDSS J161412.28+191219.4(*)': 'SDSS J161431.28+191219.4'}
todo = {i: alias[d.at[i, 'id_value'].strip()] for i in d.index[(d.gaia_dr3 == '')] if d.at[i, 'id_value'].strip() in alias}
res = resolve_names(sorted(set(todo.values())))
for i, a in todo.items():
    r = res.get(a, {})
    if r.get('gaia'): d.at[i, 'gaia_dr3'] = r['gaia']; d.at[i, 'how'] = 'alias:' + a + ':' + str(r.get('how'))
print('aliases', {a: res.get(a, {}).get('gaia') for a in set(todo.values())}, file=log, flush=True)
# J-name rows still unresolved: try Gaia cone 5" (typo-tolerant only if unique WD-like source)
for i in d.index[(d.gaia_dr3 == '') & (d.id_type == 'name')]:
    n = d.at[i, 'id_value'].replace('(*)', '')
    m = re.search(r'J(\d{2})(\d{2})(\d{2}\.?\d*)([+\-])(\d{2})(\d{2})(\d{2}\.?\d*)', n)
    if not m: continue
    ra = f'{m.group(1)} {m.group(2)} {m.group(3)}'; de = f'{m.group(4)}{m.group(5)} {m.group(6)} {m.group(7)}'
    rows = approx(ra, de, rad=6.0)
    print(n, 'Jname 6" WD-like candidates', rows, file=log)
    if len(rows) == 1: d.at[i, 'gaia_dr3'] = str(rows[0][0]); d.at[i, 'how'] = 'jname_cone6_unique'
# Jewett short names: MWDD candidates sharing the token -> take the one with mass > 0.85 (the paper's sample is M > 0.9)
mw = mwdd_local.load()
tok = {}
for j, an in zip(mw.index, mw['allnames'].fillna('')):
    for t in an.split(';'):
        t = t.strip()
        if re.fullmatch(r'J\d{4}[+\-]\d{4}', t): tok.setdefault(t, []).append(j)
for i in d.index[(d.gaia_dr3 == '') & (d.id_type == 'shortJ')]:
    c = tok.get(d.at[i, 'id_value'], [])
    cand = [(mw.at[j, 'gaia'], mw.at[j, 'mass'], mw.at[j, 'wdid'], mw.at[j, 'G']) for j in c]
    heavy = [x for x in cand if x[1] == x[1] and x[1] > 0.85]
    print(d.at[i, 'id_value'], cand, file=log)
    gids = sorted(set(x[0] for x in heavy))
    if len(gids) == 1: d.at[i, 'gaia_dr3'] = gids[0]; d.at[i, 'how'] = 'mwdd_shortname_massive'
# extras (not in the stage-2 parse): Antunes Amaral+2025 (3 new pulsators; DR2 ids in source comments), Yang+2026 WFST ZZ Ceti
extras = [('AntunesAmaral2025', '2025A&A...694A.246A', 'SDSS J212935.23+001332.3', 'gaia2', '2687768066863960576', 'ELMV', 'new pulsator'),
          ('AntunesAmaral2025', '2025A&A...694A.246A', 'SDSS J001245.60+143956.4', 'gaia2', '2768409887481718272', 'lowmass DAV', 'new pulsator'),
          ('AntunesAmaral2025', '2025A&A...694A.246A', 'SDSS J090559.60+084324.9', 'gaia2', '591112504953277440', 'DAV', 'new pulsator'),
          ('Yang2026', '2026RAA....26d5008Y', 'J053009.62+594557.0', 'name', 'J053009.62+594557.0', 'DAV', 'new ZZ Ceti (WFST)')]
ex = []
for src, bib, n, t, v, cls, st in extras:
    g = ''
    if t == 'gaia2':
        cols, rr = gaia_q(f'SELECT dr3_source_id, angular_distance FROM gaiadr3.dr2_neighbourhood WHERE dr2_source_id = {v} ORDER BY angular_distance')
        g = str(rr[0][0]) if rr else ''
    else:
        r = resolve_names([n]).get(n, {}); g = r.get('gaia') or ''
    ex.append(dict(source=src, bib=bib, name=n, id_type=t, id_value=v, ra='', dec='', epoch='', pclass=cls, status=st, note='', gaia_dr3=g, how='extra', sep=''))
d = pd.concat([d, pd.DataFrame(ex)], ignore_index=True)
d.to_csv('lists/puls_long.csv', index=False)
un = d[(d.gaia_dr3 == '') & (d.how != 'junk_name')]
un.to_csv('out/puls_unresolved.csv', index=False)
print('after fix: rows', len(d), 'resolved', (d.gaia_dr3 != '').sum(), 'unresolved(non-junk)', len(un), file=log)
print(un[['source', 'name', 'how']].to_string(), file=log)
# rebuild master
g = d[d.gaia_dr3 != ''].groupby('gaia_dr3')
master = pd.DataFrame(dict(
    n_rows=g.size(), sources=g['source'].apply(lambda x: ';'.join(sorted(set(x)))),
    names=g['name'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:300]),
    pclass=g['pclass'].apply(lambda x: ';'.join(sorted(set(map(str, x))))),
    status=g['status'].apply(lambda x: ';'.join(sorted(set(map(str, x))))[:400]),
    notes=g['note'].apply(lambda x: ' | '.join(sorted(set(map(str, x))))[:400])))
def is_puls(sts):
    parts = sts.split(';')
    return not all(('nov' in p.lower()) or ('other variable' in p.lower()) or ('spotted' in p.lower()) for p in parts)
master['pulsator_claim'] = [is_puls(s) for s in master.status]
master.to_csv('lists/puls_master.csv')
print('master objects', len(master), 'with pulsator claim', master.pulsator_claim.sum(), file=log)
log.close(); print(open('out/fix_unresolved.log').read())

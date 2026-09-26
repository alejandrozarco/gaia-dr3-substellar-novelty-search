# Assemble published pulsating-WD lists into one long table (lists/puls_long.csv) and a per-object master (lists/puls_master.csv).
# Every source row is kept with its resolution method; unresolved rows are kept (gaia_dr3 empty) and counted, never dropped.
# Run: nice -n 10 python scripts/build_puls.py
import re, sys, os, io, json, time, csv, requests, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
import mwdd_local
from resolve import resolve_names, coord_to_gaia, jcoord
from gaia_cone import gaia_q
os.chdir('/tmp/fanout/magpuls')
ARX = 'arx/'
rows = []   # dicts: source, bib, name, id_type (gaia3/gaia2/tic/name/coord), id_value, ra, dec, epoch, pclass, status, note
def add(source, bib, name, id_type, id_value, pclass, status, ra=None, dec=None, epoch=2000.0, note=''):
    rows.append(dict(source=source, bib=bib, name=name, id_type=id_type, id_value=str(id_value) if id_value is not None else '',
                     ra=ra, dec=dec, epoch=epoch, pclass=pclass, status=status, note=note))
def clean(s):
    s = s.replace('$-$', '-').replace('$+$', '+').replace('$\\pm$', '').replace('$', '').replace('~', ' ').replace('\\,', '')
    s = re.sub(r'\\(textit|textbf|it|bf|emph)\s*', '', s); s = s.replace('{', '').replace('}', '').replace('\\\\', '')
    s = s.replace('\\ross\\', '').strip()
    return re.sub(r'\s+', ' ', s).strip()
def tex_rows(path, a, b):
    L = open(path, errors='ignore').read().split('\n')[a - 1:b]
    L = [re.sub(r'(?<!\\)%.*$', '', l.replace('\\\\%', '\\\\ %')) for l in L]
    txt = ' '.join(L)
    out = []
    for r in re.split(r'\\\\', txt):
        cells = [re.sub(r'\\hline|\\noalign\{[^}]*\}|\\smallskip', ' ', c).strip() for c in r.split('&')]
        if len(cells) >= 2: out.append(cells)
    return out
def first_int(s):
    m = re.search(r'\b(\d{5,19})\b', s); return m.group(1) if m else None

# ---------------- 1. SIMBAD WD + Pu (already queried) ----------------
d = pd.read_csv('lists/puls_simbad.csv', dtype=str)
for _, r in d.iterrows():
    add('SIMBAD_WD+Pu', 'SIMBAD 2026-09-23', r['name'], 'gaia3' if isinstance(r['gaia_dr3'], str) else 'coord',
        r['gaia_dr3'] if isinstance(r['gaia_dr3'], str) else '', 'WDpuls', 'otype Pu*/Pu?', ra=float(r['ra']), dec=float(r['dec']), epoch=2000.0,
        note=f"otype={r['otype']} sp={r['sp_type']}")
# ---------------- 2. MWDD number_periods>0 or variability==VAR/NOV ----------------
m = mwdd_local.load()
for _, r in m[(m.nper > 0) | (m['var'] == 'VAR')].iterrows():
    add('MWDD', 'MWDD table.json 2026-08-05', r['wdid'] or r['name'], 'gaia3', r['gaia'], 'WDvar',
        ('periods=%d' % r['nper']) + (' VAR' if r['var'] == 'VAR' else ''), note=f"spectype={r['spectype']}")
# ---------------- 3. VSX ZZ types ----------------
v = pd.read_csv('raw/vsx_zz.csv')
for _, r in v.iterrows():
    add('VSX', 'VizieR B/vsx', r['Name'], 'coord', '', 'VSX:' + str(r['Type']), 'VSX type', ra=r['RAJ2000'], dec=r['DEJ2000'], epoch=2000.0,
        note=f"P={r['Period']} Sp={r['Sp']}")
# ---------------- 4. Vincent+2020 table3 (new ZZ Ceti + possible) ----------------
t = pd.read_csv('raw/viz_J_AJ_160_252_table3.csv', dtype=str)
for _, r in t.iterrows():
    st = 'possible' if r['f_WD'] == '*' else 'new ZZ Ceti'
    add('Vincent2020', '2020AJ....160..252V', 'J' + r['WD'].lstrip('J'), 'gaia2', r['Gaia'], 'DAV', st, note=f"P={r['Per']}s amp={r['Ampl']}% FAP={r['l_FAP'] or ''}{r['FAP']}")
t4 = pd.read_csv('raw/viz_J_AJ_160_252_table4.csv', dtype=str)
for _, r in t4.iterrows():
    add('Vincent2020_NOV', '2020AJ....160..252V', 'J' + r['WD'].lstrip('J'), 'gaia2', r['Gaia'], 'DA', 'NOV (table4)', note=f"Pstrip={r['Pstrip']}")
# ---------------- 5. Guidry+2021 ----------------
t5 = pd.read_csv('raw/viz_J_ApJ_912_125_table5.csv', dtype=str)
for _, r in t5.iterrows():
    g2 = r['SimbadName'].replace('Gaia DR2 ', '') if isinstance(r['SimbadName'], str) else ''
    add('Guidry2021_t5', '2021ApJ...912..125G', 'WD ' + r['WD'], 'gaia2', g2, 'Guidry:' + r['Class'],
        {'ZZ': 'ZZ Ceti', 'cZZ': 'candidate ZZ Ceti'}.get(r['Class'], 'other variable'), note=f"Class={r['Class']} Teff={r['Teff']}")
t6 = pd.read_csv('raw/viz_J_ApJ_912_125_table6.csv', dtype=str)
for _, r in t6.iterrows():
    g2 = r['SimbadName'].replace('Gaia DR2 ', '') if isinstance(r['SimbadName'], str) else ''
    add('Guidry2021_t6', '2021ApJ...912..125G', 'WD ' + r['WD'], 'gaia2', g2, 'DAV', 'confirmed ZZ Ceti (t6)', note=f"Per={r['Per']}")
# ---------------- 6. Hermes+2017 K2 DAVs ----------------
h = pd.read_csv('raw/viz_J_ApJS_232_23_targets.csv', dtype=str)
for _, r in h.iterrows():
    from astropy.coordinates import SkyCoord; import astropy.units as u
    cc = SkyCoord(str(r['RAJ2000']), str(r['DEJ2000']), unit=(u.hourangle, u.deg))
    add('Hermes2017', '2017ApJS..232...23H', r['ID'] + ' ' + str(r['AName']), 'coord', '', 'DAV', 'K2 DAV', ra=cc.ra.deg, dec=cc.dec.deg)
# ---------------- 7. TMTS ZZ Cetis (Guo+2024) ----------------
z = pd.read_csv('raw/viz_J_MNRAS_528_6997_zz.csv', dtype=str)
for _, r in z.iterrows():
    add('TMTS_Guo2024', '2024MNRAS.528.6997G', r['Name'], 'coord', '', 'DAV', 'TMTS ZZ', ra=float(r['RAJ2000']), dec=float(r['DEJ2000']))
# ---------------- 8. Romero+2022 (TIC) ----------------
for c in tex_rows(ARX + '2201.04158/NewTess.tex', 171, 290):
    if re.fullmatch(r'\d{5,10}', c[0].strip()):
        add('Romero2022', '2022MNRAS.511.1574R', 'TIC ' + c[0].strip(), 'tic', c[0].strip(), 'DAV', 'new ZZ Ceti (TESS)')
# ---------------- 9. Romero+2025 (TIC) ----------------
for c in tex_rows(ARX + '2407.07260/NewTESS.tex', 74, 160):
    if re.fullmatch(r'\d{5,10}', c[0].strip()):
        st = 'new ZZ Ceti (TESS)' if 'new' in c[-1] else 'ZZ Ceti (R22, re-observed)'
        add('Romero2025', '2025ApJ...984..112R', 'TIC ' + c[0].strip().lstrip('0'), 'tic', c[0].strip().lstrip('0'), 'DAV', st)
# ---------------- 10. Bognar+2020/2023/2024 (TIC) ----------------
for path, a, b, bib, st in [('2003.11481/18DAVs.tex', 158, 200, '2020A&A...638A..82B', 'known ZZ Ceti (TESS P01)'),
                            ('2305.05246/45177corr.tex', 118, 170, '2023A&A...674A.204B', 'known ZZ Ceti (TESS P02)')]:
    for c in tex_rows(ARX + path, a, b):
        if len(c) > 2 and re.fullmatch(r'\d{6,10}', c[1].strip()):
            add('Bognar' + bib[:4], bib, clean(c[0]), 'tic', c[1].strip().lstrip('0'), 'DAV', st)
for c in tex_rows(ARX + '2402.09869/rotation.tex', 285, 320):
    if len(c) > 3 and re.fullmatch(r'\d{15,19}', c[2].strip()):
        add('Bognar2024', '2024A&A...684A..76B', clean(c[0]) + ' TIC' + c[1].strip(), 'gaia3', c[2].strip(), 'DAV', 'ZZ Ceti w/ rotation multiplets')
# ---------------- 11. Romero+2019 (names) ----------------
rom19 = [('SDSS J082804.63+094956.6', 'new ZZ Ceti'), ('SDSS J094929.09+101918.8', 'new ZZ Ceti'), ('GD 195', 'new ZZ Ceti'), ('L 495-82', 'new ZZ Ceti'),
         ('BPM 30551', 'known ZZ Ceti'), ('SDSS J092511.63+050932.6', 'known ZZ Ceti'), ('HS 1249+0426', 'known ZZ Ceti'), ('WD 1345-0055', 'known ZZ Ceti'),
         ('HE 1429-037', 'known ZZ Ceti'), ('SDSS J161218.08+083028.1', 'known ZZ Ceti'), ('GD 385', 'known ZZ Ceti'), ('SDSS J215905.53+132255.8', 'known ZZ Ceti'),
         ('SDSS J221458.37-002511.9', 'known ZZ Ceti'), ('SDSS J235040.72-005430.9', 'known ZZ Ceti'),
         ('LP 375-51', 'possible variable (3-4 sigma)'), ('SDSS J095703.09+080504.8', 'possible variable (3-4 sigma)'),
         ('SDSS J212441.27-073234.9', 'possible variable (3-4 sigma)'), ('SDSS J213159.88+010856.3', 'possible variable (3-4 sigma)')]
for n, st in rom19: add('Romero2019', '2019MNRAS.490.1803R', n, 'name', n, 'DAV', st)
# ---------------- 12. Jewett+2025 massive DAVs ----------------
jw = {}
for c in tex_rows(ARX + '2510.09802/pulsator_follow_up.tex', 209, 243):
    if len(c) > 2 and re.fullmatch(r'\d{15,19}', c[1].strip()): jw[clean(c[0])] = c[1].strip()
puls_j25 = []; nov_j25 = []
for c in tex_rows(ARX + '2510.09802/pulsator_follow_up.tex', 912, 936):
    if len(c) >= 6: puls_j25.append((clean(c[0]), clean(c[2]))); nov_j25.append((clean(c[3]), clean(c[5])))
extra_j25 = {'J0049-2525': 'WD J004917.14-252556.81', 'BPM 37093': 'BPM 37093', 'GD 518': 'GD 518'}
for n, ref in puls_j25:
    if n in jw: add('Jewett2025', '2025ApJ...994..255J', n, 'gaia3', jw[n], 'DAV(massive)', 'pulsator (' + ref + ')')
    else: add('Jewett2025', '2025ApJ...994..255J', n, 'name' if n in extra_j25 else 'shortJ', extra_j25.get(n, n), 'DAV(massive)', 'pulsator (' + ref + ')')
for n, ref in nov_j25:
    if n in jw: add('Jewett2025_NOV', '2025ApJ...994..255J', n, 'gaia3', jw[n], 'DA(massive)', 'NOV (' + ref + ')')
    else: add('Jewett2025_NOV', '2025ApJ...994..255J', n, 'shortJ', n, 'DA(massive)', 'NOV (' + ref + ')')
# ---------------- 13. Corsico+2019 review tables ----------------
for (a, b, cls) in [(927, 1258, 'DAV'), (1411, 1468, 'DBV'), (1546, 1580, 'ELMV'), (1627, 1670, 'preELMV'), (1796, 1824, 'DQV'), (2697, 2715, 'hotDAV')]:
    for c in tex_rows(ARX + '1907.00115/paper.tex', a, b):
        n = clean(c[0])
        if not n or n.lower().startswith(('name', 'star')) or 'hline' in n or 'noalign' in n: continue
        n = re.sub(r'^.*\\hline\s*', '', n).replace('\\noalign smallskip', '').replace('noalign smallskip', '').strip()
        if len(n) < 3: continue
        add('Corsico2019', '2019A&ARv..27....7C', n, 'name', n, cls, 'review list', note=clean(c[-1]) if cls == 'DQV' else '')
# ---------------- 14. Vanderbosch+2022 DBVs ----------------
vt = open(ARX + '2201.09893/main.tex', errors='ignore').read().split('\n')
for (a, b, st) in [(153, 210, 'new DBV'), (212, 262, 'known DBV (ref list)')]:
    for c in tex_rows(ARX + '2201.09893/main.tex', a, b):
        for cc in (c[0], c[5] if len(c) > 5 else ''):
            n = clean(cc)
            if re.search(r'J\d{4}', n) or re.search(r'^(GD|PG|EC|KUV|CBS|WD|HS|KIC|EPIC|TIC|SDSS|Gaia|PB|BPM|L|G)\b', n):
                add('Vanderbosch2022', '2022ApJ...927..158V', n, 'name', n, 'DBV', st)
print('rows so far', len(rows), flush=True)
json.dump(rows, open('raw/puls_rows_stage1.json', 'w'), default=str)

# ======================= stage 2 sources =======================
# ---------------- 15. Gianninas+2005, +2011 ZZ Cetis ----------------
g5 = pd.read_csv('raw/viz_J_ApJ_631_1100_tables.csv', dtype=str)
for _, r in g5[g5['Class'] == 'ZZ'].iterrows():
    add('Gianninas2005', '2005ApJ...631.1100G', r['Name'], 'coord', '', 'DAV', 'ZZ (G05)', ra=float(r['_RA']), dec=float(r['_DE']))
g11 = pd.read_csv('raw/viz_J_ApJ_743_138_table5.csv', dtype=str)
for _, r in g11[g11['Notes'].fillna('').str.split().apply(lambda x: '3' in x)].iterrows():
    add('Gianninas2011', '2011ApJ...743..138G', 'WD ' + r['WD'] + ' ' + str(r['OName']), 'coord', '', 'DAV', 'ZZ Ceti (G11 note 3)', ra=float(r['_RA']), dec=float(r['_DE']))
# ---------------- 16. Jestin+2026 (Gaia DR3 variable WDs vetted by ZTF) ----------------
je = pd.read_csv('raw/viz_J_A+A_712_A243_tablea1.csv', dtype=str)
for _, r in je[je['Class'].isin(['ZZ_Ceti', 'V777_Her', 'Unknown_type', 'Spotted_variables'])].iterrows():
    add('Jestin2026', '2026A&A...712A.243J', r['WDJname'], 'gaia3', r['GaiaDR3'], 'Jestin:' + r['Class'],
        {'ZZ_Ceti': 'ZZ Ceti candidate (ZTF)', 'V777_Her': 'V777 Her candidate (ZTF)', 'Unknown_type': 'GW Vir? candidate (ZTF)', 'Spotted_variables': 'spotted variable (ZTF)'}[r['Class']],
        note=f"Freq={r['Freq']}/d note={r['Note']}")
# ---------------- 17. H-deficient TESS series + ELMV + misc (TIC / Gaia) ----------------
for path, a, b, bib, cls in [('2011.03629/paper-dov-tess-lp.tex', 285, 295, '2021A&A...645A.117C', 'GWVir'),
                             ('2204.02501/mnras_template.tex', 222, 228, '2022MNRAS.513.2285U', 'GWVir'),
                             ('2210.05486/paper-dbv-tess-lp.tex', 313, 322, '2022A&A...668A.161C', 'DBV')]:
    for c in tex_rows(ARX + path, a, b):
        t_ = c[0].strip().lstrip('0')
        if re.fullmatch(r'\d{5,10}', t_): add('TESS_Hdef', bib, clean(c[1]), 'tic', t_, cls, 'TESS pulsator')
add('TESS_Hdef', '2024A&A...686A.140C', 'NGC 246', 'tic', '3905338', 'GWVir', 'TESS pulsator')
for c in tex_rows(ARX + '2607.02720/Unveiling_ELMVs_i.tex', 555, 570):
    if len(c) > 2 and re.fullmatch(r'\d{15,19}', c[1].strip()):
        add('Calcaferro2026', '2026A&A...713A.106C', clean(c[0]), 'gaia3', c[1].strip(), 'ELMV', 'ELMV (TESS)')
add('Kilic2023', '2023MNRAS.522.2181K', 'WD J004917.14-252556.81', 'name', 'WD J004917.14-252556.81', 'DAV(massive)', 'pulsator')
for n, ra, de, st in [('WD 1258+013', '13:01:10.52', '+01:07:40.05', 'known'), ('WD 1401-147', '14:03:57.11', '-15:01:09.63', 'known'),
                      ('WD 1625+125', '16:28:13.25', '+12:24:51.11', 'known'), ('WD 2246-069', '22:48:40.04', '-06:42:45.27', 'new'),
                      ('WD 2254+126', '22:56:46.16', '+12:52:49.62', 'known')]:
    from astropy.coordinates import SkyCoord; import astropy.units as u
    cc = SkyCoord(ra, de, unit=(u.hourangle, u.deg))
    add('Tucker2018', '2018MNRAS.475.4768T', n, 'coord', '', 'DAV', st + ' DAV (gPhoton)', ra=cc.ra.deg, dec=cc.dec.deg)
for c in tex_rows(ARX + '2605.03323/main.tex', 606, 662):
    t_ = c[0].strip()
    if re.fullmatch(r'\d{5,10}', t_): add('Huang2026', '2026ApJS..284...72H', 'TIC ' + t_, 'tic', t_, 'WDosc', 'TESS WD oscillator', note=f"f={c[2].strip()}/d A={c[3].strip()}ppt {clean(c[4]) if len(c) > 4 else ''}")
# ---------------- 18. Bognar & Sodor 2016 period tables (names) ----------------
for tf, cls in [('table1.txt', 'DAV(WD+MS)'), ('table2.txt', 'ELMV'), ('table3.txt', 'hotDAV'), ('table4.txt', 'DAV')]:
    for line in open(ARX + '1610.07470/' + tf, errors='ignore'):
        if line.startswith('#') or not line.strip(): continue
        m_ = re.search(r'(\d{2}) (\d{2}) (\d{2})\s+([+\-]?\d{2}) (\d{2}) (\d{2})', line)
        if not m_: continue
        pre = line[:m_.start()]
        toks = [t.strip() for t in pre.split('\t') if t.strip() and t.strip() not in ('--',)]
        if not toks: continue
        other = [t for t in toks if re.search(r'[A-Za-z]', t) and not t.startswith('(')]
        wdnum = [t for t in toks if re.fullmatch(r'\d{4}[+\-]\d{3}[A-Z]?', t)]
        name = other[0] if other else ('WD ' + wdnum[0] if wdnum else toks[0])
        add('Bognar2016', '2016IBVS.6184....1B', name, 'name', name, cls, 'period table', note='WD ' + wdnum[0] if wdnum else '')
print('rows after stage 2', len(rows), flush=True)
json.dump(rows, open('raw/puls_rows_stage2.json', 'w'), default=str)

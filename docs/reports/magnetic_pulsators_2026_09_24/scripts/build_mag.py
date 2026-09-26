# Assemble structured magnetic-WD lists into lists/mag_long.csv
# columns: source, bib, name, gaia3, gaia2, ra, dec, epoch_lo, epoch_hi (epoch range of the coordinates), field, sptype, note
import re, sys, os, io, json, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts'); os.chdir('/tmp/fanout/magpuls')
import mwdd_local
from simbad_tap import tap
rows = []
def add(source, bib, name, gaia3='', gaia2='', ra=np.nan, dec=np.nan, ep=(2000.0, 2000.0), field='', sptype='', note=''):
    rows.append(dict(source=source, bib=bib, name=str(name), gaia3=str(gaia3 or '').strip(), gaia2=str(gaia2 or '').strip(), ra=ra, dec=dec,
                     epoch_lo=ep[0], epoch_hi=ep[1], field=str(field), sptype=str(sptype), note=str(note)))
SDSS_EP = (1998.0, 2010.0)   # SDSS-I/II name coordinates are at the observation epoch
def is_mag_type(s):
    """magnetic WD spectral type? (H or P after the leading D, once non-magnetic tokens are removed)"""
    if not isinstance(s, str): return False
    t = s.strip()
    if not t.startswith('D'): return False
    if re.search(r'sd[BOA]|He-sd|PG ?1159|CSPN|PN|BHB|CV', t): return False
    t = t.replace('DAHe', 'DAH').replace('DAHE', 'DAH')
    t = re.sub(r'He-|-He|\(He\)|UHE|VERYHOT|_HOT|HOT|[Hh]ot|PEC|pec|_\(HALPHA\)|Phot[\d.]*|C2H|He', '', t)
    return any(ch in 'HP' for ch in t[1:])
# sanity tests of the type filter
for s, exp in [('DAH', 1), ('DAH:', 1), ('DBAH:', 1), ('DZH', 1), ('DCP', 1), ('DAP', 1), ('DAHe', 1), ('DAHE', 1), ('DH', 1), ('DXP', 1), ('DQpecP', 1),
               ('He-sdO', 0), ('DA-He', 0), ('DA(He)', 0), ('DC_VERYHOT', 0), ('HotDC', 0), ('DQHOT', 0), ('DQPEC', 0), ('PG1159', 0), ('DA', 0),
               ('DAO', 0), ('DA_(HALPHA)', 0), ('DQAPhot2.7', 0), ('CV-H', 0), ('DA+DAXP', 1), ('DAHM:', 1), ('DC-PEC', 0), ('DZH-PEC', 1)]:
    assert is_mag_type(s) == bool(exp), (s, is_mag_type(s))
# 1. MWDD
m = mwdd_local.load()
for _, r in m.iterrows():
    mt = is_mag_type(r['spectype']); im = r['ismag'] == 'yes'
    if mt or im:
        add('MWDD', 'MWDD 2026-08-05', r['wdid'] or r['name'], gaia3=r['gaia'], ra=r['ra'], dec=r['dec'], ep=(2016.0, 2016.0), sptype=r['spectype'],
            note=('ismag ' if im else '') + ('magtype' if mt else ''))
print('MWDD', len(rows), flush=True)
# 2. SIMBAD sp_type (WD otypes)
cols, rr = tap("SELECT b.main_id, b.ra, b.dec, b.sp_type, b.otype, i.id FROM basic AS b LEFT JOIN ident AS i ON i.oidref = b.oid AND i.id LIKE 'Gaia DR3 %' "
               "WHERE b.sp_type LIKE 'D%' AND (b.sp_type LIKE '%H%' OR b.sp_type LIKE '%P%')")
n0 = len(rows)
for mid, ra, dec, sp, ot, gid in rr:
    if is_mag_type(sp): add('SIMBAD_sptype', 'SIMBAD 2026-09-23', mid, gaia3=(gid or '').replace('Gaia DR3 ', ''), ra=ra, dec=dec, sptype=sp, note=f'otype={ot}')
print('SIMBAD', len(rows) - n0, 'of', len(rr), flush=True)
# 3. VizieR catalogues
def vz(f): return pd.read_csv('raw/' + f, low_memory=False, dtype=str)
for _, r in vz('viz_J_MNRAS_429_2934_table1.csv').iterrows():
    add('Kepler2013', '2013MNRAS.429.2934K', 'SDSS J' + r['SDSS'], ra=float(r['_RA']), dec=float(r['_DE']), ep=SDSS_EP, field=r['BHa'], sptype='DAH')
for _, r in vz('viz_J_A+A_506_1341_table3.csv').iterrows():
    add('Kulebi2009', '2009A&A...506.1341K', 'SDSS ' + r['MWD'], ra=float(r['_RA']), dec=float(r['_DE']), ep=SDSS_EP, field=r['Bp'])
for _, r in vz('viz_J_AJ_130_734_catalog.csv').iterrows():
    add('Vanlandingham2005', '2005AJ....130..734V', 'SDSS ' + r['SDSS'], ra=float(r['_RA']), dec=float(r['_DE']), ep=SDSS_EP, field=r['Bp'], note=str(r['Com']))
for _, r in vz('viz_J_ApJ_944_56_table1.csv').iterrows():
    add('Amorim2023', '2023ApJ...944...56A', 'SDSS ' + r['SDSS'], ra=float(r['_RA']), dec=float(r['_DE']), ep=SDSS_EP, field=r['B'])
h = vz('viz_J_MNRAS_520_6111_tablea1.csv')
for _, r in h.iterrows():
    if r['T5'] == '*' or r['T6'] == '*':
        add('Hardy2023', '2023MNRAS.520.6111H', r['Name'] + ' ' + str(r['MWDD']), gaia2=r['GaiaDR2'], ra=float(r['RAJ2000']), dec=float(r['DEJ2000']), ep=(2000.0, 2016.0))
for _, r in vz('viz_J_A+A_711_A70_catalog.csv').iterrows():
    if r['ObsType'] in ('Magnetic', 'DAH') or (isinstance(r['ObsSubtype'], str) and is_mag_type(r['ObsSubtype'].replace('hot ', ''))) or isinstance(r['B'], str):
        add('GarciaZamora2026', '2026A&A...711A..70G', r['Name'], gaia3=r['GaiaDR3'], ra=float(r['RA_ICRS']), dec=float(r['DE_ICRS']), ep=(2016.0, 2016.0),
            field=r['B'], sptype=f"{r['ObsType']}/{r['ObsSubtype']}")
b22 = vz('viz_J_ApJ_935_L12_table2.csv')
for _, r in b22.iterrows():
    try: B = float(r['B'])
    except: B = 0.0
    if B > 0 or is_mag_type(r['SpT']):
        add('Bagnulo2022', '2022ApJ...935L..12B', r['Name'] + ' ' + str(r['SName']), ra=float(r['_RA']), dec=float(r['_DE']), ep=(2000.0, 2000.0), field=r['B'], sptype=r['SpT'])
for _, r in vz('viz_J_MNRAS_499_1890_tablea1.csv').iterrows():
    if r['Magnetic'] == '*':
        add('McCleery2020', '2020MNRAS.499.1890M', r['WDJ'], gaia3=r['GaiaEDR3'], ra=float(r['RA_ICRS']), dec=float(r['DE_ICRS']), ep=(2016.0, 2016.0), sptype=r['SpType'])
for _, r in vz('viz_J_MNRAS_518_3055_table3.csv').iterrows():
    if r['B'] == '*' or is_mag_type(r['SpType']):
        g = str(r['SimbadName']).replace('Gaia DR3 ', '') if 'Gaia DR3' in str(r['SimbadName']) else ''
        add('OBrien2023', '2023MNRAS.518.3055O', r['Name'], gaia3=g, ra=float(r['RAJ2000']), dec=float(r['DEJ2000']), ep=(2000.0, 2000.0), sptype=r['SpType'])
ob = vz('viz_J_MNRAS_527_8687_tablea1.csv')
for _, r in ob.iterrows():
    if is_mag_type(r['SpType']):
        add('OBrien2024', '2024MNRAS.527.8687O', r['Name'], gaia3=r['GaiaDR3'], ra=float(r['RA_ICRS']), dec=float(r['DE_ICRS']), ep=(2016.0, 2016.0), sptype=r['SpType'])
kv = vz('viz_J_MNRAS_425_1394_stars.csv')
for _, r in kv.iterrows():
    try: sig = abs(float(r['Bl'])) / float(r['e_Bl'])
    except: sig = np.nan
    if (sig == sig and sig > 3) or (isinstance(r['n_WD'], str) and r['n_WD'].strip() in ('b', 'd', 'f')):
        add('KawkaVennes2012', '2012MNRAS.425.1394K', 'WD ' + r['WD'] + ' ' + r['Name'], ra=float(r['_RA']), dec=float(r['_DE']), ep=(2000.0, 2000.0),
            field=f"Bl={r['Bl']}+-{r['e_Bl']}kG", note=f"n_WD={r['n_WD']} (uncertain flag meaning)")
for _, r in vz('viz_J_ApJ_743_138_table3.csv').iterrows():
    add('Gianninas2011_mag', '2011ApJ...743..138G', 'WD ' + r['WD'] + ' ' + r['OName'], ra=float(r['_RA']), dec=float(r['_DE']), ep=(2000.0, 2000.0), field=r['Bp'])
g11 = vz('viz_J_ApJ_743_138_table5.csv')
for _, r in g11[g11['Notes'].fillna('').str.split().apply(lambda x: '5' in x)].iterrows():
    add('Gianninas2011_mag', '2011ApJ...743..138G', 'WD ' + r['WD'] + ' ' + str(r['OName']), ra=float(r['_RA']), dec=float(r['_DE']), ep=(2000.0, 2000.0), note='table5 note 5 (magnetic, non-magnetic fit)')
# SDSS WD catalogues (Kleinman 2013; Kepler 2015, 2016, 2019, 2021) and Kilic 2020
k13 = vz('viz_J_ApJS_204_5_table2.csv')
for _, r in k13.iterrows():
    if is_mag_type(r['Type']):
        add('Kleinman2013', '2013ApJS..204....5K', 'SDSS J' + str(r['SDSS']), ra=float(r['RAJ2000']), dec=float(r['DEJ2000']), ep=SDSS_EP, sptype=r['Type'])
for f, col, bib, src in [('viz_J_MNRAS_446_4078_table6.csv', 'Type', '2015MNRAS.446.4078K', 'Kepler2015'), ('viz_J_MNRAS_455_3413_table6.csv', 'SpType', '2016MNRAS.455.3413K', 'Kepler2016'),
                         ('viz_J_MNRAS_455_3413_table7.csv', 'SpType', '2016MNRAS.455.3413K', 'Kepler2016'), ('viz_J_MNRAS_486_2169_table2.csv', 'Type', '2019MNRAS.486.2169K', 'Kepler2019')]:
    for _, r in vz(f).iterrows():
        if is_mag_type(r[col]):
            nm = r.get('SDSS', r.get('SDSSJ', ''))
            add(src, bib, 'SDSS J' + str(nm), ra=float(r['_RA']), dec=float(r['_DE']), ep=SDSS_EP, sptype=r[col])
for _, r in vz('viz_J_MNRAS_507_4646_table2.csv').iterrows():
    if is_mag_type(r['Type']):
        add('Kepler2021', '2021MNRAS.507.4646K', r['Name'], ra=float(r['_RA_icrs']), dec=float(r['_DE_icrs']), ep=(2016.0, 2016.0), sptype=r['Type'])
kp = vz('viz_J_ApJ_898_84_param.csv')
for _, r in kp.iterrows():
    if is_mag_type(r['Type']):
        add('Kilic2020', '2020ApJ...898...84K', r['ID'], gaia2=r['Gaia'], sptype=r['Type'])
print('after VizieR', len(rows), flush=True)
# 4. DESI DR1 lists
a = pd.read_csv('/tmp/mwd/desi/DESI_CLASS_FINAL.txt', sep=r'\s+', low_memory=False, dtype=str)
for _, r in a.iterrows():
    if is_mag_type(str(r['CLASS'])):
        add('DESI_Amorim2026', 'Amorim+2026 (arXiv:2607.00430)', r['#Name'], gaia3=r['edr3id'], ra=float(r['RA(deg)']), dec=float(r['DEC(deg)']), ep=(2016.0, 2016.0), sptype=r['CLASS'])
s = pd.read_csv('/tmp/mwd/desi/swan_cat.csv.gz', low_memory=False, dtype=str)
for _, r in s.iterrows():
    if is_mag_type(str(r['specType'])):
        add('DESI_Swan2026', 'Swan+2026 (arXiv:2603.20487?)', r['WDJname'], gaia3=str(r['designation']).replace('Gaia DR3 ', ''), sptype=r['specType'], note=f"conf={r['specType_confidence']}")
# 5. today's new magnetic DAs (27)
ns = pd.read_csv('/tmp/mwd/report/novelty_summary.csv', dtype=str)
for _, r in ns[ns.verdict == 'NO_MAGNETIC_LABEL'].iterrows():
    add('Today27', 'this project 2026-09-23', r['simbad_name'], gaia3=r['gaia_dr3'], field=r['B_Ha_MG'], sptype='DAH (SDSS-V Zeeman)')
for g in ['4198738558061020928', '5807585134758743040', '50526755482496000', '2833867392391927936', '4241409569220727424']:
    add('Today27', 'this project 2026-09-23 (second look)', 'Gaia DR3 ' + g, gaia3=g, sptype='DAH (SDSS-V Zeeman, second look)')
d = pd.DataFrame(rows)
for c in ('gaia3', 'gaia2'):
    d[c] = d[c].replace({'nan': '', 'None': ''}).fillna('')
    d[c] = d[c].apply(lambda x: x.split('.')[0] if re.fullmatch(r'\d+\.0', x) else x)
d.to_csv('lists/mag_long.csv', index=False)
print(d.groupby('source').size().to_string())
print('total rows', len(d), 'with gaia3', (d.gaia3 != '').sum(), 'gaia2 only', ((d.gaia3 == '') & (d.gaia2 != '')).sum(), 'coords only', ((d.gaia3 == '') & (d.gaia2 == '')).sum())

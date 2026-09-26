# Cross-match pulsator master (Gaia DR3) against the structured magnetic lists (id + PM-propagated position).
# Writes raw/puls_gaia_astrometry.csv, out/overlaps_long.csv, out/overlaps_by_object.csv
import re, sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts'); os.chdir('/tmp/fanout/magpuls')
from gaia_cone import gaia_q
P = pd.read_csv('lists/puls_master.csv', dtype={'gaia_dr3': str})
ids = sorted(set(P.gaia_dr3))
# --- Gaia DR3 astrometry for all pulsator ids
if not os.path.exists('raw/puls_gaia_astrometry.csv'):
    out = []
    for k in range(0, len(ids), 400):
        c, r = gaia_q('SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, bp_rp FROM gaiadr3.gaia_source WHERE source_id IN (' + ','.join(ids[k:k + 400]) + ')', timeout=300)
        out += r
    A = pd.DataFrame(out, columns=c); A['source_id'] = A.source_id.astype(str)
    # DR2 ids for each DR3 pulsator
    d2 = []
    for k in range(0, len(ids), 400):
        c2, r2 = gaia_q('SELECT dr3_source_id, dr2_source_id, angular_distance FROM gaiadr3.dr2_neighbourhood WHERE dr3_source_id IN (' + ','.join(ids[k:k + 400]) + ')', timeout=300)
        d2 += r2
    D2 = pd.DataFrame(d2, columns=['dr3', 'dr2', 'ang']).astype({'dr3': str, 'dr2': str})
    A = A.merge(D2.groupby('dr3')['dr2'].apply(lambda x: ';'.join(sorted(set(x)))).rename('dr2_ids'), left_on='source_id', right_index=True, how='left')
    A.to_csv('raw/puls_gaia_astrometry.csv', index=False)
A = pd.read_csv('raw/puls_gaia_astrometry.csv', dtype={'source_id': str, 'dr2_ids': str})
print('pulsator ids', len(ids), 'with Gaia astrometry', len(A), flush=True)
missing = sorted(set(ids) - set(A.source_id)); print('ids not in gaia_source (bad ids?)', missing[:20])
dr2map = {}
for s, d2 in zip(A.source_id, A.dr2_ids.fillna('')):
    for x in d2.split(';'):
        if x: dr2map.setdefault(x, set()).add(s)
pos_ra = A.ra.values; pos_de = A.dec.values; pmra = A.pmra.fillna(0).values; pmde = A.pmdec.fillna(0).values
M = pd.read_csv('lists/mag_long.csv', dtype=str)
for c in ('ra', 'dec', 'epoch_lo', 'epoch_hi'): M[c] = pd.to_numeric(M[c], errors='coerce')
idset = set(A.source_id)
hits = []
for i, r in M.iterrows():
    matched = set(); how = []
    if r.gaia3 and r.gaia3 in idset: matched.add(r.gaia3); how.append('gaia3')
    if r.gaia2 and r.gaia2 in dr2map: matched |= dr2map[r.gaia2]; how.append('gaia2')
    if r.ra == r.ra and r.dec == r.dec:
        cosd = np.cos(np.radians(r.dec))
        near = np.where((np.abs(pos_de - r.dec) < 0.02) & (np.abs((pos_ra - r.ra + 180) % 360 - 180) * cosd < 0.02))[0]
        for j in near:
            best = 1e9
            for ep in np.linspace(r.epoch_lo, r.epoch_hi, 7):
                dt = ep - 2016.0
                rae = pos_ra[j] + pmra[j] * dt / 3.6e6 / np.cos(np.radians(pos_de[j])); dee = pos_de[j] + pmde[j] * dt / 3.6e6
                s = np.hypot(((rae - r.ra + 180) % 360 - 180) * cosd, dee - r.dec) * 3600
                best = min(best, s)
            tol = 3.0 if r.epoch_hi - r.epoch_lo > 1 else 2.0
            if best < tol: matched.add(A.source_id.iloc[j]); how.append(f'pos{best:.2f}"')
    for g in matched:
        hits.append(dict(gaia_dr3=g, mag_source=r.source, mag_bib=r.bib, mag_name=r['name'], mag_field=r.field, mag_sptype=r.sptype, mag_note=r.note, how=';'.join(how)))
H = pd.DataFrame(hits).fillna('').astype(str)
H.to_csv('out/overlaps_long.csv', index=False)
if len(H):
    g = H.groupby('gaia_dr3')
    O = pd.DataFrame(dict(n_mag_rows=g.size(), mag_sources=g.mag_source.apply(lambda x: ';'.join(sorted(set(x)))),
                          mag_types=g.mag_sptype.apply(lambda x: ';'.join(sorted(set(v for v in x if v and v != 'nan')))),
                          mag_fields=g.mag_field.apply(lambda x: ';'.join(sorted(set(v for v in x if v and v != 'nan'))))))
    O = O.join(P.set_index('gaia_dr3')[['sources', 'names', 'pclass', 'status', 'pulsator_claim', 'notes']], how='left')
    O = O.join(A.set_index('source_id')[['ra', 'dec', 'phot_g_mean_mag', 'bp_rp', 'parallax']], how='left')
    O.to_csv('out/overlaps_by_object.csv')
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 500)
    print(len(O), 'overlap objects'); print(O[['mag_sources', 'mag_types', 'sources', 'status']].to_string())

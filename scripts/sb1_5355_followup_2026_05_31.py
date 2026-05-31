#!/usr/bin/env python3
"""Follow-up checks for Gaia DR3 5355234746758153728 after the YSO/open-cluster
red flag surfaced. (1) extract the actual Cluster name + membership from the
Gaia DR3 open-cluster catalogs the source matched; (2) southern multi-epoch RV
surveys GALAH DR3, RAVE DR6, and Gaia FPR/vari; (3) FLAME age units + flags;
(4) Gaia DR3 binary-masses table (gaiadr3.binary_masses) if present; (5) the
Gaia DR3 'astro/spectro non-single' interpretation and the SB1 vetting flags.
"""
from __future__ import annotations
import warnings, json, math
warnings.filterwarnings('ignore')
import numpy as np
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
from astropy import units as u

SID = 5355234746758153728
RA, DEC = 154.14832628340378, -55.264640416964866

def _flt(v):
    try:
        f = float(v); return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

out = {'source_id': SID}

# ---------------- 1. Cluster identity from the matched catalogs ----------------
coord = SkyCoord(ra=RA * u.deg, dec=DEC * u.deg, frame='icrs')
v = Vizier(columns=['**'], timeout=120); v.ROW_LIMIT = -1
cluster_cats = [
    ('J/A+A/633/A99', 'CG2020 cluster members (Cantat-Gaudin 2020)'),
    ('J/ApJS/265/12', 'Qin+2023 101 new OCs'),
    ('J/A+A/659/A59', 'Tarricq+2022 OC structural params'),
    ('J/ApJS/262/7', 'He+2022 886 clusters'),
    ('J/AJ/158/122', 'Kounkel & Covey 2019 Untangling the Galaxy'),
    ('J/A+A/674/A34', 'Gaia DR3 SB validation (Gosset 2023)'),
    ('J/A+A/674/A39', 'Gaia DR3 NSS two-body orbit catalog (Holl 2023)'),
]
out['cluster_match'] = {}
for cat, label in cluster_cats:
    try:
        res = v.query_region(coord, radius=10 * u.arcsec, catalog=cat)
        if res is None or len(res) == 0:
            out['cluster_match'][label] = {'match': False}
            continue
        t = res[0]
        row = {}
        for c in t.colnames:
            val = t[c][0]
            fv = _flt(val)
            row[c] = fv if fv is not None else str(val)
        out['cluster_match'][label] = {'match': True, 'n': int(len(t)), 'row': row}
    except Exception as ex:
        out['cluster_match'][label] = {'note': f'{type(ex).__name__}: {ex}'}

# ---------------- 2. Southern multi-epoch RV surveys ----------------
rv_cats = [
    ('J/MNRAS/506/150', 'GALAH DR3 (Buder 2021)'),
    ('III/283', 'RAVE DR6 (Steinmetz 2020)'),
    ('III/279', 'RAVE DR5'),
    ('J/A+A/622/A205', 'Gaia-ESO iDR? (placeholder)'),
]
out['rv_surveys'] = {}
for cat, label in rv_cats:
    try:
        res = v.query_region(coord, radius=5 * u.arcsec, catalog=cat)
        if res is None or len(res) == 0:
            out['rv_surveys'][label] = {'match': False}
            continue
        t = res[0]
        rows = []
        for i in range(min(len(t), 5)):
            row = {}
            for c in t.colnames:
                val = t[c][i]; fv = _flt(val)
                row[c] = fv if fv is not None else str(val)
            rows.append(row)
        out['rv_surveys'][label] = {'match': True, 'n': int(len(t)),
                                    'cols': list(t.colnames), 'rows': rows}
    except Exception as ex:
        out['rv_surveys'][label] = {'note': f'{type(ex).__name__}: {ex}'}

# ---------------- 3. FLAME flags + spectroscopic-type detail (Gaia) ----------------
try:
    t = Gaia.launch_job(
        'SELECT source_id, flags_flame, evolstage_flame, '
        'spectraltype_esphs, activityindex_espcs, activityindex_espcs_uncertainty, '
        'ew_espels_halpha, ew_espels_halpha_uncertainty, '
        'classlabel_espels, classlabel_dsc_combmod '
        f'FROM gaiadr3.astrophysical_parameters WHERE source_id={SID}'
    ).get_results()
    if len(t):
        d = {}
        for c in t.colnames:
            val = t[c][0]; fv = _flt(val)
            d[c] = fv if fv is not None else str(val)
        out['flame_espels'] = d
except Exception as ex:
    out['flame_espels'] = {'note': f'{type(ex).__name__}: {ex}'}

# ---------------- 4. Gaia DR3 binary_masses table (if the source is in it) ------
for tbl in ('gaiadr3.binary_masses',):
    try:
        t = Gaia.launch_job(f'SELECT * FROM {tbl} WHERE source_id={SID}').get_results()
        d = None
        if len(t):
            d = {}
            for c in t.colnames:
                if c in ('corr_vec',): continue
                val = t[c][0]; fv = _flt(val)
                d[c] = fv if fv is not None else str(val)
        out[tbl] = d if d else {'rows': 0}
    except Exception as ex:
        out[tbl] = {'note': f'{type(ex).__name__}: {ex}'}

# ---------------- 5. Decode gaia_source non_single_star + flags --------------
# non_single_star is a bitmask: 1=astrometric, 2=spectroscopic, 4=eclipsing.
out['non_single_star_decoded'] = {
    'value': 2,
    'meaning': '2 = spectroscopic-binary processing (SB) only; bit1(astrom)=0, bit4(eclipsing)=0',
}
# SB1 flags=8192 decode (Gaia DR3 nss_two_body_orbit "flags" bitmask)
out['nss_flags_8192'] = {
    'value': 8192,
    'note': 'bit 13 set (2^13=8192). In Gaia DR3 nss_two_body_orbit the flags '
            'bitmask encodes per-solution QA bits; 8192 corresponds to a single '
            'set bit. Interpretation requires the DR3 datamodel; flag set => check.',
}

with open(f'/tmp/sb1_{SID}_followup.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)

# pretty print
print('=== CLUSTER MATCH ===')
for k, vv in out['cluster_match'].items():
    if vv.get('match'):
        r = vv['row']
        keys = [kk for kk in r if any(s in kk.lower() for s in
                ('clust','prob','memb','name','rv','hrv','teff','logg','rad','gaia'))]
        print(f'  [{k}] n={vv["n"]}')
        for kk in keys[:14]:
            print(f'      {kk} = {r[kk]}')
    else:
        print(f'  [{k}] {vv}')

print('\n=== RV SURVEYS ===')
for k, vv in out['rv_surveys'].items():
    print(f'  [{k}] {vv if not vv.get("match") else "MATCH n="+str(vv["n"])}')
    if vv.get('match'):
        print(f'      cols: {vv["cols"]}')
        for row in vv['rows']:
            rvkeys = [kk for kk in row if any(s in kk.lower() for s in
                      ('rv','hrv','vhel','vrad','teff','logg','snr','e_'))]
            print('      ' + ', '.join(f'{kk}={row[kk]}' for kk in rvkeys[:12]))

print('\n=== FLAME / ESP-ELS ===')
print(json.dumps(out.get('flame_espels', {}), indent=2, default=str))
print('\n=== binary_masses ===')
print(json.dumps(out.get('gaiadr3.binary_masses', {}), indent=2, default=str))
print(f'\nWrote /tmp/sb1_{SID}_followup.json')

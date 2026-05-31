#!/usr/bin/env python3
"""Leaner, timeout-guarded follow-up for Gaia DR3 5355234746758153728.
Each external query is wrapped in a SIGALRM hard timeout so nothing hangs.
Focus: (a) cluster name + membership prob, (b) FLAME age/evolstage detail,
(c) GALAH DR3 / RAVE DR6 presence, (d) ESP-ELS Halpha emission class.
"""
from __future__ import annotations
import warnings, json, math, signal
warnings.filterwarnings('ignore')
import numpy as np
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u

SID = 5355234746758153728
RA, DEC = 154.14832628340378, -55.264640416964866
coord = SkyCoord(ra=RA * u.deg, dec=DEC * u.deg, frame='icrs')

class _TO(Exception):
    pass

def _alarm(sig, frm):
    raise _TO()

signal.signal(signal.SIGALRM, _alarm)

def guarded(fn, secs=45, default=None):
    signal.alarm(secs)
    try:
        return fn()
    except _TO:
        return {'_timeout': secs}
    except Exception as ex:
        return {'_err': f'{type(ex).__name__}: {ex}'}
    finally:
        signal.alarm(0)

def _flt(v):
    try:
        f = float(v); return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

def _rowdict(t, i=0):
    d = {}
    for c in t.colnames:
        val = t[c][i]; fv = _flt(val)
        d[c] = fv if fv is not None else str(val)
    return d

out = {'source_id': SID}

# ---- (a) cluster name + membership ----
def q_cg2020():
    v = Vizier(columns=['**'], timeout=40); v.ROW_LIMIT = 50
    res = v.query_region(coord, radius=15 * u.arcsec, catalog='J/A+A/633/A99')
    if not res or len(res) == 0:
        return {'match': False}
    return {'match': True, 'cols': list(res[0].colnames), 'row': _rowdict(res[0])}
out['CG2020'] = guarded(q_cg2020, 50)

def q_kc2019():
    # Kounkel & Covey 2019 string theory groups; the source's bibcode cites it
    v = Vizier(columns=['**'], timeout=40); v.ROW_LIMIT = 50
    res = v.query_region(coord, radius=15 * u.arcsec, catalog='J/AJ/158/122')
    if not res or len(res) == 0:
        return {'match': False}
    return {'match': True, 'cols': list(res[0].colnames), 'row': _rowdict(res[0])}
out['KC2019'] = guarded(q_kc2019, 50)

# ---- (b) FLAME age / evolstage / spectroscopic classes (Gaia TAP, fast) ----
def q_ap_extra():
    t = Gaia.launch_job(
        'SELECT source_id, age_flame, age_flame_lower, age_flame_upper, '
        'mass_flame, mass_flame_lower, mass_flame_upper, '
        'evolstage_flame, flags_flame, spectraltype_esphs, '
        'ew_espels_halpha, ew_espels_halpha_uncertainty, ew_espels_halpha_flag, '
        'classlabel_espels, classlabel_espels_flag, '
        'classlabel_dsc_combmod, '
        'teff_esphs, logg_esphs, vsini_esphs, ag_esphs '
        f'FROM gaiadr3.astrophysical_parameters WHERE source_id={SID}'
    ).get_results()
    return _rowdict(t) if len(t) else {'rows': 0}
out['ap_extra'] = guarded(q_ap_extra, 50)

# ---- (c) GALAH DR3 + RAVE DR6 presence (via Gaia-hosted xmatch is unreliable; use Vizier with tight timeout) ----
def q_galah():
    v = Vizier(columns=['GaiaDR3', 'RV', 'e_RV', 'Teff', 'logg', 'snr_c2',
                        'flag_sp', 'flag_fe_h', 'fe_h', 'vbroad', 'alpha_fe'],
               timeout=35); v.ROW_LIMIT = 10
    res = v.query_region(coord, radius=5 * u.arcsec, catalog='J/MNRAS/506/150/main')
    if not res or len(res) == 0:
        return {'match': False}
    return {'match': True, 'n': int(len(res[0])), 'rows': [_rowdict(res[0], i) for i in range(min(len(res[0]), 5))]}
out['GALAH_DR3'] = guarded(q_galah, 40)

def q_rave():
    v = Vizier(columns=['**'], timeout=35); v.ROW_LIMIT = 10
    res = v.query_region(coord, radius=5 * u.arcsec, catalog='III/283')
    if not res or len(res) == 0:
        return {'match': False}
    return {'match': True, 'n': int(len(res[0])), 'cols': list(res[0].colnames),
            'rows': [_rowdict(res[0], i) for i in range(min(len(res[0]), 3))]}
out['RAVE_DR6'] = guarded(q_rave, 40)

# ---- (d) full SIMBAD measurement set (distances, membership otypes) ----
def q_simbad_full():
    s = Simbad()
    try:
        s.add_votable_fields('otypes', 'sp_type', 'plx_value', 'rvz_radvel',
                             'rvz_err', 'V', 'fe_h')
    except Exception:
        pass
    r = s.query_object(f'Gaia DR3 {SID}')
    if r is None or len(r) == 0:
        return {'match': False}
    d = {}
    for c in r.colnames:
        val = r[c][0]; fv = _flt(val)
        d[c] = fv if fv is not None else str(val)
    return d
out['simbad_full'] = guarded(q_simbad_full, 40)

with open(f'/tmp/sb1_{SID}_followup2.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)

print('=== CG2020 cluster membership ===')
print(json.dumps(out['CG2020'], indent=2, default=str)[:1500])
print('\n=== Kounkel-Covey 2019 ===')
print(json.dumps(out['KC2019'], indent=2, default=str)[:1200])
print('\n=== FLAME age / ESP-ELS Halpha / classes ===')
print(json.dumps(out['ap_extra'], indent=2, default=str))
print('\n=== GALAH DR3 ===')
print(json.dumps(out['GALAH_DR3'], indent=2, default=str)[:1500])
print('\n=== RAVE DR6 ===')
print(json.dumps(out['RAVE_DR6'], indent=2, default=str)[:1500])
print('\n=== SIMBAD full ===')
print(json.dumps(out['simbad_full'], indent=2, default=str))
print(f'\nWrote /tmp/sb1_{SID}_followup2.json')

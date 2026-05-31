#!/usr/bin/env python3
"""Skeptical deep-dive of spectroscopic dormant-compact candidate
Gaia DR3 5355234746758153728.

Reported (caller): nss_two_body_orbit SB1, P=211.0359 d, e=0.1016,
K1=32.065 km/s, f(M)=0.7097 Msun, M2_min=1.845 Msun.

This is a PURE SPECTROSCOPIC orbit (nss_two_body_orbit SB1) -- NO Thiele-Innes
astrometry, so there is NO astrometric inclination. M2 is f(M)+M1 with sin i
UNCONSTRAINED (i=90 gives the MINIMUM M2). The LB-1 / HR 6819 failure mode is
exactly the danger here: a single-lined spectroscopic mass function looks like
a heavy dark companion, but a second (faint, broad, or stripped) star or a Be
decretion disk can masquerade. So the priorities are:

  1. CONFIRM SINGLE-LINED. Pull the actual Gaia DR3 nss_two_body_orbit solution
     parameters and any external multi-epoch RVs (APOGEE DR17, LAMOST MRS/LRS,
     GALAH, RAVE via Vizier). Check Gaia RVS for double lines / CCF flags. Look
     for SB2 (second RV set) or emission (Be / stripped helium star).
  2. PRIMARY CLASS. Teff, logg, abs G mag, BP-RP -- MS dwarf vs giant vs sdO/B
     stripped He star. A stripped subdwarf primary fakes a high f(M).
  3. RECOMPUTE M2 from f(M)+M1 (FLAME M1, fallback isochrone/colour). No
     astrometric inclination available -> report M2_min (i=90) + the MC over
     random-i prior so the reader sees the inclination penalty.
  4. K1 RELIABILITY: epoch count (rv_n_obs / rv_nb_transits), goodness_of_fit,
     significance, eccentricity error, efficiency. Is 211 d a real orbit or an
     alias / sampling artifact?

Classify: dark_compact / ambiguous / refuted.
Outputs: /tmp/sb1_5355234746758153728_*.json + report.
"""
from __future__ import annotations
import warnings, json, math
warnings.filterwarnings('ignore')
import numpy as np
from scipy import stats

from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u

AU_KM = 1.495978707e8
G_SI = 6.6743e-11
MSUN = 1.98892e30
GMSUN = 1.32712440018e20

SID = 5355234746758153728

def _flt(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

# --------------------------------------------------------------------------- #
# Gaia fetchers
# --------------------------------------------------------------------------- #
def _tab_to_dict(t):
    out = {}
    for c in t.colnames:
        if c in ('corr_vec', 'bit_index'):
            continue
        v = t[c][0]
        fv = _flt(v)
        if fv is not None:
            out[c] = fv
        else:
            try:
                masked = bool(np.ma.is_masked(v))
            except Exception:
                masked = False
            out[c] = None if masked else str(v)
    return out

def gaia_nss(sid):
    t = Gaia.launch_job(
        f'SELECT * FROM gaiadr3.nss_two_body_orbit WHERE source_id={sid}'
    ).get_results()
    return _tab_to_dict(t) if len(t) else None

def gaia_source(sid):
    cols = ('source_id, ra, dec, parallax, parallax_error, parallax_over_error, '
            'pmra, pmdec, ruwe, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, '
            'bp_rp, g_rp, bp_g, radial_velocity, radial_velocity_error, '
            'rv_nb_transits, rv_expected_sig_to_noise, rv_template_teff, '
            'rv_template_logg, rv_template_fe_h, vbroad, vbroad_error, '
            'phot_variable_flag, '
            'ipd_frac_multi_peak, ipd_frac_odd_win, ipd_gof_harmonic_amplitude, '
            'astrometric_excess_noise, astrometric_excess_noise_sig, '
            'visibility_periods_used, astrometric_n_good_obs_al, '
            'duplicated_source, non_single_star, '
            'l, b, teff_gspphot, logg_gspphot, mh_gspphot, distance_gspphot, '
            'ag_gspphot, ebpminrp_gspphot, in_qso_candidates, in_galaxy_candidates')
    t = Gaia.launch_job(
        f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={sid}'
    ).get_results()
    return _tab_to_dict(t) if len(t) else None

def gaia_ap(sid):
    t = Gaia.launch_job(
        'SELECT source_id, teff_gspphot, logg_gspphot, mh_gspphot, '
        'teff_gspspec, logg_gspspec, mh_gspspec, '
        'mass_flame, radius_flame, lum_flame, age_flame, '
        'mh_gspphot_lower, mh_gspphot_upper, '
        'teff_gspphot_lower, teff_gspphot_upper, '
        'logg_gspphot_lower, logg_gspphot_upper, '
        'spectraltype_esphs, activityindex_espcs, ew_espels_halpha, '
        'flags_flame, libname_gspphot '
        f'FROM gaiadr3.astrophysical_parameters WHERE source_id={sid}'
    ).get_results()
    return _tab_to_dict(t) if len(t) else None

def gaia_ap_supp(sid):
    try:
        t = Gaia.launch_job(
            'SELECT source_id, logg_gspspec_ann, teff_gspspec_ann, mh_gspspec_ann '
            f'FROM gaiadr3.astrophysical_parameters_supp WHERE source_id={sid}'
        ).get_results()
        return _tab_to_dict(t) if len(t) else None
    except Exception as e:
        return {'_err': f'{type(e).__name__}: {e}'}

# --------------------------------------------------------------------------- #
# Orbit math (pure spectroscopic SB1)
# --------------------------------------------------------------------------- #
def f_spec_msun(K1_kms, P_d, e):
    """Spectroscopic mass function from K1 (semi-amplitude), P, e."""
    if K1_kms is None or K1_kms <= 0 or P_d <= 0 or e >= 1:
        return None
    K = K1_kms * 1000.0
    P_s = P_d * 86400.0
    fM = P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G_SI)
    return fM / MSUN

def solve_m2_min(fM, M1):
    """M2 at sin i = 1 (minimum): M2^3/(M1+M2)^2 = fM."""
    lo, hi = 1e-5, 1e3
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

def solve_m2_at_sini(fM, M1, sini):
    """Solve M2 from f(M) = (M2 sin i)^3 / (M1+M2)^2 for a given sin i."""
    s3 = sini ** 3
    lo, hi = 1e-5, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        # (mid*sini)^3 / (M1+mid)^2 vs fM
        if (mid * sini) ** 3 / (M1 + mid) ** 2 > fM:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

# --------------------------------------------------------------------------- #
# SIMBAD + literature
# --------------------------------------------------------------------------- #
def simbad_otype_bibs(gaia_id_str):
    s = Simbad()
    for fields in (('otype', 'ids', 'sp_type', 'plx_value', 'V', 'rvz_radvel'),
                   ('otype', 'ids', 'sp_type', 'plx_value'),
                   ('otype', 'ids')):
        try:
            s.add_votable_fields(*fields)
            break
        except Exception:
            s = Simbad()
            continue
    out = {'query': gaia_id_str}
    try:
        r = s.query_object(gaia_id_str)
        if r is not None and len(r):
            cn = r.colnames
            out['main_id'] = str(r['main_id'][0]) if 'main_id' in cn else None
            out['otype'] = str(r['otype'][0]) if 'otype' in cn else None
            out['sp_type'] = str(r['sp_type'][0]) if 'sp_type' in cn else None
            out['ids'] = str(r['ids'][0]) if 'ids' in cn else None
            out['plx_value'] = _flt(r['plx_value'][0]) if 'plx_value' in cn else None
        else:
            out['main_id'] = None
    except Exception as e:
        out['_obj_err'] = f'{type(e).__name__}: {e}'
    q = (f"SELECT b.bibcode, b.journal, b.title FROM basic AS ba "
         f"JOIN ident AS i ON i.oidref = ba.oid "
         f"JOIN has_ref AS hr ON hr.oidref = ba.oid "
         f"JOIN ref AS b ON b.oidbib = hr.oidbibref "
         f"WHERE i.id = '{gaia_id_str}'")
    try:
        t = s.query_tap(q)
        bibs = [{'bibcode': str(row['bibcode']), 'journal': str(row['journal']),
                 'title': str(row['title'])[:100]} for row in t]
        out['n_bibcodes'] = len(bibs)
        out['bibcodes'] = bibs
    except Exception as e:
        out['_bib_err'] = f'{type(e).__name__}: {e}'
    return out

def lit_crossmatch(ra, dec):
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    rad = 5 * u.arcsec
    v = Vizier(columns=['**'], timeout=90)
    v.ROW_LIMIT = -1
    cats = [
        ('J/MNRAS/518/2991', 'Shahaf+2023 Triage I (compact-companion sample)'),
        ('J/MNRAS/529/3729', 'Shahaf+2024 Triage II (white-dwarf census)'),
        ('J/A+A/674/A9', 'Gaia DR3 NSS astrometric orbits (Halbwachs 2023)'),
        ('J/A+A/674/A34', 'Gaia DR3 SB orbits validation (Gosset 2023)'),
        ('III/279', 'APOGEE DR17 (allStar)'),
        ('V/156', 'APOGEE-2 / SDSS-IV'),
        ('J/ApJS/249/3', 'APOGEE DR16 stellar params'),
    ]
    out = {}
    for cat, label in cats:
        try:
            res = v.query_region(coord, radius=rad, catalog=cat)
            if res is None or len(res) == 0:
                out[label] = {'match': False}
            else:
                t = res[0]
                out[label] = {'match': True, 'n_rows': int(len(t)),
                              'cols': list(t.colnames)[:25]}
        except Exception as e:
            out[label] = {'match': None, 'note': f'{type(e).__name__}'}
    return out

# --------------------------------------------------------------------------- #
def run():
    rec = {'source_id': SID, 'reported': {
        'P_d': 211.0359, 'e': 0.1016, 'K1_kms': 32.065,
        'fM_msun': 0.7097, 'M2_min_msun': 1.845,
        'solution': 'nss_two_body_orbit SB1'}}

    print('=' * 78)
    print(f'GAIA DR3 {SID} -- spectroscopic SB1 deep-dive')
    print('=' * 78)

    nss = gaia_nss(SID)
    gs = gaia_source(SID)
    ap = gaia_ap(SID)
    aps = gaia_ap_supp(SID)
    rec['nss'] = nss
    rec['gaia_source'] = gs
    rec['ap'] = ap
    rec['ap_supp'] = aps

    if nss is None:
        print('!! NO nss_two_body_orbit row found for this source_id.')
    else:
        print('\n--- NSS solution ---')
        print(f"  nss_solution_type = {nss.get('nss_solution_type')}")
        for k in ('period', 'period_error', 'eccentricity', 'eccentricity_error',
                  'semi_amplitude_primary', 'semi_amplitude_primary_error',
                  'semi_amplitude_secondary', 'rv_amplitude_robust',
                  'center_of_mass_velocity', 'center_of_mass_velocity_error',
                  'mass_function', 'mass_function_error',
                  't_periastron', 't_periastron_error',
                  'arg_periastron', 'arg_periastron_error',
                  'goodness_of_fit', 'significance', 'efficiency',
                  'rv_n_obs_primary', 'rv_n_obs_secondary',
                  'flags', 'parallax', 'parallax_error',
                  'a_thiele_innes', 'c_thiele_innes', 'h_thiele_innes',
                  'eccentricity_min', 'eccentricity_max'):
            if k in (nss or {}):
                print(f"    {k:32s} = {nss.get(k)}")

    print('\n--- gaia_source ---')
    if gs:
        for k in ('ra', 'dec', 'parallax', 'parallax_over_error', 'ruwe',
                  'phot_g_mean_mag', 'bp_rp', 'radial_velocity',
                  'radial_velocity_error', 'rv_nb_transits',
                  'rv_expected_sig_to_noise', 'rv_template_teff',
                  'rv_template_logg', 'vbroad', 'vbroad_error',
                  'ipd_frac_multi_peak', 'astrometric_excess_noise_sig',
                  'non_single_star', 'phot_variable_flag',
                  'teff_gspphot', 'logg_gspphot', 'distance_gspphot',
                  'ag_gspphot'):
            print(f"    {k:32s} = {gs.get(k)}")

    print('\n--- astrophysical_parameters ---')
    if ap:
        for k in ('teff_gspphot', 'logg_gspphot', 'mh_gspphot',
                  'teff_gspspec', 'logg_gspspec', 'mh_gspspec',
                  'mass_flame', 'radius_flame', 'lum_flame', 'age_flame',
                  'spectraltype_esphs', 'ew_espels_halpha', 'libname_gspphot'):
            print(f"    {k:32s} = {ap.get(k)}")
    if aps:
        print(f"    logg_gspspec_ann (supp)         = {aps.get('logg_gspspec_ann')}")
        print(f"    teff_gspspec_ann (supp)         = {aps.get('teff_gspspec_ann')}")

    # --------- recompute orbit quantities ---------
    print('\n--- ORBIT RECOMPUTATION (independent) ---')
    P = nss.get('period') if nss else rec['reported']['P_d']
    e = nss.get('eccentricity') if nss else rec['reported']['e']
    K1_sap = nss.get('semi_amplitude_primary') if nss else None
    rvrob = nss.get('rv_amplitude_robust') if nss else None
    fM_gaia = nss.get('mass_function') if nss else None

    # K1 source: nss_two_body_orbit SB1 reports semi_amplitude_primary directly (km/s).
    K1_use = K1_sap if K1_sap else rec['reported']['K1_kms']
    K1_from_rvrob = (rvrob / 2.0) if rvrob else None  # Correction B sanity

    fM_recomp = f_spec_msun(K1_use, P, e)
    fM_from_rvrob = f_spec_msun(K1_from_rvrob, P, e) if K1_from_rvrob else None

    print(f"  P = {P} d,  e = {e}")
    print(f"  semi_amplitude_primary (Gaia)  = {K1_sap} km/s")
    print(f"  rv_amplitude_robust (Gaia)     = {rvrob} km/s -> /2 = {K1_from_rvrob} km/s")
    print(f"  mass_function (Gaia col)       = {fM_gaia} (units? Msun if SB1)")
    print(f"  f(M) recomputed from K1={K1_use:.3f} = {fM_recomp:.4f} Msun")
    if fM_from_rvrob:
        print(f"  f(M) from rv_amplitude_robust/2  = {fM_from_rvrob:.4f} Msun")
    print(f"  caller-reported f(M)           = {rec['reported']['fM_msun']} Msun")

    rec['orbit_recomputed'] = {
        'P_d': P, 'e': e, 'K1_semi_amplitude_primary': K1_sap,
        'rv_amplitude_robust': rvrob, 'K1_from_rvrob_over2': K1_from_rvrob,
        'fM_gaia_col': fM_gaia, 'fM_recomp_from_K1': fM_recomp,
        'fM_from_rvrob_over2': fM_from_rvrob,
        'K1_used': K1_use,
    }

    # --------- M1 selection ---------
    M1_flame = ap.get('mass_flame') if ap else None
    print('\n--- PRIMARY MASS / CLASS ---')
    print(f"  FLAME mass_flame = {M1_flame} Msun")
    teff = (ap.get('teff_gspphot') if ap else None) or (gs.get('teff_gspphot') if gs else None)
    logg = (ap.get('logg_gspphot') if ap else None) or (gs.get('logg_gspphot') if gs else None)
    logg_spec = ap.get('logg_gspspec') if ap else None
    logg_ann = aps.get('logg_gspspec_ann') if aps else None
    rad_flame = ap.get('radius_flame') if ap else None
    lum_flame = ap.get('lum_flame') if ap else None

    # absolute G mag from NSS parallax (Correction A) else gaia_source parallax
    plx_nss = nss.get('parallax') if nss else None
    plx_gs = gs.get('parallax') if gs else None
    plx_use = plx_nss if plx_nss else plx_gs
    plx_src = 'NSS' if plx_nss else 'gaia_source'
    Gmag = gs.get('phot_g_mean_mag') if gs else None
    ag = (gs.get('ag_gspphot') if gs else None) or 0.0
    M_G = None
    if Gmag is not None and plx_use and plx_use > 0:
        M_G = Gmag + 5 * math.log10(plx_use / 1000.0) + 5 - (ag or 0.0)
    print(f"  Teff = {teff} K, logg(gspphot) = {logg}, logg(gspspec) = {logg_spec}, "
          f"logg(gspspec_ann) = {logg_ann}")
    print(f"  radius_flame = {rad_flame} Rsun, lum_flame = {lum_flame} Lsun")
    print(f"  parallax_used = {plx_use} mas ({plx_src});  BP-RP = {gs.get('bp_rp') if gs else None}")
    print(f"  M_G (extinction-corrected, A_G={ag}) = {M_G}")

    # pick M1: FLAME if available, else crude colour/teff MS prior
    if M1_flame and M1_flame > 0:
        M1_use = M1_flame; M1_src = 'FLAME'
    elif teff:
        # very crude MS mass-Teff (only as fallback)
        M1_use = max(0.5, min(3.0, (teff / 5772.0) ** 1.6)); M1_src = 'Teff-MS-crude'
    else:
        M1_use = 1.0; M1_src = 'default-1.0'

    rec['primary'] = {
        'teff_K': teff, 'logg_gspphot': logg, 'logg_gspspec': logg_spec,
        'logg_gspspec_ann': logg_ann, 'radius_flame': rad_flame,
        'lum_flame': lum_flame, 'M_G': M_G, 'parallax_used': plx_use,
        'parallax_source': plx_src, 'bp_rp': gs.get('bp_rp') if gs else None,
        'M1_used': M1_use, 'M1_source': M1_src, 'mass_flame': M1_flame,
    }

    # --------- M2 from f(M)+M1, sin i unconstrained ---------
    print('\n--- M2 (spectroscopic mass function, NO astrometric inclination) ---')
    fM = fM_recomp
    M2_min = solve_m2_min(fM, M1_use)
    print(f"  Using f(M) = {fM:.4f} Msun, M1 = {M1_use:.3f} Msun ({M1_src})")
    print(f"  M2_min (sin i = 1)             = {M2_min:.3f} Msun")
    # Monte Carlo over M1 error and random-i prior (isotropic cos i)
    rng = np.random.default_rng(1)
    n = 300000
    # M1 spread: FLAME ~10%, else 20%
    sig_M1 = 0.12 * M1_use if M1_src == 'FLAME' else 0.25 * M1_use
    M1s = np.clip(rng.normal(M1_use, sig_M1, n), 0.2, 10.0)
    # K1 spread from semi_amplitude_primary_error
    K1e = nss.get('semi_amplitude_primary_error') if nss else None
    K1e = K1e if (K1e and K1e > 0) else 0.05 * K1_use
    K1s = np.clip(rng.normal(K1_use, K1e, n), 1.0, 200.0)
    es = np.clip(rng.normal(e, (nss.get('eccentricity_error') or 0.02) if nss else 0.02, n), 0, 0.95)
    Ps = P  # period extremely well determined; ignore
    fMs = (Ps * 86400.0) * (K1s * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * math.pi * G_SI) / MSUN
    # isotropic inclination: cos i uniform in [0,1]; M2 solved per draw
    cosi = rng.uniform(0, 1, n)
    sini = np.sqrt(np.clip(1 - cosi ** 2, 1e-6, 1.0))
    # vectorized M2 solve via bisection
    lo = np.full(n, 1e-4); hi = np.full(n, 1e3)
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        f_mid = (mid * sini) ** 3 / (M1s + mid) ** 2
        gt = f_mid > fMs
        hi = np.where(gt, mid, hi)
        lo = np.where(gt, lo, mid)
    M2_iso = 0.5 * (lo + hi)
    # also M2 at i=90 distribution (just f(M),M1 errors)
    lo2 = np.full(n, 1e-4); hi2 = np.full(n, 1e3)
    for _ in range(90):
        mid = 0.5 * (lo2 + hi2)
        f_mid = mid ** 3 / (M1s + mid) ** 2
        gt = f_mid > fMs
        hi2 = np.where(gt, mid, hi2)
        lo2 = np.where(gt, lo2, mid)
    M2_min_dist = 0.5 * (lo2 + hi2)

    def pct(x):
        return {p: float(np.percentile(x, p)) for p in (2.5, 16, 50, 84, 97.5)}

    rec['M2'] = {
        'fM_msun': fM, 'M1_used': M1_use,
        'M2_min_point': M2_min,
        'M2_min_dist_pctile': pct(M2_min_dist),
        'M2_isotropic_i_pctile': pct(M2_iso),
        'P_M2_gt_1.4_min': float(np.mean(M2_min_dist > 1.4)),
        'P_M2_gt_3.0_iso': float(np.mean(M2_iso > 3.0)),
        'P_M2_gt_5.0_iso': float(np.mean(M2_iso > 5.0)),
        'frac_iso_above_NS_floor_1.3': float(np.mean(M2_iso > 1.3)),
    }
    print(f"  M2_min distribution (i=90): {pct(M2_min_dist)}")
    print(f"  M2 isotropic-i prior:       {pct(M2_iso)}")
    print(f"  P(M2_min > 1.4) = {rec['M2']['P_M2_gt_1.4_min']:.3f}")

    # --------- SIMBAD + literature ---------
    print('\n--- SIMBAD / literature ---')
    sim = simbad_otype_bibs(f'Gaia DR3 {SID}')
    rec['simbad'] = sim
    print(f"  main_id = {sim.get('main_id')}, otype = {sim.get('otype')}, "
          f"sp_type = {sim.get('sp_type')}")
    print(f"  n_bibcodes = {sim.get('n_bibcodes')}")
    if sim.get('bibcodes'):
        for b in sim['bibcodes'][:25]:
            print(f"    {b['bibcode']}  {b['title']}")

    if gs and gs.get('ra') is not None:
        lit = lit_crossmatch(gs['ra'], gs['dec'])
        rec['lit_crossmatch'] = lit
        print('  Vizier catalog matches:')
        for k, vv in lit.items():
            print(f"    {k}: {vv}")

    with open(f'/tmp/sb1_{SID}_deepdive.json', 'w') as f:
        json.dump(rec, f, indent=2, default=str)
    print(f'\nWrote /tmp/sb1_{SID}_deepdive.json')
    return rec

if __name__ == '__main__':
    run()

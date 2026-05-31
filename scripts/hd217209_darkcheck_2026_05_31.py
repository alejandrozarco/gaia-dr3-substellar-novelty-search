"""Maximum-skepticism DARK-vs-LUMINOUS companion check for the PMa-corroborated
accelerating source Gaia DR3 1928644726286367872 = HD 217209.

Context (given): HGCA chi2=151.9, Kervella snrPMa=13.18, M2_median (v3 accel grid)
=2.585 Msun, SIMBAD=HD 217209, known_multiple=false. nss_solution_type=Acceleration7
(astrometric PM-acceleration only -- NO Thiele-Innes orbit, period unconstrained).

Central question: is the accelerating companion DARK (NS/BH-range, single SED) or
LUMINOUS (an ordinary A/B/F/G/K/M star -> reject)?

Five strands:
 (1) SED 2-component fit (GALEX/Gaia/2MASS/WISE): does a luminous 2-5 Msun MS
     companion appear, or is the SED a single hot star?  A 2-5 Msun MS secondary
     (B/A/F) would be conspicuous, especially in the blue/UV.
 (2) resolved/wide companion: WDS + Gaia DR3 neighbours at matching plx+PM.
 (3) Gaia binarity diagnostics: non_single_star, RVS SB2, ipd_frac_multi_peak,
     RUWE, astrometric_excess_noise.
 (4) Is the measured PM-acceleration + HGCA chi2 consistent with a LUMINOUS stellar
     companion of mass M2, or does a DARK companion remain required?  Key point:
     M2 from a PM-acceleration is period-degenerate; M2_median=2.585 is a grid
     artifact (median over log-P 3-100 yr).  We map M2(P) and ask: at the period
     where a luminous A/F/G companion would be hidden in the SED, what M2 results?
 (5) Novelty / literature: SIMBAD bibcodes, Hipparcos, Shahaf/Halbwachs crossmatch.

Reuses canonical helpers from ns2127900_deepdive_2026_05_28.py and the v3
acceleration inversion (acceleration_inversion.py).

Outputs: /tmp/hd217209_darkcheck.json  +  /tmp/hd217209_darkcheck_report.md
"""
from __future__ import annotations
import json, math, sys, warnings
import numpy as np

warnings.filterwarnings('ignore')

sys.path.insert(0, '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts')
sys.path.insert(0, '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts/streaming/v3_acceleration')

from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad

from acceleration_inversion import (M2_from_acceleration, M2_range,
                                     acceleration_magnitude,
                                     acceleration_magnitude_error)

SID = 1928644726286367872
OUT = {}


def _flt(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# 1. Gaia source + AP + acceleration solution
# --------------------------------------------------------------------------- #
def gaia_source(sid):
    cols = ('source_id, ra, dec, parallax, parallax_error, pmra, pmdec, ruwe, '
            'phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp, '
            'phot_bp_rp_excess_factor, '
            'radial_velocity, radial_velocity_error, rv_amplitude_robust, '
            'rv_chisq_pvalue, rv_nb_transits, rv_renormalised_gof, '
            'rv_expected_sig_to_noise, rv_method_used, '
            'ipd_frac_multi_peak, ipd_frac_odd_win, ipd_gof_harmonic_amplitude, '
            'astrometric_excess_noise, astrometric_excess_noise_sig, '
            'astrometric_gof_al, astrometric_chi2_al, astrometric_n_good_obs_al, '
            'visibility_periods_used, non_single_star, phot_variable_flag, '
            'duplicated_source')
    t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={sid}').get_results()
    if len(t) == 0:
        return None
    out = {}
    for c in t.colnames:
        v = t[c][0]
        fv = _flt(v)
        out[c] = fv if fv is not None else str(v)
    return out


def gaia_ap(sid):
    cols = ('mass_flame, radius_flame, lum_flame, age_flame, '
            'mass_flame_lower, mass_flame_upper, radius_flame_lower, radius_flame_upper, '
            'teff_gspphot, logg_gspphot, mh_gspphot, distance_gspphot, ag_gspphot, ebpminrp_gspphot, '
            'teff_gspphot_lower, teff_gspphot_upper, '
            'teff_gspspec, logg_gspspec, mh_gspspec, '
            'spectraltype_esphs, activityindex_espcs, '
            'azero_esphs, ag_esphs, ebpminrp_esphs')
    try:
        t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.astrophysical_parameters WHERE source_id={sid}').get_results()
        if len(t) == 0:
            return {}
        out = {}
        for c in t.colnames:
            v = t[c][0]
            fv = _flt(v)
            out[c] = fv if fv is not None else str(v)
        return out
    except Exception as e:
        return {'_err': f'{type(e).__name__}: {e}'}


def gaia_accel(sid):
    """Full nss_acceleration_astro row."""
    try:
        t = Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_acceleration_astro WHERE source_id={sid}').get_results()
        if len(t) == 0:
            return {}
        out = {}
        for c in t.colnames:
            if c == 'corr_vec':
                continue
            v = t[c][0]
            fv = _flt(v)
            out[c] = fv if fv is not None else (None if (hasattr(v, 'mask') and v is np.ma.masked) else str(v))
        return out
    except Exception as e:
        return {'_err': f'{type(e).__name__}: {e}'}


# --------------------------------------------------------------------------- #
# 2. SIMBAD + bibcodes + Hipparcos
# --------------------------------------------------------------------------- #
def simbad_block(gaia_id_str, hd_name='HD 217209'):
    s = Simbad()
    for flds in (('otype', 'ids', 'sp_type', 'plx_value', 'V', 'B', 'U',
                  'flux(U)', 'flux(B)', 'flux(V)', 'flux(J)', 'flux(K)'),
                 ('otype', 'ids', 'sp_type', 'plx_value', 'V'),
                 ('otype', 'ids', 'sp_type')):
        try:
            s = Simbad()
            s.add_votable_fields(*flds)
            break
        except Exception:
            continue
    out = {'query': gaia_id_str}
    for qid in (gaia_id_str, hd_name):
        try:
            r = s.query_object(qid)
            if r is not None and len(r):
                out['queried'] = qid
                out['main_id'] = str(r['main_id'][0])
                for k in ('otype', 'sp_type', 'ids'):
                    if k in r.colnames:
                        out[k] = str(r[k][0])
                for k in r.colnames:
                    if k.lower().startswith('flux') or k in ('U', 'B', 'V'):
                        out[k] = _flt(r[k][0])
                break
        except Exception as e:
            out['_obj_err'] = f'{type(e).__name__}: {e}'
    # bibcodes
    q = (f"SELECT b.bibcode, b.journal, b.title FROM basic AS ba "
         f"JOIN ident AS i ON i.oidref = ba.oid "
         f"JOIN has_ref AS hr ON hr.oidref = ba.oid "
         f"JOIN ref AS b ON b.oidbib = hr.oidbibref "
         f"WHERE i.id = '{gaia_id_str}'")
    try:
        t = Simbad().query_tap(q)
        bibs = [{'bibcode': str(row['bibcode']), 'journal': str(row['journal']),
                 'title': str(row['title'])[:95]} for row in t]
        out['n_bibcodes'] = len(bibs)
        out['bibcodes'] = bibs
    except Exception as e:
        out['_bib_err'] = f'{type(e).__name__}: {e}'
    return out


# --------------------------------------------------------------------------- #
# 3. Photometry: GALEX, Gaia, 2MASS, WISE  (Vizier cone)
# --------------------------------------------------------------------------- #
def fetch_photometry(ra, dec):
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    log = {}
    phot = {}  # band -> (mag, err, system, source)

    def vquery(cat, radius_arcsec, cols=None):
        v = Vizier(columns=cols if cols else ['**', '+_r'], timeout=120)
        v.ROW_LIMIT = 5
        try:
            res = v.query_region(coord, radius=radius_arcsec * u.arcsec, catalog=cat)
            return res
        except Exception as e:
            return None

    # GALEX GR6/7 (II/335/galex_ais).  AB.
    try:
        res = vquery('II/335/galex_ais', 10)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c in (('GALEX_FUV', 'FUV'), ('GALEX_NUV', 'NUV')):
                ec = c + 'err'
                if c in t.colnames and not np.ma.is_masked(r[c]):
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else None, 'AB', 'GALEX_AIS')
            log['GALEX_AIS'] = {'found': True, 'r_arcsec': _flt(r['_r']) if '_r' in t.colnames else None}
        else:
            log['GALEX_AIS'] = {'found': False}
    except Exception as e:
        log['GALEX_AIS'] = {'err': str(e)[:80]}

    # also GALEX MIS / all-sky general (II/312 GALEX-DR5 AIS+MIS) as backup
    try:
        res = vquery('II/312/ais', 10)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c in (('GALEX_FUV', 'FUV'), ('GALEX_NUV', 'NUV')):
                if b not in phot and c in t.colnames and not np.ma.is_masked(r[c]):
                    ec = 'e_' + c
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else None, 'AB', 'GALEX_DR5')
            log['GALEX_DR5'] = {'found': True}
        else:
            log['GALEX_DR5'] = {'found': False}
    except Exception as e:
        log['GALEX_DR5'] = {'err': str(e)[:80]}

    # Gaia DR3 own photometry (I/355/gaiadr3) -- Vega
    try:
        res = vquery('I/355/gaiadr3', 5)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c, ec in (('Gaia_G', 'Gmag', 'e_Gmag'), ('Gaia_BP', 'BPmag', 'e_BPmag'),
                             ('Gaia_RP', 'RPmag', 'e_RPmag')):
                if c in t.colnames and not np.ma.is_masked(r[c]):
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else 0.005, 'Vega', 'GaiaDR3')
            log['GaiaDR3'] = {'found': True}
    except Exception as e:
        log['GaiaDR3'] = {'err': str(e)[:80]}

    # 2MASS (II/246/out) -- Vega
    try:
        res = vquery('II/246/out', 5)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c, ec in (('2MASS_J', 'Jmag', 'e_Jmag'), ('2MASS_H', 'Hmag', 'e_Hmag'),
                             ('2MASS_Ks', 'Kmag', 'e_Kmag')):
                if c in t.colnames and not np.ma.is_masked(r[c]):
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else 0.03, 'Vega', '2MASS')
            log['2MASS'] = {'found': True, 'qflg': str(r['Qflg']) if 'Qflg' in t.colnames else None}
    except Exception as e:
        log['2MASS'] = {'err': str(e)[:80]}

    # AllWISE (II/328/allwise) -- Vega
    try:
        res = vquery('II/328/allwise', 5)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c, ec in (('WISE_W1', 'W1mag', 'e_W1mag'), ('WISE_W2', 'W2mag', 'e_W2mag'),
                             ('WISE_W3', 'W3mag', 'e_W3mag'), ('WISE_W4', 'W4mag', 'e_W4mag')):
                if c in t.colnames and not np.ma.is_masked(r[c]):
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else None, 'Vega', 'AllWISE')
            log['AllWISE'] = {'found': True, 'qph': str(r['qph']) if 'qph' in t.colnames else None,
                              'var': str(r['Var']) if 'Var' in t.colnames else None}
    except Exception as e:
        log['AllWISE'] = {'err': str(e)[:80]}

    # Tycho-2 / Hipparcos B,V for the bright optical anchor (I/259/tyc2, I/311/hip2)
    try:
        res = vquery('I/259/tyc2', 5)
        if res and len(res):
            t = res[0]; r = t[0]
            for b, c, ec in (('TYCHO_BT', 'BTmag', 'e_BTmag'), ('TYCHO_VT', 'VTmag', 'e_VTmag')):
                if c in t.colnames and not np.ma.is_masked(r[c]):
                    phot[b] = (_flt(r[c]), _flt(r[ec]) if ec in t.colnames else 0.02, 'Vega', 'Tycho2')
            log['Tycho2'] = {'found': True}
    except Exception as e:
        log['Tycho2'] = {'err': str(e)[:80]}

    return phot, log


# --------------------------------------------------------------------------- #
# 4. Wide / resolved companion search
# --------------------------------------------------------------------------- #
def neighbour_search(sid, ra, dec, plx, pmra, pmdec):
    """Gaia DR3 neighbours within 60 arcsec; flag any at matching plx (within 20%)
    and common PM (within 15% in quadrature) -> physical wide companion."""
    out = {}
    try:
        q = (f"SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec, "
             f"phot_g_mean_mag, bp_rp, ruwe, "
             f"DISTANCE(POINT({ra},{dec}), POINT(ra,dec))*3600 AS sep_arcsec "
             f"FROM gaiadr3.gaia_source "
             f"WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra},{dec}, 60.0/3600.0)) "
             f"AND source_id != {sid} ORDER BY sep_arcsec ASC")
        t = Gaia.launch_job(q).get_results()
        rows = []
        for r in t:
            sep = _flt(r['sep_arcsec'])
            nplx = _flt(r['parallax'])
            npmra = _flt(r['pmra']); npmdec = _flt(r['pmdec'])
            comoving = False
            plx_match = False
            if nplx is not None and plx:
                plx_match = abs(nplx - plx) < 0.2 * plx + 3 * (_flt(r['parallax_error']) or 0.1)
            if npmra is not None and npmdec is not None and pmra and pmdec:
                dpm = math.hypot(npmra - pmra, npmdec - pmdec)
                totpm = math.hypot(pmra, pmdec)
                comoving = dpm < 0.20 * totpm + 2.0
            rows.append({'source_id': str(r['source_id']), 'sep_arcsec': sep,
                         'parallax': nplx, 'pmra': npmra, 'pmdec': npmdec,
                         'G': _flt(r['phot_g_mean_mag']), 'bp_rp': _flt(r['bp_rp']),
                         'ruwe': _flt(r['ruwe']),
                         'plx_match': plx_match, 'pm_comoving': comoving,
                         'PHYSICAL_PAIR': bool(plx_match and comoving)})
        out['n_within_60as'] = len(rows)
        out['neighbours'] = rows[:25]
        out['any_physical_pair'] = any(x['PHYSICAL_PAIR'] for x in rows)
    except Exception as e:
        out['_err'] = f'{type(e).__name__}: {e}'
    return out


def wds_check(ra, dec):
    """Washington Double Star catalog (B/wds/wds) cone, 30 arcsec."""
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    out = {}
    try:
        v = Vizier(columns=['**', '+_r'], timeout=90); v.ROW_LIMIT = 20
        res = v.query_region(coord, radius=30 * u.arcsec, catalog='B/wds/wds')
        if res is None or len(res) == 0:
            out['match'] = False
        else:
            t = res[0]
            recs = []
            for r in t:
                rec = {}
                for c in ('WDS', 'Disc', 'Comp', 'Obs1', 'Obs2', 'sep1', 'sep2',
                          'pa1', 'pa2', 'mag1', 'mag2', 'SpType', '_r'):
                    if c in t.colnames:
                        v_ = r[c]
                        rec[c] = _flt(v_) if c in ('sep1', 'sep2', 'pa1', 'pa2', 'mag1', 'mag2', '_r', 'Obs1', 'Obs2') else str(v_)
                recs.append(rec)
            out['match'] = True
            out['n'] = len(recs)
            out['entries'] = recs
    except Exception as e:
        out['match'] = None
        out['_err'] = f'{type(e).__name__}: {e}'
    return out


def lit_crossmatch(ra, dec):
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    v = Vizier(columns=['**'], timeout=60); v.ROW_LIMIT = -1
    cats = [
        ('J/MNRAS/518/2991', 'Shahaf+2023 Triage I (compact-companion)'),
        ('J/MNRAS/529/3729', 'Shahaf+2024 Triage II (WD census)'),
        ('J/A+A/674/A9', 'Gaia DR3 NSS astrometric orbits (Halbwachs 2023)'),
        ('J/A+A/657/A7', 'Kervella+2022 Hipparcos-Gaia PMa (H2G2)'),
        ('J/ApJS/254/42', 'Brandt 2021 HGCA accelerations'),
    ]
    out = {}
    for cat, label in cats:
        try:
            res = v.query_region(coord, radius=5 * u.arcsec, catalog=cat)
            if res is None or len(res) == 0:
                out[label] = {'match': False}
            else:
                t = res[0]
                out[label] = {'match': True, 'n_rows': int(len(t)),
                              'cols': list(t.colnames)[:24]}
                # capture a few useful columns generically
                row0 = {c: (str(t[c][0])) for c in list(t.colnames)[:24]}
                out[label]['row0'] = row0
        except Exception as e:
            out[label] = {'match': None, 'note': f'{type(e).__name__}'}
    return out


# --------------------------------------------------------------------------- #
# 5. SED 2-component analysis (blackbody/photosphere proxy)
# --------------------------------------------------------------------------- #
# Pivot wavelengths (Angstrom)
PIVOT = {'GALEX_FUV': 1535.1, 'GALEX_NUV': 2300.8,
         'TYCHO_BT': 4220.0, 'TYCHO_VT': 5350.0,
         'Gaia_BP': 5035.8, 'Gaia_G': 5822.4, 'Gaia_RP': 7619.0,
         '2MASS_J': 12393.1, '2MASS_H': 16494.9, '2MASS_Ks': 21638.6,
         'WISE_W1': 33897.0, 'WISE_W2': 46406.4, 'WISE_W3': 125675.9, 'WISE_W4': 223142.3}

# AB zeropoint references for converting Vega->AB roughly (only used for plotting/ratio):
VEGA2AB = {'Gaia_G': 0.107, 'Gaia_BP': 0.0292, 'Gaia_RP': 0.3542,
           '2MASS_J': 0.894, '2MASS_H': 1.374, '2MASS_Ks': 1.840,
           'WISE_W1': 2.699, 'WISE_W2': 3.339, 'WISE_W3': 5.174, 'WISE_W4': 6.620,
           'TYCHO_BT': 0.09, 'TYCHO_VT': 0.044}


def planck_lambda(wave_A, teff):
    """Planck B_lambda (arb. units) at wavelength (Angstrom) and Teff (K)."""
    h = 6.62607015e-34; c = 2.99792458e8; kB = 1.380649e-23
    lam = wave_A * 1e-10
    x = h * c / (lam * kB * teff)
    return (1.0 / lam ** 5) / (np.expm1(x))


def mag_ab_to_fnu_jy(mag_ab):
    return 3631.0 * 10 ** (-0.4 * mag_ab)


def two_temp_sed_analysis(phot, teff1, plx_mas, M1_guess=1.6):
    """Build observed f_nu SED (Jy) in AB. Fit single-photosphere (Planck @teff1)
    scale. Then ask: how bright a companion (2-5 Msun MS, Teff from mass) can be
    ADDED before it overproduces the bluest / reddest bands?  Reports the implied
    flux-ratio limits and whether a 2-5 Msun MS companion is EXCLUDED.

    Uses a Planck proxy for each photosphere (good to ~10-20% across optical-IR for
    these Teff; the conclusion is driven by order-of-magnitude flux ratios, not
    fine spectral features)."""
    # observed AB fluxes
    obs = {}
    for b, (mag, err, sysn, src) in phot.items():
        if mag is None or b not in PIVOT:
            continue
        mab = mag + (VEGA2AB.get(b, 0.0) if sysn == 'Vega' else 0.0)
        e = err if (err and err > 0) else 0.03
        # convert mag err to fractional flux err
        fnu = mag_ab_to_fnu_jy(mab)
        ferr = 0.4 * math.log(10) * e * fnu
        obs[b] = {'wave_A': PIVOT[b], 'fnu_jy': fnu, 'fnu_err_jy': ferr,
                  'mag': mag, 'mag_err': e, 'system': sysn, 'source': src,
                  'mab': mab}

    bands = sorted(obs, key=lambda b: PIVOT[b])
    if not bands:
        return {'error': 'no usable photometry'}

    # Single-photosphere model: f_nu propto nu^2 B_lambda? -> easier: model in f_nu
    # We model f_nu_model(b) = S * planck_fnu(wave, teff1). planck in f_nu:
    def planck_fnu(wave_A, teff):
        # f_nu = lambda^2/c * f_lambda ; B_lambda gives f_lambda shape
        c = 2.99792458e8
        lam = wave_A * 1e-10
        return planck_lambda(wave_A, teff) * lam ** 2 / c

    # least-squares scale for single photosphere over all detected bands
    waves = np.array([obs[b]['wave_A'] for b in bands])
    fnu = np.array([obs[b]['fnu_jy'] for b in bands])
    ferr = np.array([max(obs[b]['fnu_err_jy'], 0.02 * obs[b]['fnu_jy']) for b in bands])
    m1 = np.array([planck_fnu(w, teff1) for w in waves])
    # scale by weighted least squares (model has 1 free amplitude)
    w = 1.0 / ferr ** 2
    S1 = float(np.sum(w * fnu * m1) / np.sum(w * m1 * m1))
    model1 = S1 * m1
    resid = (fnu - model1) / ferr
    chi2_1 = float(np.sum(resid ** 2))
    dof1 = len(bands) - 1

    per_band = []
    for i, b in enumerate(bands):
        per_band.append({'band': b, 'wave_A': float(waves[i]),
                         'fnu_obs_jy': float(fnu[i]), 'fnu_model1_jy': float(model1[i]),
                         'resid_sigma': float(resid[i]),
                         'obs_over_model': float(fnu[i] / model1[i]) if model1[i] > 0 else None})

    # ----- companion injection test -----
    # MS companion mass -> (Teff, L) from a coarse main-sequence (Pecaut-Mamajek-ish)
    # Mass(Msun): (Teff_K, log10(L/Lsun))
    MS = [(0.5, 3700, -1.4), (0.7, 4600, -0.85), (0.9, 5400, -0.30),
          (1.0, 5800, 0.0), (1.3, 6500, 0.45), (1.6, 7300, 0.80),
          (2.0, 9000, 1.25), (2.5, 10500, 1.75), (3.0, 12000, 2.10),
          (4.0, 15000, 2.65), (5.0, 17000, 3.05)]

    # Primary L from Teff1 + (we will use Gaia FLAME L if available, else from radius)
    # For flux-ratio we only need RELATIVE bolometric scaling x spectral shape.
    # Normalize primary bolometric so that its synthetic f_nu matches S1 at all bands:
    # primary contributes model1.  A companion of luminosity Lc and Teff Tc contributes
    # f_nu_c(b) = Sc * planck_fnu(wave, Tc), with Sc set by Lc/Lprim ratio and Tc.
    # The bolometric flux of a Planck of amplitude S and temp T integrates to
    # F_bol propto S * T^4 * (sigma-like const) -- since planck_fnu here is per-unit
    # amplitude, integral of planck_fnu dnu propto T^? Let's just compute numerically.
    def bol_integral(S, teff):
        nu = np.linspace(1e13, 3e15, 4000)  # ~1000 A to 30 micron
        wave_A = (2.99792458e8 / nu) * 1e10
        f = np.array([planck_fnu(wa, teff) for wa in wave_A])
        return S * np.trapz(f, nu) if hasattr(np, 'trapz') else S * np.trapezoid(f, nu)

    Fbol_prim = bol_integral(S1, teff1)

    inj = []
    for mass, tc, logL in MS:
        # companion luminosity relative to primary: need primary L. Use Gaia/Teff1+R.
        # We instead fix companion via its OWN MS L and the primary via its MS L at teff1.
        # primary MS logL at teff1:
        logL_prim = np.interp(teff1, [m[1] for m in MS], [m[2] for m in MS])
        Lprim = 10 ** logL_prim
        Lc = 10 ** logL
        # amplitude of companion Planck so that bol(Sc,Tc)/bol(S1,T1) = Lc/Lprim
        bol_unit_c = bol_integral(1.0, tc)
        Sc = (Lc / Lprim) * Fbol_prim / bol_unit_c
        mc = np.array([planck_fnu(w, tc) for w in waves])
        comp_fnu = Sc * mc
        ratio = comp_fnu / model1  # companion/primary flux ratio per band
        # observed excess available per band (obs - model1) in sigma:
        max_band = bands[int(np.argmax(ratio))]
        # The companion is EXCLUDED if its predicted flux in ANY band exceeds the
        # observed flux + 3 sigma (i.e. the single-star model already saturates the
        # observed SED; an added companion would overshoot).
        overshoot_sigma = (model1 + comp_fnu - fnu) / ferr
        worst = float(np.max(overshoot_sigma))
        worst_band = bands[int(np.argmax(overshoot_sigma))]
        inj.append({'comp_mass_msun': mass, 'comp_teff': tc,
                    'flux_ratio_max_band': max_band,
                    'flux_ratio_max': float(np.max(ratio)),
                    'flux_ratio_at_BP': float(ratio[bands.index('Gaia_BP')]) if 'Gaia_BP' in bands else None,
                    'flux_ratio_at_FUV': float(ratio[bands.index('GALEX_FUV')]) if 'GALEX_FUV' in bands else None,
                    'worst_overshoot_sigma': worst, 'worst_band': worst_band,
                    'EXCLUDED_at_3sigma': bool(worst > 3.0)})

    return {'single_photosphere': {'teff1': teff1, 'scale_S1': S1,
                                   'chi2': chi2_1, 'dof': dof1,
                                   'chi2_dof': chi2_1 / dof1 if dof1 > 0 else None,
                                   'n_bands': len(bands), 'bands': bands},
            'per_band': per_band,
            'companion_injection': inj,
            'note': ('flux_ratio = companion/primary in-band; EXCLUDED_at_3sigma=True '
                     'means adding that MS companion overshoots the observed SED by >3sigma '
                     'in its worst band (single-star SED leaves no room).')}


# --------------------------------------------------------------------------- #
# 6. PM-acceleration -> M2(P) mapping + luminous-companion consistency
# --------------------------------------------------------------------------- #
def accel_m2_map(accel_mag, plx, M1):
    """M2 vs assumed period P. Also the threshold period above which M2 enters
    NS (>1.4) and BH (>3) ranges; and the M2 at periods where a luminous A/F/G
    companion would be SED-hidden vs detected."""
    Pgrid = np.geomspace(1.0, 100.0, 60)
    rows = []
    for P in Pgrid:
        m2 = M2_from_acceleration(accel_mag, plx, M1, float(P))
        # projected separation a_tot (AU) for circular orbit, total mass:
        if m2 is not None:
            a_AU = ((M1 + m2) * P ** 2) ** (1.0 / 3.0)
            ang_sep_mas = a_AU * plx  # AU * mas/pc... a_AU[AU]*plx[mas]/(1[pc]) -> mas at that distance
            rows.append({'P_yr': float(P), 'M2_msun': float(m2),
                         'a_tot_AU': float(a_AU), 'sep_mas_approx': float(ang_sep_mas)})
    def P_at_M2(target):
        for r in rows:
            if r['M2_msun'] >= target:
                return r['P_yr']
        return None
    return {'curve': rows,
            'P_for_M2_1.4': P_at_M2(1.4),
            'P_for_M2_2.0': P_at_M2(2.0),
            'P_for_M2_3.0': P_at_M2(3.0),
            'M2_at_P3yr': M2_from_acceleration(accel_mag, plx, M1, 3.0),
            'M2_at_P5yr': M2_from_acceleration(accel_mag, plx, M1, 5.0),
            'M2_at_P10yr': M2_from_acceleration(accel_mag, plx, M1, 10.0),
            'M2_at_P20yr': M2_from_acceleration(accel_mag, plx, M1, 20.0),
            'M2_at_P50yr': M2_from_acceleration(accel_mag, plx, M1, 50.0)}


# --------------------------------------------------------------------------- #
def main():
    print(f'=== HD 217209 / Gaia DR3 {SID} DARK-vs-LUMINOUS check ===\n', flush=True)
    gs = gaia_source(SID)
    OUT['gaia_source'] = gs
    print(f"Gaia: G={gs['phot_g_mean_mag']:.3f} BP-RP={gs['bp_rp']:.3f} plx={gs['parallax']:.3f}+/-{gs['parallax_error']:.3f} "
          f"RUWE={gs['ruwe']:.2f}", flush=True)
    print(f"  non_single_star={gs['non_single_star']} ipd_frac_multi_peak={gs['ipd_frac_multi_peak']} "
          f"phot_bp_rp_excess_factor={gs.get('phot_bp_rp_excess_factor')}", flush=True)
    print(f"  RV={gs.get('radial_velocity')} +/-{gs.get('radial_velocity_error')} rv_amplitude_robust={gs.get('rv_amplitude_robust')} "
          f"rv_chisq_pvalue={gs.get('rv_chisq_pvalue')} rv_nb_transits={gs.get('rv_nb_transits')}", flush=True)
    print(f"  astrom_excess_noise={gs.get('astrometric_excess_noise')} sig={gs.get('astrometric_excess_noise_sig')} "
          f"vis_periods={gs.get('visibility_periods_used')}", flush=True)

    ap = gaia_ap(SID)
    OUT['gaia_ap'] = ap
    print(f"\nAP: Teff_gspphot={ap.get('teff_gspphot')} logg={ap.get('logg_gspphot')} "
          f"FLAME mass={ap.get('mass_flame')} [{ap.get('mass_flame_lower')},{ap.get('mass_flame_upper')}] "
          f"R={ap.get('radius_flame')} L={ap.get('lum_flame')}", flush=True)
    print(f"  dist_gspphot={ap.get('distance_gspphot')} AG={ap.get('ag_gspphot')} spectraltype_esphs={ap.get('spectraltype_esphs')}", flush=True)

    acc = gaia_accel(SID)
    OUT['gaia_accel'] = acc
    accel_mag = acceleration_magnitude(acc.get('accel_ra'), acc.get('accel_dec'))
    accel_err = acceleration_magnitude_error(acc.get('accel_ra'), acc.get('accel_dec'),
                                             acc.get('accel_ra_error'), acc.get('accel_dec_error'))
    plx = acc.get('parallax') or gs['parallax']
    OUT['accel_mag_mas_yr2'] = accel_mag
    OUT['accel_mag_err'] = accel_err
    OUT['plx_used'] = plx
    print(f"\nAccel: |a|={accel_mag:.3f}+/-{accel_err:.3f} mas/yr^2 (S/N={accel_mag/accel_err:.1f}), "
          f"nss_plx={plx:.3f} sig={acc.get('significance'):.1f} gof={acc.get('goodness_of_fit')}", flush=True)

    # SIMBAD + bibs
    sb = simbad_block(f'Gaia DR3 {SID}')
    OUT['simbad'] = sb
    print(f"\nSIMBAD: main_id={sb.get('main_id')} otype={sb.get('otype')} sp_type={sb.get('sp_type')} "
          f"n_bibs={sb.get('n_bibcodes')}", flush=True)
    if sb.get('ids'):
        print(f"  IDS: {sb['ids'][:300]}", flush=True)

    # photometry
    phot, plog = fetch_photometry(gs['ra'], gs['dec'])
    OUT['photometry'] = {b: {'mag': v[0], 'err': v[1], 'system': v[2], 'source': v[3]} for b, v in phot.items()}
    OUT['photometry_log'] = plog
    print(f"\nPhotometry bands: {sorted(phot)}", flush=True)
    for b in sorted(phot, key=lambda x: PIVOT.get(x, 1e9)):
        print(f"    {b:12s} {phot[b][0]:.3f} +/- {str(phot[b][1]):8s} {phot[b][2]:5s} ({phot[b][3]})", flush=True)

    # SED 2-component
    teff1 = ap.get('teff_gspphot') or 7325.0
    sed = two_temp_sed_analysis(phot, teff1, plx)
    OUT['sed_analysis'] = sed
    if 'single_photosphere' in sed:
        sp = sed['single_photosphere']
        print(f"\nSED single-photosphere fit (Teff={teff1:.0f}K): chi2/dof={sp.get('chi2_dof')} over {sp['n_bands']} bands", flush=True)
        print("  per-band obs/model1:", flush=True)
        for pb in sed['per_band']:
            print(f"    {pb['band']:12s} obs/model={pb['obs_over_model']:.3f} ({pb['resid_sigma']:+.1f}sigma)", flush=True)
        print("  companion-injection (MS secondary):", flush=True)
        for ij in sed['companion_injection']:
            print(f"    M2={ij['comp_mass_msun']:.1f} Msun (Teff{ij['comp_teff']}): flux_ratio_max={ij['flux_ratio_max']:.3f} "
                  f"@{ij['flux_ratio_max_band']}, FUV_ratio={ij['flux_ratio_at_FUV']}, "
                  f"overshoot={ij['worst_overshoot_sigma']:+.1f}sigma@{ij['worst_band']} EXCLUDED={ij['EXCLUDED_at_3sigma']}", flush=True)

    # neighbour + WDS
    nb = neighbour_search(SID, gs['ra'], gs['dec'], gs['parallax'], gs['pmra'], gs['pmdec'])
    OUT['neighbours'] = nb
    print(f"\nGaia neighbours within 60\": n={nb.get('n_within_60as')} any_physical_pair={nb.get('any_physical_pair')}", flush=True)
    for x in (nb.get('neighbours') or [])[:8]:
        print(f"    sep={x['sep_arcsec']:.2f}\" G={x['G']} plx={x['parallax']} pm=({x['pmra']},{x['pmdec']}) "
              f"plx_match={x['plx_match']} comoving={x['pm_comoving']} PHYS={x['PHYSICAL_PAIR']}", flush=True)

    wds = wds_check(gs['ra'], gs['dec'])
    OUT['wds'] = wds
    print(f"\nWDS: match={wds.get('match')} n={wds.get('n')}", flush=True)
    for e in (wds.get('entries') or [])[:6]:
        print(f"    {e}", flush=True)

    lit = lit_crossmatch(gs['ra'], gs['dec'])
    OUT['literature'] = lit
    print("\nLiterature crossmatch:", flush=True)
    for k, v in lit.items():
        print(f"    {k}: {v.get('match')}", flush=True)

    # accel M2(P) map
    M1 = ap.get('mass_flame') or 1.6
    amap = accel_m2_map(accel_mag, plx, M1)
    OUT['accel_m2_map'] = amap
    OUT['M1_used'] = M1
    print(f"\nPM-accel M2(P) map (M1={M1:.2f} Msun):", flush=True)
    print(f"    M2(P=3yr)={amap['M2_at_P3yr']:.3f}  M2(P=5yr)={amap['M2_at_P5yr']:.3f}  "
          f"M2(P=10yr)={amap['M2_at_P10yr']:.3f}  M2(P=20yr)={amap['M2_at_P20yr']:.3f}  "
          f"M2(P=50yr)={amap['M2_at_P50yr']:.3f}", flush=True)
    print(f"    P needed for M2>=1.4 (NS): {amap['P_for_M2_1.4']} yr;  M2>=2.0: {amap['P_for_M2_2.0']} yr;  "
          f"M2>=3.0 (BH): {amap['P_for_M2_3.0']} yr", flush=True)

    json.dump(OUT, open('/tmp/hd217209_darkcheck.json', 'w'), indent=1, default=str)
    print("\n[written /tmp/hd217209_darkcheck.json]", flush=True)


if __name__ == '__main__':
    main()

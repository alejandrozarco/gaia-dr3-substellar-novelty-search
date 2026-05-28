"""Corrected pipeline (v2) — applies three fixes to the original cascade.

This module mirrors scripts/streaming/consumer.py + scripts/streaming/apply_filter32.py
but with the three corrections that emerged from the HD 1957 deep-dive and the
web-tool verification session:

  Correction A: prefer NSS parallax (nss_two_body_orbit.parallax) over
                gaia_source.parallax when both are available.  The gaia_source
                fit absorbs orbital displacement as fake parallax — the bias
                is 1.2-2.5x for the Tier-1 candidates, inflating M_2 by the
                same factor.

  Correction B: rv_amplitude_robust is peak-to-trough, NOT the semi-amplitude
                K_1.  For circular orbits the ratio is exactly 2; for the
                BH2 cross-check (e=0.52) it was 1.74.  So we use
                K_1_obs = rv_amplitude_robust / 2  before comparing to
                K_pred(i=90°) in Filter #32.

  Correction C: Filter #30 K-giant chromatic check now uses logg with a
                three-step fallback chain:
                    logg_gspphot   →  logg_gspspec_ann  →  logg_gspspec
                because gspphot returns NaN for binaries (the orbital
                photometric signature confuses the SED fit).  Both HD 1957
                and BD+38 2040 had logg_gspphot=NaN but logg_gspspec_ann<2.7.

The math is the same as scripts/web_tool/app.py (single-source verification
tool).  See docs/CASCADE_CORRECTIONS_2026_05_28.md for the methodology note.

Do NOT use this module to mutate the original main_hunt_derived.parquet.
See run_v2.py for the driver that writes main_hunt_derived_v2.parquet.
"""
from __future__ import annotations
import math
import pandas as pd

# ----------------------------------------------------------------------------
# Geometry & mass-function math (identical to consumer.py / web_tool app.py)
# ----------------------------------------------------------------------------


def photocentric_a_mas(A, B, F, G):
    """Photocentric semi-major axis a_phot in mas from Thiele-Innes (A,B,F,G).

    Halbwachs+ 2023, Gaia DR3 NSS doc.  Identical to consumer.photocentric_a_mas.
    """
    if any(v is None for v in (A, B, F, G)):
        return None
    try:
        if any(isinstance(v, float) and math.isnan(v) for v in (A, B, F, G)):
            return None
    except TypeError:
        return None
    u = 0.5 * (A * A + B * B + F * F + G * G)
    v = A * G - B * F
    disc = max(0.0, u * u - v * v)
    return math.sqrt(u + math.sqrt(disc))


def solve_m2(fM, M1):
    """Bisect mass function   m_2^3 / (M_1 + m_2)^2 = f(M)  for m_2 (M_sun).

    Identical to consumer.solve_m2 (80 iterations of bisection on [1e-4, 1e3]).
    """
    lo, hi = 1e-4, 1e3
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def mass_class(m2):
    if m2 >= 3.0:
        return 'dormant_BH_candidate'
    if m2 >= 1.2:
        return 'dormant_NS_candidate'
    if m2 >= 0.5:
        return 'WD_or_low_mass_star'
    if m2 >= 0.08:
        return 'M_dwarf_companion'
    if m2 >= 0.013:
        return 'BD_candidate'
    return 'planet_candidate'


def K1_kms(P_d, e, M1, M2, sini):
    """Spectroscopic RV semi-amplitude of the primary, in km/s."""
    if P_d <= 0 or e >= 1.0 or M1 <= 0 or M2 <= 0:
        return 0.0
    P_s = P_d * 86400.0
    num = (2 * math.pi * 6.6743e-11 / P_s) ** (1 / 3) * (M2 * 1.989e30) * sini
    den = ((M1 + M2) * 1.989e30) ** (2 / 3) * math.sqrt(1 - e * e)
    return (num / den) / 1000.0


# ----------------------------------------------------------------------------
# Correction A: NSS plx selection
# ----------------------------------------------------------------------------

def select_plx(plx_gs, plx_nss):
    """Return (plx_used, plx_source) using NSS plx when available.

    plx_gs   = gaia_source.parallax (single-star fit, biased for binaries)
    plx_nss  = nss_two_body_orbit.parallax (orbit-fit, unbiased)

    Returns (None, None) if neither is available/positive.
    """
    def _is_good(v):
        if v is None:
            return False
        try:
            if isinstance(v, float) and math.isnan(v):
                return False
        except TypeError:
            return False
        return float(v) > 0

    if _is_good(plx_nss):
        return float(plx_nss), 'NSS'
    if _is_good(plx_gs):
        return float(plx_gs), 'gaia_source'
    return None, None


# ----------------------------------------------------------------------------
# Correction B: K_obs / 2 conversion for Filter #32
# ----------------------------------------------------------------------------

def filter32_v2(K_obs_rvampl, P_d, e, M1, M2_astrom):
    """Filter #32 with Correction B applied.

    Gaia DR3 rv_amplitude_robust is the peak-to-trough robust estimator of
    the RV time series, NOT the semi-amplitude K_1.  We convert to K_1 via
        K_1_obs ≈ rv_amplitude_robust / 2        (sinusoidal limit)

    Gaia BH2 verification:
        rv_amplitude_robust = 36.96 km/s  (Gaia DR3)
        K_1 (El-Badry+ 2023) = 21.2 km/s
        ratio = 36.96 / 21.2 = 1.74  (~2, suppressed by e=0.52 eccentricity)

    Returns (status, sini_implied, K_pred_i90).
    """
    if K_obs_rvampl is None or pd.isna(K_obs_rvampl) or K_obs_rvampl <= 0:
        return 'NO_DATA', None, None
    K1_obs = float(K_obs_rvampl) / 2.0  # peak-to-trough → semi-amplitude
    K_max = K1_kms(P_d, e, M1, M2_astrom, 1.0)
    if K_max <= 0:
        return 'NO_DATA', None, K_max
    sini_implied = K1_obs / K_max
    status = 'PASS' if sini_implied <= 1.05 else 'FAIL'
    return status, sini_implied, K_max


# ----------------------------------------------------------------------------
# Correction C: F#30 logg fallback chain
# ----------------------------------------------------------------------------

def _nan_safe(v):
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
    except TypeError:
        return None
    return float(v)


def filter30_v2(bp_rp, logg_gspphot, logg_gspspec_ann, logg_gspspec,
                teff_gspphot=None, teff_gspspec_ann=None):
    """Filter #30 chromatic-bias risk with logg fallback chain.

    Fires on (any of):
        BP-RP > 1.2
        logg < 2.7   (preferring logg_gspphot, then _ann, then _gspspec)
        K-giant proxy: 3700 ≤ Teff ≤ 5200 K  AND logg < 3.0

    HD 1957 and BD+38 2040 both have logg_gspphot=NaN and were missed by the
    original cascade.  HD 1957 has logg_gspspec_ann=2.63 (below 2.7) — v2
    catches it correctly.

    Returns (status_str, cbias_risk_bool, logg_used, logg_source, reason_str).
    """
    # logg fallback chain
    logg_gs = _nan_safe(logg_gspphot)
    logg_ann = _nan_safe(logg_gspspec_ann)
    logg_sp = _nan_safe(logg_gspspec)
    if logg_gs is not None:
        logg_used, logg_source = logg_gs, 'gspphot'
    elif logg_ann is not None:
        logg_used, logg_source = logg_ann, 'gspspec_ann'
    elif logg_sp is not None:
        logg_used, logg_source = logg_sp, 'gspspec'
    else:
        logg_used, logg_source = None, 'NONE'

    teff_used = _nan_safe(teff_gspspec_ann)
    if teff_used is None:
        teff_used = _nan_safe(teff_gspphot)

    bp_rp_v = _nan_safe(bp_rp)
    cbias_color = bp_rp_v is not None and bp_rp_v > 1.2
    cbias_logg = logg_used is not None and logg_used < 2.7
    cbias_kgiant = (teff_used is not None and 3700.0 <= teff_used <= 5200.0
                    and (logg_used is None or logg_used < 3.0))
    cbias_risk = bool(cbias_color or cbias_logg or cbias_kgiant)
    status = 'FAIL' if cbias_risk else 'PASS'
    bits = []
    if cbias_color:
        bits.append(f'BP-RP={bp_rp_v:.2f} > 1.2')
    if cbias_logg:
        bits.append(f'log g={logg_used:.2f} ({logg_source}) < 2.7')
    if cbias_kgiant:
        bits.append(f'K-giant proxy (Teff={teff_used:.0f} K, logg<3)')
    reason = ', '.join(bits) if bits else 'no chromatic-bias signatures'
    return status, cbias_risk, logg_used, logg_source, reason


# ----------------------------------------------------------------------------
# Filter #31 (unchanged — for completeness)
# ----------------------------------------------------------------------------

def filter31(K_obs, pval):
    if K_obs is None or pval is None or pd.isna(K_obs) or pd.isna(pval):
        return 'NO_DATA'
    if K_obs > 5 and pval < 0.05:
        return 'PASS'
    if K_obs > 5 and pval > 0.5:
        return 'FAIL'
    return 'AMBIGUOUS'


# ----------------------------------------------------------------------------
# Tier classification — identical to web_tool/app.py derive_one()
# ----------------------------------------------------------------------------

def tier_label(cls, f29, f30, f31, f32):
    is_compact_class = cls in ('dormant_BH_candidate', 'dormant_NS_candidate')
    if not is_compact_class:
        return f'Rejected — class={cls}'
    if f29 == 'FAIL':
        return 'Demoted (failed F#29 SB2)'
    if f30 == 'FAIL':
        return 'Demoted (failed F#30 K-giant chromatic)'
    if f32 == 'FAIL':
        return 'Demoted (failed F#32 joint K_obs/K_pred)'
    if f31 == 'FAIL':
        return 'Demoted (failed F#31 phantom RV)'
    if f31 in ('AMBIGUOUS', 'NO_DATA'):
        return 'Tier-2 (RV inconclusive — needs follow-up)'
    if cls == 'dormant_BH_candidate':
        return 'Tier-1 BH'
    if cls == 'dormant_NS_candidate':
        return 'Tier-1 NS'
    return 'Tier-2 (unexpected combination)'


# ----------------------------------------------------------------------------
# Single-row v2 derivation — mirrors web_tool/app.py derive_one()
# ----------------------------------------------------------------------------

def derive_row_v2(row, M1_prior=1.5):
    """Apply all three corrections to one row dict-like input.

    `row` must expose (numeric or None):
        a_phot_mas, parallax, nss_parallax,
        period (P_d), eccentricity (e),
        bp_rp, logg_gspphot, logg_gspspec_ann, logg_gspspec,
        teff_gspphot, teff_gspspec_ann,
        rv_amplitude_robust, rv_chisq_pvalue,
        in_sb2 (bool), nss_solution_type (str).

    `M1_prior` is the fixed primary-mass prior in M_sun.  Defaults to 1.5
    to match the web-tool default — the published v1 catalog used
    FLAME mass with fallback to 1.0, which gave a different M_2 scale.
    The user's smoke-test expected values assume M1_prior = 1.5.

    Returns dict with the v2 columns (M2_msun_v2, filter30_v2, ..., tier_v2).
    Returns {'error': ...} if derivation impossible.
    """
    a_phot = row.get('a_phot_mas')
    plx_gs = row.get('parallax')
    plx_nss = row.get('nss_parallax')
    plx_used, plx_source = select_plx(plx_gs, plx_nss)
    P = row.get('P_d') if 'P_d' in row else row.get('period')

    if a_phot is None or plx_used is None or P is None or P <= 0:
        return {'error': 'missing parallax / period / a_phot'}

    a_phot_AU = float(a_phot) / float(plx_used)
    P_yr = float(P) / 365.25
    fM_v2 = a_phot_AU ** 3 / P_yr ** 2

    M1_v2 = float(M1_prior)

    M2_v2 = solve_m2(fM_v2, M1_v2)
    cls_v2 = mass_class(M2_v2)

    e_val = _nan_safe(row.get('eccentricity') or row.get('e'))
    if e_val is None:
        e_val = 0.0

    # F#29 — SB2 (unchanged)
    nss_type = str(row.get('nss_solution_type') or '')
    in_sb2 = ('SB2' in nss_type) or bool(row.get('in_sb2', False))
    f29 = 'FAIL' if in_sb2 else 'PASS'

    # F#30 with logg fallback (Correction C)
    f30, cbias_risk_v2, logg_used, logg_source, f30_reason = filter30_v2(
        bp_rp=row.get('bp_rp'),
        logg_gspphot=row.get('logg_gspphot') if 'logg_gspphot' in row else row.get('logg'),
        logg_gspspec_ann=row.get('logg_gspspec_ann'),
        logg_gspspec=row.get('logg_gspspec'),
        teff_gspphot=row.get('teff_gspphot') if 'teff_gspphot' in row else row.get('Teff'),
        teff_gspspec_ann=row.get('teff_gspspec_ann'),
    )

    # F#31 — RV reality check (unchanged)
    K_obs = row.get('rv_amplitude_robust')
    pval = row.get('rv_chisq_pvalue')
    f31 = filter31(K_obs, pval)

    # F#32 with K_obs / 2 conversion (Correction B)
    f32, sini_implied_v2, K_pred_i90_v2 = filter32_v2(K_obs, float(P), e_val, M1_v2, M2_v2)

    tier = tier_label(cls_v2, f29, f30, f31, f32)

    return {
        'a_phot_mas': float(a_phot),
        'plx_used': plx_used,
        'plx_source': plx_source,
        'a_phot_AU_v2': a_phot_AU,
        'P_yr_v2': P_yr,
        'e_v2': e_val,
        'M1_msun_v2': M1_v2,
        'fM_msun_v2': fM_v2,
        'M2_msun_v2': M2_v2,
        'class_v2': cls_v2,
        'logg_used': logg_used,
        'logg_source': logg_source,
        'cbias_risk_v2': cbias_risk_v2,
        'filter29_v2': f29,
        'filter30_v2': f30,
        'filter30_reason_v2': f30_reason,
        'filter31_v2': f31,
        'filter32_v2': f32,
        'sini_implied_v2': sini_implied_v2,
        'K_pred_i90_v2': K_pred_i90_v2,
        'tier_v2': tier,
    }

"""Gaia DR3 Dormant Compact-Object Cascade — single-source web tool prototype.

A Streamlit front-end onto the same cascade that scripts/streaming/consumer.py
runs in bulk over the Gaia DR3 NSS catalog.  Filters #29–#32 use the EXACT
math from consumer.py and apply_filter32.py — see those files for provenance.

Run locally:
    streamlit run app.py

The app supports two data paths:
  1. Live Gaia DR3 ADQL via astroquery.gaia (can be slow; wrapped with timeouts)
  2. Offline demo using sample_data/hd1957_demo.parquet (HD 1957 / 2543788153077017344)
"""
from __future__ import annotations
import json
import math
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Suppress astropy "converting masked element to nan" — that conversion is
# intended (we want NaN to flow into our isnan checks).  Without this every
# query of a binary with sparse NSS columns dumps ~10 lines of stderr per page.
warnings.filterwarnings('ignore', message='Warning: converting a masked element to nan.')

# ---------------------------------------------------------------------------
# Constants & paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
SAMPLE_PARQUET = HERE / 'sample_data' / 'hd1957_demo.parquet'
BENCHMARKS_JSON = HERE / 'sample_data' / 'benchmarks.json'
DEMO_SOURCE_ID = 2543788153077017344  # HD 1957

# Bulk-cascade output parquets — used to cross-reference the current source_id
# against the full v2 + v3 catalogs.  When the live row alone can't produce
# a verdict (e.g. SB1-only or Acceleration-only NSS), we surface whatever the
# bulk runs found instead.
PROJECT_ROOT = HERE.parent.parent  # scripts/web_tool/ → repo root
V2_PARQUET           = PROJECT_ROOT / 'data' / 'derived' / 'main_hunt_derived_v2.parquet'
V3_PARQUET           = PROJECT_ROOT / 'data' / 'derived' / 'acceleration_v3.parquet'
V2_ALT_PARQUET       = PROJECT_ROOT / 'data' / 'derived' / 'main_hunt_derived_v2_alt.parquet'
V2_RELAXED_PARQUET   = PROJECT_ROOT / 'data' / 'derived' / 'main_hunt_derived_v2_relaxed.parquet'


# ---------------------------------------------------------------------------
# Tier ladder — what each tier means (used in UI explainer)
# ---------------------------------------------------------------------------
# Each entry is (label, color, description, match_prefix).
# `match_prefix` is a substring (or list of prefixes) that derived['tier']
# may start with — needed because the human-readable ladder label doesn't
# always match the verbatim tier string returned by derive_one (e.g.
# label='Tier-2 (follow-up needed)' but tier='Tier-2 — compact-object…').
TIER_LADDER = [
    ('Tier-1 BH discovery candidate',     '#2ca02c',
     'M_2 ≥ 3.0 M_⊙, all four cascade filters pass — discovery-grade BH candidate, follow up with RV',
     'Tier-1 BH'),
    ('Tier-1 NS discovery candidate',     '#1f77b4',
     '1.2 ≤ M_2 < 3.0 M_⊙, all filters pass — discovery-grade NS candidate, follow up with RV',
     'Tier-1 NS'),
    ('Sub-Ch WD / massive WD companion',  '#9467bd',
     '0.5 ≤ M_2 < 1.2 M_⊙, all filters pass — confirmed white-dwarf or low-mass-stellar companion (post-mass-transfer typical)',
     'Sub-Ch'),
    ('M-dwarf companion',                 '#bcbd22',
     '0.08 ≤ M_2 < 0.5 M_⊙ — confirmed M-dwarf companion',
     'M-dwarf'),
    ('Brown-dwarf candidate',             '#e377c2',
     '0.013 ≤ M_2 < 0.08 M_⊙ — confirmed sub-stellar brown-dwarf companion',
     'Brown-dwarf'),
    ('Exoplanet candidate',               '#17becf',
     'M_2 < 0.013 M_⊙ — confirmed planet-mass companion',
     'Exoplanet'),
    ('Tier-2 (RV follow-up needed)',      '#ff7f0e',
     'Compact-object mass but RV (F#31) is inconclusive or absent (e.g. OrbitalAlternative rows where rv_amplitude_robust is null) — RV epochs would disambiguate',
     'Tier-2'),
    ('Stellar binary (SB2 detected)',     '#8c564b',
     'F#29 flagged double-lined spectroscopic features — companion is luminous, not compact',
     'Stellar binary'),
    ('K-giant systematic (M_2 inflated)', '#d62728',
     'F#30 fires — K-giant primary, photocentric chromatic bias inflates M_2 by ~2-3× (HD 1957 / 4 UMi class)',
     'K-giant systematic'),
    ('Joint-check failure (M_2 likely overestimated)', '#d62728',
     'F#32 fires — K_obs > K_pred(i=90°), suggests non-orbital RV noise or M_2 inflation',
     'Joint-check failure'),
    ('Phantom RV signal (no real variability)', '#7f7f7f',
     'F#31 fires — rv_amplitude_robust > 0 but rv_chisq_pvalue says no real variability (A-dwarf class)',
     'Phantom RV signal'),
]


# ---------------------------------------------------------------------------
# Benchmark catalog — pre-loaded known sources for verification & demo
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_benchmarks() -> dict:
    if not BENCHMARKS_JSON.exists():
        return {'groups': []}
    with open(BENCHMARKS_JSON) as fh:
        return json.load(fh)

# ---------------------------------------------------------------------------
# Cascade math — MUST match scripts/streaming/consumer.py & apply_filter32.py
# ---------------------------------------------------------------------------

def photocentric_a_mas(A: float, B: float, F: float, G: float) -> float | None:
    """Photocentric semi-major axis in mas from Thiele-Innes (A,B,F,G).

    Identical to consumer.photocentric_a_mas (Halbwachs+ 2023, Gaia DR3 NSS doc).
    """
    if any(v is None for v in (A, B, F, G)):
        return None
    if any(isinstance(v, float) and math.isnan(v) for v in (A, B, F, G)):
        return None
    u = 0.5 * (A * A + B * B + F * F + G * G)
    v = A * G - B * F
    disc = max(0.0, u * u - v * v)
    return math.sqrt(u + math.sqrt(disc))


def solve_m2(fM: float, M1: float) -> float:
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


def m2_range_isotropic_sini(fM: float, M1: float, n: int = 20000,
                             percentiles: tuple = (16.0, 50.0, 84.0)) -> dict:
    """Monte Carlo M_2 percentiles under an isotropic inclination prior.

    Assumes cos i ~ Uniform(0, 1).  For each sin i draw, solve the photocentric
    mass function for M_2 given the supplied M_1 point estimate.  Returns the
    1σ-equivalent (16/50/84%) percentiles of M_2 in M_⊙, plus the underlying
    Monte Carlo samples for further analysis.

    This is *not* a full Bayesian posterior — it marginalises over inclination
    only and treats M_1, f(M) as point estimates.  For tighter constraints
    that incorporate Gaia DR3 RV-variability evidence and an M_1 uncertainty,
    use the dossier-grade tooling in `scripts/streaming/v2_corrected/`.
    """
    import numpy as np
    if fM is None or M1 is None or fM <= 0 or M1 <= 0:
        return {'p16': None, 'p50': None, 'p84': None, 'samples': None}
    rng = np.random.default_rng(42)
    cos_i = rng.uniform(0.0, 1.0, size=n)
    sin_i = np.sqrt(1.0 - cos_i * cos_i)
    # Avoid sin_i == 0 (M_2 → ∞)
    sin_i = np.clip(sin_i, 1e-4, 1.0)
    m2_samples = np.empty(n)
    for k in range(n):
        m2_samples[k] = solve_m2(fM / sin_i[k] ** 3, M1)
    p16, p50, p84 = np.percentile(m2_samples, percentiles)
    return {'p16': float(p16), 'p50': float(p50), 'p84': float(p84),
            'samples': m2_samples}


def mass_class(m2: float) -> str:
    """Cascade mass-class labels (consumer.mass_class)."""
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


def K1_kms(P_d: float, e: float, M1: float, M2: float, sini: float) -> float:
    """RV semi-amplitude K_1 in km/s (consumer.K1_kms / apply_filter32.K1_kms_safe)."""
    if P_d <= 0 or e >= 1.0 or M1 <= 0 or M2 <= 0:
        return 0.0
    P_s = P_d * 86400.0
    num = (2 * math.pi * 6.6743e-11 / P_s) ** (1 / 3) * (M2 * 1.989e30) * sini
    den = ((M1 + M2) * 1.989e30) ** (2 / 3) * math.sqrt(1 - e * e)
    return (num / den) / 1000.0


def filter32(K_obs_rvampl, P_d, e, M1, M2_astrom):
    """Filter #32 (apply_filter32.apply_filter32_row) — CORRECTED.

    Gaia DR3 ``rv_amplitude_robust`` is the peak-to-trough robust estimator
    of the RV time series, NOT the semi-amplitude K_1.  For a sinusoidal RV
    K_1 cos(φ), peak-to-trough = 2·K_1.  We convert to K_1 here:

        K_1 ≈ rv_amplitude_robust / 2     (sinusoidal limit)

    Gaia BH2 cross-check: rv_amplitude_robust = 36.96 km/s vs El-Badry+ 2023
    K_1 = 21.2 km/s → ratio 1.74 (~2, suppressed by e=0.52 eccentricity).

    This corrects a factor-of-2 issue in the original consumer.py /
    apply_filter32.py that compensates the gaia_source.parallax bias and
    so was not previously visible.
    """
    # Belt-and-braces: astropy MaskedColumn → numpy masked element → float()
    # produces a *warning* and a real NaN, but pd.isna on the masked element
    # itself often returns False because it's a sentinel, not a NaN.  Convert
    # via try/except and then check isnan on the resulting float.
    try:
        K_obs_float = float(K_obs_rvampl) if K_obs_rvampl is not None else None
    except (TypeError, ValueError):
        K_obs_float = None
    if K_obs_float is None or math.isnan(K_obs_float) or K_obs_float <= 0:
        return 'NO_DATA', None, None
    K1_obs = K_obs_float / 2.0  # peak-to-trough -> semi-amplitude
    K_max = K1_kms(P_d, e, M1, M2_astrom, 1.0)
    if K_max <= 0:
        return 'NO_DATA', None, K_max
    sini_implied = K1_obs / K_max
    if math.isnan(sini_implied):
        return 'NO_DATA', None, K_max
    status = 'PASS' if sini_implied <= 1.05 else 'FAIL'
    return status, sini_implied, K_max


# ---------------------------------------------------------------------------
# Data acquisition: Gaia ADQL with sample-data fallback
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_sample_row() -> dict:
    df = pd.read_parquet(SAMPLE_PARQUET)
    return df.iloc[0].to_dict()


@st.cache_data(show_spinner=False)
def lookup_in_bulk_catalogs(source_id: int) -> dict:
    """Return any matching row from the bulk-cascade outputs.

    Cross-referencing is essential when the live single-source query lands
    in a degenerate channel (SB1-only / Acceleration-only) or in a sub-pool
    the v2 producer skipped (OrbitalAlternative, faint AstroSpectroSB1).
    The bulk runs have already computed mass-function inferences for these
    sources via different math; this lookup surfaces what they found so
    the user is not left with a bare "no NSS Orbital" message.

    Returns keys:
      - 'v2'        : row from main_hunt_derived_v2.parquet (production)
      - 'v3'        : row from acceleration_v3.parquet (Acceleration channel)
      - 'v2_alt'    : row from main_hunt_derived_v2_alt.parquet
                      (OrbitalAlternative ingest, today's expansion)
      - 'v2_relaxed': row from main_hunt_derived_v2_relaxed.parquet
                      (relaxed G<15 plx>0.5 expansion, today)
    """
    result = {'v2': None, 'v3': None, 'v2_alt': None, 'v2_relaxed': None}
    for key, path in (('v2', V2_PARQUET),
                       ('v3', V3_PARQUET),
                       ('v2_alt', V2_ALT_PARQUET),
                       ('v2_relaxed', V2_RELAXED_PARQUET)):
        try:
            if path.exists():
                df = pd.read_parquet(path)
                r = df[df['source_id'] == source_id]
                if len(r):
                    result[key] = r.iloc[0].to_dict()
        except Exception:
            pass
    return result


# Discovery-name → Gaia DR3 source_id aliases.  SIMBAD doesn't carry these
# "common" discovery names (Gaia BH1, etc.); the El-Badry/Gaia papers refer
# to them by source_id only.  Map them here so users can type the paper name.
DISCOVERY_ALIASES = {
    'gaia bh1':  4373465352415301632,   # El-Badry+ 2023 MNRAS 518
    'gaia bh2':  5870569352746779008,   # El-Badry+ 2023 MNRAS 521
    'gaia bh3':  4318465066420528000,   # Gaia Coll. 2024 A&A
    'gaia ns1':  None,                  # placeholder for future discoveries
}


@st.cache_data(show_spinner=False, ttl=86400)
def resolve_input_to_source_id(raw: str) -> tuple[int | None, str, str]:
    """Resolve a user input string to a Gaia DR3 source_id (int64).

    Accepts:
      - Pure integer: treated as source_id directly.
      - "Gaia DR3 NNNN" or "Gaia DR3 source NNNN": stripped to NNNN.
      - Any other string: SIMBAD object lookup → coordinates → Gaia DR3
        cone search (≤1.5″) → nearest-and-brightest match.

    Returns ``(source_id, resolved_name, status_message)``.  ``source_id``
    is ``None`` if nothing matched.  The ``status_message`` is what we show
    above the verdict so the user can verify the resolution went where
    they expected.

    Important: never round-trips through pandas float64 — Gaia source_ids
    are 64-bit integers that exceed float64 precision.  Astropy Tables
    preserve int64.
    """
    raw = (raw or '').strip()
    if not raw:
        return None, '', 'Enter a name or source_id.'

    # Discovery-name alias map (Gaia BH1/BH2/BH3 etc).  Check before stripping
    # the "Gaia " prefix below — we want "Gaia BH1" to land here, not be
    # mistreated as "BH1".
    alias_key = raw.lower().replace('  ', ' ')
    if alias_key in DISCOVERY_ALIASES and DISCOVERY_ALIASES[alias_key]:
        sid = DISCOVERY_ALIASES[alias_key]
        return sid, raw, f'Resolved via discovery-name alias: {raw} → Gaia DR3 {sid}.'

    # Strip Gaia DR3 / DR2 / EDR3 prefix
    cleaned = raw
    for prefix in ('Gaia DR3 ', 'Gaia DR2 ', 'Gaia EDR3 ', 'Gaia '):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    if cleaned.lower().startswith('source '):
        cleaned = cleaned[7:].strip()

    # Pure integer?
    if cleaned.isdigit() and len(cleaned) >= 16:
        try:
            return int(cleaned), f'Gaia DR3 {cleaned}', f'Treated as Gaia DR3 source_id directly.'
        except ValueError:
            pass

    # Name lookup via SIMBAD → coords → Gaia cone
    try:
        from astroquery.simbad import Simbad
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        s = Simbad()
        s.add_votable_fields('ra', 'dec', 'main_id')
        r = s.query_object(raw)
        if r is None or len(r) == 0:
            return None, raw, f'SIMBAD did not recognise "{raw}".'
        ra = float(r['ra'][0])
        dec = float(r['dec'][0])
        main = str(r['main_id'][0]).strip()
    except Exception as exc:  # noqa: BLE001
        return None, raw, f'SIMBAD resolution failed: {type(exc).__name__}'

    # Gaia cone search.  Two-pass: try a tight 1.5″ cone first (fast, unambiguous
    # for most stars), then widen to 10″ for high-PM stars that have moved
    # between SIMBAD's epoch and Gaia DR3's J2016.0.  In the wide pass we still
    # rank by separation × brightness so a faint background neighbour doesn't
    # win over the actual target.
    try:
        from astroquery.gaia import Gaia
        for radius_deg, radius_arcsec in ((0.00042, 1.5), (0.00278, 10.0)):
            adql = f"""SELECT source_id, phot_g_mean_mag,
                              DISTANCE(POINT('ICRS', ra, dec),
                                        POINT('ICRS', {ra}, {dec})) * 3600.0 AS sep_arcsec
                       FROM gaiadr3.gaia_source
                       WHERE 1=CONTAINS(POINT('ICRS', ra, dec),
                                         CIRCLE('ICRS', {ra}, {dec}, {radius_deg}))
                       ORDER BY phot_g_mean_mag ASC"""
            tbl = Gaia.launch_job(adql).get_results()
            if len(tbl) == 0:
                continue
            # Read int64 directly from the astropy Table (no float round-trip)
            sid = int(tbl[0]['source_id'])
            g = float(tbl[0]['phot_g_mean_mag'])
            sep = float(tbl[0]['sep_arcsec'])
            wide_note = '' if radius_arcsec == 1.5 else f' (using {radius_arcsec:.0f}″ widened cone — likely high-PM)'
            extra = f' ({len(tbl)-1} fainter source(s) also within cone)' if len(tbl) > 1 else ''
            return sid, main, (f'Resolved "{raw}" → SIMBAD "{main}" → Gaia DR3 {sid} '
                                f'(G={g:.2f}, sep={sep:.2f}″){wide_note}{extra}.')
        return None, main, f'SIMBAD found "{main}" but no Gaia DR3 source within 10″.'
    except Exception as exc:  # noqa: BLE001
        return None, main, f'Gaia ADQL cone search failed: {type(exc).__name__}'


@st.cache_data(show_spinner=False, ttl=3600)
def query_gaia_live(source_id: int, timeout_s: int = 30) -> dict | None:
    """Pull one Gaia DR3 source + NSS + AP supp via astroquery.

    Returns None on any failure; the app then falls back to sample data.
    """
    try:
        from astroquery.gaia import Gaia
        Gaia.MAIN_GAIA_TABLE = 'gaiadr3.gaia_source'
        adql = f"""
        SELECT g.source_id, g.ra, g.dec, g.l, g.b,
               g.parallax, g.pmra, g.pmdec,
               g.phot_g_mean_mag, g.bp_rp, g.ruwe,
               g.astrometric_excess_noise_sig, g.non_single_star,
               g.phot_bp_rp_excess_factor, g.ipd_frac_multi_peak,
               g.radial_velocity, g.rv_amplitude_robust, g.rv_chisq_pvalue,
               g.rv_nb_transits,
               n.nss_solution_type, n.period, n.eccentricity,
               n.a_thiele_innes, n.b_thiele_innes,
               n.f_thiele_innes, n.g_thiele_innes,
               n.significance,
               n.parallax AS nss_parallax,
               ap.teff_gspphot, ap.logg_gspphot, ap.mass_flame, ap.radius_flame,
               ap.teff_gspspec, ap.logg_gspspec, ap.spectraltype_esphs,
               aps.teff_gspspec_ann, aps.logg_gspspec_ann, aps.mh_gspspec_ann,
               aps.radius_flame_spec, aps.lum_flame_spec, aps.evolstage_flame_spec
        FROM gaiadr3.gaia_source AS g
        LEFT JOIN gaiadr3.nss_two_body_orbit AS n  USING (source_id)
        LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
        LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
        WHERE g.source_id = {int(source_id)}
        """
        job = Gaia.launch_job_async(adql)
        # astroquery sets a per-request HTTP timeout via Gaia.TIMEOUT but
        # not all builds honour it; the spinner gives the user feedback.
        tbl = job.get_results()
        if len(tbl) == 0:
            return None
        return {c: tbl[c][0] for c in tbl.colnames}
    except Exception as exc:  # noqa: BLE001  — last-resort fallback to sample
        st.warning(f'Gaia ADQL query failed ({type(exc).__name__}); falling back to sample data.')
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def query_hgca(hip: int | None, timeout_s: int = 20) -> dict | str:
    """Look up the Hipparcos-Gaia Catalog of Accelerations (Brandt 2021,
    J/ApJS/254/42) via Vizier.

    Returns a dict of the matched row, or a string status message on
    timeout/no-match so the UI can show 'HGCA: skipped (timeout)'.
    """
    if hip is None or (isinstance(hip, float) and math.isnan(hip)):
        return 'HGCA: no HIP cross-match available'
    try:
        from astroquery.vizier import Vizier
        v = Vizier(columns=['*'], timeout=timeout_s)
        res = v.query_constraints(catalog='J/ApJS/254/42/catalog', HIP=str(int(hip)))
        if res is None or len(res) == 0:
            return 'HGCA: HIP not in catalog'
        return {c: res[0][c][0] for c in res[0].colnames}
    except Exception as exc:  # noqa: BLE001
        return f'HGCA: skipped ({type(exc).__name__})'


# ---------------------------------------------------------------------------
# Derivation pipeline (single source) — mirrors consumer.derive_chunk per-row
# ---------------------------------------------------------------------------

def derive_one(row: dict, M1_prior: float) -> dict:
    """Apply Thiele-Innes -> f(M) -> M_2, then Filters #29–#32 to ONE source."""
    A = row.get('a_thiele_innes'); B = row.get('b_thiele_innes')
    F = row.get('f_thiele_innes'); G = row.get('g_thiele_innes')
    a_phot = photocentric_a_mas(A, B, F, G)

    # Prefer NSS parallax when available — gaia_source.parallax is biased by the
    # very orbital motion we're solving for (most acute for confirmed binaries
    # like Gaia BH1/BH2 where the gaia_source plx underestimates the true plx
    # by ~20-30%, which would over-inflate a_phot_AU and hence f(M)).
    plx_gs = row.get('parallax')
    plx_nss = row.get('nss_parallax')
    plx_used = None
    plx_source = None
    if plx_nss is not None and not (isinstance(plx_nss, float) and math.isnan(plx_nss)) and float(plx_nss) > 0:
        plx_used = float(plx_nss); plx_source = 'NSS'
    elif plx_gs is not None and not (isinstance(plx_gs, float) and math.isnan(plx_gs)) and float(plx_gs) > 0:
        plx_used = float(plx_gs); plx_source = 'gaia_source (biased for binaries)'

    P = row.get('period')
    if a_phot is None or plx_used is None or P is None or P <= 0:
        return {'error': 'Missing parallax / period / Thiele-Innes — cannot derive.'}

    a_phot_AU = a_phot / plx_used
    P_yr = float(P) / 365.25
    fM = a_phot_AU ** 3 / P_yr ** 2

    # M_1 prior: user slider overrides the FLAME mass when needed.
    mass_flame = row.get('mass_flame')
    M1 = float(M1_prior)
    if mass_flame is not None and not (isinstance(mass_flame, float) and math.isnan(mass_flame)):
        if mass_flame > 0.05:
            # Keep the slider as the authoritative knob in the UI, but show
            # FLAME mass as supplementary info downstream.
            pass

    M2 = solve_m2(fM, M1)
    cls = mass_class(M2)

    e_val = row.get('eccentricity')
    e_val = float(e_val) if (e_val is not None and not (isinstance(e_val, float) and math.isnan(e_val))) else 0.0

    # ---- Filter #29: SB2 check via non_single_star bits --------------------
    #   bit 1 = astrometric, bit 2 = spectroscopic, bit 4 = eclipsing.
    #   "in_sb2" in consumer.py is a separately-computed flag; here we infer
    #   from non_single_star + nss_solution_type containing 'SB2'.
    nss_type = str(row.get('nss_solution_type') or '')
    in_sb2 = ('SB2' in nss_type) or bool(row.get('in_sb2', False))
    f29 = 'FAIL' if in_sb2 else 'PASS'
    f29_reason = (f'NSS solution type "{nss_type}" contains SB2 marker' if in_sb2
                  else f'NSS solution "{nss_type}" is SB1-class (single-lined)')

    # ---- Filter #30: K-giant / chromatic-bias risk -------------------------
    #   BP-RP > 1.2 OR log g < 2.7 OR spectraltype mentions K / III
    bp_rp = row.get('bp_rp')
    logg = row.get('logg_gspspec_ann') or row.get('logg_gspphot')
    teff = row.get('teff_gspspec_ann') or row.get('teff_gspphot')
    cbias_color = bp_rp is not None and not pd.isna(bp_rp) and float(bp_rp) > 1.2
    cbias_logg = logg is not None and not pd.isna(logg) and float(logg) < 2.7
    # Crude spectral-type proxy: K-giant if Teff ~ 3700-5200 K *and* logg<3
    cbias_kgiant = (teff is not None and not pd.isna(teff) and 3700 <= float(teff) <= 5200
                    and (logg is None or pd.isna(logg) or float(logg) < 3.0))
    cbias_risk = bool(cbias_color or cbias_logg or cbias_kgiant)
    f30 = 'FAIL' if cbias_risk else 'PASS'
    f30_bits = []
    if cbias_color: f30_bits.append(f'BP-RP={bp_rp:.2f} > 1.2')
    if cbias_logg:  f30_bits.append(f'log g={logg:.2f} < 2.7')
    if cbias_kgiant: f30_bits.append(f'K-giant proxy (Teff={teff:.0f} K, logg<3)')
    f30_reason = ', '.join(f30_bits) if f30_bits else 'no chromatic-bias signatures'

    # ---- Filter #31: RV reality check via rv_amplitude_robust vs p-value ---
    K_obs = row.get('rv_amplitude_robust')
    pval = row.get('rv_chisq_pvalue')
    if K_obs is None or pval is None or pd.isna(K_obs) or pd.isna(pval):
        f31, f31_reason = 'NO_DATA', 'rv_amplitude_robust or rv_chisq_pvalue missing'
    elif K_obs > 5 and pval < 0.05:
        f31, f31_reason = 'PASS', f'K_obs={K_obs:.1f} km/s, p={pval:.3g} (significant RV variability)'
    elif K_obs > 5 and pval > 0.5:
        f31, f31_reason = 'FAIL', f'K_obs={K_obs:.1f} km/s but p={pval:.3g} (no variability)'
    else:
        f31, f31_reason = 'AMBIGUOUS', f'K_obs={K_obs}, p={pval} (boundary regime)'

    # ---- Filter #32: joint astrometric + RV consistency --------------------
    f32, sini_implied, K_pred = filter32(K_obs, float(P), e_val, M1, M2)
    if f32 == 'PASS':
        f32_reason = (f'K_obs/K_pred(i=90°) = {sini_implied:.3f} ≤ 1.05 — consistent with '
                      f'orbit at sin(i)={sini_implied:.3f}')
    elif f32 == 'FAIL':
        f32_reason = (f'K_obs/K_pred(i=90°) = {sini_implied:.2f} > 1.05 — K_obs '
                      'dominated by non-orbital noise (pulsations/RVS systematics)')
    else:
        f32_reason = 'Insufficient data (K_obs missing or K_pred=0)'

    # ---- Final tier classification ----------------------------------------
    # The cascade is a COMPANION-DETECTION pipeline. Every successful run
    # describes WHAT companion the data favours; only filter failures land
    # in the "systematic / spurious" buckets.  Wording matters: a planet
    # detection is a detection, not a rejection.
    is_compact_class = cls in ('dormant_BH_candidate', 'dormant_NS_candidate')

    # Handle the impossible-derivation case first — no NSS Orbital row, no
    # Thiele-Innes, no a_phot.  These show up as M_2 ~ 1000 (the upper bound
    # of solve_m2) or NaN.  Common when the source has an Acceleration NSS
    # (Gaia BH3) or SB1-only spectroscopic NSS (BD+38 2040).
    if M2 >= 999.0 or (isinstance(M2, float) and math.isnan(M2)):
        nss_t = str(row.get('nss_solution_type') or '').strip()
        if 'Acceleration' in nss_t:
            tier = ('No NSS Orbital solution (Acceleration channel — '
                    'P likely > Gaia mission baseline; this is the Gaia BH3 regime)')
        elif 'SB1' in nss_t or 'SB2' in nss_t:
            tier = (f'NSS {nss_t} — spectroscopic-only, no astrometric mass function '
                    'available (M_2 from K_1 + M_1 + P + sin(i) needs assumed inclination)')
        else:
            tier = 'NSS Orbital data incomplete — cannot derive M_2'
        return {
            'a_phot_mas': a_phot,
            'a_phot_AU': a_phot_AU if 'a_phot_AU' in dir() else None,
            'P_yr': P_yr if 'P_yr' in dir() else None,
            'fM_msun': fM if 'fM' in dir() else None,
            'M1_msun': M1, 'M2_msun': None,
            'class': 'no_astrometric_M2', 'plx_used': plx_used, 'plx_source': plx_source,
            'e': e_val, 'K_obs': row.get('rv_amplitude_robust'),
            'K_pred_i90': None, 'sini_implied': None,
            'in_sb2': in_sb2, 'cbias_risk': cbias_risk,
            'filter29': f29, 'filter29_reason': f29_reason,
            'filter30': f30, 'filter30_reason': f30_reason,
            'filter31': f31, 'filter31_reason': f31_reason,
            'filter32': 'NO_DATA', 'filter32_reason': 'no NSS orbital solution to compute K_pred from',
            'tier': tier,
        }

    # Filter-failure cases come first because they invalidate the M_2 value.
    if f29 == 'FAIL':
        tier = 'Stellar binary (SB2 detected — luminous secondary)'
    elif f30 == 'FAIL':
        tier = 'K-giant systematic (M_2 likely inflated by chromatic bias)'
    elif f31 == 'FAIL':
        tier = 'Phantom RV signal (no real variability — F#31 catches outlier-driven K_obs)'
    # F#32 only meaningful for stellar+compact-object mass classes — at planet/BD
    # masses K_pred → 0 and sin_i_implied is nonsense.
    elif f32 == 'FAIL' and (M2 >= 0.05 or is_compact_class):
        tier = 'Joint-check failure (M_2 likely overestimated — K_obs > K_pred(i=90°))'
    elif is_compact_class and f31 in ('AMBIGUOUS', 'NO_DATA'):
        tier = ('Tier-2 — compact-object mass but RV follow-up needed '
                f'(class={cls.replace("dormant_", "").replace("_candidate", "")})')
    # All filters pass — classify by mass.
    elif cls == 'dormant_BH_candidate':
        tier = 'Tier-1 BH discovery candidate'
    elif cls == 'dormant_NS_candidate':
        tier = 'Tier-1 NS discovery candidate'
    elif cls == 'WD_or_low_mass_star':
        tier = 'Sub-Ch / massive white-dwarf or low-mass-stellar companion'
    elif cls == 'M_dwarf_companion':
        tier = 'M-dwarf companion detected'
    elif cls == 'BD_candidate':
        tier = 'Brown-dwarf candidate detected'
    elif cls == 'planet_candidate':
        tier = 'Exoplanet candidate detected'
    else:
        tier = f'Detection ({cls})'

    return {
        'a_phot_mas': a_phot,
        'a_phot_AU': a_phot_AU,
        'P_yr': P_yr,
        'fM_msun': fM,
        'M1_msun': M1,
        'M2_msun': M2,
        'class': cls,
        'plx_used': plx_used,
        'plx_source': plx_source,
        'e': e_val,
        'K_obs': K_obs,
        'K_pred_i90': K_pred,
        'sini_implied': sini_implied,
        'in_sb2': in_sb2,
        'cbias_risk': cbias_risk,
        'filter29': f29, 'filter29_reason': f29_reason,
        'filter30': f30, 'filter30_reason': f30_reason,
        'filter31': f31, 'filter31_reason': f31_reason,
        'filter32': f32, 'filter32_reason': f32_reason,
        'tier': tier,
    }


# ---------------------------------------------------------------------------
# Plotly visualizations
# ---------------------------------------------------------------------------

def plot_phase_curve(row: dict, derived: dict) -> go.Figure:
    """Panel 1 — orbital phase diagram with sinusoidal K_1 model curve.

    Gaia DR3 only publishes a scalar ``rv_amplitude_robust`` (= peak-to-trough),
    not a time series.  Convert to semi-amplitude K_1 = rv_amplitude_robust / 2
    (the cascade fix from the methodology re-run), then sketch the eccentric
    RV curve K_1·cos(true_anomaly) using a low-order analytic approximation
    to the true anomaly.  For e > 0.5 this is qualitative only — the real
    curve would need Kepler-equation solution.
    """
    try:
        P = float(row.get('period') or 1.0)
        e = float(derived.get('e') or 0.0)
        K_obs_p2p = float(derived.get('K_obs') or 0.0)  # peak-to-trough from Gaia DR3
    except (TypeError, ValueError):
        return go.Figure().update_layout(title='Phase curve unavailable')
    K1 = K_obs_p2p / 2.0  # semi-amplitude after correction

    phi = np.linspace(0, 1, 400)
    nu = phi * 2 * math.pi
    # Low-order analytic approximation to true anomaly (only valid for moderate e)
    f_true = nu + 2 * e * np.sin(nu) + 1.25 * e * e * np.sin(2 * nu)
    rv_model = K1 * np.cos(f_true)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=phi, y=rv_model, mode='lines',
        name=f'Model K_1·cos f (K_1={K1:.1f} km/s, e={e:.3f})',
        line=dict(color='#1f77b4', width=2),
    ))
    fig.add_hline(y=0, line=dict(color='grey', dash='dot'))
    # Reference: ±K_1 lines so the user can read amplitude off the y-axis
    fig.add_hline(y=K1,  line=dict(color='grey', dash='dot', width=1),
                  annotation_text=f'+K_1 = {K1:.1f}', annotation_position='top right',
                  annotation=dict(font=dict(size=10, color='grey')))
    fig.add_hline(y=-K1, line=dict(color='grey', dash='dot', width=1),
                  annotation_text=f'−K_1 = −{K1:.1f}', annotation_position='bottom right',
                  annotation=dict(font=dict(size=10, color='grey')))

    fig.update_layout(
        title=f'Orbital phase curve — P = {P:.2f} d, e = {e:.3f}',
        xaxis_title='orbital phase φ',
        yaxis_title='RV  (km/s)  [model sketch]',
        height=320, margin=dict(t=40, b=40, l=50, r=20),
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01,
                    bgcolor='rgba(255,255,255,0.7)'),
    )
    return fig


def plot_mass_function(M1: float, fM: float, M2_solved: float) -> go.Figure:
    """Panel 2 — M_2 vs sin(i) curve for the chosen M_1 prior.

    The y-axis range and which threshold lines are drawn adapt to the actual
    mass regime of the candidate.  For a planet (M_2 ~ 0.01 M_⊙) we zoom into
    [0.001, 1]; for a compact-object candidate (M_2 ~ 1-10) we zoom out to
    [0.3, 50].  Threshold labels sit ON the dashed lines.
    """
    sini = np.linspace(0.2, 1.0, 200)  # below sin i ≈ 0.2 the inversion blows up
    M2_curve = []
    for s in sini:
        lo, hi = 1e-6, 1e3   # extend lo so the planet regime fits in the bisection
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if (mid * s) ** 3 > fM * (M1 + mid) ** 2:
                hi = mid
            else:
                lo = mid
        M2_curve.append(0.5 * (lo + hi))

    M2_min_curve = max(min(M2_curve), 1e-5)
    M2_max_curve = max(max(M2_curve), M2_solved or 1e-3)
    # Use the SOLVED M_2 (at sin i = 1) for regime classification — it's the
    # most physically meaningful value.  Max of curve is at sin i = 0.2 and
    # gets inflated by the geometric divergence.
    M2_ref = M2_solved if (M2_solved and M2_solved > 0) else M2_max_curve

    if M2_ref < 0.03:                              # planet / sub-BD regime
        regime = 'planet'
        y_bot, y_top = 5e-4, 0.1
    elif M2_ref < 0.13:                            # brown-dwarf regime
        regime = 'bd'
        y_bot, y_top = 5e-3, 1.0
    elif M2_ref < 0.5:                             # M-dwarf regime
        regime = 'mdwarf'
        y_bot, y_top = 0.02, 3.0
    elif M2_ref < 5.0:                             # WD / NS regime
        regime = 'compact'
        y_bot, y_top = 0.1, max(10.0, M2_max_curve * 1.5)
    else:                                          # NS / BH regime
        regime = 'bh'
        y_bot, y_top = 0.3, min(M2_max_curve * 1.4, 100.0)

    # Mass-regime thresholds with discovery-relevant boundaries.
    # Show in regimes where the threshold falls inside the visible y-window.
    THRESHOLDS = [
        (0.013, 'BD/planet boundary (13 M_Jup)', '#17becf', {'planet', 'bd'}),
        (0.080, 'Hydrogen-burning limit (M-dwarf floor)', '#bcbd22', {'bd', 'mdwarf'}),
        (0.500, 'WD / low-mass-star floor', '#9467bd', {'mdwarf', 'compact', 'bh'}),
        (1.200, 'NS threshold (1.2 M_⊙)', '#8c564b', {'compact', 'bh'}),
        (3.000, 'BH threshold (3.0 M_⊙)', 'black',   {'compact', 'bh'}),
    ]

    # Mass-regime shaded bands (only the ones visible in the current y-range)
    REGIMES = [
        (5e-4, 0.013, '#17becf', 'Planet / sub-BD'),
        (0.013, 0.08, '#e377c2', 'Brown dwarf'),
        (0.08, 0.5,   '#bcbd22', 'M-dwarf'),
        (0.5, 1.2,    '#9467bd', 'WD / low-mass star'),
        (1.2, 3.0,    '#1f77b4', 'NS range'),
        (3.0, 100.0,  '#2ca02c', 'BH range'),
    ]

    fig = go.Figure()
    for lo, hi, colour, label in REGIMES:
        lo_v = max(lo, y_bot); hi_v = min(hi, y_top)
        if hi_v > lo_v:
            fig.add_hrect(y0=lo_v, y1=hi_v, fillcolor=colour, opacity=0.08, line_width=0,
                          annotation_text=label,
                          annotation_position='top left',
                          annotation=dict(font=dict(size=9, color=colour)))

    # The actual mass-function curve
    fig.add_trace(go.Scatter(
        x=sini, y=M2_curve, mode='lines',
        name='M_2(sin i) for chosen M_1',
        line=dict(color='#d62728', width=3),
        hovertemplate='sin i = %{x:.2f}<br>M_2 = %{y:.5g} M_⊙<extra></extra>',
    ))

    # Threshold lines + labels, but only ones that fall in the visible y-range
    for y_thr, label, colour, where in THRESHOLDS:
        if regime not in where: continue
        if not (y_bot <= y_thr <= y_top): continue
        fig.add_shape(type='line', x0=0.2, x1=1.0, y0=y_thr, y1=y_thr,
                      line=dict(color=colour, dash='dash', width=1.5))
        fig.add_annotation(x=0.7, y=y_thr, text=label, showarrow=False,
                            bgcolor='rgba(255,255,255,0.85)',
                            font=dict(size=10, color=colour),
                            xanchor='left', yanchor='middle')

    # Solved M_2 at sin i = 1
    if M2_solved is not None and y_bot <= M2_solved <= y_top:
        fig.add_trace(go.Scatter(
            x=[1.0], y=[M2_solved], mode='markers',
            name=f'sin i = 1  (M_2 = {M2_solved:.4g})',
            marker=dict(size=14, color='#2ca02c', symbol='star',
                        line=dict(color='black', width=1)),
            hovertemplate='sin i = 1<br>M_2 = %{y:.5g} M_⊙<extra></extra>',
        ))

    # Pretty-print f(M) — switch to scientific notation when ≪ 1
    if fM is not None and fM > 0:
        fM_str = f'{fM:.4f}' if fM >= 1e-3 else f'{fM:.3e}'
    else:
        fM_str = 'n/a'
    fig.update_layout(
        title=f'Mass function: M_2 vs sin i &nbsp;(f(M) = {fM_str} M_⊙, M_1 = {M1} M_⊙)',
        xaxis_title='sin i', yaxis_title='M_2  (M_⊙)',
        xaxis=dict(range=[0.2, 1.02]),
        yaxis=dict(type='log', range=[math.log10(y_bot), math.log10(y_top)]),
        height=340, margin=dict(t=50, b=40, l=55, r=20),
        legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99,
                    bgcolor='rgba(255,255,255,0.7)'),
    )
    return fig


def plot_hr(row: dict, derived: dict) -> go.Figure:
    """Panel 3 — HR diagram (M_G vs BP-RP) with calibrated MS / giant tracks.

    Sequences follow Pecaut & Mamajek 2013 (with light extrapolation):
      MS:    M_G ≈ 4.83 + 3.1·(BP-RP)        for -0.3 ≤ BP-RP ≤ 4
      RGB:   M_G ≈ 1.5 − 0.4·(BP-RP) + 0.5·(BP-RP)²  (red-clump-anchored sketch)
    These are not isochrones — they're reference tracks to place the target.
    """
    plx_raw = row.get('parallax')
    try:
        plx = float(plx_raw) if plx_raw is not None else 1.0
        if math.isnan(plx) or plx <= 0: plx = 1.0
    except (TypeError, ValueError):
        plx = 1.0
    G = float(row.get('phot_g_mean_mag') or 10.0)
    bp_rp_raw = row.get('bp_rp')
    try:
        bp_rp = float(bp_rp_raw) if bp_rp_raw is not None else 1.0
        if math.isnan(bp_rp): bp_rp = 1.0
    except (TypeError, ValueError):
        bp_rp = 1.0
    M_G = G + 5 * math.log10(plx / 100.0)  # M_G = G + 5 log(plx[mas]/100)

    bp_seq = np.linspace(-0.3, 4.0, 100)
    # Calibrated MS — Pecaut & Mamajek 2013-ish:
    #   BP-RP=0   → M_G=+1  (A0V)
    #   BP-RP=1   → M_G=+5  (G2V)
    #   BP-RP=2   → M_G=+9  (K5V)
    #   BP-RP=3   → M_G=+12 (M3V)
    #   BP-RP=4   → M_G=+15 (M5V)
    M_ms = 1.0 + 3.5 * bp_seq + 0.2 * bp_seq * np.maximum(bp_seq - 1.5, 0)
    # Giant branch — anchored to red clump (BP-RP≈1.2, M_G≈+0.6) extending up to RGB tip
    M_giant = 0.6 + 0.3 * (bp_seq - 1.2) - 1.0 * np.maximum(bp_seq - 1.2, 0)

    cls = derived.get('class', 'unknown')
    cls_color = {
        'dormant_BH_candidate': '#000000', 'dormant_NS_candidate': '#9467bd',
        'WD_or_low_mass_star': '#1f77b4', 'M_dwarf_companion': '#d62728',
        'BD_candidate': '#e377c2', 'planet_candidate': '#17becf',
    }.get(cls, '#7f7f7f')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bp_seq, y=M_ms, mode='lines',
                              name='Main sequence (sketch)',
                              line=dict(color='lightblue', width=2)))
    fig.add_trace(go.Scatter(x=bp_seq, y=M_giant, mode='lines',
                              name='Giant branch (sketch)',
                              line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=[bp_rp], y=[M_G], mode='markers+text',
                              name=f'Target ({cls.replace("_", " ")})',
                              text=[f'  M_G={M_G:.2f}'], textposition='middle right',
                              marker=dict(size=16, color=cls_color, symbol='circle',
                                          line=dict(color='white', width=2)),
                              hovertemplate=(f'BP−RP = {bp_rp:.3f}<br>'
                                              f'M_G = {M_G:.2f}<br>'
                                              f'class = {cls}<extra></extra>')))
    fig.update_layout(
        title='HR diagram (BP-RP vs absolute G-band magnitude)',
        xaxis_title='BP-RP (colour)', yaxis_title='M_G (absolute magnitude)',
        xaxis=dict(range=[-0.5, 4.2]),
        yaxis=dict(autorange='reversed', range=[16, -3]),
        height=340, margin=dict(t=40, b=40, l=55, r=20),
        legend=dict(yanchor='bottom', y=0.02, xanchor='right', x=0.99,
                    bgcolor='rgba(255,255,255,0.7)'),
    )
    return fig


def likely_object_type(derived: dict, row: dict) -> list[tuple[str, float, str]]:
    """Return a probability spectrum [(label, prob, rationale), ...] for what
    the companion most likely is, given the derivation outcome.

    Heuristic — uses M_2, cascade tier, filter outcomes, and primary parameters
    to weight 6 broad identity classes.  This is the same logic the conversation
    used for HD 1957; it generalises to any candidate.
    """
    M2_raw = derived.get('M2_msun')
    if M2_raw is None:
        return [
            ('No mass-function derivation available', 1.0,
             'NSS Orbital row missing — likely Acceleration channel (Gaia BH3 class, '
             'P > Gaia baseline) or SB1/SB2 spectroscopic-only solution.  Cannot infer '
             'companion type from astrometric mass function.'),
        ]
    try:
        M2 = float(M2_raw)
        if math.isnan(M2):
            return [('Mass derivation NaN — incomplete NSS data', 1.0, '')]
    except (TypeError, ValueError):
        return [('Mass derivation failed', 1.0, '')]
    cls = derived.get('class', 'unknown')
    f29 = derived.get('filter29', 'NO_DATA')
    f30 = derived.get('filter30', 'NO_DATA')
    f32 = derived.get('filter32', 'NO_DATA')
    bp_rp = row.get('bp_rp')
    ruwe = row.get('ruwe')
    bp_xs = row.get('phot_bp_rp_excess_factor')

    is_kgiant_risk = (f30 == 'FAIL')
    high_ruwe = ruwe is not None and not pd.isna(ruwe) and float(ruwe) > 5
    sb2_light = bp_xs is not None and not pd.isna(bp_xs) and float(bp_xs) > 1.3
    very_high_ruwe = ruwe is not None and not pd.isna(ruwe) and float(ruwe) > 10

    # Sub-stellar regime (planet / BD)
    if M2 < 0.5:
        return [
            ('Sub-stellar / planet', 0.90,
             f'M_2={M2:.3f} below stellar minimum — exoplanet or brown dwarf'),
            ('Hierarchical triple disguising larger M_2', 0.05,
             'Possible if inner unresolved binary present'),
            ('Phantom astrometric signal (Filter #31)', 0.05,
             'Possible if rv_amplitude_robust outlier-driven'),
        ]

    # M-dwarf / low-mass stellar
    if 0.5 <= M2 < 1.2:
        return [
            ('M-dwarf or K-dwarf companion', 0.70,
             'Low-mass MS companion, would be visible at AO ~50 mas'),
            ('Helium-core / sub-Chandrasekhar WD', 0.20,
             'Possible if primary already evolved (post-mass-transfer)'),
            ('Chromatic-inflated even smaller star', 0.10,
             'If Filter #30 actually under-corrected'),
        ]

    # NS-mass regime — heaviest interpretation pressure
    if 1.2 <= M2 < 3.0:
        if is_kgiant_risk:
            # K-giant primary: very likely chromatic; chromatic-corrected M_2 → WD
            return [
                ('Massive CO/ONe white dwarf (post-mass-transfer)', 0.50,
                 'e≈0 circular orbit implies tidal circularisation via RLOF → WD; '
                 'cascade M_2 inflated by K-giant chromatic bias'),
                ('Heavy mass-gap neutron star (ECSN-formed)', 0.20,
                 'If chromatic correction is small, cascade may be correct; '
                 'would exceed PSR J0740 2.08 M_⊙ NS record — Nature-class'),
                ('Hierarchical triple (inner short-P binary + outer K-giant)', 0.15,
                 f'RUWE={ruwe} elevated; inner pair masquerades as single M_2'),
                ('Hidden K/M-dwarf companion', 0.10,
                 'If full 4 UMi-class chromatic correction (2× a_phot), M_2 → 0.7–0.9'),
                ('WD-WD inner binary + K-giant outer', 0.03,
                 'Rare configuration'),
                ('Sub-Chandrasekhar WD', 0.02,
                 'Light He-core WD progenitor'),
            ]
        else:
            return [
                ('Neutron star (canonical or massive)', 0.55,
                 f'F-G primary with clean F#30; M_2={M2:.2f} sits in NS mass range. '
                 'No chromatic concerns.'),
                ('Massive CO white dwarf near Chandrasekhar limit', 0.25,
                 'If primary has been through prior mass-transfer episode'),
                ('Mass-gap object (2.5–3 M_⊙ if true)', 0.10,
                 'Border between heavy NS and lightest BH'),
                ('Stellar companion masked by high inclination', 0.05,
                 'If sin(i) underestimated by NSS fit'),
                ('Hierarchical triple', 0.05,
                 f'Possible if RUWE={ruwe} or excess-noise abnormal'),
            ]

    # BH-mass regime
    if 3.0 <= M2 < 5.0:
        return [
            ('Low-mass stellar black hole', 0.55 if not is_kgiant_risk else 0.20,
             'Mass-gap edge — extends the lower BH mass function'),
            ('High-mass NS (TOV-limit-exceeding)', 0.15,
             'Astrophysically possible but no precedent above ~2.5 M_⊙'),
            ('Hierarchical triple (sum of stars)', 0.15,
             f'Total mass of unresolved inner binary; RUWE={ruwe}'),
            ('Chromatic-inflated stellar companion', 0.30 if is_kgiant_risk else 0.10,
             'K-giant chromatic risk inflates M_2 by up to 3×'),
            ('Hot subdwarf + accretion disc', 0.05,
             'Rare; check UV photometry'),
        ]

    # Heavy BH (stellar-mass)
    if M2 >= 5.0:
        return [
            ('Stellar-mass black hole (Gaia BH1-like)', 0.65 if not is_kgiant_risk else 0.25,
             f'M_2={M2:.1f} typical of dormant BH binaries; F#30 {("pass" if not is_kgiant_risk else "fail (chromatic risk)")}'),
            ('Hot subdwarf primary + tighter inner binary', 0.10,
             'Check primary UV/optical colours'),
            ('Hierarchical triple of 3 stars summing to >5 M_⊙', 0.15,
             f'RUWE={ruwe}; check ipd_frac_multi_peak'),
            ('Chromatic-inflated giant companion', 0.30 if is_kgiant_risk else 0.05,
             'K-giant chromatic risk'),
            ('AGN background contamination', 0.05,
             'Rare for V<13 sources'),
        ]

    return [('Unknown — cascade did not return a usable mass', 1.0, '')]


def plot_cascade_ladder(derived: dict) -> go.Figure:
    """Panel 4 — verdict ladder for Filters #29 / #30 / #31 / #32."""
    filters = ['#29 SB2', '#30 K-giant/chromatic', '#31 RV reality', '#32 Joint K_obs/K_pred']
    verdicts = [derived['filter29'], derived['filter30'], derived['filter31'], derived['filter32']]
    reasons = [derived['filter29_reason'], derived['filter30_reason'],
               derived['filter31_reason'], derived['filter32_reason']]
    colors = []
    for v in verdicts:
        if v == 'PASS': colors.append('#2ca02c')
        elif v == 'FAIL': colors.append('#d62728')
        elif v == 'AMBIGUOUS': colors.append('#ff7f0e')
        else: colors.append('#7f7f7f')
    fig = go.Figure(go.Bar(
        x=[1, 1, 1, 1], y=filters, orientation='h',
        text=[f'<b>{v}</b><br><span style="font-size:10px">{r}</span>'
              for v, r in zip(verdicts, reasons)],
        textposition='inside', insidetextanchor='start',
        marker=dict(color=colors), showlegend=False,
    ))
    fig.update_layout(
        title='Cascade verdict ladder',
        xaxis=dict(visible=False, range=[0, 1]),
        height=300, margin=dict(t=40, b=20, l=180, r=20),
    )
    return fig


# ---------------------------------------------------------------------------
# Streamlit page
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title='Gaia DR3 Dormant Compact-Object Cascade',
                       page_icon=':milky_way:', layout='wide')

    st.title('Gaia DR3 Dormant Compact-Object Cascade')
    st.caption('Filters #29 – #32 applied to a single Gaia DR3 source.  '
               'Mirrors the bulk pipeline in `scripts/streaming/consumer.py`.')

    with st.sidebar:
        st.header('Input')

        # ---- Benchmark dropdown — pre-fill from known-nature catalog -------
        benchmarks = load_benchmarks()
        bench_options = [('— pick a benchmark —', '', '')]
        for grp in benchmarks.get('groups', []):
            grp_label = grp.get('label', '')
            for item in grp.get('items', []):
                bench_options.append(
                    (f"[{grp_label[:18]}] {item['name']}",
                     str(item['source_id']),
                     f"{item.get('expected_tier','?')} | M_2_exp={item.get('M_2_expected','?')} | "
                     f"{item.get('primary_sp','')} | {item.get('notes','')}")
                )
        bench_pick = st.selectbox(
            'Benchmark (loads source_id below)',
            options=range(len(bench_options)),
            format_func=lambda i: bench_options[i][0],
            help='Pre-fill the input with a known-nature object for verification.',
        )
        chosen_sid_pref = bench_options[bench_pick][1]

        sid_text = st.text_input(
            'Object name or Gaia DR3 source_id',
            value=chosen_sid_pref or str(DEMO_SOURCE_ID),
            placeholder='HD 1957  ·  HIP 1886  ·  4 UMi  ·  Gaia BH1  ·  2543788153077017344',
            help='Accepts any SIMBAD-resolvable name (HD/HIP/HR/TYC/BD/Gaia BH names) '
                 'OR a 19-digit Gaia DR3 source_id directly.',
        )
        if chosen_sid_pref:
            st.caption(bench_options[bench_pick][2])

        M1_prior = st.slider('M_1 prior (M_⊙)', 0.5, 3.0, 1.5, 0.1,
                              help='Mass of the visible primary used to invert the mass function')
        use_live = st.checkbox('Try live Gaia ADQL (otherwise use sample)',
                                value=bool(chosen_sid_pref),
                                help='Live queries can take 10–60s; uncheck for instant demo.')
        run = st.button('Run cascade', type='primary', use_container_width=True)
        st.divider()
        st.caption('Tip — `2543788153077017344` is HD 1957, the bundled offline demo. '
                   'Other benchmarks above need live Gaia ADQL.')

    if not run:
        st.info('Enter a Gaia DR3 source_id in the sidebar and press **Run cascade**.')
        st.markdown(
            '**About this tool**\n\n'
            'Given a single Gaia DR3 source it:\n'
            '1. Pulls `gaia_source` + `nss_two_body_orbit` + `astrophysical_parameters_supp`\n'
            '2. Derives the photocentric semi-major axis from Thiele-Innes (A, B, F, G)\n'
            '3. Computes the mass function *f(M)* and solves M_2 given an M_1 prior\n'
            '4. Runs Filters **#29 SB2**, **#30 K-giant chromatic**, **#31 RV reality**, **#32 joint K_obs/K_pred**\n'
            '5. Tiers the candidate as Tier-1 BH, Tier-1 NS, Tier-2, Demoted, or Rejected.\n')
        return

    # ----------------------------- resolve input → source_id ---------------
    with st.spinner('Resolving identifier (SIMBAD → Gaia DR3) ...'):
        sid, resolved_name, resolve_msg = resolve_input_to_source_id(sid_text)
    if sid is None:
        st.error(resolve_msg)
        st.info('Tip: try a different identifier (HD/HIP/HR/TYC/BD numbers, or a 19-digit Gaia DR3 source_id).')
        return
    st.caption(f'🔎 {resolve_msg}')

    # ----------------------------- fetch data -----------------------------
    row: dict | None = None
    source_label = 'sample (offline)'
    if use_live:
        with st.spinner('Querying Gaia DR3 via astroquery.gaia ...'):
            row = query_gaia_live(sid)
        if row is not None:
            source_label = 'Gaia DR3 (live)'
    if row is None:
        if sid != DEMO_SOURCE_ID:
            st.warning(f'No live data — and sample only contains source_id={DEMO_SOURCE_ID} (HD 1957). '
                       'Showing the sample row instead.')
        row = load_sample_row()
        source_label = 'sample (offline)'

    sid_in_row = row.get('source_id', sid)
    try:
        sid_display = int(sid_in_row)
    except (TypeError, ValueError):
        sid_display = sid
    st.success(f'Data source: **{source_label}**  ·  resolved name: **{resolved_name}**  ·  '
               f'source_id = `{sid_display}`')

    # ----------------------------- derive ---------------------------------
    derived = derive_one(row, M1_prior)
    if 'error' in derived:
        st.error(derived['error'])
        with st.expander('Raw row'):
            st.dataframe(pd.DataFrame([row]).T.rename(columns={0: 'value'}))
        return

    # ----------------------------- top KPIs -------------------------------
    # Short labels keep the metric box from clipping ("Neutron sta…" issue).
    # When a filter fires, we annotate the KPIs with ⚠️ to remind the user
    # the raw M_2 is unreliable; the cascade still surfaces what the data
    # produces so power users can see the magnitude of any systematic.
    CLASS_SHORT = {
        'dormant_BH_candidate':  'BH cand.',
        'dormant_NS_candidate':  'NS cand.',
        'WD_or_low_mass_star':   'WD / low-M',
        'M_dwarf_companion':     'M-dwarf',
        'BD_candidate':          'Brown dwarf',
        'planet_candidate':      'Exoplanet',
        'no_astrometric_M2':     'no NSS Orbital',
    }
    companion_label = CLASS_SHORT.get(derived['class'], derived['class'].replace('_', ' ')[:14])

    # If any filter fails the M_2 is "raw" — warn the user
    filter_failed = any(derived.get(f) == 'FAIL' for f in ('filter29', 'filter30', 'filter31', 'filter32'))

    def fmt(v, prec=3):
        if v is None: return '—'
        try:
            if math.isnan(float(v)): return '—'
        except (TypeError, ValueError):
            return '—'
        return f'{float(v):.{prec}f}'

    m2_str = fmt(derived.get('M2_msun'), 3)
    if filter_failed and m2_str != '—':
        m2_str = f'{m2_str} ⚠'

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric('M_2 (M_⊙)', m2_str,
              help='Raw cascade output at sin i = 1 (lower bound). '
                   'See the "M_2 (isotropic prior)" row below for the inclination-marginalized range. '
                   '⚠ = unreliable because a systematic filter fired.')
    c2.metric('f(M) (M_⊙)', fmt(derived.get('fM_msun'), 4))
    c3.metric('a_phot (mas)', fmt(derived.get('a_phot_mas'), 3))
    c4.metric('sin i implied', fmt(derived.get('sini_implied'), 3))
    c5.metric('Mass class',
              companion_label + (' ⚠' if filter_failed and companion_label not in ('no NSS Orbital',) else ''),
              help='⚠ = mass class derived from a raw M_2 that a cascade filter '
                   'has flagged as unreliable.  The "Likely companion type" panel below '
                   'gives the probability spectrum after correcting for the systematic.')

    # M_2 range under isotropic inclination prior — answers "what's the actual
    # mass range?".  The headline M_2 metric above is the sin i = 1 (edge-on)
    # value, which is a strict LOWER bound.  Marginalising over cos i ∈ [0, 1]
    # gives the 16/50/84% range a follow-up observer should plan around.
    fM_val = derived.get('fM_msun')
    if fM_val is not None and not (isinstance(fM_val, float) and math.isnan(fM_val)):
        m2_range = m2_range_isotropic_sini(float(fM_val), float(M1_prior), n=10000)
        if m2_range['p50'] is not None:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric('M_2 16% (M_⊙)', f"{m2_range['p16']:.3f}",
                       help='16th percentile under isotropic inclination prior — '
                            'i.e. 84% of equally-likely inclinations give M_2 ≥ this value.')
            r2.metric('M_2 median (M_⊙)', f"{m2_range['p50']:.3f}",
                       help='Median M_2 marginalising over cos i ∈ [0, 1] uniformly. '
                            'Half of inclinations give a heavier companion, half lighter.')
            r3.metric('M_2 84% (M_⊙)', f"{m2_range['p84']:.3f}",
                       help='84th percentile — only 16% of equally-likely inclinations '
                            'give a heavier companion.')
            r4.metric('M_2 16-84 range',
                       f"[{m2_range['p16']:.2f}, {m2_range['p84']:.2f}] M_⊙",
                       help='1σ-equivalent range marginalising over inclination. '
                            'Note: this assumes M_1 is exact and ignores any additional '
                            'evidence (RV variability, ellipsoidal photometry) that would '
                            'further constrain inclination. For tighter posteriors see '
                            'the per-target dossiers in docs/dossiers/.')

    # Verdict banner — colour by category
    #   green  = compact-object discovery candidate (Tier-1 BH/NS)
    #   blue   = confirmed companion at non-discovery mass (WD / M-dwarf / BD / planet)
    #   amber  = needs RV follow-up (Tier-2)
    #   red    = systematic / spurious (filter failure)
    tier = derived['tier']
    if tier.startswith('Tier-1'):
        st.success(f'### **{tier}**', icon='🎯')
        st.caption('All cascade filters pass. M_2 sits in the dormant compact-object range — '
                   'a discovery target worth RV follow-up. Use this for VERIFICATION of known dormant '
                   'BH/NS systems (e.g. Gaia BH1) or DISCOVERY of new ones.')
    elif (tier.startswith('Sub-Ch') or tier.startswith('M-dwarf')
          or tier.startswith('Brown-dwarf') or tier.startswith('Exoplanet')):
        st.info(f'### **{tier}**', icon='🪐')
        st.caption('All cascade filters pass — this is a real companion detection, just below '
                   'the dormant-compact-object mass threshold. Use this mode for RECOVERY of known '
                   'planet hosts (HD 81040, HD 111232) or SB1 binaries; the mass-class label tells '
                   'you the companion type the data favours.')
    elif tier.startswith('Tier-2'):
        st.warning(f'### **{tier}**', icon='🔍')
        st.caption('Mass class is compact-object but RV evidence is weak — needs spectroscopic '
                   'follow-up. Promote to Tier-1 if K_1 measured.')
    elif tier.startswith('No NSS Orbital') or tier.startswith('NSS Orbital data') or tier.startswith('NSS '):
        # No mass-function derivation possible — not a failure, just missing data
        st.info(f'### **{tier}**', icon='📭')
        st.caption('No astrometric mass function available for this source. Gaia DR3 detected '
                   'binarity but the NSS solution channel does not provide the inputs the cascade '
                   'needs (Thiele-Innes constants).  Common cases: Gaia BH3-class long-period orbits '
                   '(P > Gaia mission baseline → Acceleration solution); SB1/SB2 spectroscopic-only '
                   'NSS rows.  Look up the source in published RV-derived orbital catalogs instead.')
    else:
        # Filter failure — systematic / spurious
        st.error(f'### **{tier}**', icon='⚠️')
        st.caption('A cascade filter fired — the M_2 value reported above is the RAW astrometric '
                   'derivation (no chromatic correction applied), and is unreliable. The '
                   '"Likely companion type" panel below gives the probability spectrum *after* '
                   'accounting for the systematic — e.g. for HD 1957 / 4 UMi K-giant cases, the '
                   'true companion is most likely a massive CO/ONe WD rather than the raw NS-mass label.')

    # Tier ladder reference — answers "demoted from what?"
    with st.expander('Where this verdict sits on the tier ladder',
                     expanded=tier.startswith('Demoted') or tier.startswith('Rejected')):
        st.caption('Cascade ladder — every Tier-1 candidate has *passed* all four filters; '
                   '"Demoted" means a mass candidate that failed somewhere in F#29/F#30/F#32.')
        rows = []
        for label, color, descr, match_prefix in TIER_LADDER:
            this_row = tier.startswith(match_prefix)
            marker = '➤  ' if this_row else '   '
            rows.append({'': marker, 'tier': label, 'meaning': descr})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ----------------------------- likely object type ---------------------
    st.subheader('Likely companion type')
    st.caption('Heuristic probability spectrum based on M_2, primary type, and filter outcomes. '
               'Not a posterior — meant as a sanity check on the cascade verdict.')
    obj_types = likely_object_type(derived, row)
    obj_df = pd.DataFrame(obj_types, columns=['identity', 'probability', 'rationale'])
    # Bar chart of probabilities
    fig_obj = go.Figure(go.Bar(
        x=obj_df['probability'] * 100, y=obj_df['identity'],
        orientation='h', text=[f'{p*100:.0f}%' for p in obj_df['probability']],
        textposition='outside',
        marker=dict(color=['#2ca02c' if p >= 0.4 else '#1f77b4' if p >= 0.15 else '#7f7f7f'
                          for p in obj_df['probability']]),
        showlegend=False,
    ))
    fig_obj.update_layout(
        xaxis_title='probability (%)',
        xaxis=dict(range=[0, max(obj_df['probability']) * 130]),
        height=70 + 38 * len(obj_df),
        margin=dict(t=20, b=30, l=10, r=30),
        yaxis=dict(autorange='reversed'),
    )
    col_a, col_b = st.columns([3, 4])
    col_a.plotly_chart(fig_obj, use_container_width=True)
    col_b.dataframe(obj_df[['identity', 'rationale']], hide_index=True, use_container_width=True)

    # ----------------------------- plots ----------------------------------
    if derived.get('M2_msun') is not None and derived.get('fM_msun') is not None:
        g1, g2 = st.columns(2)
        g1.plotly_chart(plot_phase_curve(row, derived), use_container_width=True)
        g2.plotly_chart(plot_mass_function(M1_prior, derived['fM_msun'], derived['M2_msun']),
                        use_container_width=True)
        g3, g4 = st.columns(2)
        g3.plotly_chart(plot_hr(row, derived), use_container_width=True)
        g4.plotly_chart(plot_cascade_ladder(derived), use_container_width=True)
    else:
        st.info('Plots disabled — no mass function available for this source. '
                'Either the NSS Orbital row is missing (Acceleration / SB1 / SB2 only) '
                'or required astrometry is incomplete.  The cascade ladder still '
                'shows individual filter outcomes below.')
        st.plotly_chart(plot_cascade_ladder(derived), use_container_width=True)

    # ----------------------------- bulk-catalog cross-reference ----------
    # Always show what the bulk v2 + v3 runs said about this source_id, even
    # when the single-source derivation couldn't produce a verdict.  This is
    # critical for sources in degenerate channels (SB1-only / Acceleration-
    # only) — e.g. Gaia DR3 77413727493690112 = HD 12871 has no Thiele-Innes
    # in the Orbital table but DOES appear in v3 as a top BH-mass candidate
    # (M_2_median ≈ 8 M_⊙ with period degeneracy).
    bulk = lookup_in_bulk_catalogs(int(sid_display))
    any_bulk_hit = any(bulk.get(k) for k in ('v2', 'v3', 'v2_alt', 'v2_relaxed'))
    if any_bulk_hit:
        st.subheader('🔗 Cross-reference: bulk-cascade catalogs')
        st.caption('This source appears in one or more bulk-cascade outputs. v2 = production NSS Orbital + '
                   'AstroSpectroSB1 (56,100 sources). v3 = NSS Acceleration channel (16,949). '
                   'v2_alt = OrbitalAlternative / Validated ingest (629). '
                   'v2_relaxed = expanded producer cuts G<15, plx>0.5 (71,346 new rows). '
                   'The bulk verdicts are shown below — these may add or revise the single-source verdict.')

        if bulk.get('v2'):
            r2 = bulk['v2']
            tier_v2 = r2.get('tier_v2', '(missing)')
            M2 = r2.get('M2_msun_v2')
            M2_str = f'{float(M2):.3f}' if M2 is not None and not pd.isna(M2) else '—'
            sini = r2.get('sini_implied_v2')
            sini_str = f'{float(sini):.3f}' if sini is not None and not pd.isna(sini) else '—'
            st.markdown(f"**v2 (NSS Orbital + AstroSpectroSB1)** &nbsp;·&nbsp; tier = **{tier_v2}** &nbsp;·&nbsp; "
                         f"M_2 = {M2_str} M_⊙ &nbsp;·&nbsp; sin i = {sini_str} &nbsp;·&nbsp; "
                         f"F#29={r2.get('filter29_v2','?')} F#30={r2.get('filter30_v2','?')} "
                         f"F#31={r2.get('filter31_v2','?')} F#32={r2.get('filter32_v2','?')}")

        if bulk.get('v2_alt'):
            ra = bulk['v2_alt']
            tier_alt = ra.get('tier_v2', '(missing)')
            M2_alt = ra.get('M2_msun_v2')
            M2_alt_str = f'{float(M2_alt):.3f}' if M2_alt is not None and not pd.isna(M2_alt) else '—'
            nss_type = ra.get('nss_solution_type', ra.get('nss_solution_type_v2', '?'))
            st.markdown(f"**v2_alt (OrbitalAlternative / Validated channel)** &nbsp;·&nbsp; "
                         f"nss_solution_type = `{nss_type}` &nbsp;·&nbsp; "
                         f"tier = **{tier_alt}** &nbsp;·&nbsp; M_2 = {M2_alt_str} M_⊙")
            st.caption('ℹ Pulled from `nss_two_body_orbit` rows that the production v2 producer '
                       'skipped because `rv_amplitude_robust` is null for the entire OrbitalAlternative '
                       'class. F#31/F#32 are NO_DATA → cascade caps at Tier-2 even for plausible '
                       'compact-mass companions. Verify via HGCA / Kervella / archival RV.')

        if bulk.get('v2_relaxed'):
            rr = bulk['v2_relaxed']
            tier_rel = rr.get('tier_v2', '(missing)')
            M2_rel = rr.get('M2_msun_v2')
            M2_rel_str = f'{float(M2_rel):.3f}' if M2_rel is not None and not pd.isna(M2_rel) else '—'
            sini_rel = rr.get('sini_implied_v2')
            sini_rel_str = f'{float(sini_rel):.3f}' if sini_rel is not None and not pd.isna(sini_rel) else '—'
            st.markdown(f"**v2_relaxed (G<15, plx>0.5 expansion)** &nbsp;·&nbsp; tier = **{tier_rel}** &nbsp;·&nbsp; "
                         f"M_2 = {M2_rel_str} M_⊙ &nbsp;·&nbsp; sin i = {sini_rel_str}")

        if bulk.get('v3'):
            r3 = bulk['v3']
            tier3 = r3.get('tier_v3', '(missing)')
            # v3 produces a (min, median, max) over the assumed-period grid
            M2_min = r3.get('M2_min')
            M2_med = r3.get('M2_median')
            M2_max = r3.get('M2_max')
            def fp(v): return f'{float(v):.2f}' if v is not None and not pd.isna(v) else '—'
            st.markdown(
                f"**v3 (NSS Acceleration channel — BH3-regime)** &nbsp;·&nbsp; "
                f"tier = **{tier3}** &nbsp;·&nbsp; "
                f"M_2 over assumed P ∈ [3, 100] yr: "
                f"min = **{fp(M2_min)}**, **median = {fp(M2_med)}**, max = {fp(M2_max)} M_⊙"
            )
            if M2_med is not None and not pd.isna(M2_med) and float(M2_med) >= 3.0:
                st.warning(
                    f'⚠ The v3 acceleration channel ranks this source as a **BH-mass-median candidate** '
                    f'(M_2_median = {fp(M2_med)} M_⊙). The period is degenerate without an orbital '
                    f'solution, so confirmation requires either (a) long-baseline RV monitoring to pin '
                    f'down P, or (b) cross-check against any SB1 row in nss_two_body_orbit '
                    f'(if K_1 + P are both available, the spectroscopic mass function collapses '
                    f'the v3 estimate and may diagnose a hierarchical triple).'
                )

    else:
        # Source wasn't in any bulk run.  Most likely it's in NSS but outside
        # the cuts (e.g. low significance, no NSS, or Eclipsing channel).
        st.caption('ℹ This source was not in any bulk-cascade run (v2, v2_alt, v2_relaxed, v3). '
                   'Either no NSS solution at all, or the NSS channel is not covered by the current '
                   'cascade scope (e.g. NSS Eclipsing).')

    # ----------------------------- HGCA lookup ----------------------------
    st.subheader('Hipparcos-Gaia Catalog of Accelerations (Brandt 2021)')
    hip_raw = row.get('hip')
    hip_val: int | None
    try:
        hip_val = int(hip_raw) if hip_raw is not None and not pd.isna(hip_raw) else None
    except (TypeError, ValueError):
        hip_val = None
    with st.spinner('Vizier J/ApJS/254/42/catalog ...'):
        hgca = query_hgca(hip_val, timeout_s=20)
    if isinstance(hgca, str):
        st.info(hgca)
    else:
        st.dataframe(pd.DataFrame([hgca]).T.rename(columns={0: 'value'}), use_container_width=True)

    # ----------------------------- tables ---------------------------------
    with st.expander('Derived parameters'):
        derived_disp = {k: v for k, v in derived.items() if not k.endswith('_reason')}
        st.dataframe(pd.DataFrame([derived_disp]).T.rename(columns={0: 'value'}),
                     use_container_width=True)

    with st.expander('Filter reasons (verbatim)'):
        st.json({k: derived[k] for k in derived if k.startswith('filter') and '_reason' in k})

    with st.expander('Gaia DR3 row (gaia_source + AP)'):
        gaia_cols = ['source_id', 'ra', 'dec', 'l', 'b', 'parallax', 'pmra', 'pmdec',
                      'phot_g_mean_mag', 'bp_rp', 'ruwe', 'astrometric_excess_noise_sig',
                      'non_single_star', 'radial_velocity',
                      'teff_gspphot', 'logg_gspphot',
                      'teff_gspspec_ann', 'logg_gspspec_ann', 'mh_gspspec_ann',
                      'radius_flame_spec', 'lum_flame_spec', 'evolstage_flame_spec']
        gaia_disp = {c: row.get(c) for c in gaia_cols if c in row}
        st.dataframe(pd.DataFrame([gaia_disp]).T.rename(columns={0: 'value'}),
                     use_container_width=True)

    with st.expander('NSS solution row (nss_two_body_orbit)'):
        nss_cols = ['nss_solution_type', 'period', 'eccentricity',
                     'a_thiele_innes', 'b_thiele_innes',
                     'f_thiele_innes', 'g_thiele_innes', 'significance',
                     'rv_amplitude_robust', 'rv_chisq_pvalue', 'rv_nb_transits']
        nss_disp = {c: row.get(c) for c in nss_cols if c in row}
        st.dataframe(pd.DataFrame([nss_disp]).T.rename(columns={0: 'value'}),
                     use_container_width=True)

    with st.expander('Full input row (everything we pulled)'):
        st.dataframe(pd.DataFrame([row]).T.rename(columns={0: 'value'}),
                     use_container_width=True)


if __name__ == '__main__':
    main()

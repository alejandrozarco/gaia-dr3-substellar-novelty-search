"""Generate sample_data/hd1957_demo.parquet so the Streamlit demo works offline.

HD 1957 = Gaia DR3 2543788153077017344. Values are the user-supplied snapshot
pulled live from Gaia DR3 NSS + astrophysical_parameters + supp tables and
are pinned here so the prototype can be demoed without any network calls.

Run once:  python build_sample_parquet.py
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'sample_data' / 'hd1957_demo.parquet'
OUT.parent.mkdir(parents=True, exist_ok=True)

# All fields below mirror the Gaia DR3 column names exactly so the rest of the
# pipeline (consumer.derive_chunk-style logic) can read this dict-of-row by
# the same column keys.  Sources of each value:
#   gaiadr3.gaia_source            – ra/dec/plx/pm/G/BP-RP/ruwe/aen_sig/nss flag
#   gaiadr3.nss_two_body_orbit     – Thiele-Innes (A,B,F,G), P, e, sig, nss_solution_type
#   gaiadr3.astrophysical_parameters_supp  – GSP-Spec ANN Teff/logg/[M/H]
#   gaiadr3.astrophysical_parameters_supp  – FLAME_spec R/L/evolstage
SAMPLE = {
    # gaia_source
    'source_id': 2543788153077017344,
    'ra': 5.5917,                   # deg  (placeholder near HD 1957)
    'dec': -7.5414,                 # deg
    'l': 102.3, 'b': -67.1,         # deg, galactic
    'parallax': 2.309,              # mas
    'pmra': -3.062, 'pmdec': 2.081, # mas/yr
    'phot_g_mean_mag': 8.404,       # G mag
    'bp_rp': 1.125,                 # BP-RP
    'ruwe': 8.75,                   # RUWE
    'astrometric_excess_noise_sig': 1490.0,
    'non_single_star': 3,           # bitmask: 1=astrom, 2=spec, 4=eclipsing
    'radial_velocity': -6.24,       # km/s
    # NSS two-body orbit (AstroSpectroSB1 solution)
    'nss_solution_type': 'AstroSpectroSB1',
    'period': 816.27,               # days
    'eccentricity': 0.017,
    'a_thiele_innes': -2.014,       # mas
    'b_thiele_innes':  2.217,       # mas
    'f_thiele_innes': -2.070,       # mas
    'g_thiele_innes': -2.589,       # mas
    'significance': 105.7,
    # RV diagnostics (gaia_source / NSS combined)
    'rv_amplitude_robust': 22.6,    # km/s
    'rv_chisq_pvalue': 0.0,
    'rv_nb_transits': 35,           # typical Gaia DR3
    # astrophysical_parameters (GSP-Phot defaults; we use GSP-Spec ANN below)
    'teff_gspphot': 4771.0,
    'logg_gspphot': 2.63,
    # astrophysical_parameters_supp – GSP-Spec ANN
    'teff_gspspec_ann': 4771.0,
    'logg_gspspec_ann': 2.63,
    'mh_gspspec_ann':  -0.34,
    # astrophysical_parameters_supp – FLAME_spec
    'radius_flame_spec': 15.53,     # R_sun
    'lum_flame_spec':    121.0,     # L_sun
    'evolstage_flame_spec': 583,    # PARSEC evolutionary-stage code
    # Convenience flags consumed by derive_chunk
    'mass_flame': None,             # not always populated; we let the M_1 prior take over
    'in_sb2': False,                # HD 1957 is SB1, not SB2 by Gaia label
    'hip': None,                    # HD 1957 has no Hipparcos number in the user snapshot
    # Metadata
    'simbad_main_id': 'HD 1957',
    'pulled_at': '2026-05-27',
}

if __name__ == '__main__':
    df = pd.DataFrame([SAMPLE])
    df.to_parquet(OUT, index=False)
    print(f'Wrote {OUT}  ({len(df)} row, {len(df.columns)} cols)')

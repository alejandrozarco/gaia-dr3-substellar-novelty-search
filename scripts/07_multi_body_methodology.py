"""
Multi-body Gaia astrometric methodology paper (Pick #2)

For each Gaia DR3 NSS Orbital substellar source, identify long-baseline
H-G/Hip-Gaia PMa residuals (Kervella 2022 + Brandt 2021/2024 HGCA) that
exceed what the NSS orbital fit can produce alone -> implies outer companion.

Pilot case: HD 128717 (Gaia DR3 1610837178107032192)
  NSS Orbital: P=1089d (inner)
  Gaia-6 b   : P=3420d (Halbwachs+ 2022 OrbitalTargetedSearch outer companion)
"""

import polars as pl
import numpy as np
from pathlib import Path

OUT = Path('data/candidate_dossiers/multi_body_gaia_2026_05_12')
OUT.mkdir(parents=True, exist_ok=True)


# ------- Load all catalogs --------
nss_orb = pl.read_csv(
    'data/candidate_dossiers/full_nss_orbital_2026_05_12/substellar_2678_ranked.csv',
    infer_schema_length=10000,
)
print(f'NSS Orbital substellar rows: {nss_orb.shape[0]}')

nss_acc = pl.read_parquet(
    'data/external_catalogs/parquets/gaia_dr3_nss_acceleration_astro.parquet'
)
print(f'NSS Acceleration rows: {nss_acc.shape[0]}')

kerv = pl.read_parquet(
    'data/external_catalogs/parquets/kervella2022_pma_dr3.parquet'
).with_columns(
    pl.col('GaiaEDR3').cast(pl.Int64, strict=False).alias('source_id')
)
print(f'Kervella PMa rows: {kerv.shape[0]} (valid Gaia IDs: {kerv.filter(pl.col("source_id").is_not_null()).shape[0]})')

brandt = pl.read_parquet('data/external_catalogs/parquets/brandt2021_hgca.parquet').rename(
    {'Gaia': 'source_id'}
)
print(f'Brandt 2021 HGCA rows: {brandt.shape[0]}')

tok_comp = pl.read_csv(
    'data/external_catalogs/raw/tokovinin_msc/tokovinin_msc_2018_components.csv',
    infer_schema_length=5000,
)
print(f'Tokovinin MSC components rows: {tok_comp.shape[0]}')

# Augmented NSS orbital w/ TIC, HIP, Name
nss_orb_extra = pl.read_csv(
    'data/candidate_dossiers/full_nss_orbital_2026_05_12/substellar_2678_with_tic.csv',
    infer_schema_length=10000,
)
print(f'NSS Orbital substellar with TIC/HIP/Name: {nss_orb_extra.shape[0]}')


# ------- Test #1: Disjoint check --------
direct = nss_orb.select('source_id').join(nss_acc.select('source_id'), on='source_id', how='inner')
print(f'\n[TEST #1] Direct NSS Orbital substellar x NSS Acceleration: {direct.shape[0]} (expected: 0)')


# ------- Cross-match Kervella PMa onto NSS Orbital substellar --------
keep_kerv = [
    'source_id', 'HIP', 'Name', 'PlxG3', 'M1', 'snrPMaH2G2',
    'PMaRAH2G2', 'e_PMaRAH2G2', 'PMaDEH2G2', 'e_PMaDEH2G2',
    'dVt', 'e_dVt', 'dVtPA', 'e_dVtPA',
    'M23au', 'M25au', 'e_M25au', 'M210au', 'M230au',
    'BinH2G2',
]
joined = nss_orb.join(kerv.select(keep_kerv), on='source_id', how='left')
print(f'\nNSS Orbital substellar x Kervella PMa: '
      f'{joined.filter(pl.col("dVt").is_not_null()).shape[0]} matched of {joined.shape[0]}')


# ------- Brandt 2021 HGCA cross-match --------
keep_brandt = [
    'source_id', 'pmRAhg', 'pmDEhg', 'e_pmRAhg', 'e_pmDEhg',
    'pmRAhip', 'pmDEhip', 'e_pmRAhip', 'e_pmDEhip',
    'dpmRA', 'dpmDE', 'chi2',
]
joined = joined.join(brandt.select(keep_brandt), on='source_id', how='left')
print(f'NSS Orbital substellar x Brandt 2021 HGCA: '
      f'{joined.filter(pl.col("chi2").is_not_null()).shape[0]} matched')


# ------- Compute NSS-predicted dVt --------
# For a Keplerian companion with period P, eccentricity e, secondary mass M2 (Mj),
# primary mass M1 (Msun), star reflex amplitude is:
#  K_rel = 2*pi*a_rel/P    (velocity in AU/yr)
#  Star reflex velocity amplitude:  K_star = K_rel * M2/(M1+M2)
# In tangential direction, the maximum is K_star * (1 + e cos f) ; rms tangential ~ K_star/sqrt(2)
#
# However, the Hipparcos-Gaia proper motion difference is:
#   dVt = pmGaia - pmHG (positional pm) ~ instantaneous orbital velocity sampled in DR3 epoch
# That is, dVt ~ acceleration over (Gaia epoch span ~ 3 yr).
#
# We compute the "max plausible NSS-only dVt" as the orbital velocity amplitude of the star.
# This is conservative (true rms is K_star/sqrt(2), but instantaneous phase can reach K_star).

# Mass: use derived M_2_mjup_ours where available, else mass ratio * M1
df = joined.with_columns([
    pl.col('M1').cast(pl.Float64).alias('M1_kerv'),  # Msun (Kervella)
    pl.col('M_host_msun_used').cast(pl.Float64).alias('M1_used'),
    pl.col('M_2_mjup_ours').cast(pl.Float64).alias('M2_mjup_nss'),
    pl.col('period').cast(pl.Float64).alias('P_d_nss'),
    pl.col('eccentricity').cast(pl.Float64).alias('e_nss'),
])

# Choose primary mass: prefer Kervella M1, fall back to our M_host_msun_used
df = df.with_columns(
    pl.when(pl.col('M1_kerv').is_not_null())
      .then(pl.col('M1_kerv'))
      .otherwise(pl.col('M1_used'))
      .alias('M1_msun')
)

# Predicted star reflex velocity amplitude from NSS orbit (m/s)
# K_star = 2*pi*AU/yr * a_star_AU where a_star_AU = a_rel_AU * M2/(M1+M2)
# a_rel = (M_tot * P_yr^2)^(1/3) ; M_tot in Msun
def add_pred(df_in):
    """
    Compute geometric quantities for NSS inner orbit + a *realistic* prediction
    of how much dVt the inner orbit ALONE can produce in Kervella's H2-G2 PMa.

    Critical physics:
      - For Gaia DR3 NSS Orbital sources, the published `pmra/pmdec` is the
        systemic (orbit-corrected) proper motion (Thiele-Innes 7-param fit).
      - Hipparcos pm: single-epoch fit, includes inner-orbital reflex phase
        for short-P orbits.
      - H-G pm (positional difference, 25-yr baseline): averages inner orbit
        to ~ 0 for P << 25 yr.
      - dVt = pm_G(orbit-corrected) - pm_HG(orbit-averaged) ≈ 0 if no outer
        companion.  Any observed dVt > a few sigma → outer companion.

    Residual contribution from inner orbit:
      For P ~ 0.5-1 baseline, leakage into pm_HG is order
        K_star * P / baseline.
      We adopt this as conservative leak.
    """
    M1 = df_in['M1_msun'].to_numpy()
    M2_mj = df_in['M2_mjup_nss'].to_numpy()
    P_d = df_in['P_d_nss'].to_numpy()
    plx = df_in['PlxG3'].to_numpy()
    plx_nss = df_in['parallax'].to_numpy()
    plx = np.where(np.isfinite(plx) & (plx > 0), plx, plx_nss)
    P_yr = P_d / 365.25
    Mj2Msun = 1 / 1047.93
    M_tot = M1 + M2_mj * Mj2Msun
    a_rel_au = (M_tot * P_yr ** 2) ** (1 / 3)
    a_star_au = a_rel_au * (M2_mj * Mj2Msun) / M_tot
    AU_km = 1.495978707e8
    K_star_kms = 2 * np.pi * a_star_au * AU_km / (P_d * 86400)
    K_star_ms = K_star_kms * 1000.0
    d_pc = np.where(plx > 0, 1000.0 / plx, np.nan)
    HG_baseline_yr = 25.0
    # Leak fraction: for P >= baseline (long inner orbit), full K_star leaks
    # For P << baseline, leak ~ P/baseline (because Hip-Gaia pm averages
    # multiple orbital periods -> residual is order 1/N_periods)
    leak_frac = np.clip(P_yr / HG_baseline_yr, 0, 1)
    pred_dVt_ms = K_star_ms * leak_frac
    return df_in.with_columns([
        pl.Series('a_rel_au', a_rel_au),
        pl.Series('a_star_au', a_star_au),
        pl.Series('K_star_ms_NSS', K_star_ms),
        pl.Series('leak_frac_NSS', leak_frac),
        pl.Series('pred_dVt_ms_NSS', pred_dVt_ms),
        pl.Series('d_pc', d_pc),
    ])

df = add_pred(df)


# Excess dVt:
# excess = observed - predicted
# sigma in observed dVt is e_dVt ; predicted has its own uncertainty driven by M2 (we'll ignore)
df = df.with_columns([
    (pl.col('dVt') - pl.col('pred_dVt_ms_NSS')).alias('excess_dVt_ms'),
    ((pl.col('dVt') - pl.col('pred_dVt_ms_NSS')) / pl.col('e_dVt')).alias('excess_dVt_sigma'),
])


# ------- Tokovinin MSC join (on HIP) --------
# We need HIP for tokovinin matching. Join NSS-orb-extra (with HIP) for that
extra_keep = ['source_id', 'HIP', 'Name', 'TIC']
extra_unique = nss_orb_extra.select(extra_keep).unique(subset=['source_id'], keep='first')
df = df.join(extra_unique.rename({'HIP': 'HIP_aug', 'Name': 'Name_aug', 'TIC': 'TIC_aug'}),
             on='source_id', how='left')

# Tokovinin: build a HIP -> in-Tok column
tok_hip = tok_comp.filter(pl.col('HIP').is_not_null()).select('HIP').unique()
tok_hip = tok_hip.with_columns(pl.lit(True).alias('in_tokovinin_msc'))
df = df.join(tok_hip, left_on='HIP_aug', right_on='HIP', how='left').with_columns(
    pl.col('in_tokovinin_msc').fill_null(False)
)


# ------- Classification --------
# Multi-body candidate criteria (in order of priority):
#  - dVt observed exists, snrPMaH2G2 >= 3 (significant detection)
#  - excess_dVt_sigma >= 3 (excess beyond what NSS orbit can produce)
#
# Classification tiers:
#  S = excess >=3 sigma + Kervella M2 implied at >=10au exceeds NSS M2 by >3x (outer dominates)
#  A = excess >=3 sigma (outer companion strongly favored)
#  B = excess 2-3 sigma (outer hint)
#  C = excess <2 sigma (NSS fit consistent with single body)

# Compute Kervella outer-companion mass at semi-major appropriate to a long-P companion
# (Kervella M210au is a representative outer companion mass estimate)
df = df.with_columns([
    pl.col('M210au').cast(pl.Float64).alias('M2_outer_10au_Mj_kerv'),
    pl.col('M25au').cast(pl.Float64).alias('M2_5au_Mj_kerv'),
    pl.col('M230au').cast(pl.Float64).alias('M2_30au_Mj_kerv'),
    pl.col('M23au').cast(pl.Float64).alias('M2_3au_Mj_kerv'),
])
df = df.with_columns(
    (pl.col('M2_outer_10au_Mj_kerv') / pl.col('M2_mjup_nss')).alias('M_outer_to_NSS_ratio')
)

def classify(row):
    snr = row['snrPMaH2G2']
    chi2 = row['chi2']  # Brandt 2021 HGCA chi2 (3 d.o.f. under no-companion model)
    if (snr is None or not np.isfinite(snr) or snr < 3) and (chi2 is None or not np.isfinite(chi2) or chi2 < 11.34):
        return 'no_HGCA_signal'  # chi2 > 11.34 ~ 99% confidence (3 dof)
    exc = row['excess_dVt_sigma']
    if exc is None or not np.isfinite(exc):
        # Has HGCA signal but no excess computed -> still inner-companion only?
        return 'no_excess_computed'
    if exc >= 3:
        rat = row['M_outer_to_NSS_ratio']
        in_tok = row['in_tokovinin_msc']
        if (rat is not None and np.isfinite(rat) and rat >= 3) or in_tok:
            return 'S_multi_body'
        return 'A_multi_body_candidate'
    if exc >= 2:
        return 'B_outer_hint'
    if exc <= -3:
        return 'D_NSS_alias_or_oversized'
    return 'C_single_companion_consistent'

df_pd = df.to_pandas()
df_pd['classification'] = df_pd.apply(classify, axis=1)
df = pl.from_pandas(df_pd)

# Summary counts
cls_counts = df.group_by('classification').agg(pl.len().alias('n')).sort('n', descending=True)
print('\nClassification counts:')
print(cls_counts)


# ------- Output the tier-S+A table and full table --------
output_cols = [
    'source_id', 'Name_aug', 'HIP_aug', 'TIC_aug',
    'P_d_nss', 'e_nss', 'M2_mjup_nss', 'a_rel_au', 'a_star_au',
    'M1_msun',
    'PlxG3', 'd_pc', 'priority_score',
    'snrPMaH2G2', 'dVt', 'e_dVt', 'BinH2G2',
    'pred_dVt_ms_NSS', 'excess_dVt_ms', 'excess_dVt_sigma',
    'M2_3au_Mj_kerv', 'M2_5au_Mj_kerv', 'M2_outer_10au_Mj_kerv', 'M2_30au_Mj_kerv',
    'M_outer_to_NSS_ratio',
    'chi2',  # Brandt HGCA chi2
    'dpmRA', 'dpmDE',
    'in_tokovinin_msc',
    'classification',
]
out_cols = [c for c in output_cols if c in df.columns]
df_out = df.select(out_cols).sort('excess_dVt_sigma', descending=True, nulls_last=True)
df_out.write_csv(OUT / 'multi_body_candidates.csv')
print(f'\nWrote {df_out.shape[0]} rows -> {OUT}/multi_body_candidates.csv')

# Tier S+A only
tier_sa = df_out.filter(pl.col('classification').is_in(['S_multi_body', 'A_multi_body_candidate']))
tier_sa.write_csv(OUT / 'tier_S_multi_body.csv')
print(f'Tier S+A rows: {tier_sa.shape[0]} -> {OUT}/tier_S_multi_body.csv')

# Top 20 print
print('\nTop 20 by excess_dVt_sigma:')
print(df_out.head(20).select(['source_id', 'Name_aug', 'P_d_nss', 'M2_mjup_nss',
                              'snrPMaH2G2', 'dVt', 'pred_dVt_ms_NSS', 'excess_dVt_sigma',
                              'M2_outer_10au_Mj_kerv', 'classification']))

# Save also classifications summary
with open(OUT / 'summary_counts.txt', 'w') as f:
    for row in cls_counts.iter_rows(named=True):
        f.write(f"{row['classification']}\t{row['n']}\n")

# Verify HD 128717
print('\n=== Verification: HD 128717 (Gaia DR3 1610837178107032192) ===')
hd = df.filter(pl.col('source_id') == 1610837178107032192)
if hd.shape[0]:
    print(hd.select(['source_id', 'Name_aug', 'P_d_nss', 'M2_mjup_nss',
                     'snrPMaH2G2', 'dVt', 'pred_dVt_ms_NSS', 'excess_dVt_ms',
                     'excess_dVt_sigma', 'M2_3au_Mj_kerv', 'M2_5au_Mj_kerv',
                     'M2_outer_10au_Mj_kerv', 'classification']))

#!/usr/bin/env python3
"""RV-coverage inventory for the 2,678 Gaia DR3 NSS Orbital substellar candidates.

Cross-matches each candidate against accessible RV archives (locally cached):

  Direct source_id join:
    - LAMOST DR10 multi-epoch (3.78M visits) — σ_RV ~1 km/s
    - GALAH DR4 (918k visits)                — σ_RV ~300 m/s

  Coord cone-match (with PM correction):
    - HARPS RVBank Trifonov 2020 (213k RVs, 1822 targets)   — σ_RV ~1-5 m/s
    - APOGEE DR17 allVisit (2.66M visits)                    — σ_RV ~100-200 m/s
    - Trifonov 2025 HIRES (79k RVs, 1702 targets)            — σ_RV ~2-5 m/s
    - NASA Exoplanet Archive published RVs (43k)             — published-orbit overlap

Output:
  data/candidate_dossiers/rv_coverage_2026_05_12/rv_inventory.csv

Per candidate columns:
  source_id, ra, dec, V, P_NSS_d, M2_Mj, e, K_pred_mps,
  harps_N, harps_baseline_d, harps_sigma_mps,
  apogee_N, apogee_baseline_d, apogee_sigma_mps,
  lamost_N, lamost_baseline_d, lamost_sigma_mps,
  galah_N, galah_baseline_d, galah_sigma_mps,
  hires_N, hires_baseline_d, hires_sigma_mps,
  nasa_exo_published (bool),
  total_archives, total_visits, best_sigma_mps,
  K_pred_to_sigma_ratio, sampling_complete (bool)
"""
import os
import sys
import numpy as np
import polars as pl
from scipy.spatial import cKDTree

# ---- paths
SUBSTELLAR_CSV = 'data/candidate_dossiers/full_nss_orbital_2026_05_12/substellar_2678_ranked.csv'
HARPS_TARGETS = 'data/external_catalogs/parquets/harps_rvbank_targets.parquet'
HARPS_RVS = 'data/external_catalogs/parquets/harps_rvbank.parquet'
APOGEE = 'data/external_catalogs/parquets/apogee_dr17_allVisit.parquet'
LAMOST = 'data/external_catalogs/parquets/lamost_dr10_multi_epoch_rv.parquet'
GALAH = 'data/external_catalogs/parquets/galah_dr4_rv.parquet'
HIRES_TARGETS = 'data/external_catalogs/parquets/trifonov2025_hires_targets.parquet'
HIRES_RVS = 'data/external_catalogs/parquets/trifonov2025_hires_rv.parquet'
NASA_EXO = 'data/external_catalogs/parquets/nasa_exo_rv.parquet'
NASA_COORDS = 'data/external_catalogs/parquets/nasa_exo_rv_star_coords.parquet'

OUT_DIR = 'data/candidate_dossiers/rv_coverage_2026_05_12'
os.makedirs(OUT_DIR, exist_ok=True)

CONE_ARCSEC = 5.0  # tolerance for coord cone matching


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def build_kdtree(ra, dec):
    """Build a flat-Earth k-d tree on (RA·cos(Dec), Dec). Good to ~0.01% for 5"
    cone matches at any latitude."""
    rad = np.radians(dec)
    x = ra * np.cos(rad)
    y = dec
    return cKDTree(np.column_stack([x, y])), x, y


def cone_match(cand_ra, cand_dec, tree, catalog_ra, catalog_dec, tol_arcsec=CONE_ARCSEC):
    """Returns list of catalog row indices within tol_arcsec of each candidate.

    `tree` is built on (RA·cos(Dec), Dec) of the catalog.
    `catalog_ra`, `catalog_dec` are the original (deg) arrays.
    Returns: list of np.ndarray (one per candidate)
    """
    tol_deg = tol_arcsec / 3600.0
    cand_rad = np.radians(cand_dec)
    cx = cand_ra * np.cos(cand_rad)
    cy = cand_dec
    # query_ball_point: all points within tol_deg
    matches = tree.query_ball_point(np.column_stack([cx, cy]), tol_deg)
    return matches


def k_pred_mps(M2_Mj, M1_Msun, P_d, e):
    """Predicted RV semi-amplitude at sin i = 1.

    K_1 [m/s] = 28.4329 × (M_2 / M_J) × (M_1 + M_2)^(-2/3) [M_sun]
              × (P / yr)^(-1/3) × (1 - e²)^(-1/2)
    """
    M2_Msun = M2_Mj / 1047.5651
    P_yr = P_d / 365.25
    return 28.4329 * M2_Mj * (M1_Msun + M2_Msun) ** (-2/3) * P_yr ** (-1/3) / np.sqrt(1 - e**2)


# -----------------------------------------------------------------------------
# Load candidates
# -----------------------------------------------------------------------------
print('Loading 2,678 substellar candidates...')
cand = pl.read_csv(SUBSTELLAR_CSV, infer_schema_length=10000, ignore_errors=True)
cand = cand.select([
    pl.col('source_id'),
    pl.col('ra'),
    pl.col('dec'),
    pl.col('pmra'),
    pl.col('pmdec'),
    pl.col('parallax'),
    pl.col('phot_g_mean_mag').alias('G'),
    pl.col('Vmag'),
    pl.col('HIP'),
    pl.col('Name'),
    pl.col('SpType'),
    pl.col('period').alias('P_NSS_d'),
    pl.col('eccentricity').alias('e_NSS'),
    pl.col('M_2_mjup_ours').alias('M2_Mj'),
    pl.col('M_host_msun_used').alias('M1_Msun'),
    pl.col('distance_pc').alias('d_pc'),
    pl.col('snrPMaH2G2').alias('hgca_snrPMa'),
    pl.col('label').alias('sahlmann_label'),
    pl.col('priority_score'),
])
print(f'  {len(cand):,} candidates loaded')
print(f'  P_NSS range: {cand["P_NSS_d"].min():.0f} – {cand["P_NSS_d"].max():.0f} d')
print(f'  M2 range: {cand["M2_Mj"].min():.1f} – {cand["M2_Mj"].max():.1f} M_J')

# Compute K_pred
print('Computing K_pred...')
M1 = cand['M1_Msun'].fill_null(1.0).to_numpy()
M2 = cand['M2_Mj'].to_numpy()
P = cand['P_NSS_d'].to_numpy()
e = cand['e_NSS'].fill_null(0.0).to_numpy()
e = np.clip(e, 0.0, 0.95)
K = k_pred_mps(M2, M1, P, e)
cand = cand.with_columns(pl.Series('K_pred_mps', K))
print(f'  K_pred range: {np.nanmin(K):.0f} – {np.nanmax(K):.0f} m/s')
print(f'  K_pred median: {np.nanmedian(K):.0f} m/s')

# Precomputed candidate (ra, dec) arrays for cone search
cand_ra = cand['ra'].to_numpy()
cand_dec = cand['dec'].to_numpy()
cand_source_ids = cand['source_id'].to_numpy()


# -----------------------------------------------------------------------------
# Match 1: LAMOST DR10 (source_id join, then aggregate per candidate)
# -----------------------------------------------------------------------------
print('\n--- LAMOST DR10 multi-epoch ---')
lam = pl.scan_parquet(LAMOST).select([
    pl.col('gaia_dr3_source_id'),
    pl.col('mjd'),
    pl.col('rv_kms'),
    pl.col('sigma_kms'),
]).filter(
    pl.col('gaia_dr3_source_id').is_in(cand_source_ids.tolist())
    & pl.col('rv_kms').is_not_null()
    & pl.col('sigma_kms').is_not_null()
).collect()
print(f'  {len(lam):,} LAMOST RVs match our candidates')

lam_agg = lam.group_by('gaia_dr3_source_id').agg([
    pl.len().alias('lamost_N'),
    (pl.col('mjd').max() - pl.col('mjd').min()).alias('lamost_baseline_d'),
    pl.col('sigma_kms').median().alias('lamost_sigma_kms'),
])
print(f'  {len(lam_agg):,} unique candidates with LAMOST RVs')


# -----------------------------------------------------------------------------
# Match 2: GALAH DR4 (source_id join, then aggregate)
# -----------------------------------------------------------------------------
print('\n--- GALAH DR4 ---')
gal = pl.scan_parquet(GALAH).select([
    pl.col('gaiadr3_source_id'),
    pl.col('mjd'),
    pl.col('rv_comp_1'),
    pl.col('e_rv_comp_1'),
]).filter(
    pl.col('gaiadr3_source_id').is_in(cand_source_ids.tolist())
    & pl.col('rv_comp_1').is_not_null()
    & pl.col('e_rv_comp_1').is_not_null()
).collect()
print(f'  {len(gal):,} GALAH RVs match our candidates')

gal_agg = gal.group_by('gaiadr3_source_id').agg([
    pl.len().alias('galah_N'),
    (pl.col('mjd').max() - pl.col('mjd').min()).alias('galah_baseline_d'),
    pl.col('e_rv_comp_1').median().alias('galah_sigma_kms'),
])
print(f'  {len(gal_agg):,} unique candidates with GALAH RVs')


# -----------------------------------------------------------------------------
# Match 3: APOGEE DR17 (coord cone match)
# -----------------------------------------------------------------------------
print('\n--- APOGEE DR17 ---')
apo_meta = pl.scan_parquet(APOGEE).select([
    pl.col('APOGEE_ID'),
    pl.col('RA'),
    pl.col('DEC'),
    pl.col('MJD'),
    pl.col('VHELIO'),
    pl.col('VRELERR'),
    pl.col('SNR'),
]).filter(
    pl.col('VHELIO').is_not_null() & (pl.col('VHELIO') > -9000)
    & pl.col('VRELERR').is_not_null() & (pl.col('VRELERR') > 0)
    & pl.col('RA').is_not_null() & pl.col('DEC').is_not_null()
).collect()
print(f'  APOGEE valid visits: {len(apo_meta):,}')

# Unique stars (by APOGEE_ID) for the spatial index
apo_unique = apo_meta.unique(subset=['APOGEE_ID'])
print(f'  APOGEE unique targets: {len(apo_unique):,}')

apo_ra = apo_unique['RA'].to_numpy()
apo_dec = apo_unique['DEC'].to_numpy()
apo_ids = apo_unique['APOGEE_ID'].to_numpy()

tree_apo, _, _ = build_kdtree(apo_ra, apo_dec)
matches_apo = cone_match(cand_ra, cand_dec, tree_apo, apo_ra, apo_dec, CONE_ARCSEC)

# Per candidate, collect APOGEE_IDs of hits
hits_apo = {}  # source_id -> list of APOGEE_IDs
for i, m in enumerate(matches_apo):
    if len(m) > 0:
        sid = int(cand_source_ids[i])
        hits_apo[sid] = [str(apo_ids[j]) for j in m]

print(f'  Candidates with APOGEE match (any): {len(hits_apo):,}')

# Aggregate visits per matched APOGEE_ID
all_apo_ids = set()
for ids in hits_apo.values():
    all_apo_ids.update(ids)
apo_agg = apo_meta.filter(pl.col('APOGEE_ID').is_in(list(all_apo_ids))).group_by('APOGEE_ID').agg([
    pl.len().alias('apogee_N'),
    (pl.col('MJD').max() - pl.col('MJD').min()).alias('apogee_baseline_d'),
    pl.col('VRELERR').median().alias('apogee_sigma_kms'),
])
apo_agg_dict = {row['APOGEE_ID']: row for row in apo_agg.to_dicts()}
print(f'  Aggregated {len(apo_agg_dict):,} matched APOGEE targets')


# -----------------------------------------------------------------------------
# Match 4: HARPS RVBank Trifonov 2020 (coord cone match — only 1822 targets)
# -----------------------------------------------------------------------------
print('\n--- HARPS RVBank Trifonov 2020 ---')
harps_tgt = pl.read_parquet(HARPS_TARGETS)
print(f'  HARPS targets: {len(harps_tgt):,}')

h_ra = harps_tgt['ra_deg'].to_numpy()
h_dec = harps_tgt['dec_deg'].to_numpy()
h_names = harps_tgt['name'].to_numpy()

tree_h, _, _ = build_kdtree(h_ra, h_dec)
matches_h = cone_match(cand_ra, cand_dec, tree_h, h_ra, h_dec, CONE_ARCSEC)

hits_h = {}
for i, m in enumerate(matches_h):
    if len(m) > 0:
        sid = int(cand_source_ids[i])
        hits_h[sid] = [str(h_names[j]) for j in m]

print(f'  Candidates with HARPS match: {len(hits_h):,}')

if hits_h:
    all_h_names = set()
    for nms in hits_h.values():
        all_h_names.update(nms)
    harps_rvs = pl.read_parquet(HARPS_RVS).filter(pl.col('name').is_in(list(all_h_names)))
    h_agg = harps_rvs.group_by('name').agg([
        pl.len().alias('harps_N'),
        (pl.col('bjd').max() - pl.col('bjd').min()).alias('harps_baseline_d'),
        pl.col('sigma_kms').median().alias('harps_sigma_kms'),
    ])
    h_agg_dict = {row['name']: row for row in h_agg.to_dicts()}
else:
    h_agg_dict = {}


# -----------------------------------------------------------------------------
# Match 5: Trifonov 2025 HIRES (coord cone match — 1702 targets)
# -----------------------------------------------------------------------------
print('\n--- Trifonov 2025 HIRES ---')
hires_tgt = pl.read_parquet(HIRES_TARGETS)
print(f'  HIRES targets: {len(hires_tgt):,}')

hi_ra = hires_tgt['ra_deg'].to_numpy()
hi_dec = hires_tgt['dec_deg'].to_numpy()
hi_names = hires_tgt['name'].to_numpy()

tree_hi, _, _ = build_kdtree(hi_ra, hi_dec)
matches_hi = cone_match(cand_ra, cand_dec, tree_hi, hi_ra, hi_dec, CONE_ARCSEC)

hits_hi = {}
for i, m in enumerate(matches_hi):
    if len(m) > 0:
        sid = int(cand_source_ids[i])
        hits_hi[sid] = [str(hi_names[j]) for j in m]

print(f'  Candidates with HIRES match: {len(hits_hi):,}')

if hits_hi:
    all_hi_names = set()
    for nms in hits_hi.values():
        all_hi_names.update(nms)
    hires_rvs = pl.read_parquet(HIRES_RVS).filter(pl.col('name').is_in(list(all_hi_names)))
    # rv_cor_mps in m/s; e_rv_cor_mps in m/s
    hi_agg = hires_rvs.group_by('name').agg([
        pl.len().alias('hires_N'),
        (pl.col('bjd').max() - pl.col('bjd').min()).alias('hires_baseline_d'),
        pl.col('e_rv_cor_mps').median().alias('hires_sigma_mps'),
    ])
    hi_agg_dict = {row['name']: row for row in hi_agg.to_dicts()}
else:
    hi_agg_dict = {}


# -----------------------------------------------------------------------------
# Match 6: NASA Exoplanet Archive published RVs
# -----------------------------------------------------------------------------
print('\n--- NASA Exoplanet Archive published RVs ---')
nasa_coords = pl.read_parquet(NASA_COORDS)
n_ra = nasa_coords['ra'].to_numpy()
n_dec = nasa_coords['dec'].to_numpy()
n_ids = nasa_coords['star_id'].to_numpy()

tree_n, _, _ = build_kdtree(n_ra, n_dec)
matches_n = cone_match(cand_ra, cand_dec, tree_n, n_ra, n_dec, CONE_ARCSEC)

hits_n = {}
for i, m in enumerate(matches_n):
    if len(m) > 0:
        sid = int(cand_source_ids[i])
        hits_n[sid] = [str(n_ids[j]) for j in m]
print(f'  Candidates with NASA-published RV: {len(hits_n):,}')


# -----------------------------------------------------------------------------
# Build inventory table
# -----------------------------------------------------------------------------
print('\n--- Building inventory table ---')

# Initialize all candidate rows with zeros
inv = cand.clone()

# Polars join the source_id-keyed aggregates
inv = inv.join(lam_agg.rename({'gaia_dr3_source_id': 'source_id'}), on='source_id', how='left')
inv = inv.join(gal_agg.rename({'gaiadr3_source_id': 'source_id'}), on='source_id', how='left')

# For coord-matched archives, build join tables
def coord_match_to_polars(hits_dict, agg_dict, name_col='name', n_col=None, b_col=None, s_col=None):
    """Convert dict-of-lists hits to a polars DataFrame with one row per source_id.
    If multiple catalog names match, take the one with max N visits."""
    rows = []
    for sid, names in hits_dict.items():
        best = None
        for nm in names:
            if nm in agg_dict:
                rec = agg_dict[nm]
                if best is None or rec[n_col] > best[n_col]:
                    best = rec
        if best is not None:
            rows.append({'source_id': sid,
                         n_col: best[n_col],
                         b_col: best[b_col],
                         s_col: best[s_col]})
    if not rows:
        return pl.DataFrame(schema={'source_id': pl.Int64, n_col: pl.UInt32, b_col: pl.Float64, s_col: pl.Float64})
    return pl.DataFrame(rows)

h_df = coord_match_to_polars(hits_h, h_agg_dict, n_col='harps_N', b_col='harps_baseline_d', s_col='harps_sigma_kms')
hi_df = coord_match_to_polars(hits_hi, hi_agg_dict, n_col='hires_N', b_col='hires_baseline_d', s_col='hires_sigma_mps')
apo_df = coord_match_to_polars(hits_apo, apo_agg_dict, n_col='apogee_N', b_col='apogee_baseline_d', s_col='apogee_sigma_kms')

inv = inv.join(h_df, on='source_id', how='left')
inv = inv.join(hi_df, on='source_id', how='left')
inv = inv.join(apo_df, on='source_id', how='left')

# NASA published flag
nasa_published_ids = set(hits_n.keys())
inv = inv.with_columns(
    pl.col('source_id').is_in(list(nasa_published_ids)).alias('nasa_exo_published')
)

# Fill nulls
for c in ['lamost_N', 'galah_N', 'harps_N', 'hires_N', 'apogee_N']:
    inv = inv.with_columns(pl.col(c).fill_null(0))

# Convert all sigma columns to consistent units (m/s)
inv = inv.with_columns([
    (pl.col('lamost_sigma_kms') * 1000).alias('lamost_sigma_mps'),
    (pl.col('galah_sigma_kms') * 1000).alias('galah_sigma_mps'),
    (pl.col('harps_sigma_kms') * 1000).alias('harps_sigma_mps'),
    (pl.col('apogee_sigma_kms') * 1000).alias('apogee_sigma_mps'),
]).drop(['lamost_sigma_kms', 'galah_sigma_kms', 'harps_sigma_kms', 'apogee_sigma_kms'])

# Total archives + visits + best sigma
inv = inv.with_columns([
    ((pl.col('harps_N') > 0).cast(pl.Int8) + (pl.col('apogee_N') > 0).cast(pl.Int8)
     + (pl.col('lamost_N') > 0).cast(pl.Int8) + (pl.col('galah_N') > 0).cast(pl.Int8)
     + (pl.col('hires_N') > 0).cast(pl.Int8) + pl.col('nasa_exo_published').cast(pl.Int8)
     ).alias('total_archives'),
    (pl.col('harps_N').fill_null(0) + pl.col('apogee_N').fill_null(0)
     + pl.col('lamost_N').fill_null(0) + pl.col('galah_N').fill_null(0)
     + pl.col('hires_N').fill_null(0)).alias('total_visits'),
])

# Best sigma (smallest finite value)
inv = inv.with_columns(
    pl.min_horizontal([
        pl.col('harps_sigma_mps').fill_null(1e9),
        pl.col('hires_sigma_mps').fill_null(1e9),
        pl.col('apogee_sigma_mps').fill_null(1e9),
        pl.col('galah_sigma_mps').fill_null(1e9),
        pl.col('lamost_sigma_mps').fill_null(1e9),
    ]).alias('best_sigma_mps')
).with_columns(
    pl.when(pl.col('best_sigma_mps') >= 1e9).then(None).otherwise(pl.col('best_sigma_mps')).alias('best_sigma_mps')
)

# K_pred / best_sigma ratio (single-epoch S/N for detection)
inv = inv.with_columns(
    (pl.col('K_pred_mps') / pl.col('best_sigma_mps')).alias('K_to_sigma_ratio')
)

# Sampling completeness: best archive baseline > P_NSS AND best archive N >= 5
inv = inv.with_columns([
    pl.max_horizontal([
        pl.col('harps_baseline_d').fill_null(0),
        pl.col('apogee_baseline_d').fill_null(0),
        pl.col('lamost_baseline_d').fill_null(0),
        pl.col('galah_baseline_d').fill_null(0),
        pl.col('hires_baseline_d').fill_null(0),
    ]).alias('best_baseline_d'),
    pl.max_horizontal([
        pl.col('harps_N').fill_null(0),
        pl.col('apogee_N').fill_null(0),
        pl.col('lamost_N').fill_null(0),
        pl.col('galah_N').fill_null(0),
        pl.col('hires_N').fill_null(0),
    ]).alias('best_N'),
])

inv = inv.with_columns([
    ((pl.col('best_baseline_d') > pl.col('P_NSS_d')) & (pl.col('best_N') >= 5)).alias('sampling_complete'),
])


# -----------------------------------------------------------------------------
# Save
# -----------------------------------------------------------------------------
out_path = os.path.join(OUT_DIR, 'rv_inventory.csv')
inv.write_csv(out_path)
print(f'\nWritten {out_path}')
print(f'Inventory has {len(inv):,} candidates × {len(inv.columns)} columns')


# -----------------------------------------------------------------------------
# Summary stats
# -----------------------------------------------------------------------------
print('\n=== RV COVERAGE SUMMARY (2,678 substellar candidates) ===\n')
def pct(n, tot=len(inv)):
    return f'{n:4d} ({100*n/tot:5.2f}%)'

n_any = (inv['total_archives'] > 0).sum()
n_2plus = (inv['total_archives'] >= 2).sum()
n_3plus = (inv['total_archives'] >= 3).sum()
n_sampling = inv['sampling_complete'].sum()

print('  ANY archive coverage:        ', pct(n_any))
print('  ≥ 2 archives:                ', pct(n_2plus))
print('  ≥ 3 archives:                ', pct(n_3plus))
print('  Sampling-complete (N≥5, baseline > P_NSS): ', pct(n_sampling))
print()

print('Per-archive coverage:')
print(f'  HARPS RVBank:           {pct(int((inv["harps_N"] > 0).sum()))}')
print(f'  HIRES Butler/Trifonov:  {pct(int((inv["hires_N"] > 0).sum()))}')
print(f'  APOGEE DR17:            {pct(int((inv["apogee_N"] > 0).sum()))}')
print(f'  GALAH DR4:              {pct(int((inv["galah_N"] > 0).sum()))}')
print(f'  LAMOST DR10:            {pct(int((inv["lamost_N"] > 0).sum()))}')
print(f'  NASA Exo published:     {pct(int(inv["nasa_exo_published"].sum()))}')
print()

# Sampling-complete with K_pred detection capability
inv_good = inv.filter(
    pl.col('sampling_complete')
    & (pl.col('K_pred_mps') > 3 * pl.col('best_sigma_mps'))  # K detectable at 3σ single-epoch
    & (pl.col('M2_Mj') < 80)  # substellar
)
print(f'GOOD (sampling + 3σ K + substellar):  {pct(len(inv_good))}')

inv_marginal = inv.filter(
    pl.col('sampling_complete')
    & (pl.col('K_pred_mps') > pl.col('best_sigma_mps'))  # K > σ (multi-epoch S/N possible)
    & (pl.col('M2_Mj') < 80)
)
print(f'MARGINAL (sampling + K > σ + substellar): {pct(len(inv_marginal))}')

# Show top 20 by total visits, sampling-complete, substellar
print('\n--- Top 30 sampling-complete substellar candidates ---')
top = inv.filter(
    pl.col('sampling_complete') & (pl.col('M2_Mj') < 80)
).sort('total_visits', descending=True).head(30).select([
    'source_id', 'Name', 'HIP', 'Vmag', 'P_NSS_d', 'M2_Mj', 'e_NSS', 'K_pred_mps',
    'total_archives', 'total_visits', 'best_sigma_mps', 'K_to_sigma_ratio',
    'harps_N', 'apogee_N', 'lamost_N', 'galah_N', 'hires_N',
    'nasa_exo_published'
])
with pl.Config(tbl_rows=30, tbl_cols=18, tbl_width_chars=400):
    print(top)

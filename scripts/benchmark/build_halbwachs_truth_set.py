"""Build augmented truth set: Halbwachs/Gaia DR3 binary_masses + Marcussen 2023.

Halbwachs/Gaia DR3 binary_masses (I/360/binmass, 195k rows) provides direct
M_2 measurements for ~29k NSS sources via spectroscopic mass-ratio fits.
Independent of Sahlmann 2025.

Classification rules:
  * POSITIVE if M_2 < 0.0764 M_sun (i.e., < 80 M_J — substellar)
  * NEGATIVE if M_2 >= 0.5 M_sun (clearly stellar)
  * Excluded if 0.0764 <= M_2 < 0.5 (red-dwarf boundary — ambiguous for
    benchmark purposes since the cascade's M_2 marg includes this range)

Then cross-match against v2_scan_full_pool by source_id and combine with
the Marcussen+Albrecht 2023 truth set (already built in v1.3.0).
"""
import polars as pl

OUT_DIR = "/Users/legbatterij/claude_projects/ostinato/notes/2026-05-13-cascade-benchmark"
REPO = "/tmp/gaia-novelty-publication"
HALBWACHS_FILE = "/Users/legbatterij/claude_projects/ostinato/data/external_catalogs/gaia_dr3_binary_masses_clean.csv"

# Load
hb = pl.read_csv(HALBWACHS_FILE, schema_overrides={"Source": pl.Int64})

# Cast numeric strings
for c in ["M1", "e_M1", "E_M1", "M2", "e_M2", "E_M2", "FluxRatio"]:
    if hb[c].dtype == pl.Utf8:
        hb = hb.with_columns(pl.col(c).str.strip_chars().cast(pl.Float64, strict=False))

v2 = pl.read_csv(f"{REPO}/v2_scan_full_pool.csv")
v4 = pl.read_csv(f"{REPO}/v4_scan_full_pool.csv")

print(f"Halbwachs binary_masses: {hb.height} rows")
print(f"  with direct M_2:        {hb.filter(pl.col('M2').is_not_null()).height}")
print(f"v2 scan pool:             {v2.height} rows")
print(f"v4 scan pool:             {v4.height} rows")

# Limit to sources with direct M2
hb = hb.filter(pl.col("M2").is_not_null())

# Apply classification (M_2 in Msun; thresholds in Msun)
M_SUBSTELLAR_HI = 0.0764   # 80 MJ
M_STELLAR_LO = 0.5

hb = hb.with_columns(
    pl.when(pl.col("M2") < M_SUBSTELLAR_HI)
    .then(pl.lit("POSITIVE"))
    .when(pl.col("M2") >= M_STELLAR_LO)
    .then(pl.lit("NEGATIVE"))
    .otherwise(pl.lit(None))
    .alias("truth_bucket")
)
hb_truth = hb.filter(pl.col("truth_bucket").is_not_null())
print(f"\nHalbwachs entries with clean substellar/stellar label: {hb_truth.height}")
print(hb_truth.group_by("truth_bucket").len().sort("truth_bucket"))

# Cross-match against v2 scan pool
hb_truth = hb_truth.with_columns(pl.col("Source").alias("source_id"))
v2_join = v2.select([
    "source_id", "nss_solution_type", "period_d", "eccentricity",
    "significance", "ruwe", "M_2_mjup_face_on", "M_2_mjup_marginalized",
    "phot_g_mean_mag", "HIP", "Name", "Vmag", "SpType",
    "documented_fp", "ruwe_pass", "nasa_exo_match", "hgca_chisq", "v2_verdict",
])
hb_pool = hb_truth.join(v2_join, on="source_id", how="inner")
print(f"\nHalbwachs entries in v2 scan pool: {hb_pool.height}")
print(hb_pool.group_by("truth_bucket").len().sort("truth_bucket"))

# Add v4 verdicts
v4_verdict = v4.select(["source_id", "v4_verdict"])
hb_pool = hb_pool.join(v4_verdict, on="source_id", how="left")

print()
print("=" * 70)
print("Halbwachs truth-set distribution by v4 verdict")
print("=" * 70)
print(hb_pool.group_by(["truth_bucket", "v4_verdict"]).agg(pl.len().alias("n")).sort(["truth_bucket", "n"], descending=[False, True]))

# Save expanded independent truth set
hb_pool.write_csv(f"{REPO}/benchmark_output/truth_set_halbwachs.csv")
hb_pool.write_csv(f"{OUT_DIR}/truth_set_halbwachs.csv")
print(f"\nWrote Halbwachs truth set: {hb_pool.height} rows")

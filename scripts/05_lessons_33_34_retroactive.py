"""
Retroactive application of Lessons #33 (A9 i-marg) + #34 (universal Kervella PMa M_2)
across ALL candidate pools.

Output dir: data/candidate_dossiers/lessons_33_34_retroactive_2026_05_13/
"""
import os
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import polars as pl


# ---------------------------------------------------------------------------
# Constants & I/O
# ---------------------------------------------------------------------------
ROOT = Path(os.environ.get("GAIA_NOVELTY_DATA_ROOT", str(Path(__file__).resolve().parent.parent)))
OUT = ROOT / "data/candidate_dossiers/lessons_33_34_retroactive_2026_05_13"
OUT.mkdir(parents=True, exist_ok=True)

KERV_PATH = ROOT / "data/external_catalogs/parquets/kervella2022_pma_dr3.parquet"

MASTER_NOT_NOVEL = (
    ROOT
    / "data/candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/master_filter_NOT_NOVEL.csv"
)

POOLS = {
    "NSS_Orbital_substellar": "data/candidate_dossiers/full_nss_orbital_2026_05_12/substellar_2678_ranked.csv",
    "NSS_Accel_cleaned": "data/candidate_dossiers/nss_accel_broader_full_filter_2026_05_12/cleaned_post_all_filters.csv",
    "NSS_Accel_priority": "data/candidate_dossiers/nss_acceleration_mining_2026_05_12/nss_accel_substellar_priority.csv",
    "MEGA_expanded": "data/candidate_dossiers/mega_pipeline_2026_05_12/expanded_candidate_pool.csv",
    "Truly_novel_l17_l19": "data/candidate_dossiers/new_filters_l17_l19_2026_05_12/cleaned_nss_orbital_post_l17_l19.csv",
    "A9_actionable": "data/candidate_dossiers/nss_accel9_extended_2026_05_13/actionable_a9_clean.csv",
    "A9_novel_extra": "data/candidate_dossiers/nss_accel9_extended_2026_05_13/top_30_a9_novel.csv",
}

# Thresholds — Lesson #34
KERV_M2_STELLAR_FACE = 200.0   # M_Jup — face-on minimum is already stellar
KERV_M2_LIKELY = 100.0         # combined with high SNR
KERV_SNR_HIGH = 50.0

# ---------------------------------------------------------------------------
# Kervella loading
# ---------------------------------------------------------------------------
def load_kervella() -> pl.DataFrame:
    df = pl.read_parquet(KERV_PATH)
    # Coerce types
    df = df.with_columns(
        pl.col("HIP").cast(pl.Float64, strict=False),
        pl.col("GaiaEDR3").cast(pl.Utf8, strict=False),
        pl.col("M25au").cast(pl.Float64, strict=False),
        pl.col("M210au").cast(pl.Float64, strict=False),
        pl.col("M230au").cast(pl.Float64, strict=False),
        pl.col("snrPMaH2G2").cast(pl.Float64, strict=False),
        pl.col("snrPMaH2EG3b").cast(pl.Float64, strict=False),
        pl.col("dVt").cast(pl.Float64, strict=False),
        pl.col("e_dVt").cast(pl.Float64, strict=False),
    )
    # Add SNR(dVt) = dVt / e_dVt (use only when both available)
    df = df.with_columns(
        (pl.col("dVt") / pl.col("e_dVt")).alias("snr_dVt"),
    )
    # Best-SNR PMa = max of H2G2, H2EG3a, H2EG3b
    df = df.with_columns(
        pl.max_horizontal(
            pl.col("snrPMaH2G2").fill_null(0.0),
            pl.col("snrPMaH2EG3a").cast(pl.Float64, strict=False).fill_null(0.0),
            pl.col("snrPMaH2EG3b").fill_null(0.0),
        ).alias("snrPMa_best")
    )
    return df.select(
        ["HIP", "GaiaEDR3", "M25au", "M210au", "M230au",
         "snrPMaH2G2", "snrPMaH2EG3b", "snrPMa_best",
         "dVt", "e_dVt", "snr_dVt", "Vmag", "SpType", "RUWE", "PlxG3"]
    )


def classify_kervella(m25: float | None, snr_best: float | None) -> str:
    """Lesson #34: Universal Kervella M_2 filter.

    Returns flag:
      STELLAR_KERVELLA_HIGH_M  — M2(5au) > 200 MJ face-on minimum
      LIKELY_STELLAR_HIGH_SNR_KERVELLA — high SNR + M2(5au) > 100
      KERVELLA_AMBIGUOUS — has Kervella signal but not stellar threshold
      NO_KERVELLA — no record / no signal
    """
    if m25 is None or (isinstance(m25, float) and math.isnan(m25)):
        return "NO_KERVELLA"
    if m25 > KERV_M2_STELLAR_FACE:
        return "STELLAR_KERVELLA_HIGH_M"
    if snr_best is not None and not math.isnan(snr_best):
        if snr_best > KERV_SNR_HIGH and m25 > KERV_M2_LIKELY:
            return "LIKELY_STELLAR_HIGH_SNR_KERVELLA"
    return "KERVELLA_AMBIGUOUS"


# ---------------------------------------------------------------------------
# Lesson #33 — Proper i-marginalization for A9 jerk inference
# ---------------------------------------------------------------------------
def imarg_a9_posterior(
    accel_mas_yr2: float, accel_err_mas_yr2: float,
    jerk_mas_yr3: float, jerk_err_mas_yr3: float,
    distance_pc: float,
    M1_msun: float = 1.0,
    N: int = 200000,
    rng: np.random.Generator | None = None,
) -> dict:
    """Proper inclination + orbital-phase marginalized M_2 posterior.

    Lesson #33: face-on (sin i = 1) is a peculiar assumption. Under isotropic
    P(i) ∝ sin(i), with marginalized orbital phase, the posterior admits
    edge-on solutions with longer P_orb and substantially higher M_2 for the
    same observed (accel, jerk).

    Units (matching `nss_accel9_extended_2026_05_13.py`):
      accel_mag = mas/yr²
      jerk_mag  = mas/yr³

    Convert to physical at given distance d [pc]:
      a_phys [m/s²] = accel[mas/yr²] × MAS_RAD × d[m] / YR_S²
      j_phys [m/s³] = jerk[mas/yr³]  × MAS_RAD × d[m] / YR_S³

    Geometric model (circular orbit, true anomaly φ, inclination i):
      Plane-of-sky position vector r_proj = a · (cos φ, sin φ · cos i)
      Acceleration mag (in plane-of-sky):
         |a_proj| = ω² a · f_accel(φ, i)
         where f_accel = sqrt(cos²φ + sin²φ · cos²i)
      Jerk mag (in plane-of-sky):
         |j_proj| = ω³ a · f_jerk(φ, i)
         where f_jerk = sqrt(sin²φ + cos²φ · cos²i)

    Ratio:
      R = |j|/|a| = ω · (f_jerk / f_accel)
      ⇒ ω = R · (f_accel / f_jerk)
      ⇒ P[yr] = 2π/ω

    a [m] = |a_phys| / (ω² · f_accel)
    Kepler-3:  ω² · a³ = G · M_tot
      ⇒ M_tot = ω² · a³ / G

    M2 obtained by subtracting M1.
    """
    rng = rng or np.random.default_rng(42)

    # Constants
    G_SI = 6.67430e-11
    M_SUN_KG = 1.98892e30
    M_JUP_KG = 1.89812e27
    YR_S = 365.25 * 86400.0
    MAS_RAD = 4.84813681109536e-9
    PC_M = 3.0856775814913673e16

    # Sample
    cos_i = rng.uniform(-1.0, 1.0, N)           # isotropic in cos i
    phi = rng.uniform(0.0, 2.0 * math.pi, N)
    cos2_i = cos_i ** 2

    # Sample observed accel, jerk with Gaussian errors
    sig_a = max(accel_err_mas_yr2, abs(accel_mas_yr2) * 0.01)
    sig_j = max(jerk_err_mas_yr3, abs(jerk_mas_yr3) * 0.01)
    a_obs_mas = np.abs(rng.normal(accel_mas_yr2, sig_a, N))
    j_obs_mas = np.abs(rng.normal(jerk_mas_yr3, sig_j, N))

    # Convert to physical (m/s², m/s³) at the source distance
    d_m = max(distance_pc, 1.0) * PC_M
    a_phys = a_obs_mas * MAS_RAD * d_m / (YR_S ** 2)   # m/s²
    j_phys = j_obs_mas * MAS_RAD * d_m / (YR_S ** 3)   # m/s³

    # Geometric factors
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    f_accel = np.sqrt(cos_phi ** 2 + sin_phi ** 2 * cos2_i)
    f_jerk = np.sqrt(sin_phi ** 2 + cos_phi ** 2 * cos2_i)
    # Avoid pathological zeros at deep edge-on + transit / quadrature combos
    f_accel = np.clip(f_accel, 1e-4, None)
    f_jerk = np.clip(f_jerk, 1e-4, None)

    # Angular frequency [rad/s]:  ω = (|j|/|a|) · (f_accel/f_jerk)
    omega = (j_phys / np.clip(a_phys, 1e-40, None)) * (f_accel / f_jerk)
    # Period in years
    P_yr = (2.0 * math.pi / omega) / YR_S
    # Semi-major axis [m]
    a_sma = a_phys / (omega ** 2 * f_accel)
    # Kepler-3 total mass
    M_tot_kg = (omega ** 2) * (a_sma ** 3) / G_SI
    M_tot_msun = M_tot_kg / M_SUN_KG
    M2_msun = M_tot_msun - M1_msun
    M2_mjup = M2_msun * M_SUN_KG / M_JUP_KG

    # Physical plausibility: PMa is sensitive for P_orb ~ 0.1–1000 yr
    # We require M_tot > M1 (else the data are inconsistent with that geometry).
    mask = (
        (P_yr > 0.1)
        & (P_yr < 1000.0)
        & np.isfinite(M2_mjup)
        & (M2_msun > 0)
        & (M2_mjup < 1e6)
    )
    n_valid = int(mask.sum())
    if n_valid < 30:
        # Fall back: report just face-on as a sanity check
        return {
            "M_2_mjup_imarg_median": float("nan"),
            "M_2_mjup_imarg_1lo": float("nan"),
            "M_2_mjup_imarg_1hi": float("nan"),
            "M_2_mjup_imarg_2hi": float("nan"),
            "P_substellar_imarg": float("nan"),
            "P_orb_yr_median": float("nan"),
            "n_samples_valid": n_valid,
        }
    m2 = M2_mjup[mask]
    p = P_yr[mask]
    return {
        "M_2_mjup_imarg_median": float(np.nanmedian(m2)),
        "M_2_mjup_imarg_1lo": float(np.nanpercentile(m2, 16.0)),
        "M_2_mjup_imarg_1hi": float(np.nanpercentile(m2, 84.0)),
        "M_2_mjup_imarg_2hi": float(np.nanpercentile(m2, 97.5)),
        "P_substellar_imarg": float(np.mean(m2 < 80.0)),
        "P_orb_yr_median": float(np.nanmedian(p)),
        "n_samples_valid": n_valid,
    }


# ---------------------------------------------------------------------------
# Pool processing
# ---------------------------------------------------------------------------
def load_pool(path: str) -> pl.DataFrame:
    return pl.read_csv(ROOT / path, infer_schema_length=20000)


def add_kervella_columns(df: pl.DataFrame, kerv: pl.DataFrame) -> pl.DataFrame:
    """Cross-match on HIP first, fall back to Gaia EDR3 source_id."""
    # Find ID columns
    hip_col = None
    for c in ["HIP", "HIP_hgca", "hip"]:
        if c in df.columns:
            hip_col = c
            break
    src_col = None
    for c in ["source_id", "GaiaEDR3"]:
        if c in df.columns:
            src_col = c
            break

    # Build join key
    if hip_col is not None:
        df = df.with_columns(pl.col(hip_col).cast(pl.Float64, strict=False).alias("_hip_join"))
    else:
        df = df.with_columns(pl.lit(None).cast(pl.Float64).alias("_hip_join"))
    if src_col is not None:
        df = df.with_columns(pl.col(src_col).cast(pl.Utf8, strict=False).alias("_src_join"))
    else:
        df = df.with_columns(pl.lit(None).cast(pl.Utf8).alias("_src_join"))

    kerv_hip = kerv.rename({"HIP": "_hip_join"}).drop("GaiaEDR3")
    kerv_src = kerv.rename({"GaiaEDR3": "_src_join"}).drop("HIP")

    out = df.join(kerv_hip, on="_hip_join", how="left", suffix="_kerv")
    # Where HIP join failed, try source_id
    out = out.join(
        kerv_src.select(
            "_src_join",
            pl.col("M25au").alias("M25au_src"),
            pl.col("M210au").alias("M210au_src"),
            pl.col("M230au").alias("M230au_src"),
            pl.col("snrPMa_best").alias("snrPMa_best_src"),
            pl.col("dVt").alias("dVt_src"),
            pl.col("snr_dVt").alias("snr_dVt_src"),
        ),
        on="_src_join",
        how="left",
    )
    out = out.with_columns(
        pl.col("M25au").fill_null(pl.col("M25au_src")),
        pl.col("M210au").fill_null(pl.col("M210au_src")),
        pl.col("M230au").fill_null(pl.col("M230au_src")),
        pl.col("snrPMa_best").fill_null(pl.col("snrPMa_best_src")),
        pl.col("dVt").fill_null(pl.col("dVt_src")),
        pl.col("snr_dVt").fill_null(pl.col("snr_dVt_src")),
    ).drop(["M25au_src", "M210au_src", "M230au_src", "snrPMa_best_src", "dVt_src", "snr_dVt_src"])

    # Compute classification
    def _cls(row):
        return classify_kervella(row["M25au"], row["snrPMa_best"])
    out = out.with_columns(
        pl.struct(["M25au", "snrPMa_best"]).map_elements(_cls, return_dtype=pl.Utf8).alias("kervella_flag_l34")
    )
    return out


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def phase1_universal_kervella(kerv: pl.DataFrame) -> dict[str, pl.DataFrame]:
    annotated: dict[str, pl.DataFrame] = {}
    summary_rows = []
    for name, path in POOLS.items():
        df = load_pool(path)
        df = add_kervella_columns(df, kerv)
        cnt = df.group_by("kervella_flag_l34").len().sort("len", descending=True)
        n_stellar = int(df.filter(pl.col("kervella_flag_l34") == "STELLAR_KERVELLA_HIGH_M").height)
        n_likely = int(df.filter(pl.col("kervella_flag_l34") == "LIKELY_STELLAR_HIGH_SNR_KERVELLA").height)
        n_total = df.height
        summary_rows.append({
            "pool": name,
            "n_total": n_total,
            "n_stellar_high_m": n_stellar,
            "n_likely_high_snr": n_likely,
            "n_with_kervella": int(df.filter(pl.col("kervella_flag_l34") != "NO_KERVELLA").height),
        })
        annotated[name] = df
        print(f"[Kervella] {name}: total={n_total}  stellar={n_stellar}  likely={n_likely}")
        print(cnt)
    summary = pl.DataFrame(summary_rows)
    summary.write_csv(OUT / "kervella_per_pool_summary.csv")
    return annotated


def phase1_collect_caught(annotated: dict[str, pl.DataFrame]) -> pl.DataFrame:
    """Collect all candidates newly flagged as stellar by Kervella."""
    pieces = []
    for name, df in annotated.items():
        # name / hip / source_id columns differ
        col_name = next((c for c in ["Name", "Name_hgca", "name"] if c in df.columns), None)
        col_hip = next((c for c in ["HIP", "HIP_hgca", "hip"] if c in df.columns), None)
        col_src = next((c for c in ["source_id"] if c in df.columns), None)
        col_v = next((c for c in ["Vmag", "Vmag_hgca", "v_mag", "phot_g_mean_mag"] if c in df.columns), None)
        col_sp = next((c for c in ["SpType", "SpType_hgca", "sptype"] if c in df.columns), None)
        col_dist = next((c for c in ["distance_pc"] if c in df.columns), None)

        sel = df.filter(
            pl.col("kervella_flag_l34").is_in(
                ["STELLAR_KERVELLA_HIGH_M", "LIKELY_STELLAR_HIGH_SNR_KERVELLA"]
            )
        )
        if sel.height == 0:
            continue
        out = pl.DataFrame({
            "pool": [name] * sel.height,
            "Name": sel[col_name] if col_name else pl.Series([None] * sel.height, dtype=pl.Utf8),
            "HIP": sel[col_hip].cast(pl.Float64, strict=False) if col_hip else pl.Series([None] * sel.height, dtype=pl.Float64),
            "source_id": sel[col_src].cast(pl.Int64, strict=False) if col_src else pl.Series([None] * sel.height, dtype=pl.Int64),
            "Vmag": sel[col_v].cast(pl.Float64, strict=False) if col_v else pl.Series([None] * sel.height, dtype=pl.Float64),
            "SpType": sel[col_sp] if col_sp else pl.Series([None] * sel.height, dtype=pl.Utf8),
            "distance_pc": sel[col_dist] if col_dist else pl.Series([None] * sel.height, dtype=pl.Float64),
            "M25au_mjup": sel["M25au"],
            "M210au_mjup": sel["M210au"],
            "snrPMa_best": sel["snrPMa_best"],
            "kervella_flag_l34": sel["kervella_flag_l34"],
        })
        pieces.append(out)
    if not pieces:
        return pl.DataFrame()
    full = pl.concat(pieces, how="vertical_relaxed")
    full.write_csv(OUT / "kervella_stellar_caught.csv")
    return full


def phase2_a9_imarginalized(kerv: pl.DataFrame) -> pl.DataFrame:
    """Reapply i-marg to A9 actionable + novel pool."""
    paths = [
        "data/candidate_dossiers/nss_accel9_extended_2026_05_13/actionable_a9_clean.csv",
        "data/candidate_dossiers/nss_accel9_extended_2026_05_13/cleaned_a9_pool_annotated.csv",
    ]
    dfs = []
    for p in paths:
        if (ROOT / p).exists():
            d = pl.read_csv(ROOT / p, infer_schema_length=20000)
            d = d.with_columns(pl.lit(p.split("/")[-1]).alias("_a9_source"))
            dfs.append(d)
    a9 = pl.concat(dfs, how="diagonal_relaxed")
    print(f"\n[A9 i-marg] processing {a9.height} A9 rows")

    # Estimate M1 from HGCA M1 if present, SpType spectral mass otherwise, fallback 1.0.
    if "M1_msun" in a9.columns:
        M1 = a9["M1_msun"].to_numpy()
    elif "M1" in a9.columns:
        M1 = a9["M1"].to_numpy()
    else:
        M1 = np.ones(a9.height)

    a9 = add_kervella_columns(a9, kerv)

    accel = a9["accel_mag"].to_numpy()
    accel_err = a9["accel_mag_err"].to_numpy() if "accel_mag_err" in a9.columns else None
    jerk = a9["jerk_mag"].to_numpy()
    jerk_err = a9["jerk_mag_err"].to_numpy() if "jerk_mag_err" in a9.columns else None
    dist = a9["distance_pc"].to_numpy() if "distance_pc" in a9.columns else None
    if dist is None and "parallax" in a9.columns:
        dist = 1000.0 / np.maximum(a9["parallax"].to_numpy(), 1e-3)

    rng = np.random.default_rng(2025_05_13)
    out_rows = []
    for i in range(a9.height):
        if not (np.isfinite(accel[i]) and np.isfinite(jerk[i])):
            out_rows.append({
                "M_2_mjup_imarg_median": float("nan"),
                "M_2_mjup_imarg_1lo": float("nan"),
                "M_2_mjup_imarg_1hi": float("nan"),
                "M_2_mjup_imarg_2hi": float("nan"),
                "P_substellar_imarg": float("nan"),
                "P_orb_yr_median": float("nan"),
                "n_samples_valid": 0,
            })
            continue
        ms1 = float(M1[i]) if np.isfinite(M1[i]) and M1[i] > 0 else 1.0
        a_err = float(accel_err[i]) if accel_err is not None and np.isfinite(accel_err[i]) else 0.1 * abs(float(accel[i]))
        j_err = float(jerk_err[i]) if jerk_err is not None and np.isfinite(jerk_err[i]) else 0.1 * abs(float(jerk[i]))
        d_pc = float(dist[i]) if dist is not None and np.isfinite(dist[i]) else 50.0
        post = imarg_a9_posterior(
            accel_mas_yr2=float(accel[i]), accel_err_mas_yr2=a_err,
            jerk_mas_yr3=float(jerk[i]), jerk_err_mas_yr3=j_err,
            distance_pc=d_pc,
            M1_msun=ms1,
            N=200000,
            rng=rng,
        )
        out_rows.append(post)
    post_df = pl.DataFrame(out_rows)
    full = pl.concat([a9, post_df], how="horizontal")
    full.write_csv(OUT / "a9_inclination_marginalized.csv")
    return full


def phase3_apply_to_all(annotated: dict[str, pl.DataFrame], a9_imarg: pl.DataFrame) -> pl.DataFrame:
    """Phase 3 / 4 / 5 — apply both lessons, identify imposters, output final list."""
    # Pull A9-i-marg keyed by source_id for joining back to pools
    a9_key = a9_imarg.select(
        "source_id",
        pl.col("M_2_mjup_imarg_median").alias("A9_M2_imarg_med_mjup"),
        pl.col("M_2_mjup_imarg_1lo").alias("A9_M2_imarg_1lo_mjup"),
        pl.col("M_2_mjup_imarg_1hi").alias("A9_M2_imarg_1hi_mjup"),
        pl.col("M_2_mjup_imarg_2hi").alias("A9_M2_imarg_2hi_mjup"),
        pl.col("P_substellar_imarg").alias("A9_P_substellar_imarg"),
        pl.col("P_orb_yr_median").alias("A9_P_orb_yr_med"),
    ).unique(subset=["source_id"])

    rows = []
    for name, df in annotated.items():
        col_name = next((c for c in ["Name", "Name_hgca", "name"] if c in df.columns), None)
        col_hip = next((c for c in ["HIP", "HIP_hgca", "hip"] if c in df.columns), None)
        col_src = next((c for c in ["source_id"] if c in df.columns), None)
        col_v = next((c for c in ["Vmag", "Vmag_hgca", "v_mag"] if c in df.columns), None)
        col_sp = next((c for c in ["SpType", "SpType_hgca"] if c in df.columns), None)
        col_dist = next((c for c in ["distance_pc"] if c in df.columns), None)

        # Pull M2 estimates (varies by pool)
        col_m2 = None
        for c in ["M_2_mjup_ours", "M_2_median_mjup", "m2_mjup_P10yr", "M2_marg", "M_2_median_true"]:
            if c in df.columns:
                col_m2 = c
                break
        col_score = None
        for c in ["composite_score", "master_score", "priority_score", "substellar_rank_score", "roi_score"]:
            if c in df.columns:
                col_score = c
                break

        sel = df.with_columns(
            pl.lit(name).alias("origin_pool"),
            (pl.col(col_name) if col_name else pl.lit(None)).alias("Name"),
            (pl.col(col_hip).cast(pl.Float64, strict=False) if col_hip else pl.lit(None).cast(pl.Float64)).alias("HIP"),
            (pl.col(col_src).cast(pl.Int64, strict=False) if col_src else pl.lit(None).cast(pl.Int64)).alias("source_id"),
            (pl.col(col_v).cast(pl.Float64, strict=False) if col_v else pl.lit(None).cast(pl.Float64)).alias("Vmag"),
            (pl.col(col_sp) if col_sp else pl.lit(None)).alias("SpType"),
            (pl.col(col_dist) if col_dist else pl.lit(None).cast(pl.Float64)).alias("distance_pc"),
            (pl.col(col_m2).cast(pl.Float64, strict=False) if col_m2 else pl.lit(None).cast(pl.Float64)).alias("M2_orig_mjup"),
            (pl.col(col_score).cast(pl.Float64, strict=False) if col_score else pl.lit(None).cast(pl.Float64)).alias("orig_score"),
        ).select(
            "origin_pool", "Name", "HIP", "source_id", "Vmag", "SpType", "distance_pc",
            "M2_orig_mjup", "orig_score",
            "M25au", "M210au", "snrPMa_best", "kervella_flag_l34",
        )
        rows.append(sel)
    full = pl.concat(rows, how="vertical_relaxed")

    # Join A9 i-marg
    full = full.join(a9_key, on="source_id", how="left")

    # Deduplicate by source_id keeping best score, but propagate Name/HIP/SpType from
    # *any* pool's record where present.
    name_lookup = (
        full.filter(pl.col("Name").is_not_null())
        .group_by("source_id")
        .agg(pl.col("Name").first().alias("Name_best"),
             pl.col("HIP").first().alias("HIP_best"),
             pl.col("SpType").first().alias("SpType_best"),
             pl.col("Vmag").first().alias("Vmag_best"))
    )
    full = full.sort("orig_score", descending=True, nulls_last=True)
    full = full.unique(subset=["source_id"], keep="first")
    full = full.join(name_lookup, on="source_id", how="left").with_columns(
        pl.col("Name").fill_null(pl.col("Name_best")),
        pl.col("HIP").fill_null(pl.col("HIP_best")),
        pl.col("SpType").fill_null(pl.col("SpType_best")),
        pl.col("Vmag").fill_null(pl.col("Vmag_best")),
    ).drop(["Name_best", "HIP_best", "SpType_best", "Vmag_best"])

    # Apply imposter flag (combined Lessons 33 + 34) — fill nulls in each comparison
    full = full.with_columns(
        kerv_stellar=(pl.col("kervella_flag_l34") == "STELLAR_KERVELLA_HIGH_M").fill_null(False),
        kerv_likely=(pl.col("kervella_flag_l34") == "LIKELY_STELLAR_HIGH_SNR_KERVELLA").fill_null(False),
        a9_imarg_stellar=(pl.col("A9_M2_imarg_med_mjup").fill_null(0.0) > 80.0),
    )
    full = full.with_columns(
        (pl.col("kerv_stellar") | pl.col("kerv_likely") | pl.col("a9_imarg_stellar")).alias("imposter_l33_l34")
    )

    # Composite score updated: penalize imposters, reward substellar evidence
    # base = orig_score, multiplied by (1 - imposter), boosted by inverse M2
    full = full.with_columns(
        pl.when(pl.col("imposter_l33_l34"))
        .then(pl.lit(0.0))
        .otherwise(pl.col("orig_score").fill_null(0.0))
        .alias("score_post_l33_l34")
    )

    full.write_csv(OUT / "all_pools_annotated.csv")
    return full


def phase4_update_master_filter(full: pl.DataFrame) -> pl.DataFrame:
    """Update master_filter_NOT_NOVEL.csv with newly caught imposters."""
    master = pl.read_csv(MASTER_NOT_NOVEL, infer_schema_length=10000)
    master = master.with_columns(pl.col("source_id").cast(pl.Int64, strict=False))
    n_before = master.height

    new_imposters = full.filter(pl.col("imposter_l33_l34")).select(
        pl.col("source_id"),
        pl.col("Name").alias("name"),
        pl.lit("KERVELLA_OR_A9_IMARG").alias("verdict"),
        pl.lit("Lesson_33_34").alias("table"),
        pl.lit("2026-05-13 retroactive").alias("reference"),
        pl.lit(3).alias("prio"),
    ).drop_nulls(subset=["source_id"]).unique(subset=["source_id"])

    # Be more specific in verdict
    new_imposters = new_imposters.join(
        full.select(
            pl.col("source_id"),
            pl.col("kervella_flag_l34"),
            pl.col("A9_M2_imarg_med_mjup"),
        ),
        on="source_id",
        how="left",
    ).with_columns(
        pl.when(pl.col("kervella_flag_l34") == "STELLAR_KERVELLA_HIGH_M")
        .then(pl.lit("KERV_M2_5AU_GT_200MJ"))
        .when(pl.col("kervella_flag_l34") == "LIKELY_STELLAR_HIGH_SNR_KERVELLA")
        .then(pl.lit("KERV_HIGH_SNR_M2_GT_100MJ"))
        .when(pl.col("A9_M2_imarg_med_mjup") > 80.0)
        .then(pl.lit("A9_IMARG_M2_GT_80MJ"))
        .otherwise(pl.lit("KERVELLA_OR_A9_IMARG"))
        .alias("verdict"),
    ).select("source_id", "name", "verdict", "table", "reference", "prio")

    # Drop ones already in master
    already = set(master["source_id"].to_list())
    new_only = new_imposters.filter(~pl.col("source_id").is_in(list(already)))
    print(f"[Master filter] before={n_before}  new imposters caught (not already)={new_only.height}")

    combined = pl.concat([master, new_only], how="vertical_relaxed")
    combined.write_csv(OUT / "master_filter_NOT_NOVEL_updated.csv")
    return combined


def phase5_final_ranked(full: pl.DataFrame) -> pl.DataFrame:
    surv = full.filter(~pl.col("imposter_l33_l34"))
    # Build final ranked novelty list
    surv = surv.with_columns(
        pl.col("score_post_l33_l34").rank(method="ordinal", descending=True).alias("rank_post_l33_l34"),
    ).sort("score_post_l33_l34", descending=True, nulls_last=True)

    surv_export = surv.select(
        "rank_post_l33_l34", "origin_pool", "Name", "HIP", "source_id",
        "Vmag", "SpType", "distance_pc",
        "M2_orig_mjup",
        pl.col("M25au").alias("Kervella_M2_5au_mjup"),
        pl.col("M210au").alias("Kervella_M2_10au_mjup"),
        "snrPMa_best",
        "kervella_flag_l34",
        "A9_M2_imarg_med_mjup", "A9_M2_imarg_1lo_mjup", "A9_M2_imarg_1hi_mjup",
        "A9_P_substellar_imarg", "A9_P_orb_yr_med",
        "score_post_l33_l34",
    )
    surv_export.write_csv(OUT / "FINAL_RANKED_NOVELTY.csv")
    return surv_export


# ---------------------------------------------------------------------------
# Verdicts on specific targets
# ---------------------------------------------------------------------------
def verdict_specific(annotated: dict[str, pl.DataFrame], a9_imarg: pl.DataFrame) -> dict[str, dict]:
    """Returns named-target verdict dict."""
    targets = {
        "HD 120954": {"HIP": 67777.0},
        "HD 7399":   {"HIP": 5750.0},
        "HD 30944":  {"HIP": 22711.0},
        "HD 115916": {"HIP": 65167.0},
        "BD+26 4555": {"HIP": 113826.0},
        "HD 38094":  {"HIP": 27077.0},
        "HD 222451": {"HIP": 116727.0},
        "HD 101767": {"HIP": 57084.0},
        "HD 104828": {"HIP": 58860.0},
    }
    verdicts = {}
    for name, key in targets.items():
        hip = key["HIP"]
        info: dict = {"HIP": hip, "name": name}
        # check Kervella + flag in each pool
        in_pools = []
        for pool_name, df in annotated.items():
            col_hip = next((c for c in ["HIP", "HIP_hgca", "hip"] if c in df.columns), None)
            if col_hip is None:
                continue
            hit = df.filter(pl.col(col_hip).cast(pl.Float64, strict=False) == hip)
            if hit.height > 0:
                in_pools.append(pool_name)
                # use first
                row = hit.row(0, named=True)
                info[f"{pool_name}_kerv_flag"] = row.get("kervella_flag_l34")
                info[f"{pool_name}_M25au"] = row.get("M25au")
        info["in_pools"] = ",".join(in_pools)

        # A9 i-marg
        a9_col_hip = "HIP_hgca"
        if a9_col_hip in a9_imarg.columns:
            hit = a9_imarg.filter(pl.col(a9_col_hip).cast(pl.Float64, strict=False) == hip)
            if hit.height > 0:
                row = hit.row(0, named=True)
                info["A9_M2_face_mjup"] = row.get("M_2_face_mjup")
                info["A9_M2_imarg_median_mjup"] = row.get("M_2_mjup_imarg_median")
                info["A9_M2_imarg_1hi_mjup"] = row.get("M_2_mjup_imarg_1hi")
                info["A9_M2_imarg_2hi_mjup"] = row.get("M_2_mjup_imarg_2hi")
                info["A9_P_substellar"] = row.get("P_substellar_imarg")
                info["A9_P_orb_yr_median"] = row.get("P_orb_yr_median")
        verdicts[name] = info
    return verdicts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 80)
    print("Retroactive Lessons #33 (A9 i-marg) + #34 (Universal Kervella PMa M_2)")
    print("=" * 80)

    print("\n[Phase 0] Loading Kervella 2022 PMa catalog")
    kerv = load_kervella()
    print(f"  Kervella rows: {kerv.height}")

    print("\n[Phase 1] Universal Kervella stellar pre-filter applied to ALL pools")
    annotated = phase1_universal_kervella(kerv)
    caught = phase1_collect_caught(annotated)
    print(f"\n[Phase 1] Total newly-caught stellar imposters across pools: {caught.height}")

    print("\n[Phase 2] Inclination-marginalized A9 jerk posterior")
    a9_imarg = phase2_a9_imarginalized(kerv)
    print(f"  A9 rows processed: {a9_imarg.height}")

    print("\n[Phase 3] Combined re-ranking across all pools")
    full = phase3_apply_to_all(annotated, a9_imarg)
    print(f"  total unique candidates: {full.height}")
    print(f"  imposters flagged: {full.filter(pl.col('imposter_l33_l34')).height}")

    print("\n[Phase 4] master_filter_NOT_NOVEL update")
    master_updated = phase4_update_master_filter(full)
    print(f"  master filter rows now: {master_updated.height}")

    print("\n[Phase 5] FINAL_RANKED_NOVELTY")
    final = phase5_final_ranked(full)
    print(f"  surviving truly-novel candidates: {final.height}")

    print("\n[Phase 6] Specific-target verdicts")
    verdicts = verdict_specific(annotated, a9_imarg)
    import json
    with open(OUT / "specific_target_verdicts.json", "w") as fh:
        json.dump(verdicts, fh, indent=2, default=str)
    for k, v in verdicts.items():
        print(f"  {k}: in_pools={v.get('in_pools')}  A9_imarg_med={v.get('A9_M2_imarg_median_mjup')}  A9_P_substellar={v.get('A9_P_substellar')}")

    print("\nDONE — outputs in", OUT)


if __name__ == "__main__":
    main()

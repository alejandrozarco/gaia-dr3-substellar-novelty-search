"""Apply Filters L17 (K_RV/K_pred), L18 (Trifonov sb_flag), L19 (WDS visual binary) to surviving NSS candidate pools.

L17: K_RV/K_pred pre-screen
  - Inputs: candidate with archival RV (HARPS/HIRES/APOGEE) AND (NSS-Accel sig > 20 OR HGCA snrPMa > 5)
  - Compute K_RV (peak-to-peak/2 in archival data)
  - Compute K_pred at sin(i)=1 (formula 28.4329 * M2_MJ * Mtot^-2/3 * P^-1/3 / sqrt(1-e^2))
  - If K_RV / K_pred > 2 -> STELLAR_K_RV_INCONSISTENT

L18: Trifonov 2025 HIRES sb_flag cross-match
  - Compute sb_flag = (rms_resid > 5*med_sig) AND (rms_resid > 1000 m/s) for ALL Trifonov targets
  - Cross-match by Gaia DR3 source_id when available; otherwise coord cone 5" with PM correction
  - If matched AND sb_flag=True -> STELLAR_HIRES_SB

L19: WDS within 15" companion check
  - For each candidate's PM-corrected coords (at WDS observation epoch ~2010 typical):
    - find WDS rows within 15"
    - if WDS sep in 1-15" AND mag2 < 14 -> VISUAL_BINARY_OUTER
"""
from __future__ import annotations

import math
import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path("/Users/legbatterij/claude_projects/ostinato")
OUT_DIR = ROOT / "data/candidate_dossiers/new_filters_l17_l19_2026_05_12"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ----------- Helpers --------------------------------------------------------

GAIA_EPOCH = 2016.0  # Gaia DR3 ref epoch
WDS_EPOCH = 2010.0   # typical WDS recent obs epoch -- close enough for 15" search
PM_DELTA_YR = WDS_EPOCH - GAIA_EPOCH  # negative (we shift back from Gaia 2016 to ~2010)


def pm_correct(ra, dec, pmra, pmdec, delta_yr):
    """Return (ra', dec') after applying PM in mas/yr over delta_yr.
    pmra is in mas/yr along RA*cos(dec); pmdec in mas/yr.
    """
    cosd = np.cos(np.deg2rad(dec))
    cosd = np.where(np.abs(cosd) < 1e-9, 1e-9, cosd)
    dra_deg = (pmra / 1000.0 / 3600.0) * delta_yr / cosd
    ddec_deg = (pmdec / 1000.0 / 3600.0) * delta_yr
    return ra + dra_deg, dec + ddec_deg


def cone_match_flat(ra_a, dec_a, ra_b, dec_b, tol_arcsec):
    """Naive O(N*M) cone match (RA*cos(Dec) flat tree) — fine for our sizes.
    Returns boolean of shape (len(a), len(b)).
    """
    cosd = np.cos(np.deg2rad(dec_a[:, None]))
    dra = (ra_a[:, None] - ra_b[None, :]) * cosd * 3600.0
    ddec = (dec_a[:, None] - dec_b[None, :]) * 3600.0
    sep = np.sqrt(dra * dra + ddec * ddec)
    return sep <= tol_arcsec, sep


# ----------- Load pools ------------------------------------------------------

print("[1] Loading pools ...")
nss_orb_truly = pl.read_csv(ROOT / "data/candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/cleaned_nss_orbital_truly_novel.csv")
nss_accel_tierS = pl.read_csv(ROOT / "data/candidate_dossiers/nss_accel_14450_filter_2026_05_12/tier_S_survivors.csv")
nss_accel_14450 = pl.read_csv(ROOT / "data/candidate_dossiers/nss_accel_14450_filter_2026_05_12/cleaned_14450.csv")
nss_accel_broader = nss_accel_14450.filter(pl.col("imposter_filter") == "")
print(f"  NSS Orb truly_novel: {nss_orb_truly.height}")
print(f"  NSS Accel Tier S: {nss_accel_tierS.height}")
print(f"  NSS Accel broader (not flagged): {nss_accel_broader.height}")

# NSS orbital truly_novel lacks ra/dec/pm — join from full NSS orbital
print("[2] Joining NSS orbital coords + pm ...")
nss_full = pl.read_parquet(ROOT / "data/external_catalogs/parquets/gaia_dr3_nss_two_body_orbit.parquet")
nss_full_slim = nss_full.select(["source_id", "ra", "dec", "pmra", "pmdec"]).unique(subset=["source_id"])
nss_orb_truly = nss_orb_truly.join(nss_full_slim, on="source_id", how="left")
# Some sources may have nulls (e.g., NSS combined astro+spectro pool); fill via Sahl/inventory
print(f"  After join: {nss_orb_truly.height} rows; with ra: {nss_orb_truly.filter(pl.col('ra').is_not_null()).height}")


# ----------- Filter L18: Trifonov sb_flag -----------------------------------

print("\n[3] Computing Trifonov sb_flag for ALL targets (RV-table-based) ...")
trif_targets = pl.read_parquet(ROOT / "data/external_catalogs/parquets/trifonov2025_hires_targets.parquet")
trif_rv = pl.read_parquet(ROOT / "data/external_catalogs/parquets/trifonov2025_hires_rv.parquet")

# Compute sb_flag = (rms_resid > 5*med_sig) AND (rms_resid > 1000 m/s) per target
# We use linear-detrended residuals; if N<3 -> False
def compute_target_sb(rv_df: pl.DataFrame) -> dict:
    """Per-target: linear detrend, return sb_flag and stats."""
    out = {}
    for tgt, sub in rv_df.group_by("name", maintain_order=True):
        # safe-extract
        tgt = tgt[0] if isinstance(tgt, tuple) else tgt
        bjd = sub["bjd"].to_numpy()
        # Use rv_cor_mps (corrected), else rv_raw_mps
        rv = sub["rv_cor_mps"].to_numpy() if sub["rv_cor_mps"].null_count() < len(sub) else sub["rv_raw_mps"].to_numpy()
        sig = sub["e_rv_cor_mps"].to_numpy() if sub["e_rv_cor_mps"].null_count() < len(sub) else sub["e_rv_mps"].to_numpy()
        # filter NaN
        mask = np.isfinite(bjd) & np.isfinite(rv) & np.isfinite(sig)
        bjd = bjd[mask]; rv = rv[mask]; sig = sig[mask]
        if len(bjd) < 3:
            out[tgt] = {"sb_flag": False, "rms_resid": float("nan"), "med_sig": float("nan"), "n_rv": int(len(bjd)), "p2p": float("nan")}
            continue
        # WLS linear fit
        t = (bjd - bjd.min()) / 365.25
        w = 1.0 / np.where(sig > 0, sig * sig, 1.0)
        Sw = w.sum(); Swx = (w*t).sum(); Swy = (w*rv).sum(); Swxx = (w*t*t).sum(); Swxy = (w*t*rv).sum()
        det = Sw*Swxx - Swx*Swx
        if det == 0:
            out[tgt] = {"sb_flag": False, "rms_resid": float(np.std(rv)), "med_sig": float(np.median(sig)), "n_rv": int(len(bjd)), "p2p": float(rv.max()-rv.min())}
            continue
        m = (Sw*Swxy - Swx*Swy) / det
        b = (Swxx*Swy - Swx*Swxy) / det
        resid = rv - m*t - b
        rms = float(np.sqrt(np.mean(resid*resid)))
        med = float(np.median(sig))
        sb = bool((rms > 5*med) and (rms > 1000.0))
        out[tgt] = {"sb_flag": sb, "rms_resid": rms, "med_sig": med, "n_rv": int(len(bjd)), "p2p": float(rv.max()-rv.min())}
    return out


trif_sb_dict = compute_target_sb(trif_rv)
print(f"  Targets evaluated: {len(trif_sb_dict)}")
n_sb = sum(1 for v in trif_sb_dict.values() if v["sb_flag"])
print(f"  sb_flag=True: {n_sb}")

# Build a polars frame: name, ra_deg, dec_deg, sb_flag, p2p
trif_sb_rows = []
for r in trif_targets.iter_rows(named=True):
    stats = trif_sb_dict.get(r["name"], {"sb_flag": False, "rms_resid": float("nan"), "med_sig": float("nan"), "n_rv": 0, "p2p": float("nan")})
    trif_sb_rows.append({
        "name": r["name"], "simbad": r["simbad"], "ra_deg": r["ra_deg"], "dec_deg": r["dec_deg"],
        "sb_flag": stats["sb_flag"], "rms_resid_mps": stats["rms_resid"], "p2p_mps": stats["p2p"], "n_rv_eval": stats["n_rv"],
    })
trif_sb_df = pl.DataFrame(trif_sb_rows)
print(f"  Trifonov sb-eval rows: {trif_sb_df.height}; sb_flag=True: {trif_sb_df.filter(pl.col('sb_flag')==True).height}")

# Also add explicit sb_flag-True from the HGCA candidates CSV (already-known Gaia IDs)
trif_hgca_cands = pl.read_csv(ROOT / "data/candidate_dossiers/trifonov2025_hires_overlap_2026_05_11/trifonov_new_hgca_rv_candidates.csv")
known_sb_gaia = set(trif_hgca_cands.filter(pl.col("sb_flag") == True)["Gaia"].to_list())
print(f"  Trifonov HGCA cand sb_flag=True Gaia IDs (priority match): {len(known_sb_gaia)}")


def apply_l18(pool_df: pl.DataFrame, name_col: str = "Name") -> pl.DataFrame:
    """Match pool to Trifonov sb_flag=True (coord cone 5" PM-corrected; also direct Gaia ID)."""
    # First: direct Gaia ID match (cheaper)
    direct = pool_df.with_columns(
        pl.col("source_id").is_in(list(known_sb_gaia)).alias("_L18_gaia_match")
    )
    # Coord cone match: only need to do for sb_flag=True Trifonov entries
    sb_true = trif_sb_df.filter(pl.col("sb_flag") == True)
    if pool_df.filter(pl.col("ra").is_not_null()).height == 0 or sb_true.height == 0:
        result = direct.with_columns(pl.col("_L18_gaia_match").alias("L18_flag"))
        return result.with_columns(
            pl.when(pl.col("L18_flag")).then(pl.lit("STELLAR_HIRES_SB")).otherwise(pl.lit(None)).alias("L18_reason")
        )
    # PM-correct candidate coords back to ~mid-2010 (Trifonov RV mid-baseline ~2005)
    pool_arr = direct.filter(pl.col("ra").is_not_null()).select(["source_id", "ra", "dec", "pmra", "pmdec"])
    pool_ra = pool_arr["ra"].to_numpy()
    pool_dec = pool_arr["dec"].to_numpy()
    pool_pmra = np.nan_to_num(pool_arr["pmra"].to_numpy(), nan=0.0)
    pool_pmdec = np.nan_to_num(pool_arr["pmdec"].to_numpy(), nan=0.0)
    p_ra, p_dec = pm_correct(pool_ra, pool_dec, pool_pmra, pool_pmdec, PM_DELTA_YR)
    sb_ra = sb_true["ra_deg"].to_numpy()
    sb_dec = sb_true["dec_deg"].to_numpy()
    # batched cone match (chunked to keep memory sane)
    matched_ids = set()
    sb_match_info = {}  # source_id -> (trif_name, sep)
    CHUNK = 1000
    for ci in range(0, len(p_ra), CHUNK):
        c_ra = p_ra[ci:ci+CHUNK]
        c_dec = p_dec[ci:ci+CHUNK]
        match_mat, sep_mat = cone_match_flat(c_ra, c_dec, sb_ra, sb_dec, 5.0)
        idx = np.argwhere(match_mat)
        for i_local, j in idx:
            sid = pool_arr["source_id"][ci + int(i_local)]
            matched_ids.add(sid)
            trif_name = sb_true["name"][int(j)]
            sb_match_info[sid] = (trif_name, float(sep_mat[i_local, j]))
    # Combine with direct
    print(f"  L18 coord-cone matches: {len(matched_ids)}; direct Gaia matches: {direct.filter(pl.col('_L18_gaia_match'))['source_id'].n_unique()}")
    cone_matched_list = list(matched_ids)
    result = direct.with_columns([
        (pl.col("_L18_gaia_match") | pl.col("source_id").is_in(cone_matched_list)).alias("L18_flag"),
    ])
    # add L18_reason
    result = result.with_columns(
        pl.when(pl.col("L18_flag")).then(pl.lit("STELLAR_HIRES_SB")).otherwise(pl.lit(None)).alias("L18_reason")
    ).drop("_L18_gaia_match")
    return result


# ----------- Filter L19: WDS visual binary -----------------------------------

print("\n[4] Loading WDS catalog ...")
wds = pl.read_parquet(ROOT / "data/external_catalogs/parquets/wds_b_wds.parquet")
print(f"  WDS rows: {wds.height}")


def apply_l19(pool_df: pl.DataFrame) -> pl.DataFrame:
    """Cross-match pool against WDS within 15"."""
    if pool_df.filter(pl.col("ra").is_not_null()).height == 0:
        return pool_df.with_columns([
            pl.lit(False).alias("L19_flag"),
            pl.lit(None, dtype=pl.Utf8).alias("L19_reason"),
            pl.lit(None, dtype=pl.Utf8).alias("L19_WDS"),
            pl.lit(None, dtype=pl.Float64).alias("L19_sep_arcsec"),
            pl.lit(None, dtype=pl.Float64).alias("L19_mag2"),
        ])
    # PM-correct candidate coords back to ~mid-2000 (typical WDS recent epoch is 1990-2015; use 2010)
    pool_ra = pool_df["ra"].to_numpy()
    pool_dec = pool_df["dec"].to_numpy()
    pool_pmra = np.nan_to_num(pool_df["pmra"].to_numpy(), nan=0.0)
    pool_pmdec = np.nan_to_num(pool_df["pmdec"].to_numpy(), nan=0.0)
    # Mask null ra
    ra_mask = np.isfinite(pool_ra) & np.isfinite(pool_dec)
    p_ra, p_dec = pm_correct(pool_ra, pool_dec, pool_pmra, pool_pmdec, PM_DELTA_YR)

    wds_ra = wds["ra_deg"].to_numpy()
    wds_dec = wds["dec_deg"].to_numpy()
    wds_sep1 = wds["sep1"].to_numpy()
    wds_sep2 = wds["sep2"].to_numpy()
    wds_mag1 = wds["mag1"].to_numpy()
    wds_mag2 = wds["mag2"].to_numpy()
    wds_wdsid = wds["WDS"].to_list()

    # Pre-filter WDS by declination band (matches are within 15") to reduce work
    # Use chunked cone match
    L19_flag = np.zeros(len(pool_ra), dtype=bool)
    L19_reason = [None] * len(pool_ra)
    L19_wdsid = [None] * len(pool_ra)
    L19_sep = [None] * len(pool_ra)
    L19_mag2 = [None] * len(pool_ra)

    # Use a dec-band index for WDS: bucket by 1-deg dec
    wds_dec_buckets: dict[int, list[int]] = {}
    for i, d in enumerate(wds_dec):
        b = int(math.floor(d))
        wds_dec_buckets.setdefault(b, []).append(i)

    for k in range(len(p_ra)):
        if not ra_mask[k]:
            continue
        dec_k = p_dec[k]
        ra_k = p_ra[k]
        # Get candidate WDS rows in dec bands [dec-1, dec, dec+1] (15" << 1 deg)
        bk = int(math.floor(dec_k))
        idxs = []
        for bb in (bk-1, bk, bk+1):
            if bb in wds_dec_buckets:
                idxs.extend(wds_dec_buckets[bb])
        if not idxs:
            continue
        idxs = np.array(idxs)
        cand_ra = wds_ra[idxs]
        cand_dec = wds_dec[idxs]
        cosd = np.cos(np.deg2rad(dec_k))
        dra = (ra_k - cand_ra) * cosd * 3600.0
        ddec = (dec_k - cand_dec) * 3600.0
        sep = np.sqrt(dra*dra + ddec*ddec)
        # within 15" cone
        within = np.where(sep <= 15.0)[0]
        if len(within) == 0:
            continue
        # For each match, apply per-rule: sep1 in [1,15] AND mag2 < 14 -> imposter
        best = None
        for j_local in within:
            j = idxs[j_local]
            s1 = wds_sep1[j]
            m2 = wds_mag2[j]
            if not (np.isfinite(s1) and np.isfinite(m2)):
                continue
            if 1.0 <= float(s1) <= 15.0 and float(m2) < 14.0:
                # candidate flagged
                if (best is None) or (float(s1) < best[1]):
                    best = (wds_wdsid[j], float(s1), float(m2), float(sep[j_local]))
        if best:
            L19_flag[k] = True
            L19_reason[k] = "VISUAL_BINARY_OUTER"
            L19_wdsid[k] = best[0]
            L19_sep[k] = best[1]
            L19_mag2[k] = best[2]

    return pool_df.with_columns([
        pl.Series("L19_flag", L19_flag),
        pl.Series("L19_reason", L19_reason, dtype=pl.Utf8),
        pl.Series("L19_WDS", L19_wdsid, dtype=pl.Utf8),
        pl.Series("L19_sep_arcsec", L19_sep, dtype=pl.Float64),
        pl.Series("L19_mag2", L19_mag2, dtype=pl.Float64),
    ])


# ----------- Filter L17: K_RV/K_pred -----------------------------------------

print("\n[5] Building K_RV per source from RV archives ...")
# Use rv_inventory (orbital pool) + Trifonov RV (HIRES) for peak-to-peak measurement
rv_inv = pl.read_csv(ROOT / "data/candidate_dossiers/rv_coverage_2026_05_12/rv_inventory.csv")

# K_RV from Trifonov RV: peak-to-peak / 2 by Gaia source (via trif name match)
# Build a name->Gaia map from existing Trifonov HGCA cands (this has Gaia IDs)
trif_name_to_gaia = {}
for r in trif_hgca_cands.iter_rows(named=True):
    if r["trif_name"]:
        trif_name_to_gaia[r["trif_name"]] = int(r["Gaia"])
# Also possibly from 999sb1
trif_sb1 = pl.read_csv(ROOT / "data/candidate_dossiers/trifonov2025_hires_overlap_2026_05_11/trifonov_x_999sb1.csv")
for r in trif_sb1.iter_rows(named=True):
    if r["trif_name"]:
        trif_name_to_gaia[r["trif_name"]] = int(r["source_id"])

# K_RV from Trifonov by Gaia source
def make_kRV_from_trifonov() -> dict:
    """Returns dict source_id -> K_RV in m/s (peak-to-peak/2)."""
    out = {}
    for name, info in trif_sb_dict.items():
        if name in trif_name_to_gaia and np.isfinite(info["p2p"]):
            sid = trif_name_to_gaia[name]
            out[sid] = info["p2p"] / 2.0
    return out


kRV_from_trif = make_kRV_from_trifonov()
print(f"  Trifonov-derived K_RV entries: {len(kRV_from_trif)}")

# Also compute K_RV from HARPS rvbank (per-target peak-to-peak / 2) and match by coord (PM-corrected)
print("  Computing HARPS K_RV (per-target peak-to-peak/2)...")
harps_rvb = pl.read_parquet(ROOT / "data/external_catalogs/parquets/harps_rvbank.parquet")
harps_targets = pl.read_parquet(ROOT / "data/external_catalogs/parquets/harps_rvbank_targets.parquet")
# Group HARPS rvbank by name to get p2p
harps_stats = (
    harps_rvb.group_by("name").agg([
        ((pl.col("rv_kms").max() - pl.col("rv_kms").min()) * 1000.0).alias("p2p_mps"),
        pl.col("rv_kms").count().alias("n_rv"),
    ])
)
# Join HARPS p2p back into targets
harps_with_stats = harps_targets.join(harps_stats, on="name", how="inner")
print(f"  HARPS targets with rvbank p2p: {harps_with_stats.height}")

def make_kRV_from_harps_coord_dict(pool_df: pl.DataFrame) -> dict:
    """For pool with (ra, dec, pmra, pmdec, source_id), cross-match against HARPS targets within 5" PM-corrected. Return source_id -> K_RV (m/s)."""
    if pool_df.filter(pl.col("ra").is_not_null()).height == 0:
        return {}
    pool_valid = pool_df.filter(pl.col("ra").is_not_null())
    p_ra = pool_valid["ra"].to_numpy()
    p_dec = pool_valid["dec"].to_numpy()
    p_pmra = np.nan_to_num(pool_valid["pmra"].to_numpy(), nan=0.0)
    p_pmdec = np.nan_to_num(pool_valid["pmdec"].to_numpy(), nan=0.0)
    # HARPS baselines span 2003-2018; PM correct to mid 2010
    pc_ra, pc_dec = pm_correct(p_ra, p_dec, p_pmra, p_pmdec, PM_DELTA_YR)
    h_ra = harps_with_stats["ra_deg"].to_numpy()
    h_dec = harps_with_stats["dec_deg"].to_numpy()
    h_p2p = harps_with_stats["p2p_mps"].to_numpy()
    # Chunk
    out = {}
    CHUNK = 1000
    for ci in range(0, len(pc_ra), CHUNK):
        c_ra = pc_ra[ci:ci+CHUNK]
        c_dec = pc_dec[ci:ci+CHUNK]
        match_mat, sep_mat = cone_match_flat(c_ra, c_dec, h_ra, h_dec, 5.0)
        idx = np.argwhere(match_mat)
        for i_local, j in idx:
            sid = pool_valid["source_id"][ci + int(i_local)]
            if h_p2p[j] is not None and np.isfinite(h_p2p[j]):
                # Take min sep match
                K_rv = float(h_p2p[j]) / 2.0
                if sid not in out:
                    out[sid] = K_rv
                else:
                    out[sid] = max(out[sid], K_rv)  # take largest p2p
    return out


# Apply HARPS K_RV cross-match to all three pools
kRV_harps_orb = make_kRV_from_harps_coord_dict(nss_orb_truly)
kRV_harps_accS = make_kRV_from_harps_coord_dict(nss_accel_tierS)
kRV_harps_accB = make_kRV_from_harps_coord_dict(nss_accel_broader)
print(f"  HARPS-derived K_RV: orbital={len(kRV_harps_orb)} accelS={len(kRV_harps_accS)} accelB={len(kRV_harps_accB)}")
# Combine into a single fn that prefers Trifonov, then HARPS
def get_kRV(sid, pool_dict):
    if sid in kRV_from_trif:
        return kRV_from_trif[sid]
    return pool_dict.get(sid)

# K_pred from m2/m1/P/e (compute on the fly)
def K_pred_mps(M2_MJ, M1_Msun, P_d, e):
    """Predicted RV semi-amplitude at sin(i)=1."""
    if (M2_MJ is None or M1_Msun is None or P_d is None or
        not np.isfinite(M2_MJ) or not np.isfinite(M1_Msun) or
        M1_Msun <= 0 or P_d <= 0):
        return None
    M_total = M1_Msun + M2_MJ / 1047.5  # M_J -> M_sun
    P_yr = P_d / 365.25
    if e is None or not np.isfinite(e):
        e = 0.0
    K = 28.4329 * M2_MJ * (M_total ** (-2.0/3.0)) * (P_yr ** (-1.0/3.0)) / math.sqrt(max(1.0 - e*e, 1e-6))
    return K  # m/s


def apply_l17_orbital(pool_df: pl.DataFrame) -> pl.DataFrame:
    """For NSS Orbital truly-novel: gate on snrPMaH2G2>5 OR (RV available + sig from inventory).
    Compute K_RV from Trifonov / HARPS / inventory if available; K_pred from M2_marg, M1=1.0 (or rv_inv M1_Msun), P (period), e (eccentricity)."""
    # join with rv_inv to get HARPS/HIRES N + Sahl/HGCA snrPMa
    rv_inv_slim = rv_inv.select(["source_id", "M1_Msun", "harps_N", "hires_N", "apogee_N", "lamost_N", "galah_N", "hgca_snrPMa", "K_pred_mps"]).unique(subset=["source_id"])
    joined = pool_df.join(rv_inv_slim, on="source_id", how="left", suffix="_rvi")
    K_RV_list = []
    K_RV_src_list = []
    K_pred_list = []
    L17_flag = []
    L17_reason = []
    for r in joined.iter_rows(named=True):
        sid = r["source_id"]
        m1 = r["M1_Msun"] if r["M1_Msun"] is not None else 1.0
        M2_MJ = r["M2_marg"]
        P_d = r["period"]
        ecc = r["eccentricity"] if r["eccentricity"] is not None else 0.0
        Kp = K_pred_mps(M2_MJ, m1, P_d, ecc)
        if Kp is None:
            Kp = r.get("K_pred_mps")
        K_pred_list.append(Kp)
        # K_RV: Trifonov first, then HARPS
        K_rv = kRV_from_trif.get(sid)
        src = "trifonov" if K_rv is not None else None
        if K_rv is None:
            K_rv = kRV_harps_orb.get(sid)
            if K_rv is not None:
                src = "harps_rvbank"
        K_RV_list.append(K_rv)
        K_RV_src_list.append(src)
        # Gate L17 only when archival RV exists AND (snrPMaH2G2>5)
        snr_HG2 = r.get("snrPMaH2G2") or r.get("hgca_snrPMa") or 0.0
        snr_HG2 = snr_HG2 if snr_HG2 is not None else 0.0
        rv_archived = (r.get("harps_N", 0) or 0) > 0 or (r.get("hires_N", 0) or 0) > 0 or (r.get("apogee_N", 0) or 0) > 0 or (K_rv is not None)
        flag = False
        reason = None
        if rv_archived and snr_HG2 > 5 and K_rv is not None and Kp is not None and Kp > 0:
            if (K_rv / Kp) > 2.0:
                flag = True
                reason = f"STELLAR_K_RV_INCONSISTENT (K_RV={K_rv:.0f} K_pred={Kp:.0f} ratio={K_rv/Kp:.2f}, src={src})"
        L17_flag.append(flag)
        L17_reason.append(reason)
    return joined.with_columns([
        pl.Series("K_RV_archival_mps", K_RV_list, dtype=pl.Float64),
        pl.Series("K_RV_source", K_RV_src_list, dtype=pl.Utf8),
        pl.Series("K_pred_used_mps", K_pred_list, dtype=pl.Float64),
        pl.Series("L17_flag", L17_flag),
        pl.Series("L17_reason", L17_reason, dtype=pl.Utf8),
    ])


def apply_l17_accel(pool_df: pl.DataFrame, harps_dict: dict) -> pl.DataFrame:
    """For NSS Accel: K_pred from m2_mjup_P10yr + assume P=10yr + M1=1.0 (or default).
    Gate: significance > 20 OR snrPMa_best > 5."""
    K_RV_list = []
    K_RV_src_list = []
    K_pred_list = []
    L17_flag = []
    L17_reason = []
    for r in pool_df.iter_rows(named=True):
        sid = r["source_id"]
        M2_MJ = r["m2_mjup_P10yr"]
        m1 = 1.0
        P_d = 10.0 * 365.25
        Kp = K_pred_mps(M2_MJ, m1, P_d, 0.3)
        K_pred_list.append(Kp)
        K_rv = kRV_from_trif.get(sid)
        src = "trifonov" if K_rv is not None else None
        if K_rv is None:
            K_rv = harps_dict.get(sid)
            if K_rv is not None:
                src = "harps_rvbank"
        K_RV_list.append(K_rv)
        K_RV_src_list.append(src)
        sig = r.get("significance", 0.0) or 0.0
        snr_best = r.get("snrPMa_best", 0.0) or 0.0
        if K_rv is not None and Kp is not None and Kp > 0 and (sig > 20 or snr_best > 5):
            if (K_rv / Kp) > 2.0:
                L17_flag.append(True)
                L17_reason.append(f"STELLAR_K_RV_INCONSISTENT (K_RV={K_rv:.0f} K_pred={Kp:.0f} ratio={K_rv/Kp:.2f}, src={src})")
                continue
        L17_flag.append(False)
        L17_reason.append(None)
    return pool_df.with_columns([
        pl.Series("K_RV_archival_mps", K_RV_list, dtype=pl.Float64),
        pl.Series("K_RV_source", K_RV_src_list, dtype=pl.Utf8),
        pl.Series("K_pred_used_mps", K_pred_list, dtype=pl.Float64),
        pl.Series("L17_flag", L17_flag),
        pl.Series("L17_reason", L17_reason, dtype=pl.Utf8),
    ])


# ----------- Apply ----------------------------------------------------------

print("\n[6] Apply L18 + L19 to NSS Orbital truly_novel ...")
orb1 = apply_l18(nss_orb_truly)
orb2 = apply_l19(orb1)
orb3 = apply_l17_orbital(orb2)
print(f"  After L17|L18|L19 filters: catches L17={orb3.filter(pl.col('L17_flag')).height} L18={orb3.filter(pl.col('L18_flag')).height} L19={orb3.filter(pl.col('L19_flag')).height}")

print("\n[7] Apply L18 + L19 + L17 to NSS Accel Tier S ...")
accS_1 = apply_l18(nss_accel_tierS)
accS_2 = apply_l19(accS_1)
accS_3 = apply_l17_accel(accS_2, kRV_harps_accS)
print(f"  catches L17={accS_3.filter(pl.col('L17_flag')).height} L18={accS_3.filter(pl.col('L18_flag')).height} L19={accS_3.filter(pl.col('L19_flag')).height}")

print("\n[8] Apply L18 + L19 + L17 to NSS Accel broader 14407 ...")
accB_1 = apply_l18(nss_accel_broader)
accB_2 = apply_l19(accB_1)
accB_3 = apply_l17_accel(accB_2, kRV_harps_accB)
print(f"  catches L17={accB_3.filter(pl.col('L17_flag')).height} L18={accB_3.filter(pl.col('L18_flag')).height} L19={accB_3.filter(pl.col('L19_flag')).height}")


# ----------- Save outputs ---------------------------------------------------

print("\n[9] Saving outputs ...")
# Combined imposter list with reasons
def collect_caught(df, pool_label):
    rows = df.filter(pl.col("L17_flag") | pl.col("L18_flag") | pl.col("L19_flag"))
    if rows.height == 0:
        return None
    cols = ["source_id", "L17_flag", "L17_reason", "L18_flag", "L18_reason", "L19_flag", "L19_reason", "L19_WDS", "L19_sep_arcsec", "L19_mag2"]
    if "Name" in rows.columns: cols.append("Name")
    if "HIP" in rows.columns: cols.append("HIP")
    if "Vmag" in rows.columns: cols.append("Vmag")
    if "SpType" in rows.columns: cols.append("SpType")
    cols = [c for c in cols if c in rows.columns]
    out = rows.select(cols).with_columns(pl.lit(pool_label).alias("pool"))
    return out


caught_orb = collect_caught(orb3, "NSS_ORBITAL")
caught_accS = collect_caught(accS_3, "NSS_ACCEL_TIERS")
caught_accB = collect_caught(accB_3, "NSS_ACCEL_BROADER")
parts = [c for c in (caught_orb, caught_accS, caught_accB) if c is not None]
if parts:
    # Align columns
    cols_union = []
    for p in parts:
        for c in p.columns:
            if c not in cols_union:
                cols_union.append(c)
    aligned = []
    for p in parts:
        for c in cols_union:
            if c not in p.columns:
                p = p.with_columns(pl.lit(None).alias(c))
        aligned.append(p.select(cols_union))
    caught_all = pl.concat(aligned)
    caught_all.write_csv(OUT_DIR / "imposters_caught.csv")
    print(f"  Saved imposters_caught.csv ({caught_all.height} rows)")
else:
    pl.DataFrame({"source_id": []}).write_csv(OUT_DIR / "imposters_caught.csv")
    print("  No imposters caught.")

# Clean pools after filtering
def write_clean(df, path):
    cleaned = df.filter(~(pl.col("L17_flag") | pl.col("L18_flag") | pl.col("L19_flag")))
    cleaned.write_csv(path)
    return cleaned


cleaned_orb = write_clean(orb3, OUT_DIR / "cleaned_nss_orbital_post_l17_l19.csv")
cleaned_accS = write_clean(accS_3, OUT_DIR / "cleaned_nss_accel_post_l17_l19.csv")
cleaned_accB = write_clean(accB_3, OUT_DIR / "cleaned_nss_accel_broader_post_l17_l19.csv")
print(f"  Saved cleaned NSS Orbital: {cleaned_orb.height}")
print(f"  Saved cleaned NSS Accel Tier S: {cleaned_accS.height}")
print(f"  Saved cleaned NSS Accel broader: {cleaned_accB.height}")

# Verdict for the 4 watched candidates
watch = {"HD 88201", "HD 28264", "HD 101767", "HD 66434"}
verdicts = []
for name in watch:
    found = False
    for df, pool in ((orb3, "NSS_ORBITAL"), (accS_3, "NSS_ACCEL_TIERS"), (accB_3, "NSS_ACCEL_BROADER")):
        if "Name" in df.columns:
            hit = df.filter(pl.col("Name") == name)
            if hit.height > 0:
                row = hit.row(0, named=True)
                verdicts.append({
                    "name": name, "pool": pool,
                    "L17_flag": bool(row.get("L17_flag", False)),
                    "L17_reason": row.get("L17_reason"),
                    "L18_flag": bool(row.get("L18_flag", False)),
                    "L18_reason": row.get("L18_reason"),
                    "L19_flag": bool(row.get("L19_flag", False)),
                    "L19_reason": row.get("L19_reason"),
                    "L19_WDS": row.get("L19_WDS"),
                    "L19_sep": row.get("L19_sep_arcsec"),
                    "L19_mag2": row.get("L19_mag2"),
                })
                found = True
                break
    if not found:
        verdicts.append({"name": name, "pool": "NOT_FOUND"})

with open(OUT_DIR / "watchlist_verdicts.json", "w") as f:
    json.dump(verdicts, f, indent=2, default=str)
print("\n[10] Watchlist verdicts saved.")
for v in verdicts:
    print(v)


# Top 10 after filters for each pool
def top_orbital(df: pl.DataFrame):
    cleaned = df.filter(~(pl.col("L17_flag") | pl.col("L18_flag") | pl.col("L19_flag")))
    return cleaned.sort("combined_score", descending=True).head(10)


def top_accel(df: pl.DataFrame):
    cleaned = df.filter(~(pl.col("L17_flag") | pl.col("L18_flag") | pl.col("L19_flag")))
    if "composite_sub_score" in cleaned.columns:
        return cleaned.sort("composite_sub_score", descending=True).head(10)
    elif "roi_score" in cleaned.columns:
        return cleaned.sort("roi_score", descending=True).head(10)
    return cleaned.head(10)


top_orb_n = top_orbital(orb3)
top_acc_n = top_accel(accS_3)
top_accB_n = top_accel(accB_3)

top_orb_n.write_csv(OUT_DIR / "top10_nss_orbital_post_l17_l19.csv")
top_acc_n.write_csv(OUT_DIR / "top10_nss_accel_tierS_post_l17_l19.csv")
top_accB_n.write_csv(OUT_DIR / "top10_nss_accel_broader_post_l17_l19.csv")
print(f"  Top NSS Orbital saved ({top_orb_n.height} rows)")
print(f"  Top NSS Accel Tier S saved ({top_acc_n.height} rows)")
print(f"  Top NSS Accel broader saved ({top_accB_n.height} rows)")


# Final summary saved as JSON
summary = {
    "pools": {
        "nss_orbital": {
            "input": nss_orb_truly.height,
            "L17_caught": int(orb3.filter(pl.col('L17_flag')).height),
            "L18_caught": int(orb3.filter(pl.col('L18_flag')).height),
            "L19_caught": int(orb3.filter(pl.col('L19_flag')).height),
            "any_caught": int(orb3.filter(pl.col('L17_flag') | pl.col('L18_flag') | pl.col('L19_flag')).height),
            "surviving": int(cleaned_orb.height),
        },
        "nss_accel_tierS": {
            "input": nss_accel_tierS.height,
            "L17_caught": int(accS_3.filter(pl.col('L17_flag')).height),
            "L18_caught": int(accS_3.filter(pl.col('L18_flag')).height),
            "L19_caught": int(accS_3.filter(pl.col('L19_flag')).height),
            "any_caught": int(accS_3.filter(pl.col('L17_flag') | pl.col('L18_flag') | pl.col('L19_flag')).height),
            "surviving": int(cleaned_accS.height),
        },
        "nss_accel_broader": {
            "input": nss_accel_broader.height,
            "L17_caught": int(accB_3.filter(pl.col('L17_flag')).height),
            "L18_caught": int(accB_3.filter(pl.col('L18_flag')).height),
            "L19_caught": int(accB_3.filter(pl.col('L19_flag')).height),
            "any_caught": int(accB_3.filter(pl.col('L17_flag') | pl.col('L18_flag') | pl.col('L19_flag')).height),
            "surviving": int(cleaned_accB.height),
        },
    },
    "watch": verdicts,
}
with open(OUT_DIR / "summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("\n[DONE]")
print(json.dumps(summary, indent=2, default=str))

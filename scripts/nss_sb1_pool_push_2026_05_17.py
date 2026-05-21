"""NSS SB1 pure-spectroscopic pool push (2026-05-17).

Goal: scan the *entire* Gaia DR3 NSS SB1 pool (nss_solution_type='SB1') for
substellar-mass companions using the Pourbaix mass function, then run the
v9b cascade on every survivor. Compare results to the existing 11 headline
candidates.

Why now: the cascade so far has been driven by Orbital and (via Fix E)
Acceleration solution types. SB1 entries (single-line spectroscopic binaries
solved purely from RV) are an orthogonal pool — Gaia detected the companion
via the host's RV reflex, not via astrometric wobble. For substellar
companions around bright F/G stars this is often the *only* solution type
that gets fit, because the astrometric wobble is below ~~0.1 mas.

Mass function (Pourbaix 2018):
  f(M) = K_1^3 P (1 - e^2)^(3/2) / (2 pi G)
       = M_2^3 sin^3(i) / (M_1 + M_2)^2

For a known primary mass M_1 (we will look it up from Gaia main-table
photometry + isochrones, or fall back to a 1.0 M_sun prior), we solve for
M_2 given an isotropic-cos(i) prior, just as in the rest of the pipeline.

Pipeline:
  1. SELECT * FROM gaiadr3.nss_two_body_orbit WHERE nss_solution_type='SB1'
     AND eccentricity IS NOT NULL AND semi_amplitude_primary IS NOT NULL
     AND significance > 5 AND period BETWEEN 30 AND 5000.
  2. For each, look up M_1 from gaiadr3.astrophysical_parameters (mass_flame)
     or fall back to 1.0 M_sun.
  3. Compute K_1 in m/s from semi_amplitude_primary (km/s -> m/s).
  4. Compute mass function f(M), then solve M_2 sin i with isotropic prior:
     M_2_marg = median over cos(i)~U(-1,1) of the cubic-equation root.
  5. Keep sources with M_2_marg < 80 M_J.
  6. For each survivor: HGCA chi^2 (Brandt 2024), Kervella SNR, exoplanet.eu
     coord cross-match (PM-corrected), Sahlmann 2025 verdict, ESO archive
     presence, 24-catalog negatives.
  7. Compare against the existing 11 — flag any genuinely new substellar
     candidate.

Run:
    /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
        scripts/nss_sb1_pool_push_2026_05_17.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import polars as pl
from astroquery.gaia import Gaia

ROOT = Path("/tmp/gaia-novelty-publication")
OUT = ROOT / "data" / "intermediate"
OUT.mkdir(parents=True, exist_ok=True)

G_SI = 6.67430e-11           # m^3 kg^-1 s^-2
M_SUN_KG = 1.98892e30
M_JUP_KG = 1.89813e27
M_JUP_PER_SUN = M_SUN_KG / M_JUP_KG  # ~~1047
DAY_S = 86400.0


def query_sb1_pool() -> pl.DataFrame:
    """Pull the entire NSS SB1 pool (with significance and reasonable P)."""
    q = """
    SELECT
        nss.source_id,
        nss.nss_solution_type,
        nss.period,
        nss.eccentricity,
        nss.semi_amplitude_primary,
        nss.semi_amplitude_primary_error,
        nss.significance,
        nss.t_periastron,
        nss.arg_periastron,
        nss.inclination,
        nss.bit_index,
        nss.flags,
        g.ra,
        g.dec,
        g.phot_g_mean_mag,
        g.bp_rp,
        g.parallax,
        g.parallax_error,
        g.ruwe,
        g.ipd_frac_multi_peak,
        g.non_single_star
    FROM gaiadr3.nss_two_body_orbit AS nss
    JOIN gaiadr3.gaia_source AS g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type = 'SB1'
      AND nss.eccentricity IS NOT NULL
      AND nss.semi_amplitude_primary IS NOT NULL
      AND nss.significance >= 5.0
      AND nss.period BETWEEN 30.0 AND 5000.0
      AND g.phot_g_mean_mag < 12.0
      AND g.parallax > 5.0
    """
    print("Submitting SB1 ADQL query (this can take 1-2 min)…")
    job = Gaia.launch_job_async(q)
    res = job.get_results().to_pandas()
    print(f"Retrieved {len(res)} SB1 rows")
    return pl.from_pandas(res)


def mass_function_mjup(K_1_mps: float, P_days: float, e: float) -> float:
    """f(M) in M_jup units."""
    K = float(K_1_mps)
    P = float(P_days) * DAY_S
    e = float(e)
    fM_kg = K**3 * P * (1 - e**2) ** 1.5 / (2 * math.pi * G_SI)
    return fM_kg / M_JUP_KG


def m2_from_mass_func(fM_mjup: float, M_1_msun: float, sin_i: float) -> float:
    """Solve cubic M_2^3 sin^3 i = f(M) (M_1+M_2)^2 for M_2 (in M_jup)."""
    if sin_i <= 0:
        return float("inf")
    M_1_mjup = M_1_msun * M_JUP_PER_SUN
    rhs_coef = fM_mjup / (sin_i ** 3)

    # Solve M_2^3 - rhs_coef*(M_1+M_2)^2 = 0 numerically.
    # M_2 ranges from 0.01 M_jup to 1000 M_sun.
    lo, hi = 1e-3, 1e6
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lhs = mid ** 3
        rhs = rhs_coef * (M_1_mjup + mid) ** 2
        if lhs > rhs:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def marginalize_m2(fM_mjup: float, M_1_msun: float, n_samp: int = 4000) -> tuple[float, float, float]:
    """Marginalize M_2 over isotropic cos(i) ~ U(-1,1) prior."""
    rng = np.random.default_rng(42)
    cosi = rng.uniform(-1.0, 1.0, size=n_samp)
    sini = np.sqrt(np.maximum(0.0, 1.0 - cosi**2))
    m2s = np.array([m2_from_mass_func(fM_mjup, M_1_msun, float(si))
                    for si in sini])
    m2s = m2s[np.isfinite(m2s)]
    if m2s.size == 0:
        return float("nan"), float("nan"), float("nan")
    return (
        float(np.percentile(m2s, 16)),
        float(np.percentile(m2s, 50)),
        float(np.percentile(m2s, 84)),
    )


def lookup_primary_mass(source_ids: list[int]) -> pl.DataFrame:
    """Look up M_1 from astrophysical_parameters (FLAME)."""
    if not source_ids:
        return pl.DataFrame({"source_id": [], "mass_flame": []})
    chunks = []
    for i in range(0, len(source_ids), 5000):
        sub = source_ids[i:i+5000]
        ids = ",".join(str(int(x)) for x in sub)
        q = (f"SELECT source_id, mass_flame FROM gaiadr3.astrophysical_parameters "
             f"WHERE source_id IN ({ids})")
        job = Gaia.launch_job_async(q)
        chunks.append(job.get_results().to_pandas())
    import pandas as pd
    return pl.from_pandas(pd.concat(chunks, ignore_index=True))


def compute_m2_for_pool(pool: pl.DataFrame) -> pl.DataFrame:
    """Add f(M), M_2 face-on, M_2 marg, M_2_1sig_lo/hi columns."""
    ids = pool["source_id"].cast(pl.Int64).to_list()
    print(f"Looking up M_1 (mass_flame) for {len(ids)} sources…")
    flame = lookup_primary_mass(ids)
    pool = pool.join(flame, on="source_id", how="left")

    fM = []
    m2_face = []
    m2_marg_lo = []
    m2_marg_med = []
    m2_marg_hi = []
    for r in pool.iter_rows(named=True):
        K_kms = r["semi_amplitude_primary"]
        P_d = r["period"]
        e = r["eccentricity"]
        if K_kms is None or P_d is None or e is None:
            fM.append(None); m2_face.append(None)
            m2_marg_lo.append(None); m2_marg_med.append(None); m2_marg_hi.append(None)
            continue
        K_mps = float(K_kms) * 1000.0
        fM_v = mass_function_mjup(K_mps, P_d, e)
        M1 = r.get("mass_flame")
        M1 = float(M1) if M1 is not None and M1 > 0.1 else 1.0
        face = m2_from_mass_func(fM_v, M1, sin_i=1.0)
        lo, med, hi = marginalize_m2(fM_v, M1)
        fM.append(fM_v); m2_face.append(face)
        m2_marg_lo.append(lo); m2_marg_med.append(med); m2_marg_hi.append(hi)

    return pool.with_columns([
        pl.Series("f_M_mjup", fM),
        pl.Series("m2_face_mjup", m2_face),
        pl.Series("m2_marg_1sig_lo_mjup", m2_marg_lo),
        pl.Series("m2_marg_med_mjup", m2_marg_med),
        pl.Series("m2_marg_1sig_hi_mjup", m2_marg_hi),
    ])


def main():
    pool = query_sb1_pool()
    pool.write_csv(OUT / "nss_sb1_pool_raw_2026_05_17.csv")
    print(f"Pool size (V<12, plx>5 mas, sig>5, P 30-5000d): {len(pool)}")

    enriched = compute_m2_for_pool(pool)
    enriched.write_csv(OUT / "nss_sb1_pool_with_m2_2026_05_17.csv")

    substellar = enriched.filter(pl.col("m2_marg_med_mjup") < 80.0)
    print(f"Marginalized substellar (M_2_marg < 80 M_J): {len(substellar)}")

    # Conditional RUWE: SB1 is in ORBIT_REFLEX set, so lax<7
    cond_ruwe_pass = substellar.filter(
        (pl.col("ruwe").is_null()) | (pl.col("ruwe") < 7.0)
    )
    print(f"After conditional RUWE<7 (SB1 in orbit-reflex set): {len(cond_ruwe_pass)}")

    cond_ruwe_pass = cond_ruwe_pass.with_columns([
        (1000.0 / pl.col("parallax")).alias("dist_pc_naive"),
    ])

    out_top = cond_ruwe_pass.sort("m2_marg_med_mjup").head(200)
    out_top.write_csv(OUT / "nss_sb1_substellar_top200_2026_05_17.csv")

    # Compare to existing 11 — any source_id overlap?
    existing = pl.read_csv(ROOT / "novelty_candidates.csv")
    overlap = cond_ruwe_pass.join(
        existing.select("gaia_dr3_source_id"),
        left_on="source_id", right_on="gaia_dr3_source_id", how="inner"
    )
    print(f"Overlap with existing 11 candidates: {len(overlap)}")

    print("\nTop 15 SB1 substellar candidates by M_2_marg ascending:")
    show_cols = [
        "source_id", "phot_g_mean_mag", "ruwe", "significance",
        "period", "eccentricity", "semi_amplitude_primary",
        "m2_face_mjup", "m2_marg_med_mjup",
        "m2_marg_1sig_lo_mjup", "m2_marg_1sig_hi_mjup",
        "dist_pc_naive",
    ]
    print(cond_ruwe_pass.sort("m2_marg_med_mjup").select(show_cols).head(15))


if __name__ == "__main__":
    sys.exit(main() or 0)

"""Two-Keplerian multi-survey RV joint fitter (planet-hunt edition).

Methodological angle: combine sparse RV data from multiple archives (HARPS RVBank,
HIRES Trifonov 2025, APOGEE DR17, GALAH DR4, NASA Exo) at per-instrument γ
offsets to detect INNER planet companions hiding in NSS-detected systems, or
hot Jupiters that single-survey pipelines miss.

Pipeline:
  1. Load and concatenate RVs from all archives for a single target
  2. Apply per-instrument γ offsets (nuisance parameters)
  3. Fit 1-Keplerian, 2-Keplerian (inner+outer) models via dynesty nested sampling
  4. Compute Bayes factor log10 BF(2-Kep vs 1-Kep)
  5. Output posterior tables, MAP params, archive coverage summary

Reference: extends rv_bayesian_fitter.py (single-planet) to nested 2-Kep model.
"""
import os
from __future__ import annotations

import json
import math
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import polars as pl

warnings.filterwarnings("ignore")

# Project root
ROOT = Path(os.environ.get("GAIA_NOVELTY_DATA_ROOT", str(Path(__file__).resolve().parent.parent)))
sys.path.insert(0, str(ROOT / "scripts"))

import dynesty  # noqa: E402
from dynesty import utils as dyutils  # noqa: E402
from scipy.special import betaincinv  # noqa: E402

# Physical constants
DAY_S = 86400.0
YR_D = 365.25
G_CGS = 6.67430e-8
M_SUN_G = 1.98892e33
M_JUP_G = 1.89813e30


# =============================================================================
# Kepler solver and orbit model
# =============================================================================
def solve_kepler(M, e, max_iter=50, tol=1e-9):
    M = np.atleast_1d(M).astype(np.float64)
    M_wrap = np.mod(M, 2 * np.pi)
    if e < 0.5:
        E = M_wrap.copy()
    else:
        E = M_wrap + e * np.sign(np.sin(M_wrap)) * 0.85
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M_wrap
        fp = 1.0 - e * np.cos(E)
        dE = -f / fp
        E = E + dE
        if np.max(np.abs(dE)) < tol:
            break
    n_cycles = np.floor(M / (2 * np.pi))
    return E + 2 * np.pi * n_cycles


def rv_kep_ecc(t_bjd, K, P_d, t_per, e, omega):
    M = 2 * np.pi * (t_bjd - t_per) / P_d
    E = solve_kepler(M, e)
    nu = 2 * np.arctan2(
        np.sqrt(1 + e) * np.sin(E / 2),
        np.sqrt(1 - e) * np.cos(E / 2),
    )
    return K * (np.cos(nu + omega) + e * np.cos(omega))


def m2_sini_jup(K_kms, P_d, e, m_host_sun):
    """Mass function → M_2 sin i in M_Jup."""
    K_cgs = np.asarray(K_kms) * 1e5
    P_s = np.asarray(P_d) * DAY_S
    f_M_g = K_cgs**3 * P_s * (1 - np.asarray(e) ** 2) ** 1.5 / (2 * np.pi * G_CGS)
    M1_g = m_host_sun * M_SUN_G
    M2_g = 0.05 * M1_g * np.ones_like(K_cgs)
    for _ in range(60):
        f_eval = M2_g**3 / (M1_g + M2_g) ** 2
        df = 3 * M2_g**2 / (M1_g + M2_g) ** 2 - 2 * M2_g**3 / (M1_g + M2_g) ** 3
        step = np.where(np.abs(df) > 1e-30, (f_eval - f_M_g) / df, 0)
        M2_g = M2_g - step
        if np.max(np.abs(step) / np.maximum(M2_g, 1e6)) < 1e-7:
            break
    return M2_g / M_JUP_G


# =============================================================================
# Multi-archive RV ingestion
# =============================================================================
def cone_match(df, ra_col, dec_col, ra0, dec0, radius_arcsec=5.0):
    """Cone match around (ra0, dec0). Returns filtered df."""
    cone_deg = radius_arcsec / 3600.0
    dec_buf = cone_deg
    ra_buf = cone_deg / max(np.cos(np.radians(dec0)), 0.05)
    return df.filter(
        (pl.col(ra_col) > ra0 - ra_buf)
        & (pl.col(ra_col) < ra0 + ra_buf)
        & (pl.col(dec_col) > dec0 - dec_buf)
        & (pl.col(dec_col) < dec0 + dec_buf)
    )


def load_target_rvs(target_meta):
    """Load all RVs for a target from the 5 archives.

    target_meta: dict with keys
      'name', 'ra', 'dec', 'gaia_id' (optional),
      'harps_name' (e.g. 'HD142A'), 'nasa_exo_name' (e.g. 'HD 142'),
      'hires_name' (e.g. 'HD33636').

    Returns: polars DataFrame with columns [t_bjd, rv_kms, sigma_kms, instrument]
    """
    parts = []

    # --- HARPS RVBank (Trifonov 2020) ---
    harps_p = ROOT / "data/external_catalogs/parquets/harps_rvbank.parquet"
    df_h = pl.read_parquet(harps_p)
    harps_name = target_meta.get("harps_name")
    if harps_name:
        sub = df_h.filter(pl.col("name") == harps_name)
        if len(sub) > 0:
            # HARPS RVBank stores absolute RV in km/s with sigma in km/s
            parts.append(
                sub.select(
                    [
                        pl.col("bjd").alias("t_bjd"),
                        pl.col("rv_kms").alias("rv_kms"),
                        pl.col("sigma_kms").alias("sigma_kms"),
                        pl.lit("HARPS").alias("instrument"),
                    ]
                )
            )
            print(
                f"  HARPS RVBank ({harps_name}): N={len(sub)}, "
                f"baseline={(sub['bjd'].max()-sub['bjd'].min()):.0f}d, "
                f"σ_med={sub['sigma_kms'].median()*1000:.2f} m/s"
            )

    # --- HIRES Trifonov 2025 (column-named *_kms but actually m/s units!) ---
    hires_p = ROOT / "data/external_catalogs/parquets/trifonov2025_hires_rv.parquet"
    df_hi = pl.read_parquet(hires_p)
    hires_name = target_meta.get("hires_name")
    if hires_name:
        sub = df_hi.filter(pl.col("name") == hires_name)
        if len(sub) > 0:
            # rv_cor_kms is actually m/s; convert to true km/s by /1000
            parts.append(
                sub.select(
                    [
                        pl.col("bjd").alias("t_bjd"),
                        (pl.col("rv_cor_kms") / 1000.0).alias("rv_kms"),
                        (pl.col("e_rv_cor_kms") / 1000.0).alias("sigma_kms"),
                        pl.lit("HIRES").alias("instrument"),
                    ]
                )
            )
            print(
                f"  HIRES Trifonov2025 ({hires_name}): N={len(sub)}, "
                f"baseline={(sub['bjd'].max()-sub['bjd'].min()):.0f}d, "
                f"σ_med={sub['e_rv_cor_kms'].median():.1f} m/s"
            )

    # --- APOGEE DR17 (cone match) ---
    apogee_p = ROOT / "data/external_catalogs/parquets/apogee_dr17_allVisit.parquet"
    df_a = pl.read_parquet(apogee_p)
    sub = cone_match(df_a, "RA", "DEC", target_meta["ra"], target_meta["dec"], radius_arcsec=5.0)
    sub = sub.filter(pl.col("VHELIO").is_not_nan() & pl.col("VRELERR").is_not_nan())
    sub = sub.filter(pl.col("VRELERR") > 0)
    if len(sub) > 0:
        # VHELIO is in km/s, VRELERR in km/s
        parts.append(
            sub.select(
                [
                    (pl.col("MJD") + 2400000.5).alias("t_bjd"),  # MJD → JD (approx BJD)
                    pl.col("VHELIO").alias("rv_kms"),
                    pl.col("VRELERR").alias("sigma_kms"),
                    pl.lit("APOGEE").alias("instrument"),
                ]
            )
        )
        print(
            f"  APOGEE DR17 (cone): N={len(sub)}, "
            f"baseline={(sub['MJD'].max()-sub['MJD'].min()):.0f}d, "
            f"σ_med={sub['VRELERR'].median()*1000:.0f} m/s"
        )

    # --- GALAH DR4 (cone match) ---
    galah_p = ROOT / "data/external_catalogs/parquets/galah_dr4_rv.parquet"
    df_g = pl.read_parquet(galah_p)
    sub = cone_match(df_g, "ra", "dec", target_meta["ra"], target_meta["dec"], radius_arcsec=5.0)
    if len(sub) > 0:
        sub = sub.filter(pl.col("rv_comp_1").is_not_null() & pl.col("e_rv_comp_1").is_not_null())
        if len(sub) > 0:
            parts.append(
                sub.select(
                    [
                        (pl.col("mjd") + 2400000.5).alias("t_bjd"),
                        pl.col("rv_comp_1").alias("rv_kms"),
                        pl.col("e_rv_comp_1").alias("sigma_kms"),
                        pl.lit("GALAH").alias("instrument"),
                    ]
                )
            )
            print(
                f"  GALAH DR4 (cone): N={len(sub)}, "
                f"baseline={(sub['mjd'].max()-sub['mjd'].min()):.0f}d, "
                f"σ_med={sub['e_rv_comp_1'].median()*1000:.0f} m/s"
            )

    # --- NASA Exo Archive RVs (multi-instrument) ---
    nasa_p = ROOT / "data/external_catalogs/parquets/nasa_exo_rv.parquet"
    df_n = pl.read_parquet(nasa_p)
    nasa_name = target_meta.get("nasa_exo_name")
    if nasa_name:
        sub = df_n.filter(pl.col("star_id") == nasa_name)
        if len(sub) > 0:
            # Note: NASA Exo rv_kms is in km/s but for some instruments (HRS, HIRES)
            # the units_orig is 'm/s' and values are in m/s already — already-scaled
            # to km/s correctly in the rv_kms col (small values e.g. 0.0856 km/s)
            # Use t_bjd column if available, else t_orig
            t_col = "t_bjd" if "t_bjd" in sub.columns else "t_orig"
            # Group by instrument so each NASA-Exo instrument is treated as separate
            for inst in sub["instrument"].unique().to_list():
                inst_sub = sub.filter(pl.col("instrument") == inst)
                # Clean instrument name (remove spaces, special chars)
                inst_clean = inst.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                inst_label = f"NASA_{inst_clean[:20]}"
                parts.append(
                    inst_sub.select(
                        [
                            pl.col(t_col).alias("t_bjd"),
                            pl.col("rv_kms").alias("rv_kms"),
                            pl.col("sigma_kms").alias("sigma_kms"),
                            pl.lit(inst_label).alias("instrument"),
                        ]
                    )
                )
                print(
                    f"  NASA Exo ({inst}): N={len(inst_sub)}, "
                    f"σ_med={inst_sub['sigma_kms'].median()*1000:.1f} m/s"
                )

    if not parts:
        raise RuntimeError(f"No RV data found for {target_meta['name']}")

    df = pl.concat(parts, how="vertical")
    # Filter out invalid rows
    df = df.filter(
        pl.col("t_bjd").is_not_null()
        & pl.col("rv_kms").is_not_null()
        & pl.col("sigma_kms").is_not_null()
        & (pl.col("sigma_kms") > 0)
    )
    df = df.sort("t_bjd")
    return df


# =============================================================================
# 2-Keplerian model + likelihood + prior transform
# =============================================================================
class TwoKeplerianModel:
    """Joint 1- and 2-Keplerian Bayesian fitter for sparse multi-archive RVs.

    Parameter vector (1-Kep): [γ_0, γ_1, ..., γ_{n_inst-1}, log_σ_jit, log10P, K, t_per_phi, e, ω]
    Parameter vector (2-Kep): same prefix + [log10P_in, K_in, t_per_phi_in, e_in, ω_in]
    """

    def __init__(self, df: pl.DataFrame, m_host_sun: float,
                 outer_P_nss: float | None = None, outer_P_err: float | None = None,
                 inner_P_range: tuple[float, float] = (1.0, 500.0)):
        self.t = df["t_bjd"].to_numpy().astype(np.float64)
        self.rv = df["rv_kms"].to_numpy().astype(np.float64)
        self.sigma = df["sigma_kms"].to_numpy().astype(np.float64)
        self.inst = df["instrument"].to_numpy()
        self.m_host_sun = m_host_sun
        self.outer_P_nss = outer_P_nss
        self.outer_P_err = outer_P_err
        self.inner_P_range = inner_P_range

        # Instrument indicators
        self.instruments = sorted(set(self.inst.tolist()))
        self.n_inst = len(self.instruments)
        self.indicators = {s: (self.inst == s).astype(np.float64) for s in self.instruments}

        # Per-instrument median RV (for γ prior centering)
        self.gamma_med = {
            s: float(np.median(self.rv[self.indicators[s].astype(bool)]))
            for s in self.instruments
        }
        # Per-instrument prior width (smaller of: 5 km/s, 10× per-inst RV span)
        self.gamma_lo = {
            s: self.gamma_med[s] - 5.0 for s in self.instruments
        }
        self.gamma_hi = {
            s: self.gamma_med[s] + 5.0 for s in self.instruments
        }

        self.t_anchor = float(np.median(self.t))
        self.baseline = float(self.t.max() - self.t.min())
        self.n = len(self.t)

    # ---- model evaluators ----
    def _gamma_correction(self, theta_gamma):
        """Build per-data γ array from per-instrument γ vector."""
        mu = np.zeros(self.n)
        for i, s in enumerate(self.instruments):
            mu += theta_gamma[i] * self.indicators[s]
        return mu

    def model_zero(self, theta):
        """0-Kep: just γ per inst (no signal)."""
        return self._gamma_correction(theta[: self.n_inst])

    def model_1kep(self, theta):
        """1-Kep: γ_inst + 1 Keplerian orbit."""
        n_inst = self.n_inst
        mu = self._gamma_correction(theta[:n_inst])
        # log_σ_jit at index n_inst (not in mu; only affects likelihood)
        log10P = theta[n_inst + 1]
        K = theta[n_inst + 2]
        phi = theta[n_inst + 3]
        e = theta[n_inst + 4]
        omega = theta[n_inst + 5]
        P_d = 10**log10P
        t_per = self.t_anchor + phi * P_d / (2 * np.pi)
        mu += rv_kep_ecc(self.t, K, P_d, t_per, e, omega)
        return mu

    def model_2kep(self, theta):
        """2-Kep: γ_inst + inner Keplerian + outer Keplerian."""
        n_inst = self.n_inst
        mu = self._gamma_correction(theta[:n_inst])
        # log_σ_jit at idx n_inst (likelihood only)
        # Outer
        log10P_o = theta[n_inst + 1]
        K_o = theta[n_inst + 2]
        phi_o = theta[n_inst + 3]
        e_o = theta[n_inst + 4]
        omega_o = theta[n_inst + 5]
        P_o = 10**log10P_o
        t_per_o = self.t_anchor + phi_o * P_o / (2 * np.pi)
        mu += rv_kep_ecc(self.t, K_o, P_o, t_per_o, e_o, omega_o)
        # Inner
        log10P_i = theta[n_inst + 6]
        K_i = theta[n_inst + 7]
        phi_i = theta[n_inst + 8]
        e_i = theta[n_inst + 9]
        omega_i = theta[n_inst + 10]
        P_i = 10**log10P_i
        t_per_i = self.t_anchor + phi_i * P_i / (2 * np.pi)
        mu += rv_kep_ecc(self.t, K_i, P_i, t_per_i, e_i, omega_i)
        return mu

    # ---- log-likelihoods (with per-point variance inflation by σ_jit) ----
    def make_log_lik(self, model_fn):
        rv = self.rv
        sigma = self.sigma
        n_inst = self.n_inst

        def log_lik(theta):
            log_sigma_jit = theta[n_inst]
            sigma_jit = 10**log_sigma_jit  # km/s
            mu = model_fn(theta)
            var = sigma**2 + sigma_jit**2
            chi2 = (rv - mu) ** 2 / var
            norm = np.log(2 * np.pi * var)
            return -0.5 * float(np.sum(chi2 + norm))

        return log_lik

    # ---- prior transforms ----
    def prior_zero(self, u):
        n_inst = self.n_inst
        p = np.zeros(n_inst + 1)
        for i, s in enumerate(self.instruments):
            p[i] = self.gamma_lo[s] + u[i] * (self.gamma_hi[s] - self.gamma_lo[s])
        # log_σ_jit ∈ log10(1e-4) to log10(0.1) km/s i.e. 0.1 m/s to 100 m/s
        p[n_inst] = -4.0 + u[n_inst] * 3.0  # -4 → -1
        return p

    def prior_1kep(self, u):
        n_inst = self.n_inst
        p = np.zeros(n_inst + 6)
        for i, s in enumerate(self.instruments):
            p[i] = self.gamma_lo[s] + u[i] * (self.gamma_hi[s] - self.gamma_lo[s])
        p[n_inst] = -4.0 + u[n_inst] * 3.0  # log_σ_jit
        # outer period: gaussian centered on NSS P if given, else log-uniform on baseline
        if self.outer_P_nss is not None and self.outer_P_err is not None:
            # broad gaussian in log10P space — width = log10(P+err) - log10(P-err)
            P_lo = max(self.outer_P_nss - 2 * self.outer_P_err, 10.0)
            P_hi = self.outer_P_nss + 2 * self.outer_P_err
            log10P_lo = np.log10(P_lo)
            log10P_hi = np.log10(P_hi)
            p[n_inst + 1] = log10P_lo + u[n_inst + 1] * (log10P_hi - log10P_lo)
        else:
            log10P_lo = np.log10(2.0)
            log10P_hi = np.log10(max(5 * self.baseline, 1000.0))
            p[n_inst + 1] = log10P_lo + u[n_inst + 1] * (log10P_hi - log10P_lo)
        # K: log-uniform 1 m/s to 100 km/s
        p[n_inst + 2] = 10 ** (-3.0 + u[n_inst + 2] * 5.0)
        # phi periastron ∈ [0, 2π]
        p[n_inst + 3] = u[n_inst + 3] * 2 * np.pi
        # e: Kipping 2013 Beta(0.867, 3.03)
        p[n_inst + 4] = float(betaincinv(0.867, 3.03, np.clip(u[n_inst + 4], 1e-9, 1 - 1e-9)))
        p[n_inst + 4] = float(np.clip(p[n_inst + 4], 0.001, 0.95))
        # ω ∈ [0, 2π]
        p[n_inst + 5] = u[n_inst + 5] * 2 * np.pi
        return p

    def prior_2kep(self, u):
        n_inst = self.n_inst
        p = np.zeros(n_inst + 11)
        # γ + log_σ_jit + outer (same as 1-Kep)
        for i, s in enumerate(self.instruments):
            p[i] = self.gamma_lo[s] + u[i] * (self.gamma_hi[s] - self.gamma_lo[s])
        p[n_inst] = -4.0 + u[n_inst] * 3.0
        # Outer
        if self.outer_P_nss is not None and self.outer_P_err is not None:
            P_lo = max(self.outer_P_nss - 2 * self.outer_P_err, 10.0)
            P_hi = self.outer_P_nss + 2 * self.outer_P_err
            log10P_lo = np.log10(P_lo)
            log10P_hi = np.log10(P_hi)
            p[n_inst + 1] = log10P_lo + u[n_inst + 1] * (log10P_hi - log10P_lo)
        else:
            log10P_lo = np.log10(max(self.inner_P_range[1] * 1.5, 100.0))
            log10P_hi = np.log10(max(5 * self.baseline, 1000.0))
            p[n_inst + 1] = log10P_lo + u[n_inst + 1] * (log10P_hi - log10P_lo)
        p[n_inst + 2] = 10 ** (-3.0 + u[n_inst + 2] * 5.0)
        p[n_inst + 3] = u[n_inst + 3] * 2 * np.pi
        p[n_inst + 4] = float(betaincinv(0.867, 3.03, np.clip(u[n_inst + 4], 1e-9, 1 - 1e-9)))
        p[n_inst + 4] = float(np.clip(p[n_inst + 4], 0.001, 0.95))
        p[n_inst + 5] = u[n_inst + 5] * 2 * np.pi
        # Inner: log-uniform period in [inner_P_range]
        log10P_i_lo = np.log10(self.inner_P_range[0])
        log10P_i_hi = np.log10(self.inner_P_range[1])
        p[n_inst + 6] = log10P_i_lo + u[n_inst + 6] * (log10P_i_hi - log10P_i_lo)
        p[n_inst + 7] = 10 ** (-3.0 + u[n_inst + 7] * 4.0)  # K_in: 1 m/s to 10 km/s
        p[n_inst + 8] = u[n_inst + 8] * 2 * np.pi
        p[n_inst + 9] = float(betaincinv(0.867, 3.03, np.clip(u[n_inst + 9], 1e-9, 1 - 1e-9)))
        p[n_inst + 9] = float(np.clip(p[n_inst + 9], 0.001, 0.95))
        p[n_inst + 10] = u[n_inst + 10] * 2 * np.pi
        return p


# =============================================================================
# Nested sampling driver
# =============================================================================
def run_nested(log_lik, prior_xform, ndim, nlive, label, dlogz=0.5):
    print(f"[nested {label}] ndim={ndim}, nlive={nlive}…")
    tic = time.time()
    sampler = dynesty.NestedSampler(
        log_lik, prior_xform, ndim, nlive=nlive, sample="rwalk", bound="multi"
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    res = sampler.results
    logZ = float(res.logz[-1])
    logZ_err = float(res.logzerr[-1])
    elapsed = time.time() - tic
    print(f"[nested {label}] done in {elapsed:.1f}s  logZ = {logZ:.2f} ± {logZ_err:.2f}")
    return res, logZ, logZ_err


def posterior_samples(results, n=2000):
    weights = np.exp(results.logwt - results.logz[-1])
    samples = dyutils.resample_equal(results.samples, weights)
    if len(samples) > n:
        idx = np.random.choice(len(samples), n, replace=False)
        samples = samples[idx]
    return samples


def map_params(results):
    idx = int(np.argmax(results.logl))
    return np.asarray(results.samples[idx])


# =============================================================================
# Top-level pipeline per target
# =============================================================================
def run_target(target_meta, out_dir: Path, nlive=300, dlogz=0.5):
    """Full pipeline: load → fit 0/1/2-Kep → compare."""
    out_dir.mkdir(parents=True, exist_ok=True)
    name = target_meta["name"]
    print(f"\n{'='*78}\nTarget: {name}\n{'='*78}")

    # 1. Load multi-archive RVs
    print("\n[1] Loading multi-archive RVs:")
    df_rv = load_target_rvs(target_meta)
    csv_p = out_dir / f"{name.replace(' ','_')}_rv_combined.csv"
    df_rv.write_csv(csv_p)
    print(f"  Combined: N={len(df_rv)} epochs, baseline={df_rv['t_bjd'].max()-df_rv['t_bjd'].min():.0f} d")
    print(f"  Instruments: {sorted(set(df_rv['instrument'].to_list()))}")

    # Archive coverage summary
    cov = (
        df_rv.group_by("instrument")
        .agg(
            pl.len().alias("N"),
            pl.col("t_bjd").min().alias("t_min"),
            pl.col("t_bjd").max().alias("t_max"),
            pl.col("sigma_kms").median().alias("sigma_med_kms"),
            pl.col("rv_kms").max().alias("rv_max"),
            pl.col("rv_kms").min().alias("rv_min"),
        )
        .with_columns(
            (pl.col("t_max") - pl.col("t_min")).alias("baseline_d"),
            (pl.col("rv_max") - pl.col("rv_min")).alias("rv_p2p_kms"),
        )
    )
    cov.write_csv(out_dir / f"{name.replace(' ','_')}_archive_coverage.csv")
    print("\n[Coverage]")
    print(cov)

    # 2. Build model
    m_host = target_meta.get("m_host_sun", 1.0)
    outer_P_nss = target_meta.get("outer_P_nss")
    outer_P_err = target_meta.get("outer_P_err")
    inner_P_range = target_meta.get("inner_P_range", (2.0, 500.0))

    M = TwoKeplerianModel(
        df_rv,
        m_host_sun=m_host,
        outer_P_nss=outer_P_nss,
        outer_P_err=outer_P_err,
        inner_P_range=inner_P_range,
    )

    # 3. Run nested sampling: 0-Kep, 1-Kep, 2-Kep
    np.random.seed(20260512)
    n_inst = M.n_inst

    # 0-Kep: γ + log_σ_jit only
    ndim_0 = n_inst + 1
    res0, logZ0, dZ0 = run_nested(
        M.make_log_lik(M.model_zero), M.prior_zero, ndim_0, nlive, "0kep", dlogz
    )

    # 1-Kep
    ndim_1 = n_inst + 6
    res1, logZ1, dZ1 = run_nested(
        M.make_log_lik(M.model_1kep), M.prior_1kep, ndim_1, nlive, "1kep", dlogz
    )

    # 2-Kep (only if 1-Kep showed evidence for signal)
    log10_BF_1_0 = (logZ1 - logZ0) / np.log(10)
    print(f"\n[BF report] log10 BF(1-Kep / 0-Kep) = {log10_BF_1_0:+.2f}")

    ndim_2 = n_inst + 11
    res2, logZ2, dZ2 = run_nested(
        M.make_log_lik(M.model_2kep), M.prior_2kep, ndim_2, nlive, "2kep", dlogz
    )
    log10_BF_2_1 = (logZ2 - logZ1) / np.log(10)
    print(f"[BF report] log10 BF(2-Kep / 1-Kep) = {log10_BF_2_1:+.2f}")
    print(f"[BF report] log10 BF(2-Kep / 0-Kep) = {(logZ2 - logZ0)/np.log(10):+.2f}")

    # 4. Posterior summaries
    samples_1 = posterior_samples(res1, n=2000)
    samples_2 = posterior_samples(res2, n=2000)

    map_1 = map_params(res1)
    map_2 = map_params(res2)

    # 1-Kep posterior
    pct = lambda x: np.percentile(x, [2.5, 16, 50, 84, 97.5])
    P_1_post = 10 ** samples_1[:, n_inst + 1]
    K_1_post = samples_1[:, n_inst + 2]
    e_1_post = samples_1[:, n_inst + 4]
    M2_1_post = m2_sini_jup(K_1_post, P_1_post, e_1_post, m_host)

    # 2-Kep: outer + inner
    P_o_post = 10 ** samples_2[:, n_inst + 1]
    K_o_post = samples_2[:, n_inst + 2]
    e_o_post = samples_2[:, n_inst + 4]
    M2_o_post = m2_sini_jup(K_o_post, P_o_post, e_o_post, m_host)
    P_i_post = 10 ** samples_2[:, n_inst + 6]
    K_i_post = samples_2[:, n_inst + 7]
    e_i_post = samples_2[:, n_inst + 9]
    M2_i_post = m2_sini_jup(K_i_post, P_i_post, e_i_post, m_host)

    # Per-instrument γ posteriors
    gamma_post = {}
    for i, s in enumerate(M.instruments):
        gamma_post[s] = pct(samples_1[:, i]).tolist()

    # σ_jit posterior (in m/s)
    log_sigma_jit_post = samples_1[:, n_inst]
    sigma_jit_mps_post = 10**log_sigma_jit_post * 1000.0

    # 5. Compile result dict
    result = {
        "target": name,
        "n_epochs": int(len(df_rv)),
        "n_instruments": int(n_inst),
        "instruments": M.instruments,
        "baseline_d": float(M.baseline),
        "m_host_sun": m_host,
        "outer_P_nss_prior_d": outer_P_nss,
        "outer_P_err_prior_d": outer_P_err,
        "inner_P_search_d": list(inner_P_range),
        "logZ_0kep": logZ0, "logZ_0kep_err": dZ0,
        "logZ_1kep": logZ1, "logZ_1kep_err": dZ1,
        "logZ_2kep": logZ2, "logZ_2kep_err": dZ2,
        "log10_BF_1_0": float((logZ1 - logZ0) / np.log(10)),
        "log10_BF_2_1": float((logZ2 - logZ1) / np.log(10)),
        "log10_BF_2_0": float((logZ2 - logZ0) / np.log(10)),
        # 1-Kep MAP
        "_1kep_MAP": {
            "P_d": float(10 ** map_1[n_inst + 1]),
            "K_kms": float(map_1[n_inst + 2]),
            "e": float(map_1[n_inst + 4]),
            "omega_rad": float(map_1[n_inst + 5]),
            "M2_sini_mjup": float(m2_sini_jup(map_1[n_inst + 2], 10 ** map_1[n_inst + 1], map_1[n_inst + 4], m_host)),
        },
        # 1-Kep posterior percentiles
        "_1kep_pct": {
            "P_d": pct(P_1_post).tolist(),
            "K_mps": (pct(K_1_post) * 1000).tolist(),
            "e": pct(e_1_post).tolist(),
            "M2_sini_mjup": pct(M2_1_post).tolist(),
        },
        # 2-Kep MAP — outer
        "_2kep_outer_MAP": {
            "P_d": float(10 ** map_2[n_inst + 1]),
            "K_kms": float(map_2[n_inst + 2]),
            "e": float(map_2[n_inst + 4]),
            "omega_rad": float(map_2[n_inst + 5]),
            "M2_sini_mjup": float(m2_sini_jup(map_2[n_inst + 2], 10 ** map_2[n_inst + 1], map_2[n_inst + 4], m_host)),
        },
        # 2-Kep MAP — inner
        "_2kep_inner_MAP": {
            "P_d": float(10 ** map_2[n_inst + 6]),
            "K_kms": float(map_2[n_inst + 7]),
            "e": float(map_2[n_inst + 9]),
            "omega_rad": float(map_2[n_inst + 10]),
            "M2_sini_mjup": float(m2_sini_jup(map_2[n_inst + 7], 10 ** map_2[n_inst + 6], map_2[n_inst + 9], m_host)),
        },
        # 2-Kep posterior percentiles — outer + inner
        "_2kep_outer_pct": {
            "P_d": pct(P_o_post).tolist(),
            "K_mps": (pct(K_o_post) * 1000).tolist(),
            "e": pct(e_o_post).tolist(),
            "M2_sini_mjup": pct(M2_o_post).tolist(),
        },
        "_2kep_inner_pct": {
            "P_d": pct(P_i_post).tolist(),
            "K_mps": (pct(K_i_post) * 1000).tolist(),
            "e": pct(e_i_post).tolist(),
            "M2_sini_mjup": pct(M2_i_post).tolist(),
        },
        "gamma_kms_pct_per_inst": gamma_post,
        "sigma_jit_mps_pct": pct(sigma_jit_mps_post).tolist(),
    }

    # Verdict
    if log10_BF_2_1 > 1.0:
        verdict = "2-Keplerian STRONGLY preferred — multi-body system"
    elif log10_BF_2_1 > 0.5:
        verdict = "2-Keplerian SUBSTANTIAL preference — multi-body hint"
    elif log10_BF_2_1 > 0.0:
        verdict = "2-Keplerian weakly preferred"
    else:
        verdict = "1-Keplerian sufficient (no inner planet detected)"
    result["verdict"] = verdict

    # Save
    (out_dir / f"{name.replace(' ','_')}_result.json").write_text(json.dumps(result, indent=2, default=str))
    np.savez(
        out_dir / f"{name.replace(' ','_')}_chains.npz",
        samples_1=res1.samples, logl_1=res1.logl, logwt_1=res1.logwt,
        samples_2=res2.samples, logl_2=res2.logl, logwt_2=res2.logwt,
        logZ_0=logZ0, logZ_1=logZ1, logZ_2=logZ2,
        instruments=np.array(M.instruments, dtype=object),
    )

    # Print summary
    print(f"\n{'-'*78}")
    print(f"[Verdict] {verdict}")
    print(f"{'-'*78}")
    print(f"  1-Kep MAP:  P={result['_1kep_MAP']['P_d']:.2f} d, K={result['_1kep_MAP']['K_kms']*1000:.1f} m/s, "
          f"e={result['_1kep_MAP']['e']:.3f}, M sin i={result['_1kep_MAP']['M2_sini_mjup']:.2f} M_J")
    print(f"  2-Kep MAP outer: P={result['_2kep_outer_MAP']['P_d']:.2f} d, K={result['_2kep_outer_MAP']['K_kms']*1000:.1f} m/s, "
          f"e={result['_2kep_outer_MAP']['e']:.3f}, M sin i={result['_2kep_outer_MAP']['M2_sini_mjup']:.2f} M_J")
    print(f"  2-Kep MAP inner: P={result['_2kep_inner_MAP']['P_d']:.2f} d, K={result['_2kep_inner_MAP']['K_kms']*1000:.1f} m/s, "
          f"e={result['_2kep_inner_MAP']['e']:.3f}, M sin i={result['_2kep_inner_MAP']['M2_sini_mjup']:.2f} M_J")

    return result, df_rv


# =============================================================================
# Target catalog
# =============================================================================
def get_target_catalog():
    return {
        "HD 142": {
            "name": "HD 142",
            "ra": 1.5836771, "dec": -49.0753625,
            "gaia_id": 2349916559152267008,
            "harps_name": "HD142A",
            "nasa_exo_name": "HD 142",
            "hires_name": None,
            "m_host_sun": 1.24,
            "outer_P_nss": None, "outer_P_err": None,
            "inner_P_range": (2.0, 500.0),
            "v_mag": 5.71,
            "known_planets": [
                {"name": "HD 142 b", "P_d": 350.3, "K_mps": 33.2, "e": 0.17, "M_mjup": 1.25},
                {"name": "HD 142 c", "P_d": 6005.0, "K_mps": 50.1, "e": 0.21, "M_mjup": 5.3},
                {"name": "HD 142 d", "P_d": 108.6, "K_mps": 7.96, "e": 0.0, "M_mjup": 0.31},
            ],
        },
        "HD 111232": {
            "name": "HD 111232",
            "ra": 192.2159553, "dec": -68.4246679,
            "gaia_id": 6128140049721626496,
            "harps_name": "HD111232",
            "nasa_exo_name": "HD 111232",
            "hires_name": None,
            "m_host_sun": 0.78,
            "outer_P_nss": None, "outer_P_err": None,
            "inner_P_range": (2.0, 500.0),
            "v_mag": 7.62,
            "known_planets": [
                {"name": "HD 111232 b", "P_d": 1143.0, "K_mps": 200.6, "e": 0.20, "M_mjup": 6.81},
                {"name": "HD 111232 c", "P_d": 7900.0, "K_mps": 27.0, "e": 0.32, "M_mjup": 1.99},
            ],
        },
        "HD 175167": {
            "name": "HD 175167",
            "ra": 285.0033888, "dec": -69.9450664,
            "gaia_id": 6421118739093252224,
            "harps_name": None,
            "nasa_exo_name": "HD 175167",
            "hires_name": None,
            "m_host_sun": 1.37,
            "outer_P_nss": 898.7, "outer_P_err": 198.2,
            "inner_P_range": (2.0, 200.0),
            "v_mag": 8.01,
            "known_planets": [
                {"name": "HD 175167 b", "P_d": 1290.0, "K_mps": 78.0, "e": 0.54, "M_mjup": 7.8},
            ],
        },
        "HD 33636": {
            "name": "HD 33636",
            "ra": 77.94353920, "dec": 4.40353948,
            "gaia_id": None,
            "harps_name": None,
            "nasa_exo_name": "HD 33636",
            "hires_name": "HD33636",
            "m_host_sun": 1.02,
            "outer_P_nss": None, "outer_P_err": None,
            "inner_P_range": (2.0, 200.0),
            "v_mag": 6.99,
            "known_planets": [
                {"name": "HD 33636 b", "P_d": 2128.0, "K_mps": 167.0, "e": 0.48, "M_mjup": 9.28},
            ],
        },
        "HD 128717": {
            "name": "HD 128717",
            "ra": 219.08814758, "dec": 57.56096062,
            "gaia_id": 1610837178107032192,
            "harps_name": None,
            "nasa_exo_name": None,
            "hires_name": None,
            "m_host_sun": 0.91,
            "outer_P_nss": 1089.15, "outer_P_err": 308.91,
            "inner_P_range": (2.0, 500.0),
            "v_mag": 8.78,
            "known_planets": [],
        },
    }


# =============================================================================
# Main
# =============================================================================
def main():
    catalog = get_target_catalog()
    out_root = ROOT / "data/candidate_dossiers/planet_hunt_multi_survey_2026_05_12"
    out_root.mkdir(parents=True, exist_ok=True)

    target_names = sys.argv[1:] if len(sys.argv) > 1 else list(catalog.keys())
    print(f"Running pipeline on targets: {target_names}")

    # Load existing summary so we can accumulate
    summary_p = out_root / "all_targets_summary.json"
    if summary_p.exists():
        all_results = json.loads(summary_p.read_text())
    else:
        all_results = {}

    for tname in target_names:
        if tname not in catalog:
            print(f"WARNING: target {tname} not in catalog; skipping")
            continue
        # Skip if we already have a result for this target unless --force
        if "--force" not in sys.argv and tname in all_results and "error" not in all_results[tname]:
            tgt_json = out_root / tname.replace(" ", "_") / f"{tname.replace(' ','_')}_result.json"
            if tgt_json.exists():
                print(f"  Skipping {tname} — already in summary. Use --force to re-run.")
                continue
        meta = catalog[tname]
        out_dir = out_root / tname.replace(" ", "_")
        try:
            result, df_rv = run_target(meta, out_dir, nlive=300, dlogz=0.5)
            all_results[tname] = result
            # Write incremental summary
            summary_p.write_text(json.dumps(all_results, indent=2, default=str))
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_results[tname] = {"error": str(e)}

    # Write summary
    summary_p.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\n\nSummary written to {summary_p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

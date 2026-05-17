"""Activity-induced RV jitter quantification (2026-05-17).

Follow-up to v1.12.0 TESS analysis. For each candidate with non-trivial
Lomb-Scargle power in the 0.1-30 d window, estimate the expected
activity-induced RV jitter and compare to the predicted orbital K_1.

Method:
  1. Fetch TESS PDC light curve via lightkurve (stitch up to 5 sectors)
  2. Phase-fold at the v1.12.0 LS peak period; measure peak-to-peak
     modulation amplitude (binned in 20 phase bins, median per bin)
  3. Convert to RV jitter via Aigrain+2012 FF' formalism:
       σ_RV ≈ (1/2) × ξ × A_phot × v_rot
     with ξ ≈ 0.7 for mid-latitude spots / single dominant active
     region.
  4. Compare to orbital K_1 predicted from the cascade's M_2_marg at
     i=60°.
  5. Recommend confirmation strategy based on K_orb / σ_jitter ratio:
       > 50: single quadrature RV epoch suffices
       10–50: 3-5 epochs distributed across orbital phase
       3–10: GP-modeled multi-epoch + simultaneous activity index
       < 3: activity-dominated, very hard

The R_star assumption is 1 R_sun (representative for our G/K dwarf
hosts; can be refined per candidate using Gaia stellar parameters).

Output:
  data/intermediate/activity_jitter_analysis.csv
"""
from __future__ import annotations

import math
import warnings
from pathlib import Path

import numpy as np
import polars as pl

warnings.filterwarnings("ignore")

import lightkurve as lk

R_SUN_KM = 6.957e5
DAY_S = 86400.0
G = 6.674e-11
M_SUN_KG = 1.989e30
M_JUP_KG = 1.898e27


CANDIDATES = [
    # (name, Gaia DR3, LS peak P_d from v1.12.0, V_mag, NSS P_d, M_2_marg M_J)
    ("BD+56 1762",  1607476280298633984, 4.12,  10.03, 197.0, 69.1),
    ("HD 140895",   4395581616493055616, 20.71,  9.39, 1460.0, 116.2),
    ("BD+46 2473",  2121783289552546432, 1.66,   8.97,  496.0,  88.6),
    ("HD 104828",   3905850581902839168, 14.66,  9.86,  None,   None),  # Acceleration
    ("HD 76078",    1017645329162554752, 0.12,   8.72,  275.0,  77.8),  # control: quiet
]


def predict_K1_mps(P_d: float, e: float, m1_msun: float, m2_mjup: float,
                   sin_i: float) -> float:
    P_s = P_d * DAY_S
    m1 = m1_msun * M_SUN_KG
    m2 = m2_mjup * M_JUP_KG
    return (
        (2 * math.pi * G / P_s) ** (1.0 / 3.0)
        * (m2 * sin_i)
        / ((m1 + m2) ** (2.0 / 3.0))
        / math.sqrt(1 - e ** 2)
    )


def v_rot_kmps(P_rot_d: float, R_star_rsun: float = 1.0) -> float:
    return 2 * math.pi * R_star_rsun * R_SUN_KM / (P_rot_d * DAY_S)


def aigrain_jitter_mps(amp_ptp_ppt: float, v_rot_kmps: float,
                        xi: float = 0.7) -> float:
    """σ_RV (m/s) from Aigrain+2012 FF' approx.

    Inputs: amplitude in parts per thousand, v_rot in km/s.
    """
    return 0.5 * xi * (amp_ptp_ppt * 1e-3) * v_rot_kmps * 1e3


def fetch_and_measure_amplitude(gaia_id: int, P_rot_d: float) -> dict:
    """Fetch TESS LC, phase-fold, measure peak-to-peak in 20 phase bins."""
    sr = lk.search_lightcurve(f"Gaia DR3 {gaia_id}", mission="TESS")
    if len(sr) == 0:
        return {"status": "no_tess_data"}
    lcs = []
    for r in sr[:5]:
        try:
            lc = r.download()
            if lc is None:
                continue
            lcs.append(lc.remove_nans().normalize())
        except Exception:
            pass
    if not lcs:
        return {"status": "no_download"}
    full = lcs[0]
    for nl in lcs[1:]:
        full = full.append(nl)
    full = full.remove_outliers(sigma=5)
    t = full.time.value
    y = full.flux.value
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    if len(t) < 200:
        return {"status": "insufficient_data"}
    phase = (t / P_rot_d) % 1.0
    nbins = 20
    edges = np.linspace(0, 1, nbins + 1)
    binned = np.array(
        [
            np.median(y[(phase >= edges[i]) & (phase < edges[i + 1])])
            if np.any((phase >= edges[i]) & (phase < edges[i + 1]))
            else np.nan
            for i in range(nbins)
        ]
    )
    binned = binned[~np.isnan(binned)]
    if len(binned) < 5:
        return {"status": "phase_gap"}
    amp_ptp = float(binned.max() - binned.min())
    return {
        "status": "ok",
        "amp_ptp_normalized": amp_ptp,
        "amp_ptp_ppt": amp_ptp * 1000.0,
    }


def main():
    rows = []
    for name, gaia_id, P_rot, V, P_orb, m2 in CANDIDATES:
        meas = fetch_and_measure_amplitude(gaia_id, P_rot)
        if meas["status"] != "ok":
            rows.append(
                {
                    "name": name,
                    "P_rot_d": P_rot,
                    "V": V,
                    "status": meas["status"],
                }
            )
            print(f'{name}: {meas["status"]}')
            continue
        amp_ppt = meas["amp_ptp_ppt"]
        vrot = v_rot_kmps(P_rot)
        sig_jit = aigrain_jitter_mps(amp_ppt, vrot)
        if P_orb and m2:
            K = predict_K1_mps(
                P_orb, 0.3, 1.0, m2, math.sin(math.radians(60))
            )
            ratio = K / sig_jit if sig_jit > 0.1 else float("inf")
            if ratio > 50:
                strategy = "single_quadrature_epoch"
            elif ratio > 10:
                strategy = "3-5_epochs_phase_distributed"
            elif ratio > 3:
                strategy = "GP_multi_epoch_with_activity_index"
            else:
                strategy = "activity_dominated_difficult"
        else:
            K = None
            ratio = None
            strategy = "acceleration_no_K_prediction"

        rows.append(
            {
                "name": name,
                "P_rot_d": P_rot,
                "V": V,
                "amp_ptp_ppt": round(amp_ppt, 3),
                "v_rot_kmps": round(vrot, 2),
                "sigma_jitter_mps": round(sig_jit, 1),
                "K_orb_predicted_mps": round(K, 0) if K else None,
                "K_over_jitter_ratio": round(ratio, 1) if ratio else None,
                "confirmation_strategy": strategy,
                "status": "ok",
            }
        )
        K_str = f"{K:.0f}" if K else "n/a"
        ratio_str = f"{ratio:.0f}" if ratio else "n/a"
        print(
            f"{name:12s}  P_rot={P_rot:5.2f}d  A={amp_ppt:6.3f}ppt  "
            f"v_rot={vrot:6.1f}km/s  σ_jit={sig_jit:5.1f}m/s  "
            f"K={K_str}m/s  K/σ={ratio_str}  ⇒ {strategy}"
        )

    df = pl.DataFrame(rows)
    out = (
        "/tmp/gaia-novelty-publication/data/intermediate/"
        "activity_jitter_analysis.csv"
    )
    df.write_csv(out)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()

"""TESS light-curve analysis for the 10 headline candidates (2026-05-17).

Two complementary photometric channels checked for each candidate:

  1. **Transit search at the Gaia NSS Orbital period.** Even though transit
     probability for random inclinations is ~R_star/a (typically 0.5-2%
     for our orbits), a single detection would be definitive: a BD-mass
     companion transit produces a ~1% depth event lasting hours.

  2. **Rotation / activity modulation check (Lomb-Scargle 0.1-30 d).**
     Identifies activity-driven photometric variability that could mimic
     orbital signatures or partially absorb the RV amplitude. Particularly
     relevant for BD+56 1762 (SIMBAD Em*) and faint M-dwarf candidates
     (HIP 60865, HIP 20122).

Output: data/intermediate/tess_lc_analysis.csv per-candidate summary plus
text dump.
"""
from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

import numpy as np
import polars as pl

warnings.filterwarnings("ignore")

try:
    import lightkurve as lk
    from astropy.timeseries import BoxLeastSquares, LombScargle
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    sys.exit(1)


CANDIDATES = [
    # (name, Gaia DR3, NSS_P_d, NSS_e, predicted_K_mps, V_mag)
    ("HD 101767",   841536616165020416,  486.0, 0.45, 1635, 8.88),
    ("HD 104828",   3905850581902839168, None,  None, None, 9.86),  # Acceleration
    ("HD 140895",   4395581616493055616, 1460.0, 0.49, 2289, 9.39),
    ("HD 140940",   6015027554036714496, 924.0, 0.75, 4288, 8.72),
    ("BD+46 2473",  2121783289552546432, 496.0, 0.33, 1931, 8.97),
    ("BD+35 228",   321123400368013696,  560.0, 0.40, 1160, 9.08),
    ("HIP 60865",   1518957932040718464, 501.0, 0.25, 1645, 12.09),
    ("HIP 20122",   3255968634985106816, 255.0, 0.17, 2965, 13.49),
    ("HD 76078",    1017645329162554752, 275.0, 0.29, 2058, 8.72),
    ("BD+56 1762",  1607476280298633984, 197.0, 0.42, 2576, 10.03),
]


def fetch_tess_lc(gaia_id: int, max_sectors: int = 10) -> "lk.LightCurve | None":
    """Search MAST and stitch the TESS light curves available for a target."""
    try:
        sr = lk.search_lightcurve(f"Gaia DR3 {gaia_id}", mission="TESS")
        if len(sr) == 0:
            return None
        sr = sr[:max_sectors]
        lcs = []
        for r in sr:
            try:
                lc = r.download()
                if lc is None:
                    continue
                lc = lc.remove_nans().normalize().flatten(window_length=401)
                lcs.append(lc)
            except Exception:
                continue
        if not lcs:
            return None
        full = lcs[0]
        for next_lc in lcs[1:]:
            full = full.append(next_lc)
        return full
    except Exception as e:
        print(f"  search/download failed: {e}", file=sys.stderr)
        return None


def bls_transit_search(lc, P_target_d: float | None, P_margin: float = 0.2) -> dict:
    """Box-Least-Squares around the predicted NSS period."""
    if lc is None or P_target_d is None:
        return {"bls_max_power": None, "bls_period_d": None, "bls_depth": None, "bls_dur_hr": None}
    t = lc.time.value
    y = lc.flux.value
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    if len(t) < 100:
        return {"bls_max_power": None, "bls_period_d": None, "bls_depth": None, "bls_dur_hr": None}

    # Span check — BLS needs at least one full orbital period in the data
    span_d = t.max() - t.min()
    if span_d < P_target_d * 0.5:
        return {
            "bls_max_power": None, "bls_period_d": None, "bls_depth": None,
            "bls_dur_hr": None, "note": f"TESS span {span_d:.0f}d < 0.5xP={P_target_d}d",
        }

    # Run BLS in a narrow period range around P_target
    bls = BoxLeastSquares(t, y - 1.0)
    p_min = P_target_d * (1 - P_margin)
    p_max = min(P_target_d * (1 + P_margin), span_d * 0.9)
    if p_max <= p_min:
        return {"bls_max_power": None, "bls_period_d": None, "bls_depth": None, "bls_dur_hr": None}
    periods = np.linspace(p_min, p_max, 200)
    durations = np.array([2.0, 6.0, 12.0]) / 24.0  # 2, 6, 12 hours
    result = bls.power(periods, durations)
    idx = np.argmax(result.power)
    return {
        "bls_max_power": float(result.power[idx]),
        "bls_period_d": float(result.period[idx]),
        "bls_depth": float(result.depth[idx]),
        "bls_dur_hr": float(result.duration[idx] * 24.0),
    }


def ls_rotation_check(lc) -> dict:
    """Lomb-Scargle 0.1-30 d for rotation / activity periods."""
    if lc is None:
        return {"ls_peak_period_d": None, "ls_peak_power": None, "ls_n_obs": None}
    t = lc.time.value
    y = lc.flux.value
    mask = np.isfinite(t) & np.isfinite(y)
    t, y = t[mask], y[mask]
    if len(t) < 100:
        return {"ls_peak_period_d": None, "ls_peak_power": None, "ls_n_obs": len(t)}
    freqs = np.linspace(1 / 30.0, 1 / 0.1, 2000)
    ls = LombScargle(t, y - np.median(y))
    power = ls.power(freqs)
    idx = np.argmax(power)
    return {
        "ls_peak_period_d": float(1 / freqs[idx]),
        "ls_peak_power": float(power[idx]),
        "ls_n_obs": int(len(t)),
    }


def main():
    rows = []
    for name, gaia_id, P, e, K_pred, V in CANDIDATES:
        print(f"\n=== {name} (G={V}) ===")
        lc = fetch_tess_lc(gaia_id)
        if lc is None:
            print("  no TESS LC available")
            rows.append({
                "name": name, "gaia_dr3": gaia_id, "V": V, "P_nss_d": P,
                "tess_status": "no_data",
                "bls_max_power": None, "bls_period_d": None, "bls_depth": None, "bls_dur_hr": None,
                "ls_peak_period_d": None, "ls_peak_power": None, "ls_n_obs": None,
            })
            continue
        bls = bls_transit_search(lc, P)
        rot = ls_rotation_check(lc)
        print(f"  TESS LC: {rot['ls_n_obs']} points")
        if bls.get("bls_max_power") is not None:
            print(f"  BLS @ P={P}d: max_power={bls['bls_max_power']:.4f}, "
                  f"depth={bls['bls_depth']:.4f}, dur={bls['bls_dur_hr']:.1f}h")
        else:
            print(f"  BLS: {bls.get('note', 'no result')}")
        print(f"  LS peak: P={rot['ls_peak_period_d']:.2f}d, power={rot['ls_peak_power']:.4f}")
        rows.append({
            "name": name, "gaia_dr3": gaia_id, "V": V, "P_nss_d": P,
            "tess_status": "ok",
            **bls,
            **rot,
        })

    df = pl.DataFrame(rows)
    out = "/tmp/gaia-novelty-publication/data/intermediate/tess_lc_analysis.csv"
    df.write_csv(out)
    print(f"\nWrote {out}")
    print(df)


if __name__ == "__main__":
    main()

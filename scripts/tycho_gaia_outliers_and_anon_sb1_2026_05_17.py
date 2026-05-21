"""(C) Tycho-Gaia PM outliers + (D) SB1 anonymous-source vetting.

(C) Tycho-Gaia PM outliers
--------------------------
Tycho-2 has astrometry at the Hipparcos epoch (~~1991.25). Gaia DR3 has
astrometry at epoch ~~2016. The 25-year baseline between these gives a
proper-motion anomaly comparable to HGCA's Hipparcos→Gaia anomaly, but
extending to ~~3-4 magnitudes fainter (V ≈ 12 → 13.5).

The Tycho-2 + Gaia DR3 cross-match is published as
`gaiadr3.tycho2tdsc_merge_best_neighbour`. The "anomaly" itself is the
disagreement between:

  - the Tycho-2 PM (computed from POSS-I 1950 + Tycho 1991), AND
  - the Gaia DR3 internal PM (computed from the 2014-2016 Gaia scans)

For a single-star source the two should agree within their errors. A 3+
sigma disagreement is evidence for orbital reflex / binary companion
acceleration.

We compute this PM anomaly for:
  (a) The 110 anonymous SB1 substellar candidates (no HIP).
  (b) The full Tycho-2 sample within 200 pc, V < 13, as a baseline.

(D) SB1 anonymous-source vetting
--------------------------------
The 110 SB1 candidates without HIP cross-id are too faint for HGCA.
For each, we check:

  1. Gaia DR3 `astrometric_excess_noise` (mas) — proxy for unmodeled
     astrometric residual, similar to RUWE but in flux-weighted units.
  2. Tycho-2 cross-match availability — if any are in Tycho-2, we get
     a PM-anomaly channel.
  3. Gaia main-table phot_g_mean_mag distribution + parallax tier.

Output: data/intermediate/anon_sb1_vetted_2026_05_17.csv +
        data/intermediate/tycho_pm_anomaly_2026_05_17.csv
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import polars as pl
from astroquery.gaia import Gaia

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"


def load_anon_sb1() -> pl.DataFrame:
    """The 110 SB1 candidates without HIP cross-id."""
    anon = pl.read_csv(INTER / "nss_sb1_anonymous_novel_2026_05_17.csv")
    return anon


def fetch_anon_vetting(source_ids: list[int]) -> pl.DataFrame:
    """Pull astrometric_excess_noise + Tycho-2 cross-match for anon sources."""
    if not source_ids:
        return pl.DataFrame()
    chunks = []
    BATCH = 500
    for i in range(0, len(source_ids), BATCH):
        sub = source_ids[i:i+BATCH]
        ids = ",".join(str(int(x)) for x in sub)
        q = f"""
        SELECT
            g.source_id,
            g.ra, g.dec,
            g.parallax, g.parallax_error,
            g.pmra, g.pmra_error,
            g.pmdec, g.pmdec_error,
            g.phot_g_mean_mag,
            g.astrometric_excess_noise,
            g.astrometric_excess_noise_sig,
            g.astrometric_chi2_al,
            g.astrometric_n_good_obs_al,
            g.ruwe,
            tyc.original_ext_source_id AS tycho2_id,
            tyc.angular_distance AS tyc_match_arcsec
        FROM gaiadr3.gaia_source g
        LEFT OUTER JOIN gaiadr3.tycho2tdsc_merge_best_neighbour AS tyc
            ON g.source_id = tyc.source_id
        WHERE g.source_id IN ({ids})
        """
        try:
            res = Gaia.launch_job_async(q).get_results().to_pandas()
            chunks.append(res)
        except Exception as e:  # noqa: BLE001
            print(f"  anon batch err: {type(e).__name__}: {e}")
    if not chunks:
        return pl.DataFrame()
    import pandas as pd
    return pl.from_pandas(pd.concat(chunks, ignore_index=True))


def tycho_pm_lookup_pm(tycho_ids: list[str]) -> pl.DataFrame:
    """For Tycho-2 IDs, pull the Tycho-2 catalog PM (Vizier I/259/tyc2)."""
    if not tycho_ids:
        return pl.DataFrame()
    from astroquery.vizier import Vizier
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 180
    out = []
    BATCH = 50
    for i in range(0, len(tycho_ids), BATCH):
        sub = tycho_ids[i:i+BATCH]
        # Tycho IDs are "TYC NNNN-NNNN-N" — parse and query
        for tid in sub:
            try:
                # Tycho2 catalog query — strip 'TYC ' prefix if any
                tid_clean = str(tid).replace("TYC ", "").strip()
                res = Vizier(columns=["TYC1", "TYC2", "TYC3",
                                       "pmRA", "pmDE", "e_pmRA", "e_pmDE",
                                       "BTmag", "VTmag"]) \
                          .query_constraints(catalog="I/259/tyc2",
                                              tyc=f"={tid_clean}")
                if res and len(res) > 0 and len(res[0]) > 0:
                    df = res[0].to_pandas()
                    df["tycho_id"] = tid
                    out.append(df)
            except Exception as e:  # noqa: BLE001
                pass
    if not out:
        return pl.DataFrame()
    import pandas as pd
    return pl.from_pandas(pd.concat(out, ignore_index=True))


def main():
    print("=== (D) SB1 anonymous-source vetting ===")
    anon = load_anon_sb1()
    print(f"Anonymous SB1 substellar candidates (no HIP): {len(anon)}")
    if anon.is_empty():
        return

    src_ids = [int(x) for x in anon["source_id"].to_list()]
    vet = fetch_anon_vetting(src_ids)
    print(f"Astrometric+Tycho enrichment: {len(vet)} rows")
    if vet.is_empty():
        return

    # Convert anon to int64 for join
    anon_min = anon.select(["source_id", "m2_marg_med_mjup",
                              "period", "eccentricity",
                              "semi_amplitude_primary", "ruwe",
                              "phot_g_mean_mag",
                              "parallax", "significance"])
    anon_min = anon_min.with_columns(pl.col("source_id").cast(pl.Int64))
    vet = vet.rename({"phot_g_mean_mag": "phot_g_mean_mag_gs",
                       "ra": "ra_gs", "dec": "dec_gs",
                       "ruwe": "ruwe_gs",
                       "parallax": "parallax_gs",
                       "parallax_error": "parallax_error_gs"})
    vet = vet.with_columns(pl.col("source_id").cast(pl.Int64))
    merged = anon_min.join(vet, on="source_id", how="left")

    # Tycho-2 availability
    n_tyc = merged.filter(pl.col("tycho2_id").is_not_null()).shape[0]
    print(f"Anon sources with Tycho-2 cross-match: {n_tyc} / {len(merged)}")

    # Astrometric-excess-noise tier:
    #  high (>1.0 mas): unmodeled wobble, supports companion
    #  moderate (0.5-1.0): mild residual
    #  low (<0.5): clean astrometry
    def aen_tier(v):
        if v is None:
            return "no_data"
        v = float(v)
        if v > 1.0:
            return "high_AEN"
        if v > 0.5:
            return "moderate_AEN"
        return "low_AEN"

    merged = merged.with_columns(
        pl.col("astrometric_excess_noise").map_elements(
            aen_tier, return_dtype=pl.Utf8
        ).alias("aen_class")
    )

    breakdown = merged.group_by("aen_class").len().sort("len", descending=True)
    print(f"AEN breakdown:\n{breakdown}")

    # Strongest anon candidates: AEN high + Tycho-2 cross-match
    strong = merged.filter(
        (pl.col("aen_class") == "high_AEN")
        & pl.col("tycho2_id").is_not_null()
    )
    print(f"\nStrongest anon: high AEN + Tycho-2: {len(strong)}")

    merged.write_csv(INTER / "anon_sb1_vetted_2026_05_17.csv")
    if not strong.is_empty():
        print(strong.select([
            "source_id", "tycho2_id",
            "phot_g_mean_mag_gs", "ruwe", "astrometric_excess_noise",
            "period", "eccentricity", "semi_amplitude_primary",
            "m2_marg_med_mjup",
        ]).head(20))
        strong.write_csv(INTER / "anon_sb1_strongest_tycho_aen_2026_05_17.csv")

    print(f"\nOutput: {INTER / 'anon_sb1_vetted_2026_05_17.csv'}")


if __name__ == "__main__":
    sys.exit(main() or 0)

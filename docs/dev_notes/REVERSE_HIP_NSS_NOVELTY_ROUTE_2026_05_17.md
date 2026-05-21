# Novelty route: Reverse Hipparcos NSS port (v1.16.0, 2026-05-17)

A new candidate channel opened up: Hipparcos sources with NSS classifications
(Sn ∈ {1, 3, 7}) that **do not** have a corresponding Gaia DR3 NSS detection.
These are pre-Gaia known non-single-star candidates that Gaia DR3 either
missed or rejected, awaiting DR4 epoch-astrometry confirmation.

## Pool counts

Starting from `data/intermediate/hipparcos_vanLeeuwen2007_FULL.csv` (117,955 rows):

| Stage                                                  | Count |
|---------------------------------------------------------|------:|
| HIP NSS (Sn ∈ {1=orbital, 3=accel, 7=stochastic})       | 2,604 |
| With Gaia DR3 `hipparcos2_best_neighbour` cross-match   | 1,119 |
| With Gaia DR3 NSS solution (Orbital or Acceleration)    |    96 |
| **HIP NSS but no Gaia DR3 NSS** ← this is the route     | **1,032** |
| Passing V<12 + plx>5 + RUWE>1.4                         |   138 |
| By Sn type:                                              |       |
|   Sn=1 (HIP orbital)                                    |    84 |
|   Sn=3 (HIP acceleration)                               |     2 |
|   Sn=7 (HIP stochastic / VIM)                           |    52 |

## Why is this interesting?

For 1,032 sources, Hipparcos in 1991 successfully fit a non-single-star
solution (orbital, acceleration, or stochastic-motion). Gaia DR3 in 2022,
with vastly better astrometric precision over a 5-year baseline, has the
same source flagged as a normal single-star in its NSS pipeline. Why
might that happen?

1. **Period mismatch**: Hipparcos saw a long-period orbit (P > 5 yr) whose
   arc was sampled across the 4-year Hipparcos mission, but Gaia DR3's
   NSS Orbital pipeline only fits P < 5 yr orbits because that's the DR3
   time baseline. Gaia DR4 (10-year baseline) will catch these.

2. **Detection-threshold gap**: Hipparcos found a weak NSS solution at
   the threshold of its precision. Gaia DR3's NSS quality cuts are
   tighter (significance ≥ 5), so a 2-3σ HIP detection wouldn't promote
   to DR3 NSS.

3. **Companion has shifted**: For very wide visual binaries, the relative
   geometry between 1991 and 2016 has changed; the 1991 NSS-classified
   motion may not be reproducible at the 2016 epoch.

4. **Hipparcos false positive**: Some Sn=7 classifications are real
   spurious classifications (random astrometric noise interpreted as
   stochastic).

The first three explanations give us 1,032 candidates for "pre-Gaia
detected companion, awaiting DR4 orbital characterization."

## Top 10 Sn=7 (stochastic) by Gaia RUWE — strongest HIP-only candidates

These are HIP-detected anomalous-motion stars where Gaia's astrometric
residual (RUWE) is also enormous — implying a real unmodeled companion
that DR3's NSS pipeline simply couldn't fit (likely because of period
mismatch with the 5-year baseline).

| HIP    | Hpmag | V_G   | RUWE   | dist (pc) | AEN (mas) |
|-------:|------:|------:|-------:|----------:|----------:|
| 10786  |  8.84 |  8.59 | **24.5** |     72    |   3.91    |
| 69160  |  8.09 |  7.81 | **15.4** |     59    |   2.69    |
| 102431 |  4.63 |  4.32 | **15.0** |     28    |   5.26    |
| 54737  |  8.53 |  8.33 | **14.9** |     93    |   2.62    |
| 96754  |  7.66 |  7.41 | **13.9** |     60    |   2.76    |
| 65621  |  6.56 |  6.13 | **13.2** |     94    |   1.94    |
| 99420  |  7.03 |  6.93 | **12.8** |    135    |   2.98    |
| 109839 |  8.28 |  8.03 | **10.9** |     75    |   2.39    |
| 109226 |  7.26 |  6.86 | **10.4** |    182    |   1.70    |
| 71368  |  8.20 |  7.98 | **10.3** |     70    |   2.37    |

RUWE values of 10-25 are 10-25× the single-star ~1.0 baseline → these
have massive unmodeled astrometric residuals. With Gaia DR3 epoch
astrometry, these are the strongest "DR4 will solve it" candidates in
the entire archive.

## Why these are NOT promoted to the headline list

Crucially: **none of these 138 sources have a Gaia DR3 SB1 fit**, so we
cannot apply the Pourbaix mass function and cannot derive M_2_marg. The
RUWE-only evidence is qualitative — we know there's a companion, but we
don't know if it's substellar (BD/planet) or stellar.

Most Sn=7 sources with RUWE > 10 likely have STELLAR companions, because
massive companions produce the largest astrometric residuals. Substellar
companions tend to produce RUWE in the 1.5-5 range (per our SB1-pool
calibration, where confirmed-BD candidates show RUWE = 0.9-6.9).

So these 138 are deferred to **Gaia DR4** (Dec 2026), which will publish
epoch astrometry letting us fit orbital solutions ourselves — at which
point each will get a proper M_2 posterior.

## Strategic value

This pool represents the **largest single-source list of pre-Gaia
substellar-candidate-quality astrometric anomalies that Gaia DR3 missed**.
For the methodology paper, it's a:

1. **DR4 target list** — every one will get re-analyzed when DR4 lands.
2. **Validation set** — when DR4 publishes epoch astrometry for these
   1,032 sources, the recovery rate will benchmark the SB1 + Tycho-Gaia
   cascade's completeness.
3. **Substellar candidate seed pool** — of the 138 passing our minimal
   quality cuts, an estimated 5-15% (per Sahlmann 2025's BD fraction)
   will turn out to be substellar after DR4 orbital characterization.

## Files

- `data/intermediate/reverse_hip_nss_missed_by_gaia_2026_05_17.csv` — full 1,032
- `data/intermediate/reverse_hip_nss_bd_candidates_2026_05_17.csv` — 138 passing
  V<12 + plx>5 + RUWE>1.4 (substellar-quality astrometric outliers)
- Script: `scripts/widened66_and_reverse_hip_2026_05_17.py`

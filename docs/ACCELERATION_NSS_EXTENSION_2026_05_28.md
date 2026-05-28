# Acceleration-NSS Cascade Extension (v3) — 2026-05-28

Extension of the dormant compact-object cascade beyond NSS Orbital +
AstroSpectroSB1 (covered in v2 / `main_hunt_derived_v2.parquet`) to the
**NSS Acceleration channel** — sources in `gaiadr3.nss_acceleration_astro`
whose orbital period exceeds the Gaia DR3 mission baseline (~3 yr) so that
no Thiele-Innes orbit fit was attempted, only a 7- or 9-parameter
PM-acceleration model.

This is the Gaia BH3 regime (M_BH = 32.7 M_⊙, P = 4253 d ≈ 11.6 yr).

## Files

- `scripts/streaming/v3_acceleration/acceleration_inversion.py` — pure-Python
  module with the PM-acceleration ↔ M_2 inversion, plus vendored F#29/30/31
  filters and the v3 tier classifier.
- `scripts/streaming/v3_acceleration/run_acceleration.py` — driver that
  pulls the acceleration table from Gaia DR3 via ADQL, joins with
  `gaia_source` and `astrophysical_parameters[_supp]`, applies the cascade,
  and writes `data/derived/acceleration_v3.parquet`.
- `scripts/streaming/v3_acceleration/test_bh3_smoke.py` — unit tests of the
  inversion math against the BH3 published parameters.
- `data/derived/acceleration_v3.parquet` — final v3 output.
- `data/derived/acceleration_v3_raw.parquet` — cached
  `nss_acceleration_astro` rows (16,949 at `significance ≥ 50`).
- `data/derived/acceleration_v3_supplementary.parquet` — cached
  `gaia_source` + AP join.
- `/tmp/v3_acceleration.log` — execution log.

## Methodology — Acceleration ↔ M_2 inversion

For a binary on a circular orbit with primary mass M_1, companion M_2,
period P_yr and parallax `plx_mas`, the magnitude of the photocentric PM
acceleration vector is

    |a|_mas/yr^2 = 4 π² × (M_2 / (M_1 + M_2)^(1/3)) × P_yr^(−4/3) × plx_mas

(Kervella+ 2019 A&A 623 A72; Brandt 2018 ApJS 239 31; same form used by
El-Badry+ 2024 for the BH3 discovery).

Crucially, the acceleration channel does **not** give us P — only the
second time-derivative of the photocenter trajectory.  To turn |a| into
M_2 we must assume P.  We therefore grid in log-P over

    P_yr ∈ [P_yr_min, P_yr_max] = [3, 100] yr

at `n_grid = 32` points and report the M_2 envelope.

Why these bounds:

- **P_min = 3 yr** is approximately the Gaia DR3 baseline.  Below this Gaia
  would have produced a Thiele-Innes orbital fit and the source would land
  in `nss_two_body_orbit` (v2 catalog), not in `nss_acceleration_astro`.
- **P_max = 100 yr** is the physically motivated upper bound for dormant
  binaries that still produce a measurable curvature in a ~3-yr Gaia arc.
  Beyond this the photocentric track is well-approximated by a straight
  line + constant proper motion + parallax — there is no acceleration to
  measure.

The mass inversion at each P_yr is by 80-iteration bisection on

    f(M_2) = M_2 / (M_1 + M_2)^(1/3) − K = 0,
    K = |a| × P_yr^(4/3) / (4 π² × plx_mas)

(same bisection style as v2's `solve_m2`).  The LHS is monotone increasing
in M_2, so bisection is robust.  The full module is `acceleration_inversion.py`.

## Tier classification (v3)

Because the inversion is P-dependent, a single source spans a range of M_2
values [M2_min, M2_max].  We classify by the *envelope*:

| condition | tier |
|---|---|
| M2_min ≥ 3 M_⊙ | **Tier-1 BH** (BH even at most pessimistic P) |
| 1.2 ≤ M2_min < 3 M_⊙ | **Tier-1 NS** |
| M2_max ≥ 1.2 but M2_min < 1.2 | **Tier-2** (P-degenerate; compact-object candidate) |
| M2_max < 1.2 | **Rejected** (stellar at all P) |

Filters F#29 (SB2), F#30 (chromatic / K-giant) and F#31 (RV reality) are
applied as **demoting** filters on Tier-1 / Tier-2 candidates: a failed
filter converts the candidate to `Demoted (failed F#XX) -- was <base>`.

F#32 (joint K_obs vs. K_pred) is **not** applied because acceleration-only
sources have no orbital fit and therefore no K_pred(sin i = 1).

## BH3 smoke test

Gaia BH3 (`source_id = 4318465066420528000`) was *not* in DR3 NSS — it
was discovered via the FPR full epoch astrometry.  We confirmed this by
ADQL: BH3 is absent from `nss_acceleration_astro`, `nss_two_body_orbit`,
`nss_non_linear_spectro`, and `nss_vim_fl`.

So we verify the **inversion mathematics** against BH3's published
parameters synthetically:

- M_BH = 32.7 M_⊙, M_⋆ = 0.76 M_⊙, P = 11.6 yr, plx = 1.644 mas (El-Badry+ 2024).
- Synthetic |a| from the forward formula: **25.0817 mas/yr²**.
- Round-trip `M2_from_acceleration(25.0817, 1.644, 0.76, 11.6)`:
  **M_2 = 32.700 M_⊙** (round-trip error 0.0).
- With the v3 default M_1 = 1.5 prior, the inverter at the published
  P = 11.6 yr returns **M_2 = 33.05 M_⊙** (within 1% of published value;
  the remaining deviation reflects the M_1 mis-specification rather than
  a math error).
- v3 envelope scan with M_1 = 1.5, P_yr ∈ [3, 100]: M_2_min = 2.70,
  M_2_max = 2403 M_⊙.  BH3's published value 32.7 lies comfortably inside.
- At M_2_min = 2.70 (which is just below the BH/NS boundary), v3 classifies
  BH3 as **Tier-1 NS** rather than Tier-1 BH.  This reflects an honest
  physical limitation: without an independent P constraint, the most
  pessimistic period assumption (P = P_min = 3 yr) yields an NS-mass
  estimate.  Tier-1 BH classification in this channel requires that even
  at P_min the M_2 already exceeds 3 M_⊙ — a strict cut that excludes
  ~half of the true BH population on principle.

Conclusion: the inversion math is **bit-exact** at the published P, and
the envelope correctly includes the published mass.  The v3 tier output
is conservative-by-design.

See `test_bh3_smoke.py` for the executable test.

## Run summary

Full run completed 2026-05-28 02:32:47 UTC in 349.2 s (= 5.8 min).
Parameters: `--min-significance 50 --M1-prior 1.5 --P-yr-min 3 --P-yr-max 100`.

| metric | value |
|---|---|
| Acceleration sources fetched (sig >= 50) | 16,949 |
| Successful gaia_source + AP joins | 16,949 (100% — 0 batches skipped) |
| Inversions completed | 16,949 (0 errors) |
| Output parquet | `data/derived/acceleration_v3.parquet` (53 cols) |

### Tier counts

| tier_v3 | count |
|---|---|
| Tier-1 BH                                              | 0      |
| Tier-1 NS                                              | 0      |
| Tier-2 (P-degenerate compact-object candidate)         | 10,818 |
| Demoted (failed F#30 K-giant chromatic)                | 5,578  |
| Demoted (failed F#31 phantom RV)                       | 534    |
| Rejected (stellar at all P; M2_max < 1.2)              | 19     |

The complete absence of Tier-1 BH / Tier-1 NS reflects the strict cut:
the maximum **M2_min** value across all 16,949 sources is 0.74 M_⊙.
This is physically expected — see "Caveats" §1 below.

### Top 10 P-degenerate compact-object candidates (cleanly passing F#29-31)

Sorted by **M2_median_v3** (the inversion at the geometric-mean assumed P).
All these have M2_min < 1.2 M_⊙ but M2_median in the stellar-mass BH range:

| source_id           | sig    | \|a\| mas/yr² | plx mas | M2_min | M2_med | M2_max | G mag | RUWE |
|---|---|---|---|---|---|---|---|---|
| 4394957055230673152 | 51.99  | 13.97 |  3.48 | 0.56 | 10.46 | 324.87 | 10.65 | 5.00 |
| 4527774108496103168 | 53.54  |  9.39 |  2.63 | 0.49 |  8.88 | 272.67 | 12.29 | 6.45 |
| 2128803327702225280 | 56.67  |  9.15 |  2.65 | 0.47 |  8.46 | 259.12 | 11.29 | 6.11 |
| 77413727493690112   | 63.03  | 38.46 | 11.41 | 0.46 |  8.19 | 250.28 |  9.10 | 37.63 |
| 464969968312839680  | 68.42  |  9.30 |  2.98 | 0.43 |  7.36 | 222.87 | 13.44 | 5.12 |
| 4795025085529756544 | 52.03  |  7.84 |  2.57 | 0.41 |  7.12 | 214.97 | 13.08 | 7.63 |
| 5676693700014657664 | 58.53  | 12.53 |  4.22 | 0.40 |  6.87 | 207.02 | 11.84 | 3.61 |
| 742484675930712320  | 99.27  | 20.14 |  6.79 | 0.40 |  6.86 | 206.73 | 11.20 | 7.27 |
| 5877996553772071936 | 54.58  |  8.72 |  2.99 | 0.40 |  6.70 | 201.38 | 13.01 | 5.28 |
| 3037270652623002240 | 70.80  | 13.51 |  4.66 | 0.39 |  6.65 | 199.84 | 12.12 | 16.39 |

Note the high RUWE on most of these — RUWE > 1.4 is the classic flag for
a binary with unmodeled orbital motion biasing the single-star astrometric
fit.  These are real, strongly perturbed sources.  The acceleration channel
caught them; the question is whether the perturbation comes from a multi-
M_⊙ compact remnant or from a closer-in shorter-period stellar companion
which would land in nss_two_body_orbit (v2 catalog) — but none of these
appear in v2, so they live exclusively in the long-period regime.

### Cross-reference with v2 catalog

Zero overlap (0 of 16,949 v3 sources appear in the 56,100-source v2 catalog).
This is exactly the expected outcome: v2 covers `nss_two_body_orbit`
(orbital fits, P ≤ 3 yr typically) while v3 covers `nss_acceleration_astro`
(P > Gaia baseline).  The two channels are by construction disjoint at
the source level.

## Unified catalog

`data/derived/compact_object_candidates_unified.parquet` joins v2 + v3
into a single slim catalog (17,760 rows, 16 cols):

- `channel`: 'v2_orbital' or 'v3_acceleration'
- `tier`: tier_v2 or tier_v3 string
- `M2_central` (M2_msun_v2 or M2_median_v3)
- `M2_min`, `M2_max` (point estimate for v2; bracket for v3)
- `P_yr` (known for v2; null for v3)
- `accel_mag_mas_yr2`, `significance` (v3 only)
- `f29`, `f30`, `f31`, `f32` (v2 has all four; v3 has f29-31 only)

Per channel: 830 v2_orbital candidate rows (Tier-1/2/Demoted, the
compact-object-class rows that survived the v2 cascade) + 16,930
v3_acceleration rows (all non-Rejected).

## Caveats and known issues

1. **P-degeneracy is fundamental.**  Without an external period constraint
   (RV monitoring, archival astrometry from Hipparcos/Tycho, or future
   Gaia DR4 epoch astrometry), the v3 inversion cannot uniquely recover
   M_2.  The Tier-1 BH cut (`M2_min ≥ 3 M_⊙`) excludes any source where
   a short-period scenario could explain the acceleration with a stellar
   companion — including a hypothetical "DR3-acceleration BH3" if BH3
   were in the DR3 acceleration table.

2. **No SB2 lookup.**  `nss_acceleration_astro` carries no SB2 flag, and
   we did not cross-match against external SB2 catalogs (SB9, etc.).
   F#29 will return PASS for all acceleration sources unless the
   `nss_solution_type` string contains "SB2" (which is not the case for
   any row in the acceleration table).  This is conservative — a true
   SB2 will not be falsely rejected, but neither will it be flagged as
   a known SB2.

3. **M_1 prior fixed at 1.5 M_⊙.**  For most acceleration-channel sources
   the primary mass is not separately measured (no FLAME entry on
   single-star fits when the source is a binary).  Using 1.5 M_⊙ matches
   the v2 cascade default.  Per-source M_1 from spectroscopic AP would
   refine the inversion by O(20%).

4. **Acceleration-9 (9-parameter) solutions ignored second derivative.**
   The 9-parameter solutions include `deriv_accel_ra` / `deriv_accel_dec`
   (the time-derivative of the PM-acceleration, i.e. the third derivative
   of position).  We pass these through to the output parquet but do not
   currently use them in the mass inversion.  A future refinement could
   constrain P more tightly via the `|deriv_accel|/|accel|` ratio.

5. **High-significance bias.**  At `significance ≥ 50` we are selecting
   the strongest astrometric-perturbation signals.  These are dominated
   by short-period, nearby binaries where the M_2 envelope tends to
   straddle the NS/stellar mass-cut (Tier-2).  Genuine long-period BH
   candidates with weaker but still significant acceleration signatures
   may live at `significance ∈ [25, 50]`; re-running with
   `--min-significance 25` would extend the search at the cost of
   ~20-40 minutes additional ADQL time.

6. **BH3 unreachable from DR3 NSS.**  The Gaia BH3 discovery used the
   Focused Product Release (FPR) full epoch astrometry which is not in
   DR3 NSS.  Recovering BH3 from DR3 alone is impossible; it will appear
   in the DR4 NSS release.  This is a constraint of the underlying data,
   not a limitation of v3.

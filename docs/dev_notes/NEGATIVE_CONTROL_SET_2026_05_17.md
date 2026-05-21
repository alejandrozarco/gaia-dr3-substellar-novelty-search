# Independent negative control set + out-of-sample specificity (v1.16.0, 2026-05-17)

Built per the "Independent Negative Control Set" specification. The goal was
an out-of-sample specificity estimate free of the leakage that inflates the
in-sample benchmark — where Sahlmann verdicts both *label* negatives and
*feed* the cascade as a filter input.

**The single rule:** a negative's "stellar" label must come from a catalog
the cascade never touches as a filter or RV input. Otherwise a bigger set
just scales up the leakage.

## Result headline

| Tier                                   | n  | rejected | specificity | Wilson 95% CI |
|----------------------------------------|---:|---------:|------------:|---------------|
| **Gaia-SB2 (strictly disjoint)**       | 18 | 6        | **0.333**   | 0.16–0.56     |
| Combined (+ APOGEE-SB2 asterisked)     | 24 | 6        | 0.250       | 0.12–0.45     |

The frozen cascade (v1.16.0, pre-Filter-#29) correctly rejects only **1 in 3**
leak-free SB2 stellar imposters that enter the Stage-1 pool. **All 18 escapes
are SB2 binaries** — the cascade had no filter on the Gaia spectroscopic-binary
channel. This is the dominant residual blind spot, and it is invisible to the
leaky in-sample benchmark.

**One escape, HD 76078, had reached the headline candidate list as a false
positive** (see below). The control set found a real error on first construction.

## Construction

### Filter blocklist (label sources NOT allowed)
Enforced per row via `assert label_source not in FILTER_BLOCKLIST`:
`sahlmann2025, hgca_brandt2024, kervella2022_pma, wds, orb6, sb9,
tokovinin_msc, galah, trifonov2025, halbwachs2023_masses, halbwachs_holl2024,
nasa_exo, exoplanet_eu, simbad, harps, hires, apogee, carmenes, lamost,
tess_rot, gaia_var`.

### Tier A2 — Gaia DR3 SB2/SB2C ∩ pool (strictly disjoint) — 18 sources
Query `gaiadr3.nss_two_body_orbit` for SB2/SB2C solutions, cross-match by
source_id against the 9,498-source v2 pool. A pool source (admitted via its
astrometric Orbital/Acceleration solution with a substellar marginalized mass)
that ALSO carries an SB2/SB2C solution has both K1 and K2 measured — a
luminous secondary, i.e. a star. The SB2 channel is not on the blocklist and
is never consulted by any cascade filter. `independence=within_gaia_distinct_method`.
All 18 show K1 ≈ K2 in the 15–90 km/s range (near-equal-mass double-lined
stellar binaries).

### Tier A1 — APOGEE SB2 (Kounkel 2021) ∩ pool (asterisked) — 6 in-pool
Kounkel 2021 (VizieR J/AJ/162/184), SBn ≥ 2, coordinate cross-matched to the
pool. APOGEE is on the RV-input blocklist, but the SB2 *detection* (two line
sets) is independent of APOGEE RV joint-fitting (which is all the cascade uses
APOGEE for). Documented exception, tagged `independence=apogee_sb2_detection`,
droppable for a maximally-pure run.

**Coordinate-match caveat:** APOGEE 2MASS epoch-2000 positions vs Gaia
epoch-2016 without proper-motion correction produced 7 spurious 2″ matches
(matched source_id not actually in the pool). These were dropped via a strict
in-pool assertion. The official 2MASS×Gaia PM-aware cross-match would recover
them; a documented limitation of this tier. Net clean APOGEE in-pool: 6.

### Tiers B/C — not built this pass
Literature SB2 (Holl 2023, Marcussen & Albrecht 2023) and resolved-companion
flux-ratio (GRAVITY/PIONIER) are single-digit yield and were deferred. The
24 from A1+A2 give an interim specificity, exactly as the spec anticipates
("Report it as an interim number").

## The HD 76078 false positive

HD 76078 = Gaia DR3 1017645329162554752 carries **two** Gaia DR3 NSS solutions:

| Solution | P (d) | K1 (km/s) | K2 (km/s) | significance |
|----------|------:|----------:|----------:|-------------:|
| Orbital  | 274.6 | —         | —         | 10.6         |
| **SB2**  | 593.2 | 18.80     | 17.57     | **92.0**     |

The Orbital solution (the one the pool used) gave M_2_marg = 78 MJ, promoting
HD 76078 as a borderline substellar candidate. But the SB2 solution measures
both K1 and K2 with comparable amplitudes — q = K1/K2 ≈ 0.93, two
near-equal-mass luminous stars. **A measured K2 means the secondary shines —
it is a star, not a brown dwarf.** The astrometric photocentre wobble was
misinterpreted as substellar.

The clue was present all along: HD 76078's existing notes recorded
`non_single_star=3`, misread as "Orbital+Acceleration both apply". In fact the
Gaia `non_single_star` bitmask is 1=astrometric, 2=spectroscopic, 4=eclipsing;
**3 = astrometric + spectroscopic**, the spectroscopic bit being the SB2.

HD 76078 was removed from the headline list (27 → 26) and moved to
`cascade_byproducts.csv` with `category=cascade_byproduct_gaia_sb2_stellar_binary`.

## Per-filter credit (the 6 correct rejections)
| Reject reason            | count |
|--------------------------|------:|
| REJECTED_ruwe_quality    | 5     |
| REJECTED_hgca_stellar    | 1     |

The cascade caught 6 of 18 Gaia-SB2 negatives only incidentally (their RUWE
or HGCA χ² happened to trip another filter). None were caught *because* they
were SB2 — there was no SB2 filter.

## Fix: Filter #29 (Gaia SB2/SB2C rejection)

`scripts/pipeline_v11_sb2_filter_2026_05_17.py`. Rejects any source carrying a
Gaia DR3 SB2/SB2C solution. Applied to the v2 pool it newly rejects the 12
previously-leaked SB2 sources (the other 6 were already rejected), bringing
Gaia-SB2 rejection to 18/18.

**Protocol honesty:** Filter #29 is a categorical physics-motivated filter
(double-lined ⇒ luminous secondary ⇒ stellar), not a threshold tuned against
the control set. But per the spec, once added, the SB2 channel becomes a
filter input and **can no longer label future negatives**. The existing
negative set is now "spent" as a design input; re-measuring specificity needs
a fresh independent set — Tiers A1 (APOGEE-SB2), B (literature SB2), C
(resolved companions), or Gaia DR4 epoch RVs. Filter #29's 18/18 rejection of
the existing set is deterministic, not an independent re-measurement.

Two pytest regressions added (`test_regressions.py`):
`test_filter29_sb2_rejection_catches_hd76078`,
`test_filter29_no_headline_candidate_has_gaia_sb2`. 33/33 tests pass.

## What this means for the benchmark

- The **honest out-of-sample specificity of the v1.16.0 cascade (pre-#29)
  against SB2 imposters is 0.33** (Gaia-SB2 tier), CI 0.16–0.56 — report this
  *alongside*, not instead of, the leaky in-sample figure.
- The dominant false-positive channel was SB2 stellar binaries; Filter #29
  closes it.
- Specificity post-#29 cannot be claimed from this set (it's spent). DR4 is
  the natural large independent set for both recall and specificity
  re-measurement.

## Files
- `negative_control.csv` — the frozen 24-row set (provenance columns:
  gaia_dr3_id, in_pool, label_source, instrument, independence, M2_method,
  K1/K2, fp_tier, v2_verdict).
- `data/intermediate/tierA2_gaia_sb2_in_pool.csv` — 18 Gaia-SB2 negatives.
- `data/intermediate/tierA1_apogee_sb2_in_pool.csv` — 13 APOGEE matches
  (6 clean in-pool + 7 dropped coordinate artifacts).
- `scripts/build_negative_control_2026_05_17.py` — assembly + scoring.
- `scripts/pipeline_v11_sb2_filter_2026_05_17.py` — Filter #29.

## Note on the positive side (deferred)
The same independence flaw affects recall (~67 of 71 truth-set positives come
from Sahlmann, which the cascade consults). A fully clean *positive* set —
confirmed BDs with dynamical / directly-imaged masses from programs the
cascade doesn't use — is harder (such objects are rare). Pragmatic sequence
per the spec: specificity fixed now via this negative set; Gaia DR4 (Dec 2026)
serves as the large independent set for recall and probability calibration.

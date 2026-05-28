# Filter #31 proposal — paired check on `rv_amplitude_robust` + `rv_chisq_pvalue`

## The lesson

The A-dwarf candidate Gaia DR3 245948793944575360 emerged from the wider
hunt as a striking BH lead with apparent K_obs = 37 km/s matching the
predicted K_pred(i=90°) = 36.9 km/s exactly. I celebrated it as
"unique A-star + BH discovery class (HR 6819-style)" before performing
the standard sanity check on `rv_chisq_pvalue`.

The deep dive revealed:
- `rv_amplitude_robust` = 37.2 km/s
- `rv_chisq_pvalue` = **0.9989**
- `rv_renormalised_gof` = -3.16

A pvalue of 0.999 means the constant-RV model fits the time series
**better than expected by chance**. The "amplitude" is inflated by
single-epoch outliers (the source is in the galactic plane, b = -4°, with
heavy extinction A_0 = 1.67 mag — crowded-field RVS contamination is the
likely explanation).

The "perfect K_1 match at i=90°" was a coincidence between two unrelated
systematic effects:
1. The inflated astrometric M_2 (chromatic photocentric bias in a young
   A-dwarf with a debris disk — K-W4 = +1.3 mag confirms cool dust)
2. The inflated RV amplitude (single-epoch outliers in the RVS time series)

Both effects are real, neither is binary motion.

## The rule

**Filter #31: A cascade candidate's claim of an RV-confirmed companion
requires BOTH:**

1. `rv_amplitude_robust` ≥ 5 km/s  (substantial scatter)
2. `rv_chisq_pvalue` < 0.05  (constant-RV model rejected)
3. `rv_nb_transits` ≥ 10  (good statistics)

Additional sanity criteria (advisory, not blocking):
- `rv_renormalised_gof` ≥ 5 (model fits poorly, supporting non-constant)
- `radial_velocity_error` not abnormally large vs typical for Vmag

## Calibration on known cases

| Source | K_obs | pval | rgof | Filter #31 verdict | True nature |
|---|---:|---:|---:|---|---|
| HD 207141 | 31.5 | 0.0 | 57.4 | **PASS** | Real binary (cascade lead) |
| TYC 1363-2339-1 | 23.2 | 0.0 | 19.3 | **PASS** | Real binary (cascade lead) |
| 4 UMi (HIP 69112) | 26.3 | 0.0 | nan | PASS | Real binary (lit-confirmed SB1, but A/F secondary not BH) |
| Gaia 245948793944575360 (A-dwarf) | 37.2 | 0.9989 | -3.16 | **FAIL** | Not a real binary — disk + contamination |

**The 4 UMi case shows Filter #31 alone is necessary but not sufficient**
— it correctly accepts the real binary nature, but does not distinguish
luminous vs dark secondary. That's what Filter #30 (chromatic-bias
flag) and UV/IUE follow-up are for.

## What Filter #31 catches that Filter #29 doesn't

Filter #29 (Gaia SB2/SB2C rejection) only catches sources where the
secondary is bright enough to produce SB2 lines in Gaia DR3 NSS. The
A-dwarf case has no SB2 entry — the apparent binary is an artifact, not
a real binary at all, so it wouldn't be in any SB1/SB2 catalog. Filter
#31 catches this entire class of "phantom RV variability" that the SB2
filter has no way to know about.

## Implementation

```python
def filter_31(row):
    """row = Gaia DR3 source row with rv_amplitude_robust, rv_chisq_pvalue,
    rv_nb_transits."""
    K = row.get('rv_amplitude_robust')
    p = row.get('rv_chisq_pvalue')
    n = row.get('rv_nb_transits')
    if K is None or p is None: return 'NO_RV_DATA'
    if n is not None and n < 10: return 'LOW_N_TRANSITS'
    if K < 5: return 'TOO_LOW_AMPLITUDE'
    if p > 0.5: return 'FAIL_pvalue_too_high'
    if p > 0.05: return 'AMBIGUOUS'
    return 'PASS'
```

## Status

Applied in the 2026-05-27 parallel deep dive on 7 surviving top BH leads.
Results saved to `parallel_deep_dive_2026_05_27.csv`. The A-dwarf
candidate (already known failure) included as a reference case.

## Why this matters for the broader Gaia DR3 BH-hunting community

Andrews+ 2026 (arXiv:2603.20371) confirmed 0/31 of their RV-followup
sample, attributing failures to systematic biases. Filter #31 is a
**pre-RV-follow-up screen** that should be applied before committing
telescope time. It would have demoted the A-dwarf candidate to "young
A-dwarf with debris disk" *before* any RV proposal, saving the time and
preventing a tempting publication misstep.

Combined with Filter #30 (K-giant chromatic-bias), the cascade's
BH/NS verdict becomes substantially more robust:

- Filter #29 (existing): Gaia SB2/SB2C rejection
- Filter #30 (proposed): chromatic-bias flag (BP-RP > 1.2 OR log g < 2.7
  OR III/IV luminosity class) → "needs UV / IUE follow-up"
- Filter #31 (proposed): paired K_obs + pvalue check → "real binary
  vs artifact"

Together: a roughly community-standard pre-filter that mirrors the
Andrews+ 2026 recommendation for "more conservative significance / GOF
cuts" but operationalized at the source-classification level.

# Observing proposal sketch — TYC 1363-2339-1

*Draft for adaptation to specific TAC format. ~1 page.*

---

## Title

Confirming a dormant compact-object candidate in the NS/BH mass-gap:
radial-velocity follow-up of the Gaia DR3 NSS Orbital binary TYC 1363-2339-1

## Abstract

We propose ~12 radial-velocity epochs of the previously unstudied F-type
subgiant TYC 1363-2339-1 (V=9.9, Gaia DR3 666596383384888320,
TIC 17819651) over its 946-day orbital period. The Gaia DR3 NSS Orbital
solution yields an astrometric M₂ = 3.88 M☉ that agrees with M₂ = 3.94 M☉
derived independently from the Gaia DR3 RV amplitude at i = 60°. The
convergence at M₂ ≈ 3-4 M☉ places the companion in the NS/BH "mass gap"
with strong cross-method support. The target has **zero bibliographic
references on SIMBAD** and is not in any prior compact-object hunt — a
clean, near-circular, Northern-hemisphere lead.

## Scientific justification

Gaia DR3 enabled the first systematic astrometric hunt for dormant
compact companions (El-Badry 2023a, Shahaf+ 2023, Andrews+ 2023).
Follow-up by Andrews+ 2026 (arXiv:2603.20371) confirmed zero new BHs
from 31 candidates, attributing failures to systematic biases for
evolved/red-giant primaries. Our independent cascade pipeline applied
to the full Gaia DR3 NSS catalog identifies TYC 1363-2339-1 as a
distinct class:

1. The host is a *non-evolved* F-type subgiant (Teff=6797 K, log g=3.86,
   BP-RP=0.56), avoiding the K-giant chromatic photocentric bias
   calibrated against the HIP 69112/4 UMi literature ground truth.

2. Both astrometric and spectroscopic mass-function estimators converge
   at M₂ ≈ 3.9 M☉ at moderate inclination, placing the companion within
   the much-debated NS/BH "mass gap" (3-5 M☉).

3. The 946 d orbit is near-circular (e = 0.16), enabling clean RV phase
   coverage in a single observing season.

4. **Passes our new Filter #31** (paired K_obs + rv_chisq_pvalue check):
   rv_amplitude_robust = 23.2 km/s with rv_chisq_pvalue = 0.0 confirms
   real binary RV variability (vs the A-dwarf case where amplitude was
   inflated by outliers).

5. The host is essentially unstudied (zero SIMBAD bibliographic refs;
   spectral type unmeasured).

## Target list

| Target | α (J2000) | δ (J2000) | V | Sp type | P_orb | K_obs |
|---|---|---|---:|---|---:|---:|
| TYC 1363-2339-1 | 07:53:53.92 | +15:12:50.6 | 9.9 | F-subgiant | 946 d | 23 km/s |

## Observation strategy

- **Instrument**: HARPS-N (TNG, La Palma) preferred. Alternatives: FIES
  (NOT) or CARMENES (Calar Alto). All deliver ~1 m/s precision at V=9.9
  in 30 min exposure.
- **Cadence**: 12 epochs log-uniform over one orbital period (946 d).
- **Per-epoch S/N**: ~50 per resolution element in Mg b region.
- **Total time**: ~5 hr observing × 12 epochs = 60 hr with overheads.

## Deliverables

1. K₁ to ~3% precision
2. Locked orbital elements (e, ω, T_peri)
3. M₂ sin³i to ~5-10% precision
4. M₂ uncertain to ~10-15% with Gaia astrometric inclination prior

## Outcomes

- **M₂ > 3 M☉ confirmed**: first confirmed dormant compact discovery from
  a cascade-based Gaia DR3 candidate surviving independent literature
  filtering (Filters #29 + #30 + #31).
- **M₂ 1.5-3 M☉**: heavy NS or unusual stellar binary; refines NS-mass
  distribution at high-mass end.
- **M₂ < 1.5 M☉**: confirms a systematic bias class for F-subgiant hosts
  (joining K-giant calibration); publishable as methodology refinement.

Any outcome is publishable; the worst case is a calibration data point.

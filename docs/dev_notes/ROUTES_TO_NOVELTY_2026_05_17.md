# Routes to Novelty Discoveries — 2026-05-17 Audit

External-review-style question: what realistic paths exist to convert
any of our 10 headline candidates from "Tier 2 — novel in literature
catalogs" to "Tier 1 — confirmed novel substellar discovery"?

## Summary table

| Route | Effort | Probability | Timeline | Outcome this session |
|---|---|---|---|---|
| 1. Multi-archive RV mining | low | 30-50% | hours | **NEGATIVE** — 0 hits |
| 2. IR excess SED check | low | 10-20% | hours | **NEGATIVE** — no excess |
| 3. New RV proposal | medium | 40-50% acceptance | 6-12 months | Not pursued (telescope proposal) |
| 4. Wait for DR4 | zero | 100% (DEFINITIVE @ SNR>30) | 7 months | Recommended default |
| 5. Methodology paper | medium | high acceptance | weeks | Alternative pursuit |

## Route 1 — Multi-archive RV mining (NEGATIVE)

Queried Vizier TAP for visit-level RV time-series across:

- APOGEE DR17 (III/284/allvis) — 1.4M near-IR RV visits
- RAVE DR6 (III/283/*) — 0.5M optical RV measurements
- GALAH DR3/DR4 (J/A+A/673/A155/galahdr3) — 600K RV observations
- LAMOST DR8/DR10 various — 11M low-resolution spectra with RV
- HARPS RVBank Trifonov+2020 (J/A+A/636/A74) — not reachable via Vizier
- HIRES Levy 2025 — out of Vizier scope

For all 10 candidates and a 5″ cone-search radius: **zero archival
RV time-series in any of these catalogs.** The candidates sit in the
gap between targeted-RV samples (which preferentially observed bright
HD planet-host samples) and survey samples (RAVE/GALAH all-sky but
typically southern or red).

**Implication**: Archival RV mining cannot confirm any of our 10. The
discovery path requires new RV observations OR DR4.

## Route 2 — Infrared excess SED check (NEGATIVE)

For each candidate, fetched 2MASS J/H/Ks and WISE W1/W2 photometry
within 10″ of the Gaia DR3 coord, then compared the V-W1 color
against Pecaut & Mamajek 2013 main-sequence expectations.

Results for the candidates with successful cross-matches:

| Candidate | V | K | W1 | V-W1 | Expected (SpT) | Δ | Verdict |
|---|---|---|---|---|---|---|---|
| **HD 76078** | 8.72 | 7.33 | 7.25 | 1.47 | 1.74 (G5) | -0.26 | normal (slightly blue) |
| **BD+56 1762** | 10.03 | 8.11 | 8.05 | 1.98 | 1.77 (G5/G7) | +0.21 | normal (slightly red) |

The other 8 candidates failed cross-matching in the 60″ box, mostly
due to high proper motion shifting 2MASS/WISE epoch positions away
from the Gaia DR3 frame. A proper PM-corrected cross-match would
recover them, but the IR excess interpretation requires careful
extinction-corrected SED fitting — beyond a quick screen.

**Physical reason for the null result**: substellar companions
(13-80 M_J) at the orbital separations indicated by the cascade
(< 5 AU, P < 4 yr) emit < 1e-5 of the host's flux in IR. At
WISE sensitivity (~ 0.05 mag photometric precision), this is far
below detection. IR excess could only detect very young (< 10 Myr),
very wide BD companions, which is not the population we're searching
for.

**Implication**: IR excess is not a viable discovery channel for
the 10 candidates as configured.

## Route 3 — Targeted RV proposal

Per v1.14.0 jitter analysis, every candidate has K/σ_jitter > 100.
A single quadrature RV epoch at TRES (σ ~ 30 m/s) gives SNR > 60 on
K_orbital. Five epochs across orbital phase gives full Keplerian
recovery.

**Recommended single-target proposal**: BD+56 1762

- V = 10.03 (TRES easy)
- P = 197 d (4 quadratures per year)
- Predicted K_orbital = 2,099 m/s (Gaussian-process-correctable activity ~ 15 m/s)
- Currently no Gaia RVS time-series, no Halbwachs DPAC fit, no Sahlmann list entry — wide-open novelty profile

A 4-month TRES campaign (5 epochs at 30 m/s) costs ~10 hours of
allocated time. **TAC outcome**: 6-12 month timeline pending
proposal cycle.

## Route 4 — Wait for Gaia DR4 (recommended default)

Per v1.13.0 forecast, every NSS-Orbital candidate hits DR4_DEFINITIVE
at SNR > 30 on K_orbital from the per-transit RV release. Timeline:
~7 months from now (December 2026).

**Drawback**: anyone with the same DR3 candidate list can also do
this. The repository's advantage is the curation + verification work
(four-channel evidence per candidate), not exclusive access to the
data.

## Route 5 — Methodology paper (parallel path)

The repository contains several publishable methodology contributions
that don't depend on a discovery:

1. The Filter #28 silent-failure exposure (v1.8.0) — anyone running
   a similar Gaia DR3 NSS workflow may have the same bug
2. The independent 25-yr PMa calculation from raw catalogs (v1.11.0)
3. The four-channel verification framework (NSS + HGCA + independent
   PMa + TESS)
4. The no-HIP frontier as a structural limit (v1.10.0)
5. The Aigrain FF' activity-jitter quantification per candidate (v1.14.0)
6. The cascade test suite (this commit) preventing future regressions

Combined, this is RNAAS-grade or A&A Letters-grade methodology work
that is not gated on confirming any individual candidate.

## Conclusion

**There is no realistic path to a confirmed Tier 1 novel discovery
this session.** The repository has done what's possible with DR3 +
archival data alone. Beyond this point, novelty discovery requires
either telescope time or patience for DR4.

The most leverage-efficient next move is the methodology paper
(Route 5), which converts the accumulated work into a citable
publication regardless of whether DR4 ends up confirming the
candidates.

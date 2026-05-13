# New candidate pool vetting (2026-05-13)

Full vetting cascade applied to the 98 candidates surfaced by the
expansion audit (37 AstroSpectroSB1 + 61 SB1+Kervella hierarchical-triple).

## Filter cascade

| Stage | Filter | Removed | Survivors |
|---|---|---:|---:|
| 0 | input pool | — | 98 |
| 1 | Gaia DR3 documented-FP (cosmos.esa.int) | 0 | 98 |
| 2 | NASA Exo gaia_dr3_id cross-match | 0 | 98 |
| 3 | exoplanet.eu coord match (30 arcsec) | 10 | 88 |
| 4 | Sahlmann 2025 ML imposter verdict | 0 | 88 |
| 5 | Gaia DR3 quality + Bayesian-style score | 61 (TIER3 weak/marginal) | 27 |
| 6 | SB9 spectroscopic binary catalog (Pourbaix) | 0 | 27 |

**Note**: Stage 3 caught 10 published planet hosts that NASA Exo PS doesn't list (8 within 5 arcsec, 1 at 24 arcsec false-positive). Genuine exoplanet.eu-only published systems include HIP 117179 b, HD 115517 b, HD 156312 Bb, HIP 75202 Ab, TYC 8321-266-1 b, etc.

## 27 surviving candidates by final tier

### TIER 1A — AstroSpectroSB1 + HIP cross-id (highest confidence)

**1 candidate**: directly-constrained sin(i) **and** HIP-catalogued host.

| Source ID | HIP | P (d) | e | M₂ (M_J) | RUWE | sig |
|---|---:|---:|---:|---:|---:|---:|
| 4539057576001089408 | 91479 (LP 335-104) | 856 | 0.81 | 79.4 | 4.11 | 32.2 |

Highly eccentric, long-period, mass-marginalized at the substellar/stellar boundary. Originally LP catalog (Luyten Proper-Motion star) so high-proper-motion host. Strongest single candidate from this pool.

### TIER 1B — AstroSpectroSB1 anonymous (sin i constrained, no HIP)

**2 candidates**: directly-constrained sin(i) but anonymous Gaia DR3 sources without independent literature.

| Source ID | P (d) | e | M₂ (M_J) | G | RUWE | sig |
|---|---:|---:|---:|---:|---:|---:|
| 5302774543705601920 | 484 | 0.25 | — | 10.96 | 3.78 | 76.8 |
| 1398115488116027264 | 290 | 0.38 | — | 10.27 | 2.56 | 30.9 |

Faint anonymous targets; would need new SIMBAD/literature lookup once SIMBAD service is reachable.

### TIER 2A — SB1+Kervella clean + HIP (hierarchical triple, clean PSF)

**4 candidates**: SB1 inner orbit + Kervella PMa excess + HIP cross-id + RUWE < 2 + ipd_frac = 0.

| Source ID | HIP | P_inner (d) | e | M₂ sini (M_J) | G | RUWE | sig |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4878577214643322880 | 21449 | 37.8 | 0.04 | 42.0 | 8.74 | 0.90 | 28.1 |
| 6459416790670371712 | 105567 | 76.4 | 0.24 | 48.3 | 7.55 | 1.17 | 27.2 |
| 488408360758121856 | 17154 | 107.5 | 0.26 | 23.6 | 8.23 | 1.16 | 27.0 |
| 5428084706405323648 | 44680 | 66.3 | 0.06 | — | 8.44 | 1.11 | 22.3 |

These are bright HIP stars (V ≈ 8–9) with inner short-period BD candidate companions AND independent Kervella PMa long-baseline arc evidence for an outer body. Hierarchical triple candidates.

### TIER 2C — surviving but weaker

**20 candidates**: lower-significance AstroSpectroSB1 or SB1+Kervella with quality concerns. Listed in `final_27_tiered.csv` for completeness.

## Verification gaps acknowledged

- **SIMBAD service was unreachable** during this audit (TAP + CGI both timing out). Standard SIMBAD object_type checks (SB\*, EB\*, \*\*, WDS J\*) were not completed. This is the highest-priority follow-up vetting step when SIMBAD comes back online.
- **Vizier WDS B/wds/wds table** also returned HTTP 400 (column-name issue); deferred.
- **HD/HIP name lookups for the 9 HIP-cross-matched candidates** would benefit from a fresh ADS bibcode count to surface any 2024-2026 papers.

## Net effect on candidate inventory

| Category | Pre-audit | Post-audit (this session) | Tier-1+2A new |
|---|---:|---:|---:|
| Primary substellar tentatives (novelty_candidates.csv) | 8 | 8 (unchanged) | 0 |
| AstroSpectroSB1 supplementary pool | 37 | 37 surviving | 3 (TIER 1A+1B) |
| SB1+Kervella supplementary pool | 61 | 61 surviving | 4 (TIER 2A) |
| Total tracked | 98 → 8 primary + 90 supplementary | 7 high-confidence + 20 weak + 10 published | — |

**7 new high-confidence candidates surfaced** (1 TIER 1A + 2 TIER 1B + 4 TIER 2A) ready for individual deep-dive once SIMBAD/WDS access is restored.

## Files

- `pool_master.csv` — all 98 candidates with full filter annotations
- `pool_survivors_ranked.csv` — 88 surviving (post-exoplanet.eu filter)
- `top27_vetted.csv` — 27 TIER1+TIER2 with SIMBAD attempt (SIMBAD service outage; columns empty)
- `final_27_tiered.csv` — 27 candidates organized by final tier (1A / 1B / 2A / 2C)

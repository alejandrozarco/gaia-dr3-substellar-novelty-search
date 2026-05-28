# Top defensible dormant-compact-object leads — consolidated (post-Filter #31)

*Updated after 2026-05-27 parallel deep dive applying Filter #31.*

## After applying all three filters (#29, #30, #31)

| Rank | Designation | V/G | Class | Host | sig | P_d | e | M_2 joint | Filter #31 | IR | SIMBAD refs | Tier |
|---:|---|---:|---|---|---:|---:|---:|---|---|---|---:|---|
| **1** | **TYC 1363-2339-1** | 9.90 | BH | F-subgiant | 32 | 946 | 0.16 | **3-4 M_sun** | **PASS** | Clean | **0** | inaugural |
| **2** | **HD 207141** | 8.72 | BH | F-subgiant | 95 | 952 | 0.66 | **4.5-6 M_sun** | **PASS** | Clean | 5 | second target |
| 3 | TYC 8785-1657-1 | 10.81 | BH | F-subgiant | 64 | 491 | 0.27 | 3-4 M_sun | PASS | W4 excess | 0 | needs W4 deconfusion |
| 4 | Gaia 2801267044426382336 | 12.59 | BH | F-subgiant | 85 | 750 | 0.06 | 6.6-9 M_sun | PASS | W4 excess | 0 | needs W4 deconfusion |
| 5+ | (pending Filter #31 confirmation) | | | | | | | | | | | |
| DEMOTED | Gaia 245948793944575360 (A-dwarf) | 11.80 | — | A-dwarf | 48 | 549 | 0.06 | n/a | **FAIL** | EXCESS | none | phantom RV variability |
| DEMOTED | 4 UMi (HIP 69112) | 4.80 | — | K3-IIIb | 54 | 618 | 0.28 | 1.7 (lit) | PASS | n/a | known SB1 | calibration only |

## The two cleanly-surviving leads

### #1 TYC 1363-2339-1
- F-subgiant (Teff=6797, log g=3.86, M_1=1.88 M_sun, R=3.16 R_sun)
- d = 461 pc (Bailer-Jones), b = +20° (above plane), clean field
- NSS Orbital P=946 d, e=0.16, sig=32, K_obs=23.2 km/s
- Filter #31: PASS (rv_chisq_pvalue=0.0, rv_renormalised_gof=19.3)
- IR: K-W3=0.06 (clean), K-W4=0.29 (clean)
- 0 SIMBAD bibliographic refs; only TYC/TIC/2MASS catalog IDs
- Northern hemisphere (Dec=+15°), HARPS-N / FIES accessible
- Astrometric and RV M_2 converge: 3.88 (astrom) vs 3.94 (RV i=60°)

**Recommended inaugural RV target** — see `observing_proposal_sketch_TYC_1363-2339-1.md`.

### #2 HD 207141
- F-subgiant (Teff=6041, log g=2.90, M_1=2.60 M_sun, R=8.2 R_sun, L=83 L_sun)
- d = 599 pc (Bailer-Jones), b = -49° (high lat), clean field
- NSS Orbital P=952 d, e=0.66, sig=95, K_obs=31.5 km/s
- Filter #31: PASS (rv_chisq_pvalue=0.0, rv_renormalised_gof=57.4)
- IR: K-W3=0.03 (clean), K-W4=-0.11 (clean)
- 5 SIMBAD references (none about binarity)
- Southern hemisphere (Dec=-26°), FEROS / CHIRON / PFS accessible
- Astrometric M_2 = 7.57 vs RV at i=60° = 4.74 → joint range 4.5-6 M_sun

**Recommended secondary target** — see `HD207141_deep_dive_2026_05_27.md`.

## The two W4-excess candidates (uncertain status)

### #3 TYC 8785-1657-1
- F-subgiant (Teff=6208, log g=3.78, M_1=1.63)
- d = 552 pc, b = -34°, clean field
- NSS Orbital P=491 d, e=0.27, sig=64, K_obs=28.6 km/s
- Filter #31: PASS
- IR: K-W3=0.02 (clean) but **K-W4=1.31 (excess)**
- 0 SIMBAD refs

The K-W4-only excess pattern is suspicious. Possible explanations:
1. Cold debris disk (would not affect binary M_2 estimate)
2. Background source within the 12" W4 PSF
3. Hidden cool companion (M-dwarf) — but K-W3 should also show excess

**Investigation needed**: high-resolution mid-IR (Spitzer / JWST) or
deeper survey at intermediate wavelengths.

### #4 Gaia 2801267044426382336
- F-subgiant (Teff=5861, log g=3.82, M_1=1.54)
- d = 1143 pc, b = -43°, clean field
- NSS Orbital P=750 d, e=0.06 (near-circular), sig=85, K_obs=38.3 km/s
- Filter #31: PASS (rv_chisq_pvalue=1.5e-14, very significant)
- IR: K-W3=-0.04 (clean) but **K-W4=1.89 (excess)**
- 0 SIMBAD refs

Same W4-only excess concern. Higher significance (sig=85) than
TYC 8785, M_2 implied = 6.6-9 M_sun. Worth chasing pending W4 resolution.

## Why this differs from the v1.22 list before the 2026-05-27 reanalysis

In the v1.21/v1.22 headline, I (in retrospect, incorrectly) ranked the
A-dwarf Gaia 245948793944575360 as Tier-1 lead #2 ("UNIQUE A-star + BH
discovery class"). The 2026-05-27 deep dive revealed the K_1 signal was
not real (Filter #31 fail). That candidate is now demoted to a
"young A-dwarf with debris disk and possibly an unresolved cool
companion" — interesting in its own right but NOT a BH candidate.

Similarly, the deep dive surfaced the K-W4 excess pattern for #3 and #4,
which were enthusiastically promoted in v1.22 but now require
disambiguation.

The cleanest leads survive: TYC 1363-2339-1 (top) and HD 207141 (#2).

## Recommendation when user returns

Pick one of:
- **(a) Confirm TYC 1363-2339-1 via RV** (HARPS-N or FIES, 12 epochs over
  946d, observing proposal sketch ready)
- **(b) Push the methodology paper** (4 UMi + K-giant filter + A-dwarf
  Filter #31 calibration + Andrews+ 2026 alignment — no telescope time
  required, currently the most concrete publication)
- **(c) Regenerate the lost CSVs** so the broader candidate analysis
  is reproducible (run companions_hunt, wider_hunt, atnf, pn_central_binary,
  sb2_negative_recovery scripts in sequence; ~30 min compute)
- **(d) Submit a community email** announcing the K-giant filter +
  Filter #31 findings ahead of formal paper, since they're directly
  community-relevant for Gaia DR3 BH hunting

(a) and (b) are concurrent; (c) is independent and can run in background.

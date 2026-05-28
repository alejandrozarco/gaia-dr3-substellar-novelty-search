# Companions-of-all-kinds pivot — BH/NS hunt + multi-class test sets (2026-05-18, recovered 2026-05-27)

*Reconstructed from chat transcript after `/tmp/gaia-fresh` was wiped.
Some script content reproduced from memory; raw CSV outputs need regeneration.*

## The pivot

The cascade was originally framed for substellar companions (BD/planet
mass tail). The reframe: **same architecture, applied to the entire M_2
distribution.** The Gaia DR3 NSS Orbital + AstroSpectroSB1 tables encode
*all* close-orbit unresolved companions visible through astrometric wobble,
regardless of secondary mass. Classify candidates by their derived M_2 and
their SB2 status:

| Class | M_2 range | SB2 status | Detection signature |
|---|---|---|---|
| Dormant BH candidate | ≥ 3.0 M_sun | No SB2 | High-significance Orbital fit, dark heavy companion |
| Dormant NS candidate | 1.2-3.0 M_sun | No SB2 | Same but lighter |
| Stellar BH-imposter | ≥ 3.0 M_sun | Yes SB2 | High mass + luminous secondary = HMXB-like or fit artifact |
| WD or low-mass star | 0.5-1.4 M_sun | Either | Common; needs follow-up to disambiguate WD vs M dwarf |
| M-dwarf companion | 0.08-0.5 M_sun | Either | Bulk stellar binaries; validation regime |
| BD candidate | 0.013-0.08 M_sun | No SB2 | The original substellar problem |
| Planet candidate | < 0.013 M_sun | No SB2 | Sub-deuterium burning |

## Methodology validation (done)

Computed M_2 from Gaia DR3 NSS Thiele-Innes constants + parallax for the
3 confirmed Gaia BHs:

| Object | NSS solution | P_DR3 | a_phot (mas) | M_2 recovered | Lit M_BH |
|---|---|---:|---:|---:|---:|
| Gaia BH1 | Orbital | 185.8 d | 2.98 | 13.19 M_sun | 9.62 |
| Gaia BH2 | AstroSpectroSB1 | 1352 d | 3.88 | 15.98 M_sun | 8.94 |
| Gaia BH3 | — | — | — | (not in NSS, P > DR3 baseline) | 32.7 |

The methodology recovers both Gaia-published BHs as M_2 ≫ 3 M_sun. The
astrometry-only mass estimates overestimate the joint-fit literature values
by ~40-80% — expected, because weak inclination constraints in Gaia-only
fits inflate the implied mass.

## Hunt results

Original hunt (sig≥12, P 100-3000d, parallax≥1, G<13, a_thiele_innes NOT NULL)
returned 56,187 NSS Orbital + AstroSpectroSB1 sources. After M_2 derivation:

| Class | Hunt count |
|---|---:|
| M-dwarf companion | 32,299 |
| WD or low-mass star | 22,428 |
| Dormant NS candidate | 1,222 |
| BD candidate | 196 |
| **Dormant BH candidate** | **38** |
| Planet candidate | 3 |
| Stellar overflow (SB2 ≥ 1.2 M_sun) | 1 |

After defensibility cuts (sig ≥ 30, RUWE < 10 for BH / < 5 for NS,
parallax ≥ 1.5 mas):

| Class | Defensible count |
|---|---:|
| BH | 12 |
| NS | 153 |

## Why Gaia BH1/BH2/BH3 are absent from the original hunt's output

- BH1: G = 13.77 → excluded by G < 13 cut
- BH2: parallax = 0.67 mas → excluded by parallax ≥ 1.0 mas cut
- BH3: not in NSS at all (P > DR3 baseline)

The wider 2nd-pass hunt (G<14, parallax≥0.5, sig≥30) recovered BH2 at
M_2 = 18.31 vs lit 8.94 — confirms ~2× chromatic bias factor.

## SIMBAD cross-check of top BH candidates (the surprise)

8/9 are already-catalogued, mostly flagged "SB*":

| Gaia DR3 | SIMBAD | otype | V | sig | M_2 |
|---|---|---|---:|---:|---:|
| 692538600029976064 | BD+27 1683 | SB* (F8) | 9.46 | 191 | 10.20 |
| 6696544512063546624 | CD-34 14408 | SB* | 10.5 | 123 | 3.28 |
| 6811355413155399040 | HD 207141 | * (F5V) | 8.88 | 95 | 7.57 |
| 4433039709908858496 | HD 147132 | SB* (G6IV/V) | 8.97 | 76 | 3.28 |
| 4277855016732107520 | TYC 436-126-1 | * | 11.41 | 75 | 13.66 |
| 6471824298353396736 | TYC 8785-1657-1 | SB* | 10.93 | 64 | 3.63 |
| 4161201712124704128 | HD 169134 | SB* (K5) | 8.81 | 56 | 3.15 |
| 3868256247828634112 | — | — | — | 54 | 3.23 |
| **1714135092946125184** | ***4 UMi*** | **SB* (K3-IIIb Fe-0.5)** | **4.80** | 54 | 4.09 |

## K_1 reality check (cull from 9 to 3)

Compare observed `rv_amplitude_robust` to K_1 predicted from cascade M_2:

| Name | sig | M_1 | M_2 | K(i=90°) | K(i=60°) | K(i=30°) | Obs K | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| BD+27 1683 | 191 | 1.58 | 10.20 | 50.9 | 44.1 | 25.4 | 6.8 | FALSE POSITIVE |
| CD-34 14408 | 123 | 2.10 | 3.28 | 26.9 | 23.3 | 13.5 | 33.4 | M_2 may be UNDERestimated |
| HD 207141 | 95 | 2.60 | 7.57 | 46.7 | 40.4 | 23.4 | 31.5 | CONSISTENT |
| HD 147132 | 76 | 2.45 | 3.28 | 35.0 | 30.3 | 17.5 | 11.2 | Overestimated or face-on |
| TYC 436-126-1 | 75 | 1.70 | 13.66 | 66.7 | 57.8 | 33.4 | 4.9 | FALSE POSITIVE |
| TYC 8785-1657 | 64 | 1.63 | 3.63 | 33.6 | 29.1 | 16.8 | 28.6 | CONSISTENT |
| HD 169134 | 56 | 1.00 | 3.15 | 28.5 | 24.7 | 14.2 | 5.7 | Likely overestimated |
| (unnamed) | 54 | 1.00 | 3.23 | 28.8 | 25.0 | 14.4 | 9.0 | No significant RV variability |
| **4 UMi** | 54 | 5.21 | 4.09 | 24.1 | 20.9 | 12.0 | 26.3 | CONSISTENT (but see literature ↓) |

## 4 UMi literature verdict (NEGATIVE)

**Pourbaix & Boffin 2003 (A&A 398, 1163)** on HIP 69112:
- M_1 = 2.5 ± 0.5 M_sun, M_2 ≈ 1.7 M_sun (q ≈ 0.7), i ≈ 46° from plane
- Companion: late A — early F main sequence
- **Unpublished IUE UV observations directly detect the late-A/F companion**

**Wikipedia / SIMBAD**: SB1, P = 605.8 d (matches Gaia 618 d to 2%),
K_1 = 12.65 ± 0.16 km/s.

**Verdict: 4 UMi is NOT a dormant BH/NS host.** Known SB1 with
IUE-confirmed late-A/F secondary. Calibration data point for chromatic
bias correction.

### Calibration result: photocentric a_0 inflated 2× for red-giant hosts

| Quantity | This work (cascade) | Literature-implied | Bias factor |
|---|---:|---:|---:|
| Photocentric a_0 | 5.67 mas | 2.88 mas | **2.0×** |
| M_2 (M_1=2.5, i=46°) | 4.87 M_sun | 1.70 M_sun | **2.9×** |

The 2× a_0 inflation is the root cause of the 2.9× M_2 overestimate.
Chromatic photocentric bias for K-giant hosts.

**Proposed Filter #30**: demote any cascade BH/NS candidate where the host
has BP-RP > 1.2 OR FLAME log g < 2.7 OR III/IV spectral classification.

## Community context: Andrews+ 2026 (arXiv 2603.20371)

Independent RV follow-up of 31 Gaia DR3 NSS BH/NS candidates. **Found ZERO
new confirmed BHs.** Only one new ~1.16 M_sun NS-or-massive-WD candidate.
Recommends more conservative significance / GOF cuts — aligned with our
calibration finding.

## K-giant SB1 false-positive class (generalized 4 UMi)

SIMBAD lookup on the 15 brightest defensible NS candidates (G < 7.5)
returned: **15/15 are already-classified K-giant SB1s**, all with HD/HIP:

| Gaia DR3 sig | G | M_2_cascade | SIMBAD | otype | Sp |
|---:|---:|---:|---|---|---|
| 117 | 7.43 | 1.65 | HD 18220 | SB* | K2III |
| 110 | 5.41 | 2.24 | **48 Psc** | SB* | K5III |
| 98 | 6.49 | 1.49 | HD 213882 | SB* | K0III |
| 78 | 6.91 | 1.69 | HD 83214 | SB* | K4/5III |
| 78 | 7.33 | 1.26 | HD 25040 | SB* | G8/K0III |
| 77 | 7.03 | 1.33 | HD 199869 | SB* | K5 |
| 76 | 7.29 | 2.58 | HD 198270 | SB* | K5 |
| 66 | 6.79 | 1.41 | HD 21577 | SB* | K0 |
| 64 | 7.22 | 1.27 | HD 68730 | SB* | K0III |
| 62 | 7.40 | 1.64 | BD+41 4622 | SB* | K2 |
| 59 | 7.05 | 1.26 | HD 183629 | SB* | K0III |
| 51 | 7.36 | 1.29 | HD 121623 | SB* | K0 |
| 49 | 7.36 | 1.57 | HD 197962 | SB* | K5 |
| 47 | 7.14 | 2.85 | **HD 65186** | SB* | **K3III + A/F** (composite!) |
| 47 | 6.67 | 1.24 | HD 91869 | SB* | G8/K0III |

Same chromatic-bias pattern. HD 65186 is published as K3III + A/F composite
— literal SB1+luminous secondary — the cascade still flagged it as a
2.85 M_sun NS candidate.

## ML classifier — held-out-M2 test

RandomForest CV with M_2 + fM held out (10k-row subsample):

| Class | Precision | Recall |
|---|---:|---:|
| BD_candidate | 1.000 | **0.028** |
| M_dwarf_companion | 0.839 | 0.901 |
| WD_or_low_mass_star | 0.807 | 0.767 |
| dormant_NS_candidate | 0.911 | 0.217 |

**Only 1 of 36 BD candidates recoverable from non-M_2 features.** The
cascade's BD verdict is essentially threshold-on-M_2 — confirms the
overfitting concern. Feature importance: parallax (0.25), M_1 (0.18),
a_phot (0.17), P (0.11), RUWE (0.09).

Of 18 SB2 leak-free negatives, 6 are in the hunt pool; 3 are classified as
"BD" by the hunt's mass-class function. **None of them appear in v1.19+
headline** — Filter #29 catches all 3. So the cascade adds real specificity
beyond mass-class function (196 hunt-BD → 3 headline = 1.5% pass rate).

## Wider hunt — 13 NEW BH candidates (G<14, plx>=0.5, sig>=30)

51,409 sources; 13 new BH candidates not in original hunt, no SB2,
after chromatic-bias filter:

Top 4 with K_1 reality check:

| Gaia DR3 | G | Sp/host | sig | P | M_2 cascade | K_obs | K_pred(90°) | Verdict |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 2801267044426382336 | 12.59 | F-subgiant | 85 | 750 | 6.95 | 38.3 | 39.2 | PERFECT i=90° match |
| 245948793944575360 | 11.80 | **A-dwarf** Teff=9001 | 48 | 549 | 6.05 | 37.2 | 36.9 | (FAILED Filter #31 - see below) |
| 3586834017613414784 | 12.47 | F-dwarf | 71 | 592 | 9.90 | 41.4 | 49.7 | fits i~75°, M_2~8 |
| 5889532732877344128 | 12.67 | F-subgiant | 45 | 896 | 3.33 | 53.9 | 27.8 | M_2 UNDERestimated, true ≥13 M_sun |

Gaia BH2 also recovered: M_2=18.31 (vs lit 8.94, 2.05× bias — confirms
calibration).

## A-dwarf candidate FAILURE (2026-05-27 deep dive)

Gaia DR3 245948793944575360 was the most striking lead but **failed
Filter #31**:

- rv_amplitude_robust = 37.2 km/s (looks like a real K_1 = K_pred(90°)=36.9)
- **rv_chisq_pvalue = 0.9989 — constant-RV model fits well**
- rv_renormalised_gof = -3.16 (negative — model overfits)
- ⇒ amplitude inflated by single-epoch outliers, NOT real binary motion
- IR excess K-W3 = 0.22, K-W4 = 1.31 — disk or cool companion signature
- A_0 = 1.67 (heavy galactic-plane extinction)
- Distance disagreement: parallax 1365 pc vs gspphot 670 pc

Demoted from Tier 1 BH lead to "young A-dwarf with debris disk / unresolved
cool companion".

## Filter #31 proposal (new)

**Paired check of rv_amplitude_robust AND rv_chisq_pvalue.**

Real binary RV signal:
- rv_amplitude_robust > 5 km/s (substantial scatter)
- rv_chisq_pvalue < 0.05 (constant-RV model rejected)

Both conditions must hold. The A-dwarf candidate fails because pvalue=0.999
proves the amplitude is from outliers, not signal. HD 207141 (pvalue=0.0)
and TYC 1363-2339-1 (pvalue=0.0) pass — real RV variability.

## Test sets assembled (leak-free positive labels)

| Class | Catalog | Count |
|---|---|---:|
| Substellar pulsar companions | ATNF B/psr medM<0.05 M_sun | **37** |
| M-dwarf pulsar companions | ATNF 0.08≤medM<0.5 | 154 |
| WD pulsar companions | ATNF 0.5≤medM<1.4 | 36 |
| NS-NS binaries | ATNF 1.2≤medM<3 | 14 |
| BH-mass pulsar comp (HMXB) | ATNF medM≥3 | 5 |
| PN central binaries | Curated (Ou 5 family) | 28 |
| Gaia confirmed BHs | BH1/2/3 + literature | 5 |
| WD-MS post-CE | Rebassa-Mansergas | thousands (mostly V>14) |
| EB mass calibration | DEBCat | 50 |
| SB2 stellar negatives | Tier A2 Gaia DR3 SB2/SB2C ∩ v2 pool | 18 |

Cumulative ~400 leak-free labels — crosses the "several-hundred" ML
training threshold.

## Substellar BD list (v1.18) — K-giant filter findings

Applied chromatic-bias filter to 32 v1.18 BD candidates:

- HD 134574 (G8III, R=6.5 R_sun): M_2 = 29 MJ → corrected ~15 MJ (still BD)
- HD 15405 (log g=2.48, R=10.3 R_sun): M_2 = 14 MJ → corrected ~7 MJ
  (could fall into planet-mass)

11 other v1.18 BD candidates flagged via BP-RP > 1.2 are M-dwarf primaries
(not K-giants) — chromatic bias mechanism doesn't apply, they likely OK.

## Final headline state (v1.22, before A-dwarf demotion)

| companion_class | count |
|---|---:|
| substellar_BD | 32 (unchanged from v1.18) |
| dormant_BH_candidate | 10 |
| dormant_NS_candidate | 3 |

After A-dwarf demotion (v1.23): 9 BH + 3 NS + 32 BD = 44 candidates.

## Top defensible BH leads (after Filter #29 + #30 + #31)

| Rank | Source | V | sig | M_2 joint | Why surviving |
|---:|---|---:|---:|---|---|
| **1** | **TYC 1363-2339-1** | 9.90 | 32 | 3-4 M_sun | F-subgiant, zero SIMBAD, K_1 clean, e=0.16 circular |
| **2** | **HD 207141** | 8.72 | 95 | 4.5-6 M_sun | F-subgiant, 5 SIMBAD refs, K_1 clean, no IR excess |
| 3 | Gaia 2801267044426382336 | 12.59 | 85 | ~7 M_sun | F-subgiant, perfect K_1 match (PENDING Filter #31) |
| 4 | Gaia 5889532732877344128 | 12.67 | 45 | ~13 M_sun | F-subgiant, M_2 underestimated (PENDING #31) |
| 5 | TYC 8785-1657-1 | 10.81 | 64 | 3-4 M_sun | F-subgiant, no HD/HIP (PENDING #31) |

(Pending Filter #31 confirmations: parallel deep-dive script running.)

## What's next

1. Confirm Filter #31 application to all 7 surviving leads
2. RV follow-up campaign on top survivor (TYC 1363-2339-1 still most likely)
3. Methodology paper: Filter #30 (K-giant chromatic bias) + Filter #31
   (pvalue check) calibrated against 4 UMi + A-dwarf failures + Andrews+2026
4. ML classifier rerun with full leak-free labels + cross-matched Gaia
   features (after lost CSVs regenerated)

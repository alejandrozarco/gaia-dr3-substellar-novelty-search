# Exotic white dwarf atmospheres in SDSS-V DR20 (2026-09-24)

A fan-out agent ran this lane and was stopped by the session limit before it finished. The main thread reviewed and integrated the partial outputs.
Spectra: SDSS-V DR20 Astra 0.8.1 mwmStar coadds, with mwmVisit spectra where the check needed them. The XCSAO rest-frame shift is undone for in-stack visits.

## Sub-screens
1. **Balmer emission (DAHe):** 3,214 SnowWhite white dwarfs on the DAHe locus. A local-bump metric with a self-calibrated noise model runs over the H-alpha and H-beta windows (`scripts/emis2.py`, `scripts/run_screen2.py`).
   - Injection test with linear-Zeeman emission triplets (`scripts/inject.py`, `data/injection_results_v2.csv`). At B = 10 MG the recovery rates are:

     | S/N band | A = 0.03 | A = 0.05 | A = 0.08 | A = 0.12 |
     |---|---|---|---|---|
     | S/N > 40 | 8% | 42% | 83% | 92% |
     | S/N 20-40 | 0% | 8% | 29% | 76% |

   - Result: no new DAHe. The known DAHe J1437+0309 is recovered. J1616+5410 is not: its emission is weak in the SDSS-V coadd.
2. **Absorption classes:** 186 spectra ranked by SnowWhite probabilities for rarer classes (hot DQ, DQ, DQpec, DBH, DZ and similar), inspected visually (`plots/AB_p*.png` not kept; notes in `data/visual_notes.md`). Known controls: DQ, DQpec, DBH, DZH and DQH objects.
3. **Hot-DQ locus:** 95 objects with -0.55 < BP-RP < -0.2 and 11.3 < M_G < 12.8, not classified DA by SnowWhite, S/N > 6.

## Novelty gate (`scripts/gate.py`, `scripts/ads_alias.py`, `scripts/srcgrep.py`)
- SIMBAD identifiers, types and references.
- VizieR all-table cone.
- DESI DR1 spectrum existence and LAMOST DR10.
- MWDD `table.json`.
- ADS full text by every alias.
- Source grep of 55 arXiv papers on DQ, hot-DQ, DAQ, massive-WD and merger-remnant spectroscopy (list in `data/srcgrep_results_v2.json`). The grep includes Dufour+2008, Coutu+2019, Kilic+2023/2024/2025 (DAQ subclass; all-sky merger-remnant survey; 100 pc SDSS II), Jewett+2024, García-Zamora+2026, Vincent+2024 (XP), Manser+2024 (DESI EDR) and the DESI DR1 model-atmosphere analyses.

## Candidates (`data/cand_list.txt`)

| Gaia DR3 | G | BP-RP | M_G | spectrum | prior classification | verdict |
|---|---|---|---|---|---|---|
| 5208047381438507520 (GALEX J073504.2-794409) | 16.56 | -0.41 | 11.64 | C II 3920, 4075, 4267, 4370, 4619, 4745, 5145, 5890, 6580, 6780, 7231-7237 (one visit, S/N 23; matches PHL 657 and PB 7043 in `plots/hotDQ_comparison.png`) | DA (MWDD; Vincent+2024 XP fit: 35 kK, 1.24 Msun); DA in Bravo+2025 (photometric) | hot DQ, new classification |
| 4792264314911712512 | 18.20 | -0.41 | 12.26 | broad features at 4267, 4700-4790, 5100-5150, 6580, 7100-7230 (2 visits, S/N 20) | DA: (MWDD; XP fit 38 kK, 1.34 Msun) | probable hot DQ (broadened, possibly magnetic) |
| 6466745168812781568 (GALEX J212643.1-494857) | 19.44 | -0.33 | 11.31 | C II 3920, 4267, 4370, 5890, 7231 (2 visits, S/N 9) | none | possible hot DQ |
| 5836110898905253760 | 17.44 | 0.56 | 13.03 | C I 4771, 4932, 5052, 5381, 6014, 7117, 8337, 9097 + strong H-alpha (4 visits, consistent) | PM* only; not in MWDD | carbon-rich white dwarf with hydrogen (DQA or DAQ); 76 pc, b = -3.5 deg; BP-RP inconsistent with the spectrum slope (crowded field) |

DQ reclassification candidates of catalogued white dwarfs (MWDD DB/DA/DC types): 4864552767735594240, 5950072354156640128, 4697078562502515840, 1758536430493058944 (warm DQ), 4876216249643782656 (not in MWDD), 4839652643297670528, 3143790338389766400, 883761715259055872, 5014781450914913664, 4963240881290549888, 397957277212371072 (weak).
Checked and not new: 5243591401210032000 (DQ in SIMBAD and Ould Rouis+2026). 2564860667085575552 is a cool DQ candidate in Kilic+2025 (100 pc SDSS II, Table "need follow-up spectroscopy"); the SDSS-V spectrum shows Swan bands.
Other by-products in `data/byproducts.csv` and `data/visual_notes.md`:
- magnetic DAs not in the 78-star Zeeman list;
- new DZs;
- nebular-line contamination;
- pipeline artefacts. 614067451587640704 and 6712920500806628864 are ordinary DAs once the XCSAO shift is undone.

## TESS: Gaia DR3 5208047381438507520 = TIC 764468822 (`tess_5208047381438507520/`)
- Data: SPOC 120-s light curves in S27, S34, S37-S39, S61 and S64-S67, plus 20-s light curves in S61 and S64-S67. CROWDSAP is 0.12-0.39.
- Combined 120-s (0.05-359 c/d): highest peak S/N 4.4 (FAP 0.49), mean amplitude 1.12 ppt. There is no periodic signal above about 5 ppt.
- The 20-s light curves show low-frequency power at 0.06-0.5 c/d, which is not attributable in a crowded aperture.

Update 2026-09-24: 5208047381438507520 has a deep dive with an independent review in `docs/reports/hotdq_j0735_2026_09_24/`. It has
a public HST/COS far-UV spectrum (SNAP 17420) with carbon lines; H-alpha indicates probable hydrogen. The classification is revised to
hot DQ with probable hydrogen (DQA), pending atmosphere modelling, and the "about 5 ppt" TESS figure above is the strongest peak, not an
upper limit.

## Quantitative line test and revised certainty (2026-09-24, `scripts/spec_lines_gen.py`, `line_tests/`)
Method, applied to all visits:
- XCSAO shift undone for in-stack visits only, then an inverse-variance coadd.
- NIST template cross-correlation. The "contrast" is the peak above the off-peak scatter, not a false-alarm probability.
- Gaussian fits to nine C II features.

| Gaia DR3 | C II contrast (coadd; per visit) | C II features at a common velocity | other | revised status |
|---|---|---|---|---|
| 5208047381438507520 | 16.7 at +100 km/s (one visit) | 9, weighted mean +100 km/s | HST/COS carbon; GALEX FUV-NUV +0.32 | hot DQ with probable hydrogen (secure carbon) |
| 6466745168812781568 | 15.0 at +80; 10.5 and 8.9 | 9 of 9 between +91 and +204 km/s | GALEX FUV-NUV -0.01 +- 0.08 (DA controls: median -0.37; 4 of 243 as red); no HST | probable hot DQ (upgraded) |
| 4792264314911712512 | 5.9 at -500; visits disagree (-470, +320) | none consistent | no GALEX coverage; TESS S98 unusable (CROWDSAP 0.19, 82% scatter) | possible only (downgraded): weak broad dips near C II positions; magnetic hot DQ, high-field magnetic white dwarf or artefacts |
| 5836110898905253760 | C I contrast 8.6 at +140 km/s (r 0.40); H I 6.6 | C I lines in 4 visits | not in GALEX test | carbon + hydrogen white dwarf (DQA or DAQ) |

Known DQ-type white dwarfs in the MWDD (`line_tests/dq_counts.txt`):
- About 1,600 in total, mostly cool (under 10 kK).
- 39 with MWDD Teff at or above 18 kK, plus a few "hotDQ" labels without a temperature.
- 25 labelled DAQ.
- Hot (Teff at or above 18 kK) Q-types within about 105 pc: 4 (51.5, 95.6, 100.2 and 104.8 pc; one "DQH?" and one "DQ:").

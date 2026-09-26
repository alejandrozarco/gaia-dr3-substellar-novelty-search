# Gas-disc timelines (2026-09-26)

Ca II triplet emission equivalent width in every public spectrum of 32 gaseous-disc white dwarfs (SPARCL SDSS/BOSS/DESI, SDSS-V
visits, LAMOST DR11, ESO X-shooter/UVES phase 3). Script `gas_disc_timeline.py`; QC and results `timeline_qc.csv`,
`timeline_clean.csv`, `timeline_summary_qc.csv`, `timeline_grid.png`, `timeline_highlights.png`. First result: 9 of 25 stars
with 3 or more spectra over a year or more vary significantly (RESEARCH_LOG 2026-09-26 01:18 UTC).

## Step 1: literature check of the variable stars (`litcheck/`)
ADS full-text search by name aliases (`lit_check_ads.txt`); arXiv sources of Dennihy+2020 (2010.03693), Melis+2020
(2010.03695), Gentile Fusillo+2021 (2010.13807) and Rogers+2024 I/II (2311.14048, 2406.11470) grepped for variability
statements. Profiles re-plotted per epoch (`prof_check.png`). EWs re-measured after a 5-pixel running median, which removes
cosmic-ray spikes (`cr_check.txt`).

| star | our timeline | literature | verdict |
|---|---|---|---|
| SDSS J1617+1620 | fading, still faint | Wilson+2014: rise 2006-2008, then decline | known |
| SDSS J0845+2257 | ~21 -> ~6 A, 2005-2024 | Wilson+2015: 40% drop 2004-2008, low state to 2014; profile changes (Manser+2016) | known; low state continues to 2024 |
| SDSS J0959-0200 | weak, variable | "known to host highly variable IRT emission" (Melis+2020) | known |
| WD J2212-1352 | 12.8-23.0 A | GF21: 50% drop 2016-2017 | known |
| SDSS J0347+1624 | 21 -> 35 A, 2020-2024 (borderline) | Dennihy+2020: +30% in 300 days | known behaviour |
| Gaia J0611-6931 | 48 -> 57 A 2019-2023 (X-shooter). The 2021-08 value of 87 A comes from an S/N 18 spectrum with continuum rms 0.15, so it is not reliable | Melis+2020: no change GMOS-S vs MagE | a slow rise of about 20% at most; not claimed |
| SDSS J0738+1835 | EW scatter 2.6-20 A | no variability report | **confounded**: the photospheric Ca II triplet absorption of this DBZ dominates the window; the profiles look alike at every epoch |
| WD J2133+2428 | 10.5 A (2022-05) -> 1.3 A (2023-05) -> 0.8 A (2025-05). The raw 2025 value of 5.4 A comes from cosmic-ray spikes | GF21 (discovery; "promising target for variability monitoring"); nothing later in ADS | **switch-off in public X-shooter data** from monitoring programmes 109.2383 (Manser) and 115.27XT (Ramirez Ramirez); a 2026-06 epoch is proprietary. It is the owners' result; registered, not claimed |
| WD 0856+048, GALEX J0039-0356 | onset after 2010; 23-49 A visits | ours | (public repo) |

## Step 2: structure function (`structure_function.py`)
14 stars with mean EW of 5 A or more and 3 or more spectra; 1,424 same-star pairs. SDSS J0738 is excluded, as is the
J0611 2021-08 spectrum; the J2133 2025 spectrum uses the spike-filtered EW.

| lag | pairs | stars | median abs(dEW)/EW, pooled | equal weight per star | median noise (10% + 1 A floor) |
|---|---|---|---|---|---|
| < 4 d | 44 | 11 | 0.065 | 0.041 | 0.21 |
| 4 d - 5 wk | 43 | 5 | 0.075 | 0.100 | 0.21 |
| 5 wk - 1 yr | 196 | 11 | 0.093 | 0.084 | 0.23 |
| 1 - 3 yr | 328 | 14 | 0.133 | 0.187 | 0.19 |
| 3 - 10 yr | 582 | 11 | 0.130 | 0.186 | 0.17 |
| 10 - 30 yr | 231 | 6 | 0.093 | 0.142 | 0.17 |

The typical star changes by about 4% within days and about 20% over 1-10 years. The systematic floor is conservative: the
short-lag scatter is well below it. A few stars change by factors of several: J1617, J0845, WD 0856+048 and J2133. SDSS
J1228+1040 contributes 451 of the 582 pairs at 3-10 yr, which is why the equal-weight column is given.

## Step 3: onset search (`onset/`)
- **SDSS-V visits** (`sdssv_visit_ew.py`, then public pass-2 per-visit z):
  - 80 on/off candidates, defined as 2 or more visits with z > 6 and 1 or more visit with z < 2 (`sdssv_onoff_candidates.csv`).
  - Looked at by eye:
    - the 6 highest zmax;
    - 10 more with M_G < 13, all three coadd lines at z > 3 and z_fake < 5 (`onoff_*.png`).
  - **0 gas-disc onsets.** Most are single-visit spikes or template noise.
  - One by-product: sdss_id 74709777 = Gaia DR3 3107374277060584064, a hot white dwarf with an irradiated companion, P = 0.592887 d (`docs/reports/pceb_3107374277060584064_2026_09_26/`).
- **SDSS-V x DESI** (`sdssv_desi_pairs.py`):
  - 10,379 pairs within 2 arcsec; 2,788 with S/N > 10 in both.
  - 74 formal switch candidates (max z_cat > 8, min < 3). Most are companions (DA_MS/CV), single-line artefacts or cool white dwarfs with M_G > 13 (template).
  - 13 warm-WD candidates re-measured template-free in every epoch (`switch_timeline.csv`), and two plotted across surveys (`switch_pairs.png`).
  - **0 new switches.**
  - Recoveries:
    - WD J0234-0406 (GF21 DABZ gas disc);
    - WD J0857-2245 (faded; 0.2 A in 2022 and 2024);
    - WD J0842+2300 (Ma+2025 candidate: weak narrow emission, 0.71 +- 0.04 A at S/N 303 in DESI).
- **Conclusion:** at the S/N of the public surveys, WD 0856+048 remains the only onset. The one switch-off (WD J2133+2428) is in pointed X-shooter monitoring data.

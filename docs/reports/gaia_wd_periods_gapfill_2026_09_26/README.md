# Gaia DR3 white-dwarf periods: gap-fill of the 2026-09-24 lane (2026-09-26)

## Why
The reflection binary Gaia DR3 3107374277060584064 (docs/reports/pceb_3107374277060584064_2026_09_26/) sat in our own
2026-09-24 input list (`../gaia_wd_periods_2026_09_24/data/wd_vspur.csv`: GLS 1.68667 c/d, FAP 1.4e-5) but was never
tested, for two reasons:
- its FAP was just above the tier-1 cut (1e-5), and the tier-2 cut M_G > 9.5 excluded this hot, bright white dwarf;
- the lane treated every star in Jestin+2026 as known, and Jestin+2026 lists this one as "Variable False".

## Selection (`select_gap.py`)
Starting from wd_vspur.csv:
- **Cuts:**
  - FAP < 1e-3 and N >= 20;
  - |IPD correlation| < 0.5;
  - frequency away from the Gaia spin harmonics;
  - not already tested;
  - Dec > -28;
  - not in Steen+2024.
  - Result: 55 stars.
- **Then removed:**
  - Jestin "Variable True" (period confirmed there);
  - any VSX entry with a period.
  - Result: **13 to test** (`todo.csv`).
- **Of the 13:** 3 are catalogued CVs/dwarf novae, 4 are faint red stars with frequencies below 0.4 c/d, 1 is the PCEB itself, and the rest are hot or low-mass white dwarfs.
- **Southern stars** (Dec < -28, `south_gap.csv`, 51): nearly all already carry a VSX period (mostly VSX type VAR, many from the Ranaivomanana+2025 Gaia-only periods). Not tested here.

## ZTF test (`ztf_check.py`, `ztf_check.out`; IRSA light curves, 2 arcsec)
Each star is tested at the Gaia frequency, and the ZTF power there is ranked against the whole 0.05-50 c/d periodogram.

| Gaia DR3 | name | f_Gaia (c/d) | ZTF | status |
|---|---|---|---|---|
| 3138305596433476480 | WD? (Pelisoli ELM candidate list) | 4.12996 | top peak 4.12994, FAP 1.6e-119, 3.4% | **recovery**: Ranaivomanana+2025 (A&A 704 A70) P = 0.24213 d, cluster EB1 |
| 2795150147707769728 | GALEX J003750.4+190136 (DA) | 1.31570 | top peak 1.31577, FAP 9.9e-31, 3.0% | **new period, 18.241 h** |
| 3150708057532318208 | GALEX J075145.6+105931 (DAe) | 3.61362 | top peak 3.61368, FAP ~0, 4.5% | **recovery**: Reindl+2023 (A&A 677 A29) reflection effect, 6.64 h |
| 3890059941364406144 | SDSS J102251.62+161151.6 (DA) | 16.48874 | top peak 16.48871, FAP 4.2e-110, 2.9% | **new period, 87.33 min** |
| 2208250945549692672 | WD* DO (XP) | 0.76504 | top peak 0.76494, FAP 1.4e-95, 1.3% | **recovery**: Ranaivomanana+2025 (704 A70) P = 1.3068 d, cluster STS2; IPHAS H-alpha excess (Fratta+2021) |
| 369254560530545024 | faint (G 20.1) | 17.0416 | rank 812 (top 1.0027 = daily) | not confirmed |
| 380085093662546560 | faint (G 20.8) | 0.14638 | rank 8859 | not confirmed |
| 385698341037793152 | faint | 0.31908 | no ZTF points | hole |
| 377363321347203456 | faint | 0.01297 | below 0.05 c/d | not tested |

Jestin+2026 lists 3138305596433476480, 2795150147707769728, 3150708057532318208 and 3890059941364406144 as "Variable False".
All four have their Gaia frequency as the top ZTF peak. **A "Variable False" in Jestin+2026 is not a null.**

## Characterisation (`char.py`, `char.csv`, `char_*.png`)
Sine plus first harmonic at the ZTF frequency, fitted per band:
- **GALEX J0037+1901** (2795150147707769728):
  - Photometry: G 17.99, 199 pc; GF21 H fit 27,000 K, 1.08 Msun.
  - Light curve: semi-amplitude g 3.1% and r 3.0% (r/g 0.95), nearly sinusoidal.
  - No SPARCL or SDSS-V spectrum.
  - Reading: most likely rotation of a massive (possibly magnetic) white dwarf. Not measured.
- **SDSS J1022+1611** (3890059941364406144):
  - Photometry: G 17.81, 540 pc, M_G 9.16; GF21 H fit 22,100 K, 0.32 Msun. The SDSS DR14 fit (Kepler+2019) gives 13,200 K and log g 6.5.
  - Spectrum: the SDSS 2007 and BOSS 2012 spectra show a low-gravity DA, with no emission and no M-dwarf features to 9200 A (`j1022_spec.png`).
  - Light curve: semi-amplitude r 4.6% against g 1.8% (**r/g 2.6**).
  - Eclipses: none. Faint outliers are scattered in phase and cluster on one bad night.
  - No Gaia source within 15".
  - Reading: a low-mass (He-core) white dwarf with a red-enhanced 87-min modulation. That points to reflection off a low-mass companion (brown dwarf or late M dwarf) in an 87-min orbit, a system of the WD 1032+011 / SDSS J1205-0242 kind. Ellipsoidal variation is too weak at this radius and period, and g-mode pulsation is not expected at this Teff and coherence. **Candidate only**: needs radial velocities or infrared photometry.
  - Not magnetic as far as we know. Yu+2026 (A&A 708 A275) includes it only in their 10,279-spectrum LAMOST x GF21 cross-match table, not among their 63 magnetic white dwarfs (arXiv source checked).

## Novelty checks
- **Both new periods:**
  - SIMBAD refs are catalogue papers only.
  - VSX type "WD" (Gaia), no period.
  - VizieR all-table 5".
  - Not in Steen+2024 (arXiv source 2404.02201; control 989059981050056320 found), Ranaivomanana+2025 (693 A268 and 704 A70; control 3138305596433476480 found), Reindl+2023 (source) or Jestin as periodic.
  - ADS full text for J0037+1901, J003750.4, J1022+1611, J102251.6: nothing.
- **Holes:**
  - VizieR has no working table for Steen+2024 (J/ApJ/967/166 returns nothing even for a Steen member), so the arXiv source was used instead.
  - "J/A+A/677/A29" is not a VizieR catalogue id: astroquery returned an all-table result instead of an error. **An invalid catalogue id silently turns into an all-table cone.**

## SDSS J1022+1611: further checks (`j1022_rv.py`, `j1022_tess.py`)
- **TESS full-frame images** (TESScut, 3x3-pixel aperture):
  - The 87.33-min period is the highest peak between 5 and 30 c/d in sectors 45, 46 and 72 (FAP 7e-14, 2e-8 and 5e-11). That is an independent confirmation from space.
  - The amplitude is diluted by neighbours: 0.85, 0.30 and 0.27% of the aperture flux. With TIC Tmag 18.03 (about 9 e/s), the star's own amplitude is about 5-6.5%.
  - The semi-amplitude therefore rises from g (1.8%) to r (4.6%) to the TESS band (~6%), as expected for reflection off a cool companion. The TESS flux scale is uncertain by about 30%.
- **Radial velocities** (Balmer cores against the BOSS spectrum): SDSS 2007 +22 +- 8, LAMOST 2021 -26 +- 10 km/s. The 3.7-sigma difference is suggestive only: instrument zero points, and exposures that span much of the period.

## Part 2: weak Gaia frequencies (`todo2.csv`, `ztf_check2.py`, `ztf_check2.out`, `gate5.txt`, `gate_0720.txt`)
77 northern stars with Gaia FAP from 1e-3 to 5e-2, not Jestin-confirmed and not tested before, were run through the ZTF test at the Gaia frequency. **8** have the Gaia frequency as the top ZTF peak:

| Gaia DR3 | name | P | status |
|---|---|---|---|
| 2478893842934875136 | PHL 1016 | 2.056 h | recovery (Steen+2024) |
| 1879989790567353344 | GALEX J221519.8+253059 (DOZ) | 18.54 h | recovery (Ranaivomanana+2025, TESS) |
| 1030289712881895296 | WD 0831+537 (DAH) | 2.163 h | recovery (Steen+2024) |
| 2749524641403549312 | PB 6015 = SDSS J0032+0739 | 3.696 h | recovery (Liu+2024 PCEB) |
| 3426576074700535040 | ZTF J060649.17+250715.4 | 35.57 h | recovery (Chen+2020) |
| 3123625093275668736 | WD+M binary (Rebassa-Mansergas+2025) | **10.393 h** | **new**; r > g, likely orbital |
| 3354819845628139904 | hot subdwarf candidate (Geier+2019) | **12.589 h** | **new** |
| 974895286283420160 | WDJ072009.19+464840.48 (DA, 51 pc) | **19.143 h** | **new**; also the top peak in TESS S20, S47 and S60 |

The southern ATLAS stars are in the object journals: 6136817910121524096 (18.456 h) and 6170660401283991680 (DO, 27.006 h). GALEX J1739-6439 has emission lines in SDSS-V (`south_spec.png`).

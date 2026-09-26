# High-field magnetic white dwarfs in SDSS-V DR20 (fan-out lane, 2026-09-23/24)

Screen of SDSS-V DR20 SnowWhite rows for magnetic white dwarfs above ~10 MG, which the linear-triplet screen of
`../mwd_zeeman_sdssv_2026_09_23/` cannot see. SnowWhite p_mwd never exceeds 0.057; 280 MWDD-magnetic white dwarfs with SDSS-V
spectra show that fields above ~20 MG appear under DC, DC:, DC/DQ, DC/CV, CV and DA: classes.
- Screened (147 mwmStar + 16 mwmVisit spectra, pipeline velocity shift undone per visit): all 7 rows with p_mwd > 0.05; 40 of 517
  low-p_dah rows (SnowWhite log g at its limit or Teff in conflict with photometry); 121 of 1,143 DC-class rows not known as
  magnetic (61 above 10,000 K, 60 at 6,000-10,000 K), ranked by the misfit of the pipeline's smooth model.
- Field model: hydrogen transition wavelengths in strong fields (Schimeczek & Wunner database, DaRUS doi:10.18419/DARUS-2118)
  for a centred dipole; on 7 known magnetic white dwarfs it returns 0.5-1.05 times the published fields (factor-2 systematic).
- Positive controls recovered: WD 0330-000, HE 1043-0502, EGGR 428, J2218-0000, J0803+1229, J1427+3721, WD 1533-057,
  J0849+0037, OW J1753; missed: J0926+1321 (210 MG, S/N 17). Negative controls: 12 featureless DCs, 4 normal DAs.
- Prior-classification gate (`scripts/gate/`): MWDD, DESI DR1 (both catalogues), DESI/LAMOST/SDSS DR17 spectrum existence,
  SIMBAD, VizieR all-table at two epochs, Garcia-Zamora+2026, Yu+2026, Kalita+2026, ADS (short names, WDJ names, aliases),
  arXiv source text (controls found in Kawka, Kulebi, Hardy and Amorim+2023 sources).

Candidates (`data/RESULTS_highfield_candidates.csv`, `figures/FINAL_<gaia>.png`):

| Gaia DR3 | name | class, field (factor-2 systematic) | evidence | grade |
|---|---|---|---|---|
| 5060502958330979840 | PHL 4443 = Ton S 354 | DAH, mean \|B\| ~25-30 MG | 4 visits (S/N 20-28, MJD 60643-60675) with the same pattern: pi 6496-6510 A, sigma+ 7037-7051 A, H-beta group 4746-4749 A | secure |
| 545633955251654016 | WDJ024544.82+721144.58 | DAH, ~45-60 MG | 3 visits: pi 6393-6400 A, stationary sigma+ 7079-7086 A; 88 pc | probable |
| 6467932297772819712 | WDJ204048.29-572123.13 | DAH, ~22-25 MG | 2 visits: pi 6518-6520 A, H-beta 4778 A | probable |
| 4782336652626481280 | wide companion of HIP 20180 (F5V, 1,480 au) | DAH, ~17-20 MG | 1 visit: sigma- 6184, pi 6538, sigma+ 6884 A; F-star light may add a few % (C* 0.19) | probable |
| 4963309012356892800 | GALEX J021237.6-400841 | smeared DAH? | 1 visit S/N 11; statistic at the false-positive level | possible |
| 2192687388516522880 | WDJ210847.16+614706.96 | not hydrogen | 30%-deep trough at 4150-4380 A in 2 visits (hot DQ C II 4267 or magnetic He-rich) | possible |
| 3327361677328480256 | WDJ062718.99+093327.42 | low-field DAH, ~3 MG | H-alpha triplet 6498/6563/6631 A, 1 visit | possible |

No DESI, LAMOST or SDSS DR17 spectrum exists for any candidate; prior labels come from Gaia XP classifications only.
By-products (gate partial): 6465542891501713408 (GALEX J213644.9-515758, MWDD DC:) shows C I lines (warm DQ);
2076678981825545088 (MWDD DA) shows Balmer lines and C I 7115 A (possible DAQ). Rejected objects: `data/REJECTED_highfield.csv`.
Not screened: ~90% of the DC selection, ~92% of the flagged low-p_dah rows, DCs below 6,000 K, CV classes, unclassified rows.

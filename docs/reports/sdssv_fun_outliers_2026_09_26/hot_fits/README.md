# Hot-star model fits to SDSS-V DR20 coadds (2026-09-26)

Question: is any of the hot He II-showing SDSS-V white dwarfs without a published temperature hotter than the known ones?

## Method
- **Models:** TheoSSA (GAVO) TMAP H+He NLTE grid.
  - Teff 60-200 kK, log g 6.5-8.0, He mass fraction 0-1; 280 spectra.
  - Normalised flux, air converted to vacuum, convolved to R = 1800.
  - Eight 200 kK files are served as VOTable only; the loader reads both formats.
- **Fit** (`fit_hot.py`):
  - Per-window (a + b x) x model.
  - One velocity per star.
  - chi2 summed over the windows.
  - Range = Delta chi2 <= 6 x max(chi2r, 1).
- **Line sets:**
  - `all`: Balmer, He II and He I.
  - `he`: He I and He II only (4027, 4472, 4543, 4687, 4923, 5413, 5877).
- **Controls:** 12 stars with published temperatures. Three of them were found in this lane's own novelty gate: two O(He) stars from Jeffery+2023, and an MWDD DAO.

## Validation (`hot_fit_summary.csv`)
- **`all` set:** median fit/literature = 0.75, with most stars at the 60 kK grid floor. This is the Balmer-line problem: H+He-only models give too-low temperatures from the Balmer lines, and the older literature values of the same stars (60-75 kK) agree with it.
- **`he` set:** median 1.04; 16-84% range 0.87-1.39; worst case 45% (10 controls with S/N >= 19).
- **Low S/N:** at S/N <= 15, two controls fail (91 -> 200 kK; 75 -> unconstrained).
- **Formal ranges** are often a single grid point. They are much smaller than the empirical scatter, so use about +-30-40%.

## Results (`he` set; unclassified stars)
| sdss_id | Gaia DR3 | name | S/N | Teff (kK) | note |
|---|---|---|---|---|---|
| 73346836 | 2995107164834343680 | GALEX J0550-1554 | 25 | ~110 | DAO |
| 99327334 | 5570041179495992704 | GALEX J0629-4158 | 32 | ~100 | DAO |
| 74510696 | 3090786872841030016 | SDSS J0814+0225 | 46 | ~90 | DAO |
| 80998734 | 4036084504408126976 | - | 22 | ~90 | DAO |
| 109787602 | 6365804611201098368 | GALEX J1906-7558 | 12 | unconstrained | DAO, too noisy |
| 100568930 | 5671975077144346112 | WDJ0958-1758 | 36 | unreliable | DA with weak He II 4686 (~3%); velocity at grid edge; strong Balmer lines. A known 3.27 d, 13% photometric variable (Ranaivomanana+2025, Jestin+2026) |

## Recovered known objects (not unclassified after all)
- **SALT J174009.9-721444** (5803795977174249344): O(He), 140 +- 15 kK, log g 6.7 (Jeffery+2023, MNRAS 519, 2321, arXiv:2301.03550). Fit 110 kK. **Hottest star in the sample with a published value.**
- **SALT J172335.2-672530** (5811791728816787584): O(He), 130 +- 15 kK (Jeffery+2023). Fit 100 kK.
- **GALEX J2044-0256** (4224989806164395392): MWDD DAO 92.5 kK, with a DESI DR1 spectrum (2021). Fit 90 kK.

## Novelty gate for the six
- MWDD: none.
- VizieR all-table cone (3", `vizcone.out`): only photometric WD and hot-subdwarf candidate lists, variability tables and an ML subdwarf flag (Zhang+2025 on SDSS DR17 for J0814).
- SIMBAD references: catalogue papers only.
- ADS full text (Gaia id, GALEX, WDJ and short names): nothing relevant.
- SPARCL (SDSS/BOSS/DESI): none.
- SDSS DR18 specObj at J0814+0225: none. The Girven+2011 "DA" is a photometric selection.
- So SDSS-V DR20 appears to hold the first spectra of all six. The SDSS-V pipeline classes (DA, DA/DAO) are already public; what this adds is the He II detection and the rough temperatures.

## Conclusion
Nothing here is credibly hotter than the published 140 kK O(He) star. The earlier statement that PN Lo 1 (118 kK) was the hottest was wrong: it came from a SIMBAD measurement-table compilation that lacked the Jeffery+2023 values.

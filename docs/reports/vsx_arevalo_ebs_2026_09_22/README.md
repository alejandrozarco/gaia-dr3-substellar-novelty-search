# VSX packages — three eclipsing binaries from the Arévalo+2026 reservoir pilot (2026-09-22)

Prepared, not submitted. VSX accepts one new-star submission per user per day, so these go in over three days.
Suggested order: the clearest light curve first.

| order | primary name | Gaia DR3 | P (d) | package |
|---|---|---|---|---|
| 1 | 2MASS J22310091+0645497 | 2709405317531811840 | 6.381715 | `VSX_SUBMISSION_2MASS_J22310091+0645497.md` |
| 2 | 2MASS J21220414+0657209 | 1738942132557316864 | 1.076989 | `VSX_SUBMISSION_2MASS_J21220414+0657209.md` |
| 3 | 2MASS J10102109-0331507 | 3828306424841718656 | 3.482506 | `VSX_SUBMISSION_2MASS_J10102109-0331507.md` |

Common to all three:
- Magnitudes are ZTF r (PSF photometry from the ZTF public data release, calibrated to Pan-STARRS1). In the
  2026-09-18 filing, ZTF r was entered with the VSX passband "r".
- Positions are Gaia DR3, moved to epoch J2000.0 with the Gaia proper motions.
- Epochs are HJD (ZTF `hjd` column, mid-exposure) of primary minimum near the middle of the data.
- Duration = fitted first-to-last-contact width of the primary eclipse in ZTF r, as a percentage of the period.
- Before each submission: repeat the live VSX cone check (API, 1′) and read the wizard's review page field by field.
- Analysis records: `../arevalo_reservoir_pilot_2026_09_22/` (scripts, data, figures) and the three object journals.

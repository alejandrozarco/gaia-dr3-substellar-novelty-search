# Gaia DR3 3107374277060584064: hot white dwarf with an irradiated companion, P = 14.229 h (2026-09-26)

**Correction (2026-09-26, later that day):** `ephem.py` and `summary_fig.py` converted CoRoT times as DATEBARTT + 51544.5 (MJD). DATEBARTT is
BJD - 2400000, so the CoRoT times were offset by 51545 d and the joint ephemeris below is wrong. The corrected joint fit is in the public
repository (`scripts/reflection_3107374277060584064.py`, `tables/reflection_3107374277060584064.csv`): **P = 0.59288582 d**, ZTF r maximum at
BJD 2459300.1744. The nearest cycle-count alias is at delta chi2 81066, and all data sets agree in phase within 0.02 cycles. The per-run CoRoT periods,
ZTF, Gaia and emission-velocity results are unaffected.

By-product of the gas-disc onset search: the SDSS-V per-visit screen gave sdss_id 74709777 as an on/off Ca II candidate
(z_visits 7.4/0.9/15.6/5.3). The emission moves in velocity between visits and comes with H-alpha and H-beta emission, so it is
not a gas disc.

## Object
- Gaia DR3 3107374277060584064 = WDJ064438.09-004550.51; G 17.27, BP-RP -0.35, parallax 1.816 +- 0.088 mas (550 pc), M_G 8.57
  (too faint for a hot subdwarf); l = 212.8, b = -1.9.
- Catalogued as a white dwarf only: SIMBAD WD* "DO:" (3 refs, all catalogues: Gentile Fusillo 2019/2021, Vincent+2024 XP);
  MWDD "DO:" (XP; Teff 28 kK, log g 6.9; no binarity); SnowWhite (SDSS-V) DA:, Teff 67,140 K, log g 7.86; VSX type "WD"
  (Gaia DR3 variable, 17.13-17.34 G, no period).
- SDSS-V spectrum (4 visits, 2021): steep blue continuum, He II 4686 absorption, weak Balmer absorption; H-alpha, H-beta and
  Ca II triplet emission that shifts between visits; no [O III] 5007 (no nebula in the fibre). `spec_74709777.png`.

## Period
- **ZTF** (IRSA, 50 g + 58 r points 2018-2024): LS peak 1.68666 c/d (FAP 8e-19); semi-amplitude r 11%, g 4% (larger in
  the red: reflection). The G = 16.17 F star 4.1" away (Gaia DR3 3107374272762041856) is constant in ZTF (no power at this
  frequency). `nb.py`, `nb_fold.png`.
- **Gaia DR3:** the vari_spurious_signals diagnostics (Holl+2023, J/A+A/674/A25) list GLS frequency 1.68667 c/d for this
  source (FAP 1.4e-5); 21 G epochs fold in phase with ZTF and CoRoT (`pceb_summary.png`).
- **CoRoT** faint-star light curves of CoRoT 102743730 (the F star; the WD is inside the mask): IRa01 (2007 Feb-Apr), LRa01
  (2007 Oct-2008 Mar), LRa06 (2012 Jan-Mar), all with a single strong peak at 1.6865-1.6867 c/d and 1.7-2.0% semi-amplitude
  of the blend. Ferreira Lopes+2025 (J/A+A/703/A32) list this period (0.592812 d, "BCEP/other") for the F8 IV star. The ZTF
  test shows the variable is the WD. Files: https://cdsarc.cds.unistra.fr/ftp/B/corot/files/N2-4.4/... (see `corot_lc.py`;
  not committed, 13 MB). `corot_fold.png`.
- **Joint CoRoT + ZTF ephemeris** (`ephem.py`, `ephem.txt`): max light BMJD 59300.28308 + 0.59288695 E. The neighbouring
  cycle-count aliases (+-3e-4 c/d) are rejected by delta chi2 > 80,000 (chi2 is inflated about 38x by CoRoT red noise; still
  > 2000 after rescaling). Conservative period error about 4e-6 d. The phases of the three CoRoT runs agree to 2 deg,
  ZTF to 11 deg.

## Emission velocities (SDSS-V visits; phase 0 = maximum light)
`phase_rv.py`, `visit_phase_rv.csv`, `rv_fit.txt`:

| visit | phase | H-alpha km/s | Ca II km/s |
|---|---|---|---|
| 59272 | 0.67 | +242 +- 11 | +202 +- 11 |
| 59273 | 0.41 | no emission (S/N 4 visit) | no emission |
| 59324 | 0.24 | -166 +- 6 | -73 +- 5 |
| 59325 | 0.91 | +152 +- 13 | +147 +- 7 |

The pattern matches emission from the irradiated face of a companion: velocity near systemic at maximum light, negative at
phase 0.25 and positive at phase 0.75, and no emission near minimum light. A fit v = gamma - K sin(2 pi phase) gives K about
140 (Ca II) and 220 (H-alpha) km/s. That is 2 parameters from 3 points: consistent, not a measurement. The XCSAO shift
(-400 km/s on visit 59325) was undone (in_stack visit). That visit fits the curve, which checks the undo.

## Novelty gate (2026-09-26)
- **Catalogues:**
  - SIMBAD (3 catalogue refs);
  - MWDD table.json (DO:, no binarity);
  - VSX (WD, no period);
  - VizieR all-table 5": no binary, PCEB or CV catalogue. Jestin+2026 (J/A+A/712/A243) ZTF vetting lists it as "Variable False". Ferreira Lopes+2025 assign the CoRoT period to the neighbour.
  - Ritter-Kolb, Downes, eRASS1 CV lists: absent.
  - Chen+2020 ZTF periodic: absent (control OK).
- **Literature:** ADS by Gaia id, CoRoT id, WDJ name and short names: nothing.
- **Other surveys:**
  - DESI DR1 (Amorim, Swan): not covered.
  - LAMOST DR11 WD catalogue: no.
  - ESO archive: no data (control OK).
  - mwcheck: no radio/X-ray (eRASS1/eRASS:3 covered, absent).
  - V/84 planetary nebulae: none within 10'.

## Status
New identification: an irradiated binary (post-common-envelope candidate) with a hot (He II) white dwarf. Photometric period from
three surveys over 17 years. Open: companion type and whether a faint nebula
surrounds it. Filing = VSX revision (user action; draft in `vsx_revision_draft.md`).

## Eclipses
None. CoRoT folds in 200 bins (4.3 min) and residuals from a 3-harmonic fit: the deepest bins are -0.30, -0.37 and -0.21% of
the blend (rms 0.10, 0.18, 0.08%) at unrelated phases (0.46, 0.86, 0.68). The WD supplies about a quarter of the blended light,
so any eclipse of the WD removes less than about 1.5% of its light: no eclipse, and the inclination is not near 90 deg.

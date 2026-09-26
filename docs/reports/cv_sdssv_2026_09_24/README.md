# Cataclysmic variables in SDSS-V DR20 SnowWhite (fan-out lane, 2026-09-23/24)

Selection: `snow_white_boss_star` rows with a classification containing CV or p_cv > 0.3: 605 objects (604 with Gaia ids,
340 first observed at MJD >= 60310). All 1,210 mwmStar/mwmVisit files inspected; dispositions of all 605 in
`data/cv_lane_all605_disposition.csv` (84 known CVs; 142 M-dwarf or WD + M-dwarf emitters; 274 without CV signatures; 46 nebular
contamination; known VSX CVs, planetary nebulae, QSOs and artefacts).
Catalogues checked for all 605: Inight+2025, Inight+2023a/b, Ritter & Kolb, Downes, Rodriguez+2025, Wang+2025, Inight+2026 DESI
(1,029 CVs), identifiers from 22 arXiv sources, MWDD, DESI DR1 white dwarf catalogues, SIMBAD, PolarCat 2026, Gaia Science
Alerts; candidates also: VizieR all-table (VSX 2026-08-09), mwcheck, ZTF, ADS aliases, DESI/LAMOST coverage, SDSS DR17, TNS.
Controls: polar 2MASS J19412506+1522553 (He II/H-beta 0.72, ZTF period 1.5565 h) and NZ Boo (0.05) flagged as known by every gate.
Not available: Brink+2026 (arXiv:2607.27960, 587 eROSITA CVs in DR20) and Hernandez-Diaz+2026 tables; Munoz-Giraldo+2026 list;
live VSX (VizieR copy used); ATLAS; ZTF south of Dec -30.

Pipeline notes found in this lane: Astra applies the XCSAO shift only to visits with in_stack = True (in_stack = False visits
are barycentric); BOSS spectra of some cool white dwarfs show red "humps" at 6000-7000 A that DESI spectra of the same stars do
not; VizieR `Table.to_pandas()` converts masked int64 Gaia ids to floats.

Candidates (`data/cv_lane_candidates.csv`, `figures/spec_<ID>_<gaia>.png`):

| ID | Gaia DR3 | J2000 | class | evidence | status |
|---|---|---|---|---|---|
| A1 | 2002597083798483200 | J225737.41+541619.9 | quiescent dwarf nova (WD-dominated) | double-peaked H-alpha (EW 320 A, peaks 952 +- 9 km/s apart), H-beta, He I; 196 pc, M_G 12.35; ZTF flickering, no outburst 2018-25; 2RXS source 7.3" | no prior classification found |
| A12 | 1977447164064222976 | J213306.16+463819.3 | dwarf nova | double-peaked H-alpha (1078 +- 22 km/s) and H-beta; 341 pc; no ZTF outburst | no prior classification found; probable |
| A4 | 5568642355890359168 | J061955.19-423611.6 | WD-dominated dwarf nova | 194 pc, eRASS1/eRASS:3 | novelty unverifiable (eROSITA tables) |
| A3 | 5362131777028219904 | J110438.55-490209.6 | dwarf nova | eRASS:3 | as A4 |
| A11 | 4679467096349698048 | J040038.28-615301.5 | CV | eRASS:3 | as A4 |
| A8 | 1822575389309423232 | J200608.78+191344.9 (MGAB-V3675) | polar (VSX: CV) | He II/H-beta 0.76; ZTF high/low states 18.4-21.5; ~1 mag modulation at 2.19-2.20 h | VSX type revision candidate |
| A9 | 4784897896243243392 | J044043.51-492513.7 | magnetic CV | He II/H-beta 0.92; eRASS:3 | known CV (Gaia DR3/VSX); subtype new |
| A10 | 5664935458242923392 | J093909.75-211251.1 | magnetic CV | He II/H-beta 0.46; hard X-rays; ZTF 77.44 or 38.72 min; SIMBAD lists QSO | known CV; SIMBAD type wrong |
| A14 | 6703736482047069696 | J183046.02-500530.3 | nova-like or hot-subdwarf binary | blue continuum, H-alpha FWHM ~830 km/s | possible |
| B4 | 6403339013297801216 | J212818.03-631402.0 | WD with irradiated companion or low-state accretor | narrow Balmer emission to H10, RV -40 km/s both visits | possible |
| B10 | 1969629915562515072 | J210541.59+421137.5 | nebular object (nova remnant or young PN) | broad [O III] (~900 km/s), He II, [S III], [Ar III] | possible |
| - | 5931744839753122944 | J161626.44-550845.7 | reflection-effect binary | narrow H-alpha, RV -8 to +71 km/s over 30 d; Gaia VARIABLE | possible |

VSX evidence (nothing submitted): A1 type CV, ZTF r 17.84-18.97; A12 type CV, ZTF r 19.20-20.29 (PS1 RR Lyrae candidate 3.7"
away may contaminate); A8 revision CV -> AM:, P ~0.0913 d, maximum near BJD 2460496.708, ZTF g 17.76-21.51.

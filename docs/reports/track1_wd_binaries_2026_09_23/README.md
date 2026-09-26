# Track 1 — X-ray-selected white dwarf + M dwarf binaries in eRASS:3 × Gaia (opened 2026-09-23)

**Selection.** eRASS:3 (Ramos-Ceja+2026, `J/A+A/712/A171/dr2mg`) Gaia DR3 counterparts with `matchflag = 1`,
`pany > 0.5`, parallax > 2 mas at > 5σ, M_G > 4.5: 108,404 sources. Kept: sources more than 1 mag below the
main-sequence ridge **and** below its 99th-percentile faint envelope (ridge from 43,653 Gaia stars with
parallax > 8 mas), or on the white-dwarf side of the diagram: **335** (212 "bridge", 123 white-dwarf-like).
Controls: 6315134987927550592 (J1526) and 3021820276571880064 (BLVS J061325.64-030239.2, VSX AM:) are selected.

**Known-object sweep.** Ritter-Kolb, Downes, VSX, Gentile Fusillo+2021, SIMBAD (CDS XMatch); Schwope+2026,
SDSS DR20 eROSITA CVs, Li+2025 GPC-WDMS (by Gaia id). 175 have no VSX / CV / WD / emission-line identification.

**Light curves.** 74 of the 175 are at Dec > −28 (ZTF; `scripts/ztf_screen.py`): Lomb-Scargle 0.05-48 d⁻¹ at
10× oversampling; a period counts only if FAP < 1e-8, it beats its ±1 d⁻¹ aliases, and it is not near 1 d.
101 southern targets: ATLAS forced photometry (`scripts/atlas_runner.py`), same criteria; running.

**First results (ZTF).**

| Gaia DR3 | name | G | M_G | period | note |
|---|---|---:|---:|---|---|
| 6315134987927550592 | 1eRASS J152614.8-111331 | 17.53 | 12.12 | 2.2511 h (g, r) | control, recovered |
| 6285270400986331136 | 3eRASS J143549.0-174716 | 16.68 | 12.09 | 2.334 h (g), 1.167 h (r) | 83 pc; Koen 2022 P = 0.09725686 d, classified there as an M+M binary |
| 3016053028844771456 | 3eRASS J054159.4-071347 | 19.27 | 12.40 | 1.133 h (r) | 236 pc; not catalogued |
| 3965186104852552448 | 3eRASS J111431.9+131627 | 18.61 | 11.00 | 1.659 h (r)? | eRASS:3-only; to vet |
| 5173668607774762624 | 3eRASS J024517.4-100024 | 17.71 | 12.00 | 2.611 h (r)? | eRASS:3-only; to vet |
| 5470963190282131840 | 3eRASS J103644.5-245042 | 19.10 | 13.49 | 11.53 h (r), alias tie | eRASS:3-only; to vet |

Figures: `figures/j1435_fold.png`, `figures/j0541_fold.png`. Data: `data/targets_335.json`, `data/ztf_screen.json`.

**Southern ATLAS screen (v3), results to 2026-09-24 (`atlas_south/`).** 35 of 101 targets analysed by the runner. Flag
checks (`atlas_south/verify_flags.py`): 4864794492789757568 unmeasurable (difference-flux errors 20-40x the star);
4791412846234632320 not reproduced (power 0.003 at the flagged period; Gaia neighbour of equal parallax at 1.73");
4731701084150029824 = 2MASS J03531244-5502363 (110 pc, G 18.37, M_G 13.17): the screen's sinusoid fit flagged
0.0739348 d in o only; a box search (`atlas_south/j0353_eclipse.py`, `j0353_2p.py`, `j0353_vsx.py`) gives a flat-bottomed
eclipse of 10.6 min every 0.14786971 d (3.549 h) in o and c, depth ~30% (o) and ~57% (c), no secondary eclipse.
VSX package: `docs/reports/vsx_j0353_2026_09_24/`. The runner's sinusoid search does not target narrow eclipses; a
box search on a uniform frequency grid (1-20 c/d, step 2.5e-5 c/d) recovers this binary in both bands (robust SDE 53 and
12) and is being run on all finished light curves. The `atlas_south` scripts read the forced photometry as
`atlas_raw/<gaia_id>.txt` (copy of `atlas_fp_<gaia_id>.txt`).
Box search result (`atlas_south/bls_all2.py`, `bls_all2.json`; 39 light curves finished by 2026-09-24 00:40): with duty cycle
<= 0.25, depth S/N >= 8 and robust SDE >= 10, only 4731701084150029824 is detected (o: 0.1478699 d, SDE 53; c: 0.1478694 d,
SDE 12). All other peaks above the loose thresholds are 40-min boxes at 72-83 min periods with 3-5 uJy depths (a short-period
edge effect) or come from unmeasurable light curves.

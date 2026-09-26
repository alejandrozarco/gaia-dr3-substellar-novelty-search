# Lane M — infrared-excess orbital variability (NEOWISE × Gaia × ZTF), opened 2026-09-23

**Signature.** A periodic NEOWISE W1/W2 modulation that is larger than the optical modulation at the same period.
In white dwarf + M dwarf binaries this points to cyclotron emission from a magnetic white dwarf; ellipsoidal
modulation, irradiation and starspots all give optical amplitudes at least as large as the infrared ones.

**Positive control.** WISE J152614.95-111326.4 (Gaia DR3 6315134987927550592), published by Koen & Kniazev 2024
(PASA 41, e108): W1 0.73 mag and W2 0.78 mag at the orbital period against r 0.20 mag. Joint ZTF + WISE period
0.093796948 ± 0.000000012 d.

## Samples

| sample | selection | size |
|---|---|---:|
| Petrosky+2021 | periodic WISE variables, P < 0.35 d, × Gaia DR3 (4″), > 1 mag below the main-sequence ridge and below its p99 envelope, G−W1 consistent | 6 |
| VarWISE (Paz+2026) | pure + extended, parallax > 5σ, below the ridge, \|b\| > 10°, G−W1 consistent, W1 amplitude > 0.15 | 226 |
| eRASS:3 low-pany | Gaia counterparts with 0.05 ≤ pany < 0.5 (excluded by Track 1), below the ridge or WD side, separation < 3″ | 243 |

The ridge is the Track-1 main-sequence ridge (`docs/reports/track1_wd_binaries_2026_09_23/data/ms_ridge.json`).

## Tests per object (`scripts/wise_battery.py`)

- NEOWISE-R single exposures within 3″ of the proper-motion-propagated Gaia position; clean frames
  (qual_frame > 0, qi_fact > 0, saa_sep > 0, no moon or W1 artefact flag, nb = 1, na = 0).
- Lomb–Scargle in W1 and W2 separately (0.5–40 d⁻¹); periods within 0.4 d⁻¹ of multiples of the WISE orbital
  frequency (15.24 d⁻¹) are flagged as window aliases.
- Sinusoid amplitudes in W1, W2 and ZTF g, r, i at the same period.
- Blend tests: photocentre at bright versus faint epochs; proper motion measured from the WISE positions.
- Field controls: all sources of similar W1 within 6′, power at the same frequency.
- Novelty (`scripts/quick_known.py`): VSX API, SIMBAD, ADS full text on every designation including AllWISE, 2MASS,
  TIC and short forms (Jhhmm±ddmm), Li+2025 Gaia-XP WD+MS catalogue, VarWISE, and the van Roestel ZTF eclipsing-WD
  catalogue (public explorer table; not indexed in ADS or VizieR).

## Results

| Gaia DR3 | name | outcome |
|---|---|---|
| 6315134987927550592 | WISE J152614.95-111326.4 | control; published (Koen & Kniazev 2024) |
| 3612227169936143360 | QS Vir | known eclipsing WD + M dwarf; W1 0.16 vs g 0.43 mag |
| 4384149753578863744 | DDE 157 | known EA; no IR excess |
| 1635581274974672768 | ZTF J170512.97+660737.4 | published WD + MS binary (Li+2024; Shani+2025, P = 0.116195 d); VSX type DSCT is wrong |
| 2023161872596119296 | VarWISE J192455.37+252000.6 | dropped: spurious parallax (RUWE 8.0, multi-peak 43%) |
| 604326641854470016 | LP 486-53 | known EA (P = 0.1392 d); no IR excess |
| 5105520847021315712 | Gaia DR3 5105520847021315712 | known CV (VSX, Gaia-XP emission-line CVs 2026) |
| 513958743252720768 | ZTF J0220+6303 | known eclipsing binary (Brown+2023) and pre-polar suspect without circular polarisation (Hakala+2026). New here: eclipse ephemeris BJD_TDB 2459501.883344 + 0.099084412(30) E; IR hump at phase ~0.78, 0.2–0.5 mag in 2014–2019, ~0.05 mag in 2021–2023 (`figures/j0220_fold.png`) |
| **3513017956589117056** | **WISE J122637.85-230414.2 (J1226-2304)** | **coherent infrared periodic variable with a mid-IR excess and candidate magnetic WD + M-dwarf binary; cyclotron emission favoured, orbital period unconfirmed**: W1 modulation at P = 0.07968186(4) d, W1 maximum BJD_TDB 2459999.9470(12); W1 full amplitude 0.96 mag (2010) falling to 0.25–0.34 mag (2020–24) at constant phase, W2 0.29 mag; ZTF forced r < 0.14 mag (95%); WISE photocentre and proper motion follow the Gaia star; g-r 0.65 mag bluer than 18,323 M dwarfs of the same i-z (a cool WD-like component); eRASS1 + eRASS:3 (few counts). Period listed by Petrosky+2021 (EB flag); Pelisoli+2025: WD-pulsar candidate of unclear nature. Independent re-analysis reproduces all measurements (`figures/j1226_fold.png`, `figures/j1226_referee_summary.png`, journal). Deep dive (`figures/j1226_deep_dive.png`, `scripts/j1226_deep.py`, `scripts/j1226_2p.py`): no coherent modulation in PS1 grizy 2010-14, SkyMapper i/z 2016-20 or DECam; per WISE visit the mean W1 flux is flat (0.39-0.44 mJy) while the W1 semi-amplitude fell from 0.15-0.19 mJy (2011-16) to 0.04-0.07 mJy (2018-24), 0.12 mJy in mid-2024; phase of maximum stable; coherent odd/even (2P) term delta chi2 5.5, p = 0.06 (P and 2P open); mean flux 2.0x (W1) and 3.6x (W2) the M-dwarf photosphere predicted from VHS J/Ks; unWISE W1 and W2 centroids coincide within 0.1" |
| 548694338491992960 | ZTF J0229+7531 | known: van Roestel ZTF eclipsing white dwarf catalogue (Zenodo 15007293, April 2026; P 0.150207791 d; eclipsing, ellipsoidal, spot). Our eclipse ephemeris BJD_TDB 2459476.991530 + 0.150207823(67) E agrees (`figures/j0229_fold.png`, journal) |
| 3965186104852552448 | 3eRASS J111431.9+131627 | new candidate accreting WD + M4 binary, P = 0.06914240 d; no IR excess (`figures/j1114_fold.png`, journal) |
| **3082614748370926848** | **VarWISE J075330.99-004209.7 (J0753-0042)** | candidate magnetic WD + low-mass-star binary; variability previously catalogued by VarWISE ('ew'); found in the 2026-09-23 extension run. NEOWISE P = 0.1053647 d (2.529 h), W1 FAP 2e-20; flat bright plateau with one deep minimum per cycle (W1 -67%, ~0.3 of P); W1 full amplitude >= 0.73 mag, W2 0.50; photocentre, WISE proper motion and 181 field stars clean; mean W1/W2 2-3x and 2.5-3.6x the M-dwarf photosphere, W1 brighter by ~0.4 mag after 2010; 370 pc, ~3 mag below the main sequence, blue optical excess; eRASS:3 source at 7.3" (pany 0.05). Optical amplitude unconstrained (ZTF near its limit; ATLAS pending) (`figures/j0753_fold.png`, journal) |
| **5456743064671253632** | **VarWISE J105943.85-274050.1 (J1059-2740)** | candidate magnetic WD + M-dwarf binary; P = 0.1209716 d after a BJD alias audit (the screen's 0.1210522 d is its -2/yr alias); W1 0.65, W2 0.53, ZTF r 0.20 (0.14-0.27) mag at that period; W1 faded by ~0.5 mag 2015-18 -> 2022-24 (`figures/j1059_fold.png`), 3.7 mag below the ridge, blue excess, NUV; coadd diffraction-spike flag and no X-ray. Bright-minus-faint W1 imaging (`figures/j1059_localise.png`): the variable flux is a point source within ~0.1-0.4" of the Gaia position (journal) |
| 936887574490787456 | VarWISE J064456.23+311538.1 | probable WISE window artefact (a field control has the same power) |
| 3377068158472469248 | J0615+2227 | dropped (blend) |

**Extension run (2026-09-23, in progress).** VarWISE below-MS rows at |b| <= 10 deg (522) plus 24 high-latitude rows that met the documented cuts but were not in the first run (`scripts/vw_pipeline_lolat.py`). Strict flags so far: J0753-0042 (above); dropped: VarWISE J072436.58-253159.8 (variable IR flux from a Gaia neighbour 0.7" away), VarWISE J123629.84-543057.2 (RUWE 6.7), VarWISE J070358.06-120159.1 (40 epochs, not significant).

**Screen completion (2026-09-23).** VarWISE: 226/226 screened; with strict cuts (non-alias period, LS power >= 0.3,
>= 150 WISE epochs, W1 amplitude >= 0.15 mag) 10 pass, all listed above (IR excess: J1526, J1226, J1059 and two
artefacts). eRASS:3 low-pany: 243/243 screened, 155 with enough WISE epochs, 0 query holes; only J1226 passes the
strict cuts. The ZTF period screen of the 62 ZTF-reachable low-pany sources found no coherent period.

## Track-1 selection gap

J1226 has eRASS:3 pany = 0.38 (pi = 1.0, separation 1.1″) and was excluded by the Track-1 cut pany > 0.5. Among the
243 low-pany sources within 3″, 18 are catalogued CVs (dwarf novae, WZ Sge stars, polars V1033 Cen and
CRTS J1944-4202).

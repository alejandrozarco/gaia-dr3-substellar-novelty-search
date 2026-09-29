# Blind spectral-anomaly search of the SDSS-V DR20 white-dwarf spectra (2026-09-29)

Motivation: search for any spectral peculiarity, not only variability or binarity.

## v1 (spec_anomaly.py)
PCA (K=12) reconstruction of 26,779 coadds with S/N >= 8; global chi^2 and 30-A window residuals. The top of both rankings was
dominated by instrument effects: single-pixel spikes surviving the coadd, blue/red camera-join steps at 5900-6400 A, sky residuals,
and ~400-A ripples. Per-visit checks (results/broadfeature_visits.png) showed the broad "features" in only one visit of each star.

## v2 (spec_anomaly_v2.py)
S/N >= 12 (18,482 spectra), 3900-8800 A, spike masking in the reconstruction, 30/80-A windows, and a visit-persistence test (each
feature re-measured in every visit, Astra shift undone). Top 400: 112 persistent, 140 not persistent, 148 single-visit.
Among plain-DA-labelled spectra with persistent features: bright non-white-dwarf contaminants (M_G < 5) with normal stellar lines;
recoveries of a known DZA (71058979) and two known magnetic DAs (61903177, 61563038); one feature (78931944) refuted by the DESI
spectrum (absent there); one (92254588 = WDJ024300.36-603414.82, 40-pc DA per O'Brien+2023) unresolved.

## LP 133-754 (Gaia DR3 1609392862209121664) — candidate CH band
Absorption deepening blueward to 4309 A and ending sharply at ~4314-4318 A in the SDSS-V coadd (3/4 visits) and independently in
the DESI DR1 spectrum; Balmer lines redshifted by +150-200 km/s; no C2, no Ca I 4227, no Mg b/Na D. Kilic+2025 type it DA (6718 K,
1.256 Msun). A CH index over 10,457 cool SDSS-V white dwarfs puts it 4th overall (behind three known DQpec stars) and first among
285 cool DAs at 12.8 sigma (results/ch_index.csv, ch_candidates.png). Journaled.

## Metal-line by-products
Three cool stars with weaker 4300-A dips plus Ca I 4227: sdss 96249344 (no neighbour; Ca II, Ca I, Fe I, Mg b, Na D: candidate
unrecognised DZ), 57901998 (0.5-arcsec neighbour, RUWE 2.6), 112581220 (G 10.2 star 5.9 arcsec away, BP/RP excess 2.86: contaminated).

## Outcome of the six plain-DA anomalies (deep prior-research check)
- 92726319 (Gaia DR3 4792905360255248768): narrow line at ~6090 A with no Zeeman partner near 7040 A; it lies in the camera-join region where most v1/v2 artefacts sit: probable instrument artefact.
- LP 133-754: CH-band candidate (journaled; see above).
- 92254588 = WDJ024300.36-603414.82 (40-pc sample; O'Brien+2023 spectroscopic DA, 5760 K): broad 4800-5800 A hump in SDSS-V only; conflicts with the published DA spectrum: probable calibration effect, unresolved.
- 78931944: refuted by DESI (feature absent).
- 65985512, 66304248: no literature; features in the camera-join region / continuum shape: not pursued.

## DESI DR1 sibling sweep (2026-09-29)
`desi_ch_sweep.py` measures the CH index on the DESI DR1 spectra of all 4,708 cool (<8000 K) DA white dwarfs in the DESI class table (Pwd > 0.8), retrieved by TARGETID from SPARCL; 4,628 have S/N > 3 (results/desi_cool_da_ch_sweep.csv). No batch failed.
- Positive control: LP 133-754's DESI spectrum gives 0.311+-0.040 (7.8 sigma) and would rank 12th by significance. It is not in the class table, so the table does not cover all of DESI DR1.
- The strongest high-S/N outliers (WDJ230234.13+075949.89, WDJ134710.47+511640.90) show no band head at 4314 A (results/desi_ch_top.png).
- One low-S/N lead: WDJ143727.61+115539.68 (S/N 4.4, 0.28+-0.05) shows a dip ending near 4315 A (results/desi_ch_low.png). It has a single DESI spectrum and no SDSS spectrum; unconfirmed.

## SDSS/BOSS DR17 blind search and CH sweep (2026-09-29)
`fetch_sdss_wd.py` stores the SDSS/BOSS DR17 spectra (via SPARCL) of the white dwarfs in Gentile Fusillo et al. (2021, sdssspec table). 257 of its rows have no DR17 spectrum within 3 arcsec (hole). `sdss_anomaly.py` scored 17,956 primary spectra with S/N >= 10 and tested the top 400 for persistence in the star's other spectra (results/sdss_anomaly_top.csv).
- Most top anomalies are known peculiar types (magnetic DA/DZ, DQ, hot DQ, CVs).
- The strongest anomalies among stars with a plain label are calibration or detector artefacts, or three high-field magnetic DAs already in Amorim et al. (2023): WDJ080938.11+373053.86, WDJ172432.15+323414.90, WDJ084929.12+285720.32.
- `ch_sweep_sdss.py` measured the CH index in 9,227 spectra of 7,677 white dwarfs with TeffH < 9000 K (results/sdss_ch_sweep.csv). High values come from main-sequence companions (DA_MS), known DQs, and the H-gamma wing near 8,000-9,000 K. Among single normal-mass stars below 8,000 K, no spectrum shows a band head at 4314 A (results/sdss_ch_top.png).

## DESI DR1 blind search (2026-09-29)
`fetch_desi_wd.py` stores the DESI DR1 coadds of all 44,417 objects in the DESI white-dwarf class table (no failed chunks). `desi_anomaly.py` scored 30,029 spectra with S/N >= 10 (results/desi_anomaly_top.csv). No per-visit persistence test is possible with coadds.
- Most top anomalies are known peculiar types (DAH, CV, DQ, DZ, DA+M).
- Among stars with a plain class, the strongest are narrow detector spikes, camera-join steps, or two stars published by Kilic et al. (2026, ApJ 1000, 216): WDJ071711.24+354706.50 (class DB; DQH, 28.2 kK) and WDJ011731.77+160239.28 (class DA; DAQ, 16.0 kK) (results/desi_anomaly_inspect.png, desi_anomaly_zoom.png).
- The nine DAQs of Kilic et al. (2026) span 13,242-17,385 K.

## Complete DESI DR1 CH sweep (2026-09-29)
`desi_wd_full.py` took all 4,827,137 DESI DR1 STAR spectra (SPARCL, no failed strips), matched them to Gentile Fusillo et al. (2021) white dwarfs with Pwd > 0.5 within 1.5 arcsec (48,918 spectra of 40,087 white dwarfs), and measured the CH index on the 1,551 cool (TeffH < 9000 K) spectra outside the DESI class table (results/desi_full_ch_new.csv, desi_full_ch_top.png).
- LP 133-754 is recovered at 7.8 sigma (rank 2).
- Rank 1 is the known DZ SDSS J082303.82+054656.1 (LP 545-12). The next two are normal DAs whose broad H-gamma wings enter the index window.
- No new CH-band white dwarf.

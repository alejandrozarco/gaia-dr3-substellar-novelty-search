# Published pulsating white dwarfs versus magnetic white dwarfs (2026-09-24)

Cross-match of 882 Gaia DR3 white dwarfs with published pulsation claims or pulsation-related labels (2,358 rows from 30
sources: SIMBAD Pu*, VSX ZZ*, MWDD periods, Vincent+2020, Guidry+2021, Hermes+2017, TMTS, Romero+2019/2022/2025, Bognar+,
Corsico+2019, Vanderbosch+2022, Jewett+2025, Jestin+2026, Huang+2026, Calcaferro+2026 and others; 604 time-series detections,
205 candidate or catalogue-only labels, 73 non-variables) against 8,512 magnetic-classification rows from 23 sources (MWDD,
SIMBAD, Kepler+2013-2021, Kleinman+2013, Kulebi+2009, Vanlandingham+2005, Amorim+2023, Hardy+2023, Garcia-Zamora+2026,
Bagnulo+2022, McCleery+2020, O'Brien+2023/2024, Kawka & Vennes 2012, Gianninas+2011, Kilic+2020, DESI DR1 Amorim+2026 and
Swan+2026, and the 27 stars of `../mwd_zeeman_sdssv_2026_09_23/`). Match by Gaia DR3/DR2 id and by position with proper
motion (2-3"). 37 overlaps; verdicts in `final/overlap_verdicts.csv`, other label conflicts in `final/other_class_conflicts.csv`,
provenance in `final/provenance.json`. SDSS-V spectra of 238 of the pulsators were screened with the Zeeman-triplet fit and a
Balmer-strength test.

Results:
- J2159+5102 (1980205739970324224) is the only published pulsator with a confirmed Zeeman triplet. Of the four magnetic
  stars observed by Vincent+2020, the other three were not variable.
- SDSS J173235.19+590533.4 (1434744751625887616), a published ZZ Ceti catalogued as DAH (1.0-2.56 MG) in SDSS-based catalogues
  and Amorim+2026: its SDSS and DESI spectra match non-magnetic ZZ Ceti stars of the same Teff and log g, with no sigma
  components at 20 or 51 A (fields above ~1 MG disfavoured).
- J1607+2933 (1317275544951049472), a Vincent+2020 non-variable inside the instability strip, is DAH in both DESI DR1
  catalogues; its DESI spectrum gives B_split ~1.2 MG.
- Label conflicts: two DBV stars catalogued as DBH:, known magnetic rotators listed as pulsators (RE J0317-853, Feige 7),
  SIMBAD Pu* types copied from the Vincent+2020 candidate list, MWDD magnetic flags on G 29-38 and six GW Vir stars.
- The Amorim+2026 classification file stores Gaia ids as rounded floats; matches to it must use positions.

Gaps: CDS xMatch and Gaia TAP upload joins timed out (per-object matching used); 5 pulsator rows unresolved; Schmidt+2003,
Uzundag+2021, Sowicka+2023, Gentile Fusillo+2016 and Steen+2024 not parsed; VSX from the VizieR snapshot.

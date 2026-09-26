# Adversarial review 2 of Gaia DR3 5208047381438507520 (2026-09-25)

Four independent reviewers worked in parallel before contacting the HST SNAP 17420 team:
- Astra (Codex gpt-6-astra, live web search): `astra_review2.md`, prompt in `PROMPT.md`.
- Spectroscopy reviewer: `spec_agent/`.
- UV and temperature reviewer: `uv_agent/`.
- Prior-work reviewer: `lit_agent/` (key files only).

## Verdict
**The carbon is real, and the object is a hot DQ.**
- The optical C II equivalent widths match the classical hot DQs of Dufour+2008 (C II 4268: 3.8 Å, against 3.4–3.6 Å in SDSS J2348−0942 and J1337−0026).
- A hydrogen-dominated DA is strongly disfavoured, but not model-excluded.
- The temperature is probably ~22 kK, not the DA-model 28.6–35 kK.

Hydrogen is "possible", not "probable". Astra keeps "probable" and asks for modelling.

**The discovery framing must change.** The 17420 team fits C and Si in every SNAP spectrum. In August 2026 Sahu presented a COS carbon and silicon analysis of 427 DAs at EuroWD. The team has very likely seen this star's UV carbon. Our contribution is the optical spectrum.

## Evidence against a hydrogen atmosphere
- **Balmer lines (same method for all stars):**
  - Hβ EW is 2.5–6 Å and Hγ 0.6 Å, against 16–23 Å and ~18 Å in 16 SDSS-V DAs at 25–48 kK. No DA is as weak (0/16).
  - The Hα:Hβ:Hγ ratio is about 9 : 2.5 : 0.6, against ~0.8 : 1 : 1 in DAs. That is a trace-hydrogen pattern, and it also rules out a diluted DA+DQ composite.
- **COS Lyα:** there are no broad wings. Flux at 1201–1211 and 1221–1238 Å is 82–90% of the 1240–1258 Å level; a hydrogen-dominated 20–35 kK, log g ~9 star would be near zero. The line centre (1214.8–1216.2 Å) is a masked gain-sag hole, which our old figure bridged.
- **COS C I:** broad troughs from the ground and 1.26 eV levels (1261, 1193, 1158, 1356–1364 Å). No DA survey shows these.

## Temperature
- The GALEX FUV−NUV colour corresponds to a ~21–22 kK blackbody.
- The flux budget (1131 Å to Ks) gives ~22 kK, probably 22–24 kK after blanketing.
- The star is a photometric twin of the Dufour+2008 hot DQs (BP-RP −0.41, M_G 11.64; those have 19.4–23.4 kK).
- C I strong, C II strong and C III modest fit ~20–24 kK.
- The DA-model 28.6–35 kK, log g 9.08 and 1.24 Msun must not be quoted.
- Astra notes the COS pseudo-continuum is not a thermometer; we agree.

## Corrections to the dossier and the first email draft
1. **Si II 1260 is interstellar** (+8 km/s, 106 mÅ; Si II 1264.7 absent). There is no photospheric Si.
2. **Velocity:** ~+80–90 km/s. The realistic error is ±20–40 km/s, not ±14. Use the excited C III 1247 and C II 1324 (+75 to +85 km/s) and the clean blue optical lines (+86 km/s). C II 1335.7 is a fragile anchor. C III 1247 is masked in FP-POS 4.
3. **Red optical features:** C II 5892 (BADSKYCHI), 6783 and 7237 (BADFLUXFACTOR, water band) are not independent evidence. Rely on 3921–4622 Å, which is unflagged.
4. **"Listed as DA in 17420"** is a generic label: all 141 targets carry "STAR, DA". SnowWhite's automatic spectroscopic class is "DA:" (a failed fit, 72 kK).
5. **Hot DQs with hydrogen are not new** (J1337−0026, Dufour+2008). Do not present DQA as novel.
6. **Not the nearest:** that is J1819−1208 = Gaia DR3 4153618204302689920 (51.5 pc, BP-RP −0.45; hot DQ, 23.8 kK, 1.24 Msun, C and O lines; Kilic et al. 2023, MNRAS 518, 2341). It is the natural reference for J0735: similar colour; J0735 is 0.54 mag brighter in M_G, so larger and less massive at a similar Teff.
7. **Variability:** drop "no variability" (TESS CROWDSAP 0.12–0.39). Say "no secure variability detected".
8. **GALEX controls:** "16 broadly matched DAs", not "same colour and absolute magnitude".
9. **Figures:** break the COS trace at masked gaps, label Lyα and N I 1200 airglow, and remove "sigma" from the CCF legend.
10. **Self-exposure:** the public repo (github.com/alejandrozarco/sdssv-white-dwarfs-2026) already contains the carbon measurements, naming lfac0z010 and 17420. Disclose this in the email, and drop or qualify "not planning to publish independently".

## Prior-work search (combined)
- **Carbon-rich classification published:** none found. Searched ADS full text (13 aliases; positive control recovered), SIMBAD, arXiv 2025–26, about 30 paper sources, AAS 245–248, ESO (with positive control), NOIRLab, MAST and the HST Cycle 33/34 catalogues.
- **Holes:** Gemini (login), 4MOST, Magellan/SAAO, EuroWD abstracts (title only per one reviewer; Astra cites an abstract booklet p. 48 describing 427 COS DAs with C/Si analysis), SDSS-V internal vetting.
- **HST 17420:** "A legacy survey for evolved planetary systems within 100pc". PI Gänsicke; co-Is include Gentile Fusillo, Koester, Hermes, Manser, Hollands, Toloza, Sahu and Williams; 15–30 kK, d ≤ 100 pc. This star is the hottest of the 8 targets above 1.1 Msun (GF21 mass).
- **TESS GI G05122** (Caiazzo, "Hunting for WD merger candidates") requested its 20-s data, so the Caltech group has it on a rotation list.
- **Risk:** the team already knows about the UV carbon = HIGH. Published scoop = LOW. Third-party scoop = LOW–MEDIUM.

## Side finding (checked 2026-09-25)
The four 17420 targets with FUV deficits larger than J0735's (1.7–3.0 mag) are explained:
- WDJ0303+0607 is a known magnetic DXP.
- WDJ1116−1637 and WDJ0840+5539 are known DBs.
- WDJ0800+0040 shows He I in SDSS-V, with no carbon.

J0735 is the only carbon-rich one (`fuv_deficit_17420.csv`).

# Open objects — inventory (2026-09-22)

Built from `docs/object_journals/INDEX.md`, `findings_register.csv` (2,037 rows), `docs/CANDIDATES.md`,
`docs/RESEARCH_LOG.md` and lane reports. Every object below is unfiled, unresolved or pending. Objects
closed as artifacts, retractions or known recoveries are not listed; they stay in the register.
Live VSX checks on 2026-09-22 used the VSX API with a 1′ target cone and a 20′ coverage control.

## 1. Awaiting the user (filing or account)

| object | what | state | next step |
|---|---|---|---|
| Rubin diaObject 170635519425249637 | SN II candidate | TNS AT draft v2 (UTC-corrected) | file on TNS once the account is active |
| Rubin diaObject 170591519677875016 | hostless transient, ATLAS pre-discovery | AstroNote + Fink feedback drafts | TNS account |
| ZTF19abxfaon = Rubin 170587115976392822 | state-changing variable, CV-like (VY Scl) | VSX + AstroNote drafts, REVISION 7; no filing recorded | VSX (one submission per day) |
| (88268) 2001 KK76 | 12 Gaia-anchored HST positions | ADES v2 package drafted, not filed (task #141) | MPC via SARC |
| Gaia DR3 2716884161263924224 = ZTF J223451.69+090546.4 | EA, P = 3.969311 d | VSX package rev. 3 (period to be doubled); Arévalo+2026 lists it as EA | revise and file |
| 2MASS J22342534+0806596 = ZTF18abxnwmb | EA | submitted to VSX 2026-09-18 | moderation |
| TYC 3477-27-1 = Gaia DR3 1593152388271709824 | EA, P = 0.6777712 d; also Gaia astrometric orbit 597 d | submitted to VSX 2026-09-22 | moderation |

## 2. Eclipsing binaries without a catalogued type or period

| Gaia DR3 | lane | P (d) | state |
|---|---|---|---|
| 2709405317531811840 = 2MASS J22310091+0645497 | Arévalo pilot | 6.381715 | VSX package in preparation |
| 1738942132557316864 = 2MASS J21220414+0657209 | Arévalo pilot | 1.076989 | VSX package in preparation |
| 3828306424841718656 = 2MASS J10102109-0331507 | Arévalo pilot | 3.482506 (or 6.965012) | VSX package in preparation |
| 2716885849186237056 | EB hunt | 0.583821 | characterisation pending |
| 2712662620728986112 | EB hunt | 9.589307 | characterisation pending; one LAMOST RV epoch |
| 2710992913538084352 | EB hunt | 15.448742 | characterisation pending; LSXPS X-ray source at 1.47″; Kostov+2025 table 2 (no period) |

## 3. Catalogued EBs whose VSX period does not phase ZTF (revision candidates)

| Gaia DR3 | VSX / Gaia DR3 period (d) | ZTF eclipse spacing (d) |
|---|---|---|
| 4353463277400908160 | 2.545907 | 1.243321 (2.486657 with equal minima) |
| 3233615666672318336 | 2.734521 | 1.537339 (3.074660) |
| 3283967904744688768 | 2.784238 | 2.912954 (5.825779) |

## 4. Variables closed for their lane's goal but never filed (all absent from VSX, 2026-09-22)

| Gaia DR3 | found by | what | record |
|---|---|---|---|
| 1487470319907416832 | DESI Phase 2B | SB1 with ZTF period 1.319478 d (ellipsoidal), M2_min 0.49 M☉ | register 2026-07-05 |
| 3831414946076844032 | DESI Phase 2B | SB1 with ZTF period 1.527990 d (eclipse), M2_min 0.47 M☉ | register 2026-07-05 |
| 1126496671074947200 (was registered as DR2 1126496666779064064) | DESI Phase 2B | SB1 with ZTF period 3.44977 d, M2_min 0.62 M☉ | register correction 2026-09-22 |
| 4416914787767626240 | DESI Phase 2B | SB1, marginal ZTF period 1.816395 d, M2_min 0.16 M☉ | in phase2b_verdicts.csv only; registered 2026-09-22 |
| 2688492537652631424 | DESI Phase 2B | SX Phe / δ Sct pulsator, P = 0.342 d | register 2026-07-05 |
| 6315134987927550592 = 1eRASS J152614.8-111331 | eRASS1 PS1 screen | active M dwarf, variability confirmed (PS1 + ZTF), no period, d ≈ 121 pc | journal |

## 5. Compact-object candidates (Gaia NSS lane)

| Gaia DR3 | what | state |
|---|---|---|
| 2909342818326298112 = WDJ060042.75-293041.36 | DA WD + dark companion 1.37 [1.23-1.52] M☉, P = 935 d | strongest candidate |
| 332248057157474176 = WDJ020915.51+380425.92 | DA WD + dark companion 1.32 M☉, P = 275 d | provisional, DR4-gated |
| 1593152388271709824 = TYC 3477-27-1 | G subgiant + dark M₂ ≈ 1.27 M☉ | watch-list, needs a clean RV epoch |
| 5858574810404752256 | M₂ ≈ 1.48 M☉, triple-vs-compact boundary | watch-list |
| 4111149395881722496 = HD 157033 | companion 0.4-6 M☉ | ambiguous |
| 1736313273270398720, 3056409026894392448, 4056403406274320768, 5815441557668429312, 6184510360847047808, 6441920468296049280, 6695559040407753984, 6846249479816261504 | Tier-1 NS-mass candidates (M2 1.27-1.89 M☉) | triage verdicts of 2026-05-28 not recoverable; need re-triage |

## 6. Unconfirmed, parked

| object | what | state |
|---|---|---|
| NSC 97192_2072 = J075308.47+003535.6 | long-term optical brightening, possible AGN (photo-z 0.99) | no spectrum; not VSX-eligible |
| Gaia DR3 3161546596480983040 (Object B) | CV, published by Schwope+2026 without period | open item: photometric period (ZTF blended by the 4.76″ neighbour, per-epoch floors 0.21-0.36 mag; Gaia DR4 epoch photometry) |
| Gaia DR3 4658651318334248960 | hot blue XP outlier | no archival spectrum |
| Gaia DR3 5222573240011621760 | eRASS1 source, ASAS-SN single-camera event (2017-03) | no ATLAS coverage; untestable |
| Gaia DR3 4822674126477654784, 2993086056306989824, 4688120596457178624 | eRASS1 bridge-pool, marginal periods | parked |
| bulge symbiotic lane | 0849a-4-25208 (0849a-4-25208), 0849a-4-17423 (0849a-4-17423), 0849a-4-33651 (0849a-4-33651), 0822a-20-1867 (0822a-20-1867) | archive-unconfirmable |

## 7. Solar-system objects (owned by the sso-recovery session since 2026-09-22)

| object | state |
|---|---|
| (330836) Orius = 2009 HW77 | 2019 limit i > 24.70 withdrawn (not reproducible); 6.1σ candidate 1.7″ from the new prediction in 2019-05-16 i and 2019-06-07 g, identity unresolved; filing on hold (task #141) |
| (88268) 2001 KK76 | see section 1 |
| 2001 KN76 | parked |

## 8. Pools never dispositioned object by object

| pool | size | record |
|---|---:|---|
| Arévalo reservoir full sweep | 270,965 stars + 2,238 control | running 2026-09-22 (`~/claude_projects/eb_sweep_2026_09_22/`) |
| EB hunt WEAK class | 420 (20,007-star hunt) + 54 (Arévalo pilot) | not inspected |
| DESI Phase 2B NO_PERIOD_PENDING (RV-variable, no period) | 23 | DR4-gated; ids in `docs/reports/desi_hunt_phase2b_2026_07_05/phase2b_verdicts.csv` |
| eRASS1-Gaia v2 uncatalogued X-ray counterparts | 137 (135 without a disposition) | lane closed null for outbursts (RESEARCH_LOG 05-31) |
| XP-outlier pilot, never novelty-checked | 578 | lane closed (scooped, 2026-07-05) |
| Tier-1 NS pool / Tier-2 / v3 acceleration | 160 / 426 / 7,062 | DR4-gated (`docs/CANDIDATES.md`) |

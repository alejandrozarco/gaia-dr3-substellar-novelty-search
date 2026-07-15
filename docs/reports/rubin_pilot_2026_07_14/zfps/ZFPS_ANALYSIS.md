# ZTF forced photometry (ZFPS) — Rubin pilot candidates

Two batches: reqids 479160/161/162/165/166 (filed by run-1 forensics agents, landed
2026-07-14 ~21:34 CEST) and reqids 479182/183 (filed during the resumed run, landed
2026-07-15 ~02:29 CEST). Full 2018–2026 JD window each. Raw light curves preserved here;
processing logs (~20 MB) left in /tmp/rubin_pilot/zfps/ (regenerable via reqid).

## Parsing lesson (SUPERSEDES the first version of this file)

The first-pass analysis treated any nonzero `procstatus` as a failed epoch and wrongly
reported "no usable ZTF data" for two candidates. **procstatus 56/57 are warnings, not
failures** — 57 = "no ref-image catalog source within 5 arcsec" (EXPECTED for hostless
transient positions; the log shows the PSF fit still runs and `forcediffimflux` is valid).
Correct filter: accept procstatus ⊆ {0,56,57} with non-null flux; reject hard codes (61+);
then infobitssci<33554432, scisigpix<=25, seeing<=4″. Detection = SNR>=4 (5 for firm).
The run-1 forensics agents parsed this correctly; the main-thread quick-look did not —
their claims were right, my first summary was wrong.

## Per-candidate results (warning-tolerant parse, 2026-07-15)

| candidate | reqid | usable epochs (8.1 yr, gri) | pre-event (MJD<61190) | event window |
|---|---|---|---|---|
| 170587105461272950 (unreported SN = ZTF26abfwqfp) | 479182 | 909 | **0/857 ≥4σ — 8 years dead quiet** | r/g 20.2–20.75, MJD 61227–61235, matches ZTF alerts |
| 170587115976392822 (8-yr variable = ZTF19abxfaon) | 479161 (+479166 dup) | 2354 | ~600 detections 18.3–20.9 in every season since 2019; chi2_red(0)=58/38/73 (g/i/r) | g/r/i 18.5–19.5 ongoing high state |
| 170591507978387512 (mundane SN) | 479162 | 1310 | quiet (chi2_red≈1); ONE isolated g 7.8σ @60094.40 — same-night r (+57 min) = −0.6σ → single-band ndet=1, treated as artifact/glint, NOT a precursor | marginal 4σ i/r 20.6–21.1 (SN near ZTF limit) |
| 170635519425249637 (SN II candidate) | 479183 (479165 first attempt, fewer epochs) | 784 | **0/732 ≥4σ over 8 yr** | first det MJD 61206.455/61206.461 (g 4.5σ + r 4.9σ same night) → **confirms the dossier's 22-day pre-Rubin ZTF detection**; r plateau 20.7–21.0 through 61231 |
| 170591519677875016 (hostless flare) | 479160 | 16 | null to r≲19.6 (sparse field coverage — genuinely few ZTF epochs here) | flare at r=21.1 is below ZTF depth; no constraint |

## Key outcomes

1. **170587105461272950:** the TNS-draft case is strengthened — ZTF forced photometry is
   dead quiet for 8 years (0 detections in 857 pre-event epochs), then detects the SN
   exactly at the Rubin/ZTF alert epochs. No precursor to ~20 mag.
2. **170635519425249637:** the forensics agent's headline claim (ZTF catches the rise 22 d
   before Rubin's first alert, bracketed by a clean non-detection at 61201.41) is
   independently reproduced from the raw IPAC product.
3. **170587115976392822:** definitive 8-year record of the uncatalogued high-amplitude
   variable; permanent archival product for the dossier.
4. **170591507978387512:** stays MUNDANE; the single-epoch g-band spike at MJD 60094.4 is
   logged as a rejected ndet=1 artifact (campaign rule-10 discipline).
5. ZTF-vs-ATLAS coverage: at these dec (−12…−18°) ZFPS coverage is field-dependent
   (16–2354 usable epochs); ATLAS FP remains the required complement.

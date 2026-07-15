# DRAFT TNS AstroNote (user files; do not submit programmatically)

Title: ATLAS pre-discovery photometry and archival constraints for the unreported Rubin/LSST transient at RA 306.74802, Dec -11.81856

Authors: A. Keur (independent)

Abstract draft:
We report archival forensics on Rubin/LSST diaObject 170591519677875016, a hostless-flagged
(Fink ELEPHANT), TNS-unreported transient. Rubin public-alert photometry shows a slowly fading
point source (i = 20.82 -> 21.14, r = 21.12; MJD 61218.32-61233.31; positional scatter ~6 mas,
excluding a solar-system origin). ATLAS forced photometry provides pre-discovery detections:
o = 19.99 +/- 0.21 at MJD 61202.53 (5.1 sigma) and c-band detections at 6.8 sigma on MJD
61207.51/61208.57, placing the onset at MJD ~61199-61202, >=16 days before the first Rubin
alert detection, with total duration >=30 days. Eleven years of ATLAS forced photometry
(4,579 epochs since 2015) and six years of ZTF data releases show no precursor outburst.
The position is empty in Legacy Survey DR10 (i-only coverage, 5-sigma i ~ 22.8-23.3),
PS1 DR2 stacks (r ~ 23.2, i ~ 23.1), Gaia DR3, NSC DR2, and CatWISE/unWISE; however, forced
template flux in the Rubin alerts reveals an underlying blue source at r = 23.96 +/- 0.05,
i ~ 23.9 (r-i ~ 0), i.e. the transient is hostless only at archival depth. The photometry is
consistent with either a supernova at z ~ 0.1-0.15 in a dwarf host (M ~ -15) or a
large-amplitude (>= 3.8 mag) long-duration dwarf-nova superoutburst of a faint blue
counterpart. Spectroscopic classification or continued Rubin photometry (rapid terminal drop
vs smooth decline) will discriminate.

Data statement: archival analysis was algorithm-assisted (AI agent), human-refereed; all
photometry is MJD-keyed and reproducible from ATLAS FP job 4539055 and the ALeRCE
multisurvey API (object 170591519677875016).

**Caveat (referee, 2026-07-15):** the underlying-source claim (template r = 23.96 +/- 0.05)
assumes the Rubin year-1 template epochs predate the ~MJD 61198 onset (not verified from
template metadata); if event-epoch images contaminate the template, the true quiescent
source is fainter and the value is a bright limit. Either way a sub-archival counterpart
exists and the ELEPHANT "hostless" label is depth-limited.

# Wave-3 RULE-v3 Re-Cut of the Precovery Campaign Supply

Date: 2026-07-07 | Work dir: /tmp/precovery_wave3/recut/
Input: the 103 SMIA-gate passers (campaign_targets.csv + smia_gate_log.csv, read-only).
Method: apply the wave-2 structural finding (RULE v3/v4) as a HARD filter, not a scoring nudge -
a target is searchable ONLY where a SMIA-passing epoch OVERLAPS catalog-searchable deep imaging,
verified per-epoch via SSOIS AT that epoch. Whole-arc footprint counts are a mirage.

## HEADLINE
Of 103 passers, 8 already worked (excluded). Of the remaining 95, 89 clear the arc-end>=2010 +
deep-era tight-box pre-filter; of those, 50 RULE-v3 PASS (>=1 SMIA-passing deep-era epoch with
CONFIRMED catalog-deep imaging within +/-45 d), and 39 are tight-box MIRAGES (0 deep frames at any
passing epoch - the wave-2 finding reproduced exactly). Folding in the arc-extension test (does the
overlapping deep epoch fall OUTSIDE the reported arc, the HW77 template?), the top 8 are all clean
arc-EXTENSION targets with tractable (<~3 arcsec) boxes, V<23.3, |b|>10, and real DECam/PS1/CFHT overlap.

## PIPELINE (per candidate)
1. arc-end gate (rule 4): require MPC last-obs year >= 2010 (tight epochs must reach the deep-archive
   era; HW77 arc->2012 is the template). 89/95 non-worked passers qualify.
2. deep-era SMIA re-check: from smia_gate_log, keep only epochs INSIDE the deep era (2013-01-01,
   2017-07-01 primary; 2021-01-01 secondary edge) that pass the gate with V<23.3.
3. per-epoch imaging EXISTENCE (rule 4, load-bearing): SSOIS byname (format=tsv, bynameHorizons,
   extres=yes), filter frames to within +/-45 d of each passing epoch AND to catalog-searchable deep
   surveys (DECam / Pan-STARRS1 / CFHT-MegaCam / Subaru-HSC). >=1 such frame => that epoch is
   genuinely searchable. This is what kills the mirages.
4. arc-extension characterization (precovery VALUE): MPC obs -> reported observed-year set; flag the
   best overlap epoch as EXTENSION (outside [arc_start,arc_end]), GAP (unobserved year inside arc),
   or SELF-ARC (overlap in a reported year => risk the deep frames ARE the reported astrometry).
5. crowding gate (e): galactic b from the overlap-frame predicted position; flag |b|<10 where box>~30".
   None of the top 8 trip it.

## THE MIRAGE FILTER (reproduces the wave-2 finding)
39/89 have a tight SMIA box at a passing epoch yet ZERO deep-survey frames within +/-45 d of ANY
passing epoch - searchable on paper, unsearchable in fact. Examples: 10370 (numbered Hylonome, 0/3),
2011 SR250, 2013 SO107, 2014 JU80, 2005 JJ186, 2013 LY35, 2014 KT101, 2001 KA77, 2015 BW524, 05145,
2014 KC102, 2000 KK4, 2002 GD32, 2003 KO20, 2015 KU178, and essentially the entire 2025-vintage
distant-longarc block (tight-looking gate boxes sit at 2021-01-01 pre-discovery extrapolations;
where deep frames DO overlap, e.g. 2025 NW189 DECam x10 at 2017, the extrapolated box is 100-1800
arcsec long - outside-arc but INTRACTABLE, so they rank at the bottom).

## KEY REVERSAL vs the original campaign ranking
- 2017 FP50 (original campaign rank 2) collapses to wave-3 rank 16: its ONLY deep overlap (DECam x10)
  sits in 2017 - its sole discovery year (7-night single-opp arc). Self-arc risk: those frames are
  plausibly the reported astrometry, near-zero precovery gain.
- 10370, 05145 (numbered/secure) are both mirages AND low-value; dropped.
- The winners are all multi-opp objects whose orbit is pinned by a multi-year arc but whose arc ENDS
  a few years before a deep-survey epoch that imaged the predicted position unreported.

## TOP 8 (all arc-EXTENSION, tractable box, V<23.3, |b|>10)
 1. 2009 QV38  (multi, arc 2009-2012) | 2013-01-01 [PS1 x18, V20.8, SMIA0.12", SMAA0.22", b+14.5]
    Brightest + tightest + most frames; +1 yr past arc-end into PS1 3pi. Best single target.
 2. 2002 KW14  (multi, arc 2002-2009) | 2017-07-01 [DECam x16, V21.8, SMIA0.21", SMAA0.54", b+12.8]
    +8 yr extension leverage yet box still sub-arcsec; largest orbit-improvement gain.
 3. 2008 SJ236 (multi, arc 2006-2011) | 2013-01-01 [PS1 x13, V21.4, SMIA0.11", SMAA0.13", b+34.9]
    +2 yr; pinpoint box, bright, high-|b| clean field.
 4. 2004 HF79  (multi, arc 2004-2015) | 2017-07-01 [DECam x4 + CFHT x87 = 91, V22.8, SMIA0.23", SMAA0.60", b+22.9]
    91 deep frames overlap; deep CFHT-MegaCam coverage, +2 yr.
 5. 2007 HV90  (multi, arc 2007-2016) | 2017-07-01 [DECam x28, V22.9, SMIA0.30", SMAA0.58", b+15.7]
    +1 yr; 28 DECam frames, tight box.
 6. 2008 HY21  (multi, arc 2004-2012) | 2013-01-01 [PS1 x4, V22.7, SMIA0.44", SMAA0.62", b-50.0]
    +1 yr; fewer frames but very clean high-|b| field.
 7. 2010 JK124 (multi, arc 2010-2014) | 2017-07-01 [DECam x8, V21.6, SMIA0.57", SMAA3.06", b+13.3]
    +3 yr; bright (V21.6), box a few arcsec.
 8. 2006 HW122 (multi, arc 2006-2015) | 2017-07-01 [DECam x4 + CFHT x119 = 123, V23.2, SMIA0.90", SMAA2.5", b+24.1]
    Faintest of the 8 (near limit) but 123 deep frames incl. deep CFHT - many stacked shots.

Runners-up (rank 9-16): 2015 SW20, 2005 LA54, 2014 QJ562 (extension, V~23), 2012 DD61, 2014 SV349,
2002 PP149 (extension), 2002 PQ152 (GAP-precovery, V22.9 PS1x2), 2017 FP50 (self-arc).

## CAVEATS (carry into per-target campaign step, unchanged from GATE-R1 rules 5/6)
- SSOIS byname positions use the full-orbit ephemeris; the +/-45 d + deep-survey filter confirms a
  deep FRAME exists at the predicted track, NOT an on-chip detection. Confirmation = pull Datalink
  cutout / cross-match NSC DR2 (DECam) or PS1 DR2 (PS1) / CFHT MegaPipe; >=2 same-night coherent
  detections; reject <10" blends and single-epoch excursions; +1 deg negative control.
- "Extension" is a YEAR-level flag; verify overlap frames post-date the last reported NIGHT before
  claiming arc extension.
- Mandatory BYCATCH pass (rule 5) after each field search; log n_unknown_candidate.

## ARTIFACTS
- wave3_targets.csv   - 50 RULE-v3 passers ranked + 39 mirages appended (full audit trail).
- wave3_final.json    - passers with per-epoch searchable-epoch detail + arc status.
- ssois_overlap.json  - per-object per-epoch deep-frame counts by survey (the rule-4 evidence).
- arc_windows.json    - MPC observed-year sets + extension/gap/self-arc classification.
- pool_prefilter.json - the 89 arc>=2010 deep-era candidates before the SSOIS existence test.
- ssois/*.tsv         - raw SSOIS byname frame lists per candidate.

# ATLAS forced photometry — Object B + WDJ020915 (2026-06-11)

First-ever optical time-series tests for both objects. Service: fallingstar-data.com/forcedphot
(difference-image PSF fluxes, MJD 57232–61174, ~10.4 yr). Raw curves: `atlas_fp_*.csv` (this dir).
Analysis scripts: `/tmp/atlas_analysis_2026_06_10.py`, `/tmp/atlas_followup_2026_06_11.py`
(quality cuts -> outburst-cluster hunt -> Lomb-Scargle + 200-permutation FAP; flux-space, per band).

## Object B (3161546596480983040) — INCONCLUSIVE (systematics-dominated, unmeasurable)
- The G=13.8 neighbour at 4.76" dominates the ~4" ATLAS PSF: minimal-cut robust sigma = 740 uJy;
  96% of epochs fail standard quality cuts (chi/N, duJy); reduced scatter ~8x formal errors.
- ">=5-sigma" and >0.7-1.4 mJy epochs occur on hundreds of nights uniformly across all 8 seasons —
  subtraction-residual noise, not outbursts (a real DN outburst = contiguous 5-20 d bright run;
  scattered bright nights also contradict the in-hand 8-yr ZTF alert null).
- Constraint delivered: only sustained events above ~3.7 mJy (mag <~15.0, i.e. amplitude >3.6 mag
  from quiescence G=18.6) are excluded — weaker than the DASCH nova-scale bound.
- LS: no significant period (perm-FAP 0.32-0.67).
- VERDICT: ATLAS cannot measure this target. The variability discriminator still hangs on ZTF
  ZFPS forced photometry (1.0" pixels resolve the 4.76" pair) — registration pending.

## WDJ020915 (332248057157474176) — QUIET; orbit-reality modestly strengthened
- 4,774 clean epochs (3,677 o + 1,097 c); reduced scatter 2.6-3.8x formal (mild systematics).
- NO outbursts: significant-epoch clusters are low-level (60-130 uJy = 5-10%), band-inconsistent
  seasonal runs -> reference/wallpaper systematics, not astrophysics.
- NO signal at the orbital period: P_orb=274.5 d perm-FAP 0.27 (o) / 0.99 (c); P_orb/2 ~1.0 both.
  No eclipse / ellipsoidal / reflection at the few-percent level.
- The two formally "significant" LS peaks are aliases: o-band P=0.9971 d sits on the diurnal
  sampling comb (window power 0.34-0.92 at 0.997-1.000 d) at 2.3% amplitude; c-band P=205 d at
  1.9% is seasonal-systematic territory (annual window power 0.62). Neither is physical.
- VERDICT: photometrically quiet at the few-percent level over 10.4 yr -> photometric variability
  does NOT explain the weak astrometric fit (F2=+8.39, RUWE=8.79). The poor fit must be orbital
  (DR4 decides; prereg threshold unchanged) or instrumental — not a variable-photocentre artifact.
  Caveat: quietness claim is floor-limited at ~2-3% by ATLAS systematics.

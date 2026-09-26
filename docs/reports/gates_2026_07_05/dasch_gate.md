# DASCH one-dip-wonders gate check -- 2026-07-05

## Verdict: MARGINAL (leaning NO-GO for a full ~25-100 object campaign; a small ~13-18 object mini-campaign is defensible)

## Funnel

| Step | Count | Note |
|---|---|---|
| 1. Raw pool (union of named source papers) | 112 | 31 ASAS-SN (JoHantgen+2026) + 81 ZTF (Tzanidakis&Davenport+2025) |
| 1b. VSX slow-fade / Gaia Alerts faders | NOT REACHED | VizieR B/vsx TAP query failed/timed out in the 1-day box; genuine gap, not a zero |
| 2. Dedupe by position | 112 | No coordinate overlap found between the two source lists (disjoint footprints/mag regimes) |
| 3. Brightness filter (quiescent <~14 mag, DASCH plate limit) | 39 | ASAS-SN: 31/31 (selection cut IS 13<g<14, true by construction). ZTF: ~8/81 (EXTRAPOLATED from the 29/81 rows visible in the arXiv preprint; the full 81-row table is withheld for the online-journal MRT and not yet public) |
| 4. Remove already-period-solved / DASCH-already-tried / wrong-class (aperiodic dust/YSO) | 18 (13 clean + 5 marginal) | Full per-object census done for ASAS-SN (all 31 read from paper text). ZTF: no per-object census possible (table not public); analogous attrition applied only as a soft estimate (~3 survivors) |
| **Final: named, verified survivors today** | **13 clean + 5 marginal = 18** | All ASAS-SN; ZTF contribution unverifiable pending journal table release |

**Against the referee's thresholds (GO >=~25, NO-GO <~10): 18 lands in the 10-25 MARGINAL band**, weighted toward the low end because the only concrete, checkable number is 13 (clean) to 18 (clean+marginal) — the extra ~3-21 from ZTF is a soft, unverifiable extrapolation, not confirmed survivors.

## DASCH DR7 access: CONFIRMED POSITIVE

- `daschlab` (official Python package, v1.0.0, MIT license, PyPI) installs cleanly in a fresh venv
  (needed system `pkg-config` + `cairo` via Homebrew for the `pycairo` dependency -- not present by
  default on this machine, added at the system level, NOT pip-installed into ostinato).
- End-to-end positive-control pull for a known bright variable (V* RY Cnc) succeeded:
  name resolve -> refcat (517 APASS sources) -> exposures (13,431 plates) -> light curve
  (3,653 photometric points spanning ~1880s-1990s) in **35 seconds wall-clock**, one process, no errors.
- Saved to `DASCH_CONTROL_lightcurve_RY_Cnc.ecsv`.
- **Throughput estimate for a future campaign**: ~30-40s/object end-to-end (dominated by the
  exposures + lightcurve API calls). A 25-object campaign ~15-25 min; a 100-object campaign
  ~1-1.5 hr of API wall-clock, trivially solo-scale and largely parallelizable.

## Scoop-risk finding: ACTIVE, NAMED RISK -- not yet fully materialized as a systematic sweep

- **Tzanidakis & Davenport (University of Washington) are simultaneously (a) the authors of the
  81-candidate ZTF dipper list itself, AND (b) actively DASCH-native, publishing dipper+DASCH work
  in real time in 2026** (Gaia-GIC-1 / Gaia20ehk, ApJL March 2026, arXiv:2603.10952 -- a
  single-object planetesimal-collision dipper characterized partly with archival photometry).
- No evidence found (arXiv or web search) of a **systematic** DASCH-plate sweep already published
  or announced across either the ASAS-SN 31 or ZTF 81 candidate lists as a batch. The specific
  niche ("recover eclipse periods for these named dipper lists via DASCH DR7") is NOT yet
  evaporated -- but the two people best positioned to do it own half the raw material and are
  demonstrably already fusing DASCH with dipper science this same season.
- **The ASAS-SN discovery team itself already tried DASCH** on one of their own targets
  (ASASSN-25bv / J085816-430955): "We looked at the DASCH light curve ... but there is too much
  scatter in the data to search for earlier events." This is a live, first-party data point that
  DASCH's photographic-plate noise floor is a real, non-trivial obstacle for this specific use
  case -- not just a hypothetical risk.
- `prior_art.py` arXiv screen returned 0 hits for both "DASCH photographic plate eclipse period
  recovery mystery dipper" and "DASCH century plate dipper stars systematic follow up campaign" --
  weak evidence of novelty (arXiv-only), consistent with (not proof against) an unpublished
  competing effort already underway.

## Key caveats / gaps (time-boxed, not fully closed)

1. **ZTF 81-row machine-readable table is not public.** The arXiv PDF/TeX source explicitly
   truncates it ("This table will be provided in its entirety in machine-readable form in the
   online journal") -- only 29/81 rows are visible. The ZTF contribution to the funnel is a soft
   extrapolation, not a verified count.
2. **VSX (`B/vsx`) VizieR TAP queries failed/timed out** in this session (both constrained-Type
   queries and a plain cone search returned empty or ReadTimeout) -- could not independently pull
   VSX slow-fade/deep-eclipse types as the spec requested. Treat as an unexplored lane, not a null.
3. **Gaia Alerts "fader" candidates**: not reached at all in the time-box.
4. **No per-object literature/ADS search was run for each of the 18 ASAS-SN survivors individually**
   beyond what the discovery paper itself already reports (the paper's own text IS a
   already-completed literature check for prior periods on each object, which is the strongest
   available proxy given the time-box).
5. The ZTF sample's mean/median distance (0.3-4.3 kpc for FGK dwarfs) and extinction-corrected
   G0~4-7 imply the **true apparent-G distribution skews well fainter than 14** for the bulk of the
   81 -- this is a real astrophysical mismatch between the lane spec's assumed "bright ZTF subset"
   and what the paper actually selected (a deep, all-sky-depth FGK MS sample, not a bright cut).

## Top-priority targets if proceeding (all from ASAS-SN, all verified bright + open + untried)

Highest priority = clean single-dip EBs, no existing period, never DASCH-attempted:

1. ASASSN-23ht (J073234-200049) -- min P>=8yr, symmetric single dip, upper MS
2. ASASSN-24cf (J175602+013135) -- RS CVn-tagged giant, deep/long single dip
3. ASASSN-23ik (J223332+565552) -- classified Algol-type but NO period ever published (best textbook case)
4. J073924-272916 -- red giant, ATLAS period is spurious, clean re-derivation target
5. J162209-444247 -- eROSITA coronal source, rotation period known but orbital period wide open
6. J183606-314826 -- AAVSO semi-regular tag exists but at wrong period (191d pulsation != orbital)
7. J190316-195739 -- RAVE spectroscopic confirmation of red-clump nature, clean target
8. J074007-161608, J094848-545959, J183210-173432, J205245-713514, J212132+480140,
   J225702+562312 -- remaining clean single-dip EBs, no disqualifying prior work

Then, lower priority (marginal/refinement value, rough periods already exist):
J005255+633515, J062510-075341, J124745-622756, J160757-574540, J202402+383938.

## Recommendation

Do **not** commit to the full 1-2 week ~25-100-object systematic campaign as scoped. The concrete,
verified survivor count (13-18) sits below the referee's GO threshold and only reaches the low end
of MARGINAL with an unverifiable ZTF extrapolation. Options, in order of preference:
(a) **shrink scope** to a fast 1-3 day mini-campaign on the 13 clean ASAS-SN single-dip survivors
    only (skip ZTF entirely until its table is public) -- this is cheap (DASCH throughput ~30-40s/obj)
    and low-risk, but should be framed as a small, bounded exercise, not the
    ~25-100 object sample originally envisioned;
(b) **wait** for the ZTF paper's ApJ machine-readable table to post (it is already accepted/in
    production per the ApJ 991, 118 citation found), then re-run this exact gate with the full
    81-row table and the VSX lane fixed -- likely raises the count meaningfully if the ZTF bright
    fraction holds near ~10%, i.e. roughly the same order of magnitude, so this may not change the
    verdict;
(c) **NO-GO** and reallocate to a higher-EV lane from the discovery menu, given the scoop-risk
    finding that the two authors of half the candidate pool are themselves fusing DASCH with
    dipper science in real time this season.

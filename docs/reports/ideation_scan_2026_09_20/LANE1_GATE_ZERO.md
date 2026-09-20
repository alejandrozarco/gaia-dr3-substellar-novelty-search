# Lane #1 — reference-poisoned outbursters: GATE ZERO RUN, LANE KILLED (2026-09-20)

Top-ranked lane from the v6 scan (novelty 4 / labor 3 = 1.33, GO_CANDIDATE from both
reviewers). Gate zero was run the same day. **It fails on the causal premise. Lane closed.**

## The claim under test

A dwarf nova in outburst *during* its own quadrant's ZTF reference window contaminates that
reference; difference imaging then subtracts the outburst away, so the object never alerts —
making it invisible to every alert-based CV search, including Duffy+2024's ML pipeline.

This is testable because **ZTF DR light curves are PSF photometry on SCIENCE images**, so they
report total flux and are not themselves biased by the reference.

## Setup (all verified live, IRSA TAP, ~97 s for the full table)

| | |
|---|---|
| `ztf.ztf_current_meta_ref` products | 196,357 |
| window span | median **272 d**, p25 89 d, p75 598 d, p90 1,339 d |
| short windows (≤30 d) | **11,407 = 5.81%** (gate estimated 4.93%) |
| zr short-window quadrants | **5,274**, median 28 d / 18 frames, ~3,850 deg² |
| VSX dwarf novae (UG*, dec > −31) falling in them | **1,111** |
| templates tested | 80, randomly sampled |

### New structural finding: references built in HOURS, not days

Duration distribution, which the gate had not resolved below 30 d:

| window duration | n | % | median nframes |
|---|---|---|---|
| **≤ 6 h (single high-cadence block)** | **1,375** | **0.82%** | 15 |
| 6–24 h (single night) | 142 | 0.08% | 15 |
| 1–7 d | 2,750 | 1.64% | 8 |
| 7–30 d | 4,676 | 2.79% | 16 |
| 30–365 d | 86,706 | 51.79% | 15 |
| > 1 yr | 71,778 | 42.87% | 16 |

**1,517 references (0.91%) are co-added from frames spanning under 24 hours**, 1,454 of them in
zr (~1,061 deg²). One template, Gaia19dtv, has a reference built from **40 frames inside a
1.5-hour window**, and its ZTF light curve contains **132 epochs at ~40 s cadence** in that same
block — a high-cadence campaign. Such a reference has *no temporal averaging at all*: if the
source was bright that hour, the reference is ~100% poisoned. This is a strictly stronger
poisoning regime than the 23–30 d windows the gate modelled, and it is worth remembering even
though it does not save this lane.

## Gate zero, part (a) — do the epochs exist? PASS

| status | n |
|---|---|
| SPARSE (<30 clean zr epochs) | 34 |
| NO_EPOCHS_IN_WINDOW | 28 |
| CLEAN (in-window not brighter) | 14 |
| **POISONED** (in-window median ≥1.0 mag brighter) | **2** |
| PARTIAL (brightest in-window epoch ≥1.0 mag brighter) | 2 |

**39% (18/46)** of usable templates have ZTF epochs inside their own reference window, and
**11% of those (2/18, i.e. 2.5% of the 80 sampled)** are genuinely poisoned. The mechanism is
real but rare — already implying a small absolute yield.

## Gate zero, part (b) — does poisoning suppress alerts? **FAIL**

The gate's own stop rule: *"If (a) is healthy but (b) fails, the causal premise is wrong and the
lane dies regardless of yield."*

| template | poisoning | ALeRCE |
|---|---|---|
| ZTF18abaaqcg (UGSU:, 23 d / 15 fr) | in-window median **2.32 mag** brighter | **857 detections**, alert id `ZTF18abaaqcg` |
| Gaia19dtv (UG, 1.5 h / 40 fr) | in-window median **1.60 mag** brighter | **220 detections**, alert id `ZTF18adaucrp` |
| MNIC V87 (PARTIAL) | Δ_bright 1.27 | 761 detections, `ZTF18abjhdlx` |
| MGAB-V774 (PARTIAL, Δ_median −0.07) | **not actually poisoned** | no alerts — see note |

**Both genuinely poisoned templates alert abundantly, and both carry ZTF alert designations** —
i.e. the alert stream itself discovered and named them. ZTF18abaaqcg's first alert (MJD 58281.43)
falls **one day after its reference window closed** (58280.35): it began alerting immediately.

## Why the premise is wrong

**Difference imaging is signed.** Contaminating a reference changes the sign and amplitude of the
residual; it does not remove it.

1. With the outburst in the reference, *quiescence* becomes a strong **negative** residual — which
   is detectable, not invisible.
2. Dwarf-nova outbursts vary in amplitude and duration; any outburst brighter or longer than the
   one frozen into the reference still yields a positive residual.
3. A 15–18 frame outlier-rejected co-add only partially retains a short outburst anyway, so the
   subtraction is rarely a clean cancellation.

### The distinction that matters, and it validates the other find

- **Constant-bright source + reference containing it → no change → NO alerts.** This is a real
  broker blind spot, and it is exactly J075308.47+003535.6: 442 ZTF detections, **zero** ALeRCE
  alerts.
- **Variable source + reference containing one state → still varies → STILL alerts.** This lane.

**The broker blind spot requires the source to be CONSTANT, not merely reference-contaminated.**
That sharpens lever #3 in the session ledger and is the durable result of this gate.

## Verdict

**Lane #1 CLOSED on its causal premise**, one afternoon after being ranked first by two
independent reviewers. Cost: ~2 h of queries. This is what gate zero is for.

Loose end worth a look, not pursued: **MGAB-V774** (RA 287.57227, Dec −7.24336) is a catalogued
dwarf nova reaching r = 18.48 against a median frame limit of 20.65 — comfortably detectable —
with **no ALeRCE alerts within 3″**, and its reference is *not* poisoned (Δ_median = −0.07). The
depth explanation does not obviously apply. Either a position/crowding artifact or a genuinely
unalerted known DN.

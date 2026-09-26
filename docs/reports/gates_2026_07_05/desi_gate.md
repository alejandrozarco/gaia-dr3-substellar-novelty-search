# Gate check: DESI DR1 repeat-RV dark-companion hunt — 2026-07-05

## 1. Access confirmation
- DESI DR1 public since **19 Mar 2025**, CC BY 4.0, no login. Direct download:
  https://data.desi.lbl.gov/public/dr1/ (+ EU mirror at PIC).
- MWS stellar catalogue (Koposov+2026, Open J. Astrophys. 9, arXiv:2505.14787,
  accepted/revised Jan 2026): >4M stars w/ RV+params; **>1M stars with >=2 epochs**
  — first DR1 release to expose **individual per-epoch RVs** (not just coadded).
- Per-epoch access point used here: `rv_output/240521/healpix/<survey>/<program>/<grp>/<healpix>/
  rvtab_spectra-<survey>-<program>-<healpix>.fits` (small, ~100KB-per-pixel files;
  RVTAB has VRAD/VRAD_ERR/TARGETID/SUCCESS/RVS_WARN, FIBERMAP has MJD/NIGHT/TILEID/
  GAIA_PHOT_G_MEAN_MAG/TARGET_DEC). Combined per-program files exist too (2.8-5.6 GB,
  not needed for the gate). Also accessible via Astro Data Lab TAP (desi_dr1 db).
- Full data model: https://desi-mws-dr1-datamodel.readthedocs.io/en/latest/

## 2. Method: real data pull (not just paper-reading)
Downloaded and parsed actual per-healpix FITS tables (not simulated):
- 40 healpix pixels, main-survey **bright** program (16,593 epoch rows, 12,244 unique
  TARGETIDs, 1,852 with >=2 good epochs [SUCCESS & RVS_WARN==0]).
- 25 pixels, main **dark** program (3,926 rows, 290 multi-epoch targets).
- 25 pixels, main **backup** program (12,122 rows, 3,499 multi-epoch targets).
Pixels drawn via unseeded-random group+pixel selection spread across the sky
(scripts in /tmp/gate_desi/fetch_pixels.py, fetch_dark_pixels.py, fetch_backup_pixels.py).
Sanity-checked individual targets: e.g. TARGETID 39633134978862419 has 2 same-night
epochs (same NIGHT, different TILEID) + 1 epoch 63 days later, VRAD self-consistent
within errors (-33.07, -31.68, -32.20 km/s) — output is physically sane.

## 3. Epoch-pair time-separation histogram (measured, combined 3 programs, n=10,426 pairs)
| bin | fraction |
|---|---|
| <1 day (same-night) | **18.9%** |
| 1-10 days | 26.8% |
| 10-100 days | 51.7% |
| >100 days | 2.6% |

By program (same-night PAIR fraction): bright 45.2%, dark 31.8%, **backup only 10.2%**
(backup repeats are NOT same-night splits as the "poor conditions" narrative in the
paper might suggest at first read — they are dominated by 10-100 day re-visits, likely
distinct survey-pass revisits). Max-baseline-per-target >=1 day: bright 51.5%, dark
72.1%, backup 81.2%.

KILL CONDITION 1 (>90% same-night pairs) — **does not fire**. Same-night fraction
(18.9% combined; worst single program 45.2%) is far below the 90% threshold.

## 4. Usable-pool size estimate (multi-day baseline AND dec>-30 [ZTF] AND 16<=G<18.5)
Scaled from measured per-program fractions to the full Table-3 (Koposov+2026) counts:

| program | full-VAC repeat objs | sample frac usable | scaled usable est |
|---|---|---|---|
| main-bright | 443,413 | 32.6% | ~144,600 |
| main-dark | 240,100 | 35.9% | ~86,100 |
| main-backup | 627,492 | 39.8% | ~249,600 |
| **TOTAL** | 1,311,005 | — | **~480,000** |

KILL CONDITION 2 (<100-200k usable pool) — **does not fire**. Point estimate ~480k,
~2.4-4.8x the kill floor. Even the single weakest, most conservative slice alone
(main-bright, most similar in character to a "clean" MWS sample) is ~145k — already
at the top of the referee's 100-200k floor by itself, before adding dark+backup.

Caveats on the estimate (stated for honesty, not hidden):
- Sample is 90 healpix pixels total (~3% by pixel count of ~3200 nside=32-equivalent
  populated pixels), drawn pseudo-randomly but NOT a formal probability sample;
  treat the 480k as order-of-magnitude, not a precise forecast.
- "Usable" cut (dec>-30, 16<=G<18.5, baseline>=1d) is a simple placeholder matching
  the gate's stated bar; does not yet apply full ZTF depth/cadence-at-that-dec
  weighting, extinction, or per-star epoch-count (>=3 epochs would tighten the orbit-
  fitting requirement and shrink the pool somewhat).
- G-mag distribution of the multi-epoch sample is favorable: median G=17.98, 92.8%
  in the target 16-20 range (the exact regime the lane wants) — the sample is not
  contaminated by bright easy-Gaia-RVS stars.
- Backup-program footprint is Gaia-selected (wider/more uniform sky coverage than
  bright/dark, which follow DECaLS), so dec>-30 cut may be less limiting there.

## 5. Prior-art / scoop finding
- `scripts/litcheck/prior_art.py` (arXiv-only, strict per-term-AND-phrase query)
  returned near-zero hits for several DESI+RV+binary phrasings — the tool's query
  builder is too strict for this search (quotes every single whitespace token),
  producing false negatives. Not fixed here (out of scope for a gate) but flagged
  as a tool limitation — see below.
- Direct WebSearch/WebFetch located the flagged paper:
  **"A High-amplitude Radial Velocity Variable in DESI DR1"**, Aiden Smith,
  RNAAS 10, 25 (Jan 2026), https://iopscience.iop.org/article/10.3847/2515-5172/ae3f28
  - **Single author, single-object discovery note** (not a systematic survey paper).
  - Reports ONE candidate: Gaia DR3 3802130935635096832, DeltaRV_max~146-151 km/s
    over 38.9 days (4 epochs), flagged as needing resolved follow-up to rule out a
    blended/contaminating neighbour (0.688" separation, Delta_mag~2.21) rather than
    a genuine compact companion.
  - Abstract explicitly states the author ran "a systematic search for dark
    companions among multi-epoch targets" in DESI DR1 MWS but **published only
    the single most compelling hit**, not the full candidate list or methodology
    paper. This is consistent with the referee's read: a full
    systematic search + f(M) analysis + a proper candidate catalogue is NOT yet
    published. The niche (systematic f(M)-based compact-companion catalogue) is
    open, but a competitor is demonstrably already mid-build (submitted Jan 2026,
    ~6 months ahead) and will likely scoop the single best object if it recurs
    in our sample.
  - ACTION IF GO: front-filter Gaia DR3 3802130935635096832 out of any future
    candidate list immediately (already publicly claimed); treat the Smith(2026)
    note's existence as elevated urgency/move-soon risk, not a blocker.

## 6. Verdict: GO
None of the two stated kill conditions fire, and the prior art is a single-object
note (one object, not the lane).

Decisive numbers:
- Same-night epoch-pair fraction: **18.9%** (kill floor: >90%) — passes by a wide margin.
- Usable multi-day-baseline + ZTF + mag pool: **~480,000** (kill floor: 100-200k) —
  passes, ~2.5-5x over floor even before more careful cuts.
- Access: **public today**, direct download + Data Lab TAP, well-documented per-epoch
  files with all needed columns (TARGETID, EXPID, MJD/NIGHT/TILEID, VRAD, VRAD_ERR,
  G mag, dec).
- Scoop: one single-object RNAAS note (Jan 2026) exists; no systematic-survey paper
  found. Niche open but move-soon warranted.

Recommend proceeding to the full 3-4 week build (per the referee's honest-yield
framing: ~10-30 clean high-DeltaRV survivors expected, 0-2 reaching f(M)>1, mode
for genuine NS/BH = zero).

## Known tool issue (flagged, not fixed)
`scripts/litcheck/prior_art.py`'s `build_query()` quotes every whitespace-split
token as its own required phrase (`all:"DR1" AND all:"radial" AND ...`), which
over-constrains arXiv's search and produces false "no hits" on real prior art
(confirmed here: it missed a paper this gate found by direct WebSearch in under a
minute). Suggest a follow-up task to relax the query construction (e.g., drop
quoting single common tokens, or fall back to an unquoted `all:` OR-of-phrases
strategy) so the mandated per-lane prior-art gate is actually reliable.

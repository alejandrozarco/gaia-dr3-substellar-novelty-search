# Tier-1 NS pool archival-RV triage — re-run (2026-09-22)

`scripts/ns_pool_triage_2026_05_28.py`, unchanged, re-run through `run.py` with the output paths moved out of
`/tmp`. The 2026-05-28 run wrote only to `/tmp`; its per-source verdicts were lost when `/tmp` was cleared, and
eight register rows carried "verdict unrecoverable".

| verdict | 2026-05-28 (recorded totals) | 2026-09-22 re-run |
|---|---:|---:|
| NO_ARCHIVAL_RV | 117 | 117 |
| INCONCLUSIVE | 40 | 40 |
| CORROBORATED | 2 | 2 (2127900555635640832, 3378588057203660160) |
| REFUTED | 2 | 2 (2129927539681151872, 1379150557507688960) |

Positive control: 3378588057203660160 (HD 264291) returns CORROBORATED with 50 archival epochs, as in May.

The eight previously unrecoverable verdicts are all NO_ARCHIVAL_RV (no epochs in LAMOST LRS/MRS, APOGEE DR17,
RAVE DR6 or GALAH DR3): 1736313273270398720, 3056409026894392448, 4056403406274320768, 5815441557668429312,
6184510360847047808, 6441920468296049280, 6695559040407753984, 6846249479816261504. Four of them
(4056403406274320768, 5815441557668429312, 6184510360847047808, 6846249479816261504) carry the F#33
period-significance flag.

Files: `results.json` (all 161, per-source census and verdict), `report.md` (script report), `run.py`.

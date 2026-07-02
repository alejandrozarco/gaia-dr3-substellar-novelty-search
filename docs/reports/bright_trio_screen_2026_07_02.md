# Bright-trio archival photometry screen — Hipparcos / ASAS-3 / KELT (2026-07-02)

Report of record (agent's /tmp REPORT.md failed to write; /tmp is volatile — this copy is durable).
Closes the queued follow-up to the 2026-07-02 ASAS-SN bright-pool screen's G≲10.5 saturation blind spot.
Guardrail applied throughout: red-noise LOCAL null (power vs 600 random trial periods 300–1500 d, same LC)
+ cross-dataset/camera coherence, per the institutionalized 2026-07-02 rule.

Identity pre-check: all three source_ids SIMBAD-verified; **HD 207141 = Gaia DR3 6811355413155399040 confirmed exact**.
NSS periods from ledgers: HD 157033 none; HD 264291 P=999.42 d; HD 207141 P=951.95 d.

## Per-target × per-archive results

| target | archive | epochs | baseline | floor (mmag) | power@P vs local null | power@P/2 vs local null | verdict |
|---|---|---|---|---|---|---|---|
| HD 157033 (4111149395881722496) | Hipparcos | 75 transits | 1989.85–1993.21 | scatter=25 (aggregate only) | n/a (no P) | n/a | QUIET (ESA flag=constant); raw epochs not publicly exposed |
| HD 157033 | ASAS-3 | 781 | 2000.3–2009.0 | 13.3 | n/a | n/a | QUIET; one 0.3-mag "event" = single-frame artifact |
| HD 157033 | KELT | 0 | — | — | — | — | UNUSABLE (not in footprint) |
| HD 264291 (3378588057203660160) | Hipparcos | 0 | — | — | — | — | UNUSABLE (genuinely absent; Tycho-2 control ok) |
| HD 264291 | ASAS-3 | 368 | 2002.9–2009.9 | 17.8 | FAP=0.868 | FAP=0.101, fails dataset coherence (2.6× amplitude mismatch 34-pt vs 323-pt) | QUIET; corroborates ASAS-SN P/2 kill |
| HD 264291 | KELT | 0 | — | — | — | — | UNUSABLE (in footprint N04, saturation-excluded) |
| HD 207141 (6811355413155399040) | Hipparcos | 0 | — | — | — | — | UNUSABLE (genuinely absent; Tycho-2 control ok) |
| HD 207141 | ASAS-3 | 544 | 1998.4–2009.7 | 11.9 | FAP=0.561 (below null median) | FAP=0.643 (below null median) | QUIET, clean nulls |
| HD 207141 | KELT | 0 | — | — | — | — | UNUSABLE (not in footprint) |

## Net effect
- **HD 264291, HD 207141: photometric lane CLOSED** — ASAS-3 (decade-earlier, fully independent instrument) corroborates the ASAS-SN nulls; no further photometric lever expected.
- **HD 157033: mostly closed** — no NSS period to test, but the zero-outburst quiescence baseline now spans ~36 yr (1989–2025), further weakening an actively-interacting luminous companion; the 0.4–6 M⊙ ambiguity itself is untouched (still telescope/DR4-gated).

## Archive lessons (documented dead-ends, not "unreachable")
- Hipparcos epoch photometry: raw epochs are NOT exposed by VizieR I/239 or the ESA CGI (aggregate stats only); 2/3 targets genuinely absent from Hipparcos despite V<10 (verified with Tycho-2 positive controls).
- KELT: two distinct failure modes — true field gaps (HD 157033, HD 207141) vs bright-saturation exclusion (HD 264291), both confirmed against the archive's own extracted-source data.
- ASAS-3 remains the workhorse for V<10 southern/equatorial targets: 368–781 epochs, 12–18 mmag floors, ~1998–2009.

Provenance: /tmp/bright_trio_screen/ (asas3_*.dat raw, asas3_parsed_*.csv, asas3_results.json/csv, master_table.csv,
parse_asas3.py + analyze_asas3.py reusable); 9 per-object ledger rows appended 2026-07-02.

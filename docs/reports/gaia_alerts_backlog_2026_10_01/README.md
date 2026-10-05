# Gaia Science Alerts unclassified backlog (2026-10-01)

- `g4_backlog.csv`: WARNING - its `Source` column (Gaia DR3 id) was stored as a float; 136 of 183 checked ids are wrong in
  the last digits. Use the `DR3Name` strings or a position match, never `Source`.
- `candidates.csv`: pilot (33 alerts) - 5 candidates + 1 weak; ids verified by position.
- `full/candidates_full.csv`: full run over the 183 alerts with alert range >= 1.5 mag - 39 candidates;
  all 39 Gaia DR3 ids verified by a 1.5 arcsec VizieR I/355 position match. `full/weak_list.csv` (114), `full/gate_rejects.csv` (30).
- VSX accepts type "Microlens" (Gaia16aye, Gaia19bld are VSX Microlens entries, discoverer Gaia).

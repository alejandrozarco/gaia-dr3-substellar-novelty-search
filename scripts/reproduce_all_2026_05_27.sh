#!/bin/bash
# Master reproduction script for the 2026-05-18 companions-of-all-kinds pivot.
# Run in order; each step depends on previous outputs.
#
# Total time: ~45 min with reasonable Gaia archive load.

set -e
cd /Users/legbatterij/claude_projects/gaia-recovered-2026-05-27
PY=/Users/legbatterij/claude_projects/ostinato/.venv/bin/python

echo "=== Step 1: ATNF binary pulsar test set ==="
$PY -u scripts/atnf_binary_pulsars_2026_05_18.py

echo "=== Step 2: PN central binary curated set ==="
$PY -u scripts/pn_central_binary_test_set_2026_05_18.py

echo "=== Step 3: BH validation against Gaia BH1/2/3 ==="
$PY -u scripts/companions_of_all_kinds_validate_bhs_2026_05_18.py

echo "=== Step 4: Main companions hunt (56k sources, ~10 min) ==="
$PY -u scripts/companions_hunt_all_mass_classes_2026_05_18.py

echo "=== Step 5: SB2 negative recovery ==="
$PY -u scripts/sb2_negative_recovery_2026_05_18.py

echo "=== Step 6: Wider 2nd-pass hunt (51k, ~15 min) ==="
$PY -u scripts/wider_hunt_relaxed_cuts_2026_05_27.py

echo "=== Step 7: Derive defensible BH/NS subsets ==="
$PY -u scripts/derive_defensible_subsets_2026_05_18.py

echo "=== Step 8: ML classifier ==="
$PY -u scripts/ml_classifier_run_2026_05_27.py

echo "=== Step 9: Amateur transit candidates ==="
$PY -u scripts/amateur_transit_candidates_2026_05_18.py

echo "=== Step 10: Triage 42 defensible (12 BH + 30 NS) ==="
$PY -u scripts/triage_fast_2026_05_27.py

echo "=== Step 11: Parallel deep dive on top BH leads with Filter #31 ==="
$PY -u scripts/parallel_deep_dive_2026_05_27.py

echo ""
echo "=== ALL DONE ==="
echo ""
echo "Generated CSVs:"
ls -la data/intermediate/*.csv
ls -la *.csv | grep -E "(dormant|triage|amateur|parallel|novelty_candidates_v1)"

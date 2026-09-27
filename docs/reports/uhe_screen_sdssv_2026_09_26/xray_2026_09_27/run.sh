#!/bin/bash
# Radio / X-ray / gamma-ray counterpart check (scripts/mwcheck/mwcheck.py) of the UHE candidates and of the known UHE stars
# (../data/known_uhe_all.csv, de-duplicated within 3", plus KPD 0005+5106). Run from the repository root.
P=docs/reports/uhe_screen_sdssv_2026_09_26/xray_2026_09_27
for g in 5671975077144346112 4711031463842628736 4844689579080133248 6644780943442193664 3597350571454888448 4749559145849819008 4866851575967878144 1008280341952767232 2120335400240968448 303909583762954368; do
  python scripts/mwcheck/mwcheck.py --gaia $g > $P/candidates/$g.txt 2>&1; done
tail -n +2 $P/controls/list.csv | while IFS=, read name ra dec tag; do python scripts/mwcheck/mwcheck.py --ra $ra --dec $dec > $P/controls/$tag.txt 2>&1; done

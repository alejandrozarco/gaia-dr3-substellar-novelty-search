
## Random-window test of the ATLAS window folds (2026-09-30)
`random_window_check.py` compares the maximum Lomb-Scargle power within +-0.01 c/d of the TESS frequency with 500 windows of the same width at random frequencies (0.5-20 c/d). In two batch-8 targets the window folds were significant at f, 2f and f/2 alike, and the random-window test gave p = 0.34-0.76: excess power over the whole periodogram, not a signal at f. Results for all window-fold detections: `random_window_earlier.txt` (batches 1-7) and the batch-8 journals.
- Confirmed at p <= 0.004 in at least one band: 20 stars, including every star with a journal or public page.
- Not confirmed: WDJ021515.24-465207.42, WDJ160728.09-822336.66 (batch 8), WDJ192858.85+542950.07.
- Weak (p 0.008-0.02 in o only): WDJ043125.38-392044.13, WDJ041955.84-522122.89 (marginal).

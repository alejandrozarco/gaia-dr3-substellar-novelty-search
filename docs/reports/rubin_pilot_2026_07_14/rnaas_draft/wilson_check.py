#!/usr/bin/env python3
"""Wilson binomial confidence intervals for the RNAAS note.

Inputs (verified against
docs/reports/rubin_pilot_2026_07_14/flags/REPORT.md + flags_sample.csv):
  - hostless_candidate (ELEPHANT):        0 artifacts / 10 vetted (census of 10 unique objects)
  - extragalactic_lt20mag_candidate:      0 artifacts / 10 vetted (of 26 unique objects)
  - extragalactic_new_candidate (faint):  15 artifacts / 20 vetted (of 702 unique objects; seed 20260714)
  - overall stratified sample:            15 / 40
Channel populations (unique objects / alerts), week MJD 61228-61235:
  hostless 10/15, lt20mag 26/40, new 702/717 -> totals 738/772.

Interval: Wilson score interval at 68.27% ("1-sigma", z = 1.0).
  center = (p + z^2/2n) / (1 + z^2/n)
  half   = z/(1 + z^2/n) * sqrt(p(1-p)/n + z^2/4n^2)
"""

import math

Z = 1.0  # 68.27% two-sided normal coverage ("1 sigma")


def wilson(k, n, z=Z):
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, center - half), min(1.0, center + half)


def show(label, k, n):
    lo, hi = wilson(k, n)
    print(f"{label:45s} {k:2d}/{n:2d} = {k/n:6.3f}  Wilson68% [{lo:.4f}, {hi:.4f}]")
    return lo, hi


print("Per-channel Wilson 68.27% (z=1) intervals")
lo_h, hi_h = show("hostless_candidate (census)", 0, 10)
lo_b, hi_b = show("extragalactic_lt20mag (bright)", 0, 10)
lo_f, hi_f = show("extragalactic_new_candidate (faint tail)", 15, 20)
lo_o, hi_o = show("overall stratified sample (NOT stream-rep.)", 15, 40)

print("\nSensitivity: the 2 AMBIGUOUS faint-channel objects counted as artifacts")
show("extragalactic_new, ambiguous->artifact", 17, 20)

# ---- stream-weighted rate ----------------------------------------------------
# The stratified design over/under-samples channels, so the stream-level rate is
# the population-weighted combination of per-channel estimates:
#   p_stream = sum_i w_i * p_i,  w_i = N_i / N_tot
# Interval: weighted combination of the per-channel Wilson bounds (conservative:
# assumes fully correlated extremes; dominated by the faint channel anyway).

for weight_kind, (Nh, Nb, Nf) in {
    "unique objects": (10, 26, 702),
    "alerts": (15, 40, 717),
}.items():
    Nt = Nh + Nb + Nf
    wh, wb, wf = Nh / Nt, Nb / Nt, Nf / Nt
    p = wh * 0.0 + wb * 0.0 + wf * (15 / 20)
    lo = wh * lo_h + wb * lo_b + wf * lo_f
    hi = wh * hi_h + wb * hi_b + wf * hi_f
    print(f"\nStream-weighted by {weight_kind:14s} (N={Nt}):"
          f"  p = {p:.4f}  bounds [{lo:.4f}, {hi:.4f}]")
    print(f"  weights: hostless {wh:.4f}, lt20mag {wb:.4f}, faint-new {wf:.4f}")

print("""
Arithmetic spot-checks (by hand):
  0/10:  z^2/n = 0.1 -> denom 1.1; center = 0.05/1.1 = 0.045455;
         half = (1/1.1)*sqrt(0 + 1/400) = 0.045455  -> [0, 0.090909]
  15/20: denom 1.05; center = 0.775/1.05 = 0.738095;
         half = (1/1.05)*sqrt(0.009375 + 0.000625) = 0.095238 -> [0.642857, 0.833333]
  15/40: denom 1.025; center = 0.3875/1.025 = 0.378049;
         half = (1/1.025)*sqrt(0.0058594 + 0.00015625) = 0.075669 -> [0.302380, 0.453718]
  weighted (unique): 0.75 * 702/738 = 0.713415
""")

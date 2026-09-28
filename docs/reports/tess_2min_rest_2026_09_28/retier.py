"""Re-tier a sweep's candidates_gated.csv with the corrected attribution requirement (PDCSAP amplitude, not amplitude/CROWDSAP);
same rules as bulk_gate.py otherwise. Writes candidates_retiered.csv and prints the tier changes. Usage: python retier.py <candidates_gated.csv>"""
import sys, numpy as np, pandas as pd
C = pd.read_csv(sys.argv[1], dtype={"gaia": str}); C["known_period"] = C.known_period.fillna("").astype(str); C["ours"] = C.ours.fillna(False).astype(bool) if "ours" in C else False
C["implied_amp_old"] = C.implied_amp; C["implied_amp"] = C.amp.round(3)
slow_ok = (C.f >= 1.5) | ((C.detr_ratio > 0.5) & (C.n_detected >= 2))
C["tier_old"] = C.tier
C["tier"] = np.where(C.known_period.str.startswith("match"), "known", np.where(C.ours, "ours",
            np.where((C.implied_amp < 0.5) & slow_ok & ((C.n_detected >= 2) | (C.fap_min < 1e-30)), "A",
            np.where((C.implied_amp < 1.0) & slow_ok, "B", "contaminated/systematic"))))
C.to_csv(sys.argv[1].replace("candidates_gated", "candidates_retiered"), index=False)
print(sys.argv[1]); print(pd.crosstab(C.tier_old, C.tier))
re = C[(C.tier_old == "contaminated/systematic") & (C.tier == "A")]
print("reopened A:", len(re), "| with >= 2 detected sectors:", int((re.n_detected >= 2).sum()), "| north of dec -31 (ZTF):", int((re.Dec > -31).sum()) if "Dec" in C else int((re.dec > -31).sum()))

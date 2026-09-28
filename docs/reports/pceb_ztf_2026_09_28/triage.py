"""Triage of the DESI DR1 WD+M (PCEB candidate) ZTF period search (ztf_results.csv, produced by the Jestin-sweep search script on
ztf_sample.csv). Detection = FAP < 1e-8 and fundamental semi-amplitude > 5 sigma in g or r. Flags: 1-day alias families
(f within 0.005 c/d of n x 1 or n x sidereal day), and frequency clusters shared by >= 3 detections within 0.003 c/d (ZTF systematics).
Writes pceb_detections.csv in the schema of the per-star period gate (docs/reports/jestin_ztf_2026_09_27/gate/period_gate.py).
Usage: python triage.py"""
import os, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(os.path.join(H, "ztf_results.csv"), dtype={"GaiaDR3": str, "targetid": str})
ok = R[R.status == "ok"].copy()
sig = (ok.A1_zg > 5 * ok.eA1_zg) | (ok.A1_zr > 5 * ok.eA1_zr)
D = ok[(ok.fap_top < 1e-8) & sig.fillna(False)].copy()
sid = 1.0027379
D["alias"] = [any(abs(f - n * sid) < 0.005 for n in range(1, 50)) or any(abs(f - n) < 0.01 for n in range(1, 50)) for f in D.f_top]
f = D.f_top.values; D["f_cluster"] = [int(np.sum(np.abs(f - x) < 0.003)) for x in f]
D["gaia_agree"] = ""
out = D.rename(columns={"name": "WDJname", "G": "Gmag"})[["GaiaDR3", "WDJname", "RA_ICRS", "DE_ICRS", "Gmag", "cls", "f_top", "fap_top", "A1_zg", "A1_zr", "r_over_g", "alias", "f_cluster", "gaia_agree"]]
out["P_h"] = 24 / out.f_top
out.sort_values("fap_top").to_csv(os.path.join(H, "pceb_detections.csv"), index=False)
print(R.status.value_counts().to_dict())
print(len(ok), "ok;", len(D), "detected;", int(D.alias.sum()), "alias-flagged;", int((D.f_cluster >= 3).sum()), "in clusters;",
      int(((~D.alias) & (D.f_cluster < 3)).sum()), "to gate")
print(out[(~out.alias) & (out.f_cluster < 3)][["GaiaDR3", "WDJname", "cls", "Gmag", "P_h", "fap_top", "A1_zg", "A1_zr", "r_over_g"]].to_string(index=False))

"""Triage of the TESS 2-min S70-106 white-dwarf sweep (scratchpad sweep.csv / sweep_rest.csv).
1. Candidate stars: per-light-curve detections (status ok, fap1 < 1e-10, f1 >= 0.3 c/d), sector-shared frequency clusters
   (>= 4 light curves of different stars within 0.005 c/d in one sector) removed; a star qualifies with >= 2 sectors agreeing
   within 0.01 c/d (or a harmonic), or a single sector at fap < 1e-20 with the detrended power confirming (pow ratio > 0.5),
   or fap < 1e-30.
2. Gate per candidate: the period-gate of the ZTF lanes (VizieR all-table period columns, TIC x Oliveira da Rosa+2024, MWDD,
   SIMBAD), plus the Reindl+2021 source tables by alias, the known-UHE list, and Jestin+2026/VSX through the VizieR cone.
Usage: python triage.py <sweep.csv> [more sweeps...] (writes candidates.csv here; gate via gate_run.sh)."""
import sys, os, re, subprocess, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); SP = os.environ.get("WD_WORKDIR", ".")  # directory holding the downloaded inputs named below
S = pd.concat([pd.read_csv(f, dtype={"gaia": str}) for f in sys.argv[1:]], ignore_index=True)
S = S[S.status == "ok"].copy(); print(len(S), "light curves,", S.gaia.nunique(), "stars")
W = pd.read_csv(f"{SP}/tess2min/wd_2min_S70_S106.csv", dtype={"GaiaEDR3": str}).drop_duplicates("GaiaEDR3").set_index("GaiaEDR3")
D = S[(S.fap1 < 1e-10) & (S.f1 >= 0.3)].copy()
D["cluster"] = [int(((D.sector == s) & (np.abs(D.f1 - f) < 0.005) & (D.gaia != g)).sum()) for s, f, g in zip(D.sector, D.f1, D.gaia)]
rows = []
for g, x in D.groupby("gaia"):
    x = x[x.cluster < 3]
    if not len(x): continue
    allsec = S[S.gaia == g]; xb = x.sort_values("fap1"); f0 = xb.f1.iloc[0]
    agree = [s for s, f in zip(x.sector, x.f1) if min(abs(f - f0), abs(f - 2 * f0), abs(f - f0 / 2), abs(2 * f - f0)) < 0.01]
    pr = xb.pow1_detrended.iloc[0] / xb.pow1.iloc[0] if xb.pow1.iloc[0] > 0 else np.nan
    ok = len(agree) >= 2 or (x.fap1.min() < 1e-20 and pr > 0.5) or x.fap1.min() < 1e-30
    if not ok: continue
    w = W.loc[g]
    rows.append(dict(gaia=g, WDJname=w.WDJname, tic=int(x.tic.iloc[0]), RA=w.RA_ICRS, Dec=w.DE_ICRS, G=round(w.Gmag, 2), Tmag=round(w.Tmag, 2), plx=round(w.Plx, 2),
                     TeffH=w.TeffH, MassH=w.MassH, n_sectors=len(allsec), n_detected=len(agree), f=f0, P_h=round(24 / f0, 4), P_min=round(1440 / f0, 2),
                     fap_min=x.fap1.min(), amp=round(x.amp1.median(), 4), crowdsap=round(float(allsec.crowdsap.min()), 3), detr_ratio=round(pr, 2),
                     sectors=" ".join(map(str, sorted(x.sector))), dip_sigma=round(float(x.get("dip_sigma", pd.Series(dtype=float)).max()), 1) if "dip_sigma" in x else np.nan))
C = pd.DataFrame(rows).sort_values("fap_min"); C.to_csv(os.path.join(H, "candidates.csv"), index=False)
print(len(C), "candidate stars ->", os.path.join(H, "candidates.csv"))
# gate input in the period_gate.py shape
gi = C.rename(columns={"gaia": "GaiaDR3", "RA": "RA_ICRS", "Dec": "DE_ICRS", "G": "Gmag", "f": "f_top", "fap_min": "fap_top"}).copy()
gi["A1_zg"] = C.amp.values; gi["A1_zr"] = 0; gi["r_over_g"] = 0; gi["alias"] = False; gi["gaia_agree"] = ""
gi.to_csv(os.path.join(H, "gate_input.csv"), index=False)
# Reindl + known-UHE by alias/name (local, fast)
uhe = pd.read_csv(os.path.join(H, "..", "uhe_screen_sdssv_2026_09_26", "data", "known_uhe_all.csv"), dtype=str)
RT = open(os.path.join(H, "..", "hot_periodic_wd_2026_09_27", "prior_art", "reindl2021_arXiv2102.04504_UHE.tex")).read()
for _, r in C.iterrows():
    inuhe = (uhe.gaia == r.gaia).any()
    jn = str(r.WDJname); short = jn[3:8] if jn.startswith("WDJ") else ""
    inreindl = bool(short) and (short in RT)
    if inuhe or inreindl: print("FLAG", r.gaia, jn, "known_uhe" if inuhe else "", "reindl-name-hit" if inreindl else "")

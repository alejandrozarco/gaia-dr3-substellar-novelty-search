"""Select periodic white dwarfs from sweep.csv. Per light curve: status ok, fap1 < 1e-10, f1 >= 0.3 c/d.
Systematics: f1 values shared (within 0.005 c/d) by >= 4 light curves of different stars in the same sector are flagged 'cluster'.
Per star: detection in >= 2 sectors with f1 within 0.01 c/d (or one of them the 2x/0.5x harmonic), or a single sector with fap1 < 1e-20.
Output: candidates.csv (one row per star) with sectors, f, P, amplitude (fraction of PDCSAP flux), CROWDSAP, flags."""
import pandas as pd, numpy as np
S = pd.read_csv("sweep.csv", dtype={"gaia": str}); S = S[S.status == "ok"].copy()
W = pd.read_csv("wd_2min_S70_S106.csv", dtype={"GaiaEDR3": str}).drop_duplicates("GaiaEDR3").set_index("GaiaEDR3")
D = S[(S.fap1 < 1e-10) & (S.f1 >= 0.3)].copy()
D["cluster"] = [int(((D.sector == s) & (np.abs(D.f1 - f) < 0.005) & (D.gaia != g)).sum()) for s, f, g in zip(D.sector, D.f1, D.gaia)]
rows = []
for g, x in D.groupby("gaia"):
    x = x[x.cluster < 3]
    if not len(x): continue
    allsec = S[S.gaia == g]; f0 = x.sort_values("fap1").f1.iloc[0]
    agree = [s for s, f in zip(x.sector, x.f1) if min(abs(f - f0), abs(f - 2 * f0), abs(f - f0 / 2)) < 0.01]
    ok = len(agree) >= 2 or (len(allsec) == 1 and x.fap1.min() < 1e-20) or (x.fap1.min() < 1e-30)
    if not ok: continue
    w = W.loc[g]
    rows.append(dict(gaia=g, WDJname=w.WDJname, tic=int(x.tic.iloc[0]), G=round(w.Gmag, 2), TeffH=w.TeffH, MassH=w.MassH, n_sectors=len(allsec), n_detected=len(agree),
                     f=f0, P_h=round(24 / f0, 4), P_min=round(1440 / f0, 2), fap_min=x.fap1.min(), amp=round(x.amp1.median(), 4), crowdsap=round(allsec.crowdsap.min(), 3),
                     sectors=" ".join(map(str, sorted(x.sector))), pow_detr_ratio=round((x.pow1_detrended / x.pow1).median(), 2)))
C = pd.DataFrame(rows).sort_values("f", ascending=False); C.to_csv("candidates.csv", index=False)
print(len(S), "light curves;", S.gaia.nunique(), "stars;", len(D), "LC detections;", len(C), "candidate stars")
print((C.f > 10).sum(), "with P < 2.4 h;", ((C.f > 1) & (C.f <= 10)).sum(), "with 2.4-24 h;", (C.f <= 1).sum(), "with P > 24 h")
pd.set_option("display.width", 250); print(C.head(40).to_string(index=False))

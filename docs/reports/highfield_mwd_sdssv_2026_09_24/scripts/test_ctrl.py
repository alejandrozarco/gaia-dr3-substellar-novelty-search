import pandas as pd, numpy as np, spec as S, plots as P
d = pd.read_csv("master.csv", low_memory=False)
ids = [int(x) for x in open("ctrl_ids.txt").read().split()]
ent = []
for sid in ids:
    r = d[d.sdss_id == sid].iloc[0]; s = S.load_star(sid)
    mt = S.metrics(s["lam"], s["flux"], s["ivar"])
    lab = f"CTRL {r.mwdd_wdid} B={float(r.mwdd_B):.0f}MG | SW {r.classification} | S/N {s['snr']:.0f} | Tph {r.teff_phot if 'teff_phot' in r else ''}"
    print(sid, r.mwdd_wdid, "excess %.3f rms %.3f noise %.3f ndips %d" % (mt["excess"], mt["rms"], mt["noise"], len(mt["dips"])), [(round(a), round(b, 3)) for a, b, c in mt["dips"]][:12])
    ent.append((lab, s["lam"], s["flux"], s["ivar"]))
    P.trumpet(s["lam"], s["flux"], s["ivar"], f"plots/ctrl_{sid}_trumpet.png", title=lab)
P.grid(ent, "plots/ctrl_grid.png", ncol=2, title="positive controls (MWDD published fields)")

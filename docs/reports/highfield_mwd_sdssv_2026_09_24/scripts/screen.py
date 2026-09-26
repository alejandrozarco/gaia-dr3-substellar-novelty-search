# Screen a list of sdss_ids: feature metrics + grid plots (12 per page). usage: python screen.py <idfile> <tag>
import sys, json, pandas as pd, numpy as np, spec as S, plots as P
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id")
ids = [int(x) for x in open(sys.argv[1]).read().split()]; tag = sys.argv[2]
res = {}; ent = []
for sid in ids:
    try:
        s = S.load_star(sid)
    except Exception as e:
        print("HOLE load", sid, e); continue
    if s is None: print("HOLE empty", sid); continue
    r = d.loc[sid]; mt = S.metrics(s["lam"], s["flux"], s["ivar"])
    res[sid] = dict(gaia=int(r.gaia_dr3_source_id), cls=r.classification, snr=s["snr"], excess=mt["excess"], noise=mt["noise"],
                    ndips=len(mt["dips"]), dips=[(round(a), round(b, 3), round(c, 1)) for a, b, c in mt["dips"]],
                    teff_phot=float(r.teff_phot) if "teff_phot" in r and pd.notna(r.teff_phot) else None, MG=float(r.MG), nmf_rchi2=s["nmf_rchi2"])
    lab = f"{sid} G{int(r.gaia_dr3_source_id)} | {r.classification} | S/N {s['snr']:.0f} | G {r.g_mag:.1f} MG {r.MG:.1f} | Tph {float(r.teff_phot):.0f}" if pd.notna(r.get('teff_phot', np.nan)) else f"{sid} G{int(r.gaia_dr3_source_id)} | {r.classification} | S/N {s['snr']:.0f}"
    ent.append((lab, s["lam"], s["flux"], s["ivar"]))
json.dump(res, open(f"screen_{tag}.json", "w"), indent=1)
for k in range(0, len(ent), 12):
    P.grid(ent[k:k + 12], f"plots/screen_{tag}_{k // 12:02d}.png", ncol=2, title=f"screen {tag} page {k // 12}")
for sid, v in sorted(res.items(), key=lambda kv: -kv[1]["excess"]):
    print(sid, v["gaia"], v["cls"], f"S/N {v['snr']:.0f} exc {v['excess']*100:.1f}% ndip {v['ndips']}", v["dips"][:8])

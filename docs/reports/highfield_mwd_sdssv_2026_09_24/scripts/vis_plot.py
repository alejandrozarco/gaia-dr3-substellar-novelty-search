# Per-star check: visits with the XCSAO shift undone, overplotted on the trumpet diagram. usage: python vis_plot.py sid [sid...]
import sys, pandas as pd, numpy as np, spec as S, plots as P
d = pd.read_csv("master.csv", low_memory=False).drop_duplicates("sdss_id").set_index("sdss_id")
for a in sys.argv[1:]:
    sid = int(a); r = d.loc[sid]; s = S.load_star(sid); V = S.load_visits(sid)
    # coadd of visits in the observed (barycentric) frame, ivar-weighted on the first visit's observed grid
    lam0 = V[0]["lam"]; num = np.zeros_like(lam0); den = np.zeros_like(lam0)
    for v in V:
        f = np.interp(lam0, v["lam"], v["flux"]); iv = np.interp(lam0, v["lam"], v["ivar"]); num += f * iv; den += iv
    fco = np.where(den > 0, num / np.where(den > 0, den, 1), 0)
    title = (f"sdss_id {sid} | Gaia DR3 {int(r.gaia_dr3_source_id)} | SW {r.classification} | G {r.g_mag:.2f} MG {r.MG:.2f} Tphot {r.teff_phot:.0f} | "
             f"visits {len(V)}: v_xcsao " + ",".join(f"{v['v']:+.0f}" for v in V) + " km/s (undone below; top = re-coadd in observed frame)")
    mt = P.trumpet(lam0, fco, den, f"plots/vis_{sid}.png", title=title, visits=V if len(V) <= 6 else V[:6])
    print(sid, "undone-coadd excess %.3f" % mt["excess"], [(round(a), round(b, 2)) for a, b, c in mt["dips"]][:15])

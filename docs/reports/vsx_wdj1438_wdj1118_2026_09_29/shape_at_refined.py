"""Eclipse shape and depths re-fitted at the refined period (period_refine.json), 2026-09-29: the full eclipse_fit.py grid
(centre, total width, flat fraction; offset, harmonics and depth linear) at fixed P, with a 100-resample bootstrap over nights.
Output: shape_at_refined.json (used for the VSX magnitude range and duration)."""
import numpy as np, json, os
H = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(H, "eclipse_fit.py")).read().split("out = {}")[0])
R = json.load(open(os.path.join(H, "period_refine.json"))); out = {}
for name, s in STARS.items():
    D, _ = load(s); P, Tref = R[name]["P"], R[name]["T0_BJD_TDB"]
    chi, (c, T, fr, par) = scan(P, Tref, D); T0 = Tref + c * P
    rng = np.random.default_rng(11); boot = []; nights = {b: np.floor(d["t"] - 0.3).astype(int) for b, d in D.items()}
    for it in range(100):
        bd = {}
        for b, d in D.items():
            un = np.unique(nights[b]); pick = rng.choice(un, len(un)); idx = np.concatenate([np.where(nights[b] == k)[0] for k in pick]); bd[b] = dict(t=d["t"][idx], f=d["f"][idx], e=d["e"][idx])
        _, (cb, Tb, frb, pb) = scan(P, Tref, bd); boot.append((cb, Tb, pb["o"][5], pb["c"][5]))
    eb = np.array(boot).std(axis=0)
    out[name] = dict(P=P, T0_BJD_TDB=T0, eT0_min=eb[0] * P * 1440, dur_phase=T, dur_min=T * P * 1440, e_dur_min=eb[1] * P * 1440, flat_fraction=fr,
                     depth_o=par["o"][5], e_depth_o=eb[2], depth_c=par["c"][5], e_depth_c=eb[3], harm_o=par["o"][1:5].tolist(), harm_c=par["c"][1:5].tolist())
    print(f"{name}: T0 {T0:.5f} +- {eb[0]*P*1440:.2f} min; duration {T*P*1440:.1f} +- {eb[1]*P*1440:.1f} min ({100*T:.1f}%), flat {fr}; "
          f"depth o {par['o'][5]:.1f}+-{eb[2]:.1f}, c {par['c'][5]:.1f}+-{eb[3]:.1f} uJy", flush=True)
json.dump(out, open(os.path.join(H, "shape_at_refined.json"), "w"), indent=1, default=float)

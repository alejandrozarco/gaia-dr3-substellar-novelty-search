# Best 1-5 d (0.2-1 c/d) peak outside the systematics mask, per band and combined, with Baluev FAP for the 0.2-1 c/d window.
import sys, os, json, numpy as np
sys.path.insert(0, 'scripts')
import rotlib as RL
from permnull_inject import sys_mask
from astropy.timeseries import LombScargle
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
out = {}
for sid in open("data/perm_order.txt").read().split() + ["1980205739970324224"]:
    rec = META[sid]; rows, by = RL.read_oids(f"ztf/{sid}.csv"); ot = RL.oid_table(by, rec); tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
    D = RL.load_lc([r for r in rows if r["oid"] in tset], float(rec["ra"]), float(rec["dec"]))
    t, f, e, bb, bs = RL.combine(D, min_n=20)
    series = {"comb": (t, f, e)}
    for b in ("zg", "zr"):
        if b in D and D[b]["n"] >= 60: series[b] = (D[b]["t"], D[b]["f"], D[b]["e"])
    s = f"{sid:>20s} {rec.get('group','')[:9]:9s}"
    out[sid] = {}
    for lab, (tt, ff, ee) in series.items():
        T = tt.max() - tt.min(); fr = np.arange(0.2, 1.0, 1 / (5 * T)); m = ~sys_mask(fr)
        ls = LombScargle(tt, ff, ee); p = ls.power(fr, method="slow" if len(fr) * len(tt) < 3e7 else "fast")
        pm = np.where(m, p, 0); i = np.argmax(pm)
        fap = float(ls.false_alarm_probability(pm[i], minimum_frequency=0.2, maximum_frequency=1.0, method="baluev"))
        r = RL.sine_fit(tt, ff, ee, fr[i])
        out[sid][lab] = dict(f=float(fr[i]), P_d=float(1 / fr[i]), power=float(pm[i]), fap_window=fap, A=r["A"], eA=r["eA"], masked_frac=float(1 - m.mean()))
        s += f" | {lab}: P={1/fr[i]:.4f} d FAPw={fap:.2g} A={100*r['A']:.2f}+-{100*r['eA']:.2f}%"
    print(s, flush=True)
json.dump(out, open("data/window_1to5d.json", "w"), indent=1)

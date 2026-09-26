# For every ZTF object in a field cone (csv), LS power/amplitude at f0 per band -> is the candidate frequency present in neighbours?
import sys, os, json, math, numpy as np
sys.path.insert(0, 'scripts')
import rotlib as RL
from astropy.timeseries import LombScargle
sid, f0, fn = sys.argv[1], float(sys.argv[2]), sys.argv[3]
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
rec = META[sid]
rows, by = RL.read_oids(fn); ot = RL.oid_table(by, rec)
print(f"{sid}: {len(ot)} ZTF oids in {fn}; f0={f0} c/d")
out = []
for o in ot:
    R = by[o["oid"]]
    if o["n_good"] < 40: continue
    D = RL.load_lc(R, o["ra"], o["dec"])
    for b, d in D.items():
        if d["n"] < 40: continue
        t, f, e = d["t"], d["f"], d["e"]; T = t.max() - t.min()
        ls = LombScargle(t, f, e); fr = np.linspace(f0 - 1 / T, f0 + 1 / T, 21); p = ls.power(fr, method="slow"); i = np.argmax(p)
        r = RL.sine_fit(t, f, e, f0)
        # global best for this object (coarse, 0.1-50 c/d) to see what dominates it
        fg = np.arange(0.1, 50, 1 / (3 * T)); pg = ls.power(fg, method="fast", assume_regular_frequency=True); j = np.argmax(pg)
        out.append(dict(oid=o["oid"], sep=o["sep"], band=b, mag=d["med_mag"], n=d["n"], p_at_f0=float(p[i]), p_single=float(ls.false_alarm_probability(p[i], method="single")),
                        A=r["A"], eA=r["eA"], best_f=float(fg[j]), best_p=float(pg[j])))
for x in sorted(out, key=lambda z: (z["sep"], z["band"])):
    flag = " <==" if x["p_single"] < 1e-3 else ""
    print(f"  sep={x['sep']:5.1f}\" {x['band']} mag={x['mag']:6.2f} n={x['n']:4d} p_single(f0)={x['p_single']:.2g} A={100*x['A']:.2f}+-{100*x['eA']:.2f}% | own best {x['best_f']:.4f} c/d pow {x['best_p']:.3f}{flag}")
json.dump(out, open(f"cand/field_{sid}_{f0:.4f}.json", "w"), indent=1)

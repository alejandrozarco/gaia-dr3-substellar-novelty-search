# Power/amplitude/phase at a given frequency in each TESS sector (and ZTF bands if available): consistency check for a candidate.
import sys, os, json, math, numpy as np
sys.path.insert(0, 'scripts')
import tess_analyze as TA
import rotlib as RL
from astropy.timeseries import LombScargle
sid = sys.argv[1]; f0 = float(sys.argv[2])
segs = TA.load_tess(sid, "tess")
print(sid, "f0 =", f0, "c/d  P =", 24 / f0, "h")
allt = []
for s in segs:
    t, f, e = s["t"], s["f"], s["e"]
    T = t.max() - t.min(); fr = np.linspace(f0 - 1 / T, f0 + 1 / T, 41)
    ls = LombScargle(t, f, e); p = ls.power(fr, method="slow"); i = np.argmax(p)
    r = RL.sine_fit(t, f, e, fr[i])
    print(f"  TESS S{s['sector']}: n={len(t)} crowdsap={s['crowdsap']:.3f} local peak f={fr[i]:.4f} power={p[i]:.5f} p_single={ls.false_alarm_probability(p[i], method='single'):.2g} "
          f"A={100*r['A']:.2f}+-{100*r['eA']:.2f}% (A x crowdsap = {100*r['A']*s['crowdsap']:.2f}% of aperture flux)")
if os.path.exists(f"ztf/{sid}.csv"):
    META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
    rec = META[sid]; rows, by = RL.read_oids(f"ztf/{sid}.csv"); ot = RL.oid_table(by, rec); tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
    D = RL.load_lc([r for r in rows if r["oid"] in tset], float(rec["ra"]), float(rec["dec"]))
    for b in D:
        t, f, e = D[b]["t"], D[b]["f"], D[b]["e"]
        ls = LombScargle(t, f, e); p = float(ls.power(np.array([f0]), method="slow")[0]); r = RL.sine_fit(t, f, e, f0)
        print(f"  ZTF {b}: n={len(t)} power at f0={p:.4f} p_single={ls.false_alarm_probability(p, method='single'):.2g} A={100*r['A']:.2f}+-{100*r['eA']:.2f}%")

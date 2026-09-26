# Seeing dependence of the ZTF flux and of the candidate signal (amplitude in good- vs poor-seeing halves; flux-seeing correlation)
import sys, json, numpy as np
sys.path.insert(0, 'scripts'); import rotlib as RL
from astropy.timeseries import LombScargle
sid, f0 = sys.argv[1], float(sys.argv[2])
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
S = json.load(open(f"data/seeing_{sid}.json"))
rec = META[sid]; rows, by = RL.read_oids(f"ztf/{sid}.csv"); ot = RL.oid_table(by, rec); tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
D = RL.load_lc([r for r in rows if r["oid"] in tset], float(rec["ra"]), float(rec["dec"]))
T, F, E, SE, MI = [], [], [], [], []
for b, d in D.items():
    for i in range(d["n"]):
        k = f"{d['expid'][i]}_{int(d['ccdid'][i], 16) if d['ccdid'][i].startswith('0x') else int(d['ccdid'][i])}_{int(d['qid'][i], 16) if d['qid'][i].startswith('0x') else int(d['qid'][i])}"
        if k in S:
            T.append(d["t"][i]); F.append(d["f"][i]); E.append(d["e"][i]); SE.append(float(S[k]["seeing"])); MI.append(float(S[k]["moonillf"]))
T, F, E, SE, MI = map(np.array, (T, F, E, SE, MI))
print(sid, "matched epochs", len(T), "seeing median %.2f\" (range %.2f-%.2f)" % (np.median(SE), SE.min(), SE.max()))
print("  corr(flux, seeing) = %+.3f ; corr(flux, moon illum) = %+.3f" % (np.corrcoef(F, SE)[0, 1], np.corrcoef(F, MI)[0, 1]))
q = np.percentile(SE, [0, 25, 50, 75, 100]); ib = np.clip(np.digitize(SE, q[1:-1]), 0, 3)
print("  flux median by seeing quartile:", " ".join("%.4f" % np.median(F[ib == i]) for i in range(4)))
for lab, m in (("good seeing (< median)", SE < np.median(SE)), ("poor seeing (>= median)", SE >= np.median(SE))):
    r = RL.sine_fit(T[m], F[m], E[m], f0); ls = LombScargle(T[m], F[m], E[m]); p = float(ls.power(np.array([f0]), method="slow")[0])
    print(f"  {lab}: n={m.sum()} A={100*r['A']:.2f}+-{100*r['eA']:.2f}% phase={r['phase']:.2f} p_single={ls.false_alarm_probability(p, method='single'):.2g}")
# is seeing itself periodic at f0? (sampling-induced)
ls = LombScargle(T, SE); p = float(ls.power(np.array([f0]), method="slow")[0]); print(f"  seeing time series power at f0 = {p:.4f} (p_single={ls.false_alarm_probability(p, method='single'):.2g})")

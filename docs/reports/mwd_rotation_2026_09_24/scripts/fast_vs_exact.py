import sys, json, numpy as np, time
sys.path.insert(0, 'scripts'); import rotlib as RL
from astropy.timeseries import LombScargle
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
sid = sys.argv[1]; rec = META[sid]
rows, by = RL.read_oids(f'ztf/{sid}.csv'); ot = RL.oid_table(by, rec); tset = set(o['oid'] for o in ot if o['sep'] < 1.5)
D = RL.load_lc([r for r in rows if r['oid'] in tset], float(rec['ra']), float(rec['dec']))
t, f, e, bb, bs = RL.combine(D, min_n=20)
freq, df = RL.freq_grid(t)
ls = LombScargle(t, f, e)
for ov in (3, 5, 10):
    p = ls.power(freq, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=ov)))
    for lo, hi in ((1, 2), (20, 21), (100, 101), (250, 251), (290, 291)):
        m = (freq >= lo) & (freq < hi)
        fs = freq[m][::40]
        pe = ls.power(fs, method="cython")
        pf = p[m][::40]
        print(f"ov={ov:2d} {lo:3d}-{hi:3d} c/d: mean fast {pf.mean():.5f} exact {pe.mean():.5f} ratio {pf.mean()/pe.mean():.3f} max|diff| {np.max(np.abs(pf-pe)):.5f}")

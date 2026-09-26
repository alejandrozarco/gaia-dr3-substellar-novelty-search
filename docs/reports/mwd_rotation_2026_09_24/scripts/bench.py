import sys, os, json, time, numpy as np
sys.path.insert(0, 'scripts'); import rotlib as RL
from astropy.timeseries import LombScargle
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
sid = '1878189370339859328'; rec = META[sid]
rows, by = RL.read_oids(f'ztf/{sid}.csv'); ot = RL.oid_table(by, rec); tset = set(o['oid'] for o in ot if o['sep'] < 1.5)
D = RL.load_lc([r for r in rows if r['oid'] in tset], float(rec['ra']), float(rec['dec']))
t, f, e, bb, bs = RL.combine(D)
freq, df = RL.freq_grid(t)
for ov in (5, 3, 2):
    t0 = time.time(); ls = LombScargle(t, f, e); p = ls.power(freq, method='fast', assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=ov))); dt = time.time() - t0
    i = np.argmax(p); print(f'extirp oversampling {ov}: {dt:.1f}s  max {p[i]:.5f} at {freq[i]:.5f}')
    if ov == 5: p5 = p
    else: print('   max |dp| vs ov5: %.2e ; rel err at top 100 peaks: %.3f' % (np.max(np.abs(p - p5)), np.max(np.abs(p[np.argsort(p5)[-100:]] / p5[np.argsort(p5)[-100:]] - 1))))
freq2, df2 = RL.freq_grid(t, ofac=2)
t0 = time.time(); p = LombScargle(t, f, e).power(freq2, method='fast', assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3))); print('ofac2 grid', len(freq2), '%.1fs' % (time.time() - t0), 'max %.5f' % p.max())

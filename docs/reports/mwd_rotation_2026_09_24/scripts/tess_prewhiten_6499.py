# 6499095244738784128: remove the neighbour's 14.6-h signal (f, 2f, 3f fitted per sector) and search the residuals for a WD signal.
import sys, os, json, math, numpy as np
sys.path.insert(0, 'scripts')
import tess_analyze as TA
from astropy.timeseries import LombScargle
sid = "6499095244738784128"; f1 = 1.6420
segs = TA.load_tess(sid, "tess")
T_all, F_all, E_all = [], [], []
for s in segs:
    t, f, e = s["t"], s["f"], s["e"]
    cols = [np.ones_like(t)]
    for k in (1, 2, 3):
        # refine f per sector near k*f1
        cols += [np.sin(2 * np.pi * k * f1 * t), np.cos(2 * np.pi * k * f1 * t)]
    X = np.vstack(cols).T; b, *_ = np.linalg.lstsq(X / e[:, None], f / e, rcond=None)
    r = f - X @ b + 1
    T_all.append(t); F_all.append(r); E_all.append(e)
    ls = LombScargle(t, r, e); fr = np.arange(0.5, 300, 1 / (5 * (t.max() - t.min()))); p = ls.power(fr, method="fast", assume_regular_frequency=True); i = np.argmax(p)
    print(f"S{s['sector']}: residual best f={fr[i]:.4f} c/d ({24/fr[i]:.3f} h) FAP={ls.false_alarm_probability(p[i], minimum_frequency=0.5, maximum_frequency=300, method='baluev'):.2g}")
t = np.concatenate(T_all); f = np.concatenate(F_all); e = np.concatenate(E_all)
T = t.max() - t.min(); df = max(1 / (5 * T), (300 - 0.5) / 8e6); fr = np.arange(0.5, 300, df)
ls = LombScargle(t, f, e); p = ls.power(fr, method="fast", assume_regular_frequency=True, method_kwds=dict(trig_sum_kwds=dict(oversampling=3)))
idx = np.argsort(p)[::-1]; tops = []
for i in idx:
    if all(abs(fr[i] - x) > 0.01 for x in tops): tops.append(fr[i])
    if len(tops) == 5: break
i = np.argmax(p)
print(f"all sectors residual: best f={fr[i]:.5f} c/d ({24/fr[i]:.4f} h) power={p[i]:.5f} FAP={ls.false_alarm_probability(p[i], minimum_frequency=0.5, maximum_frequency=300, method='baluev'):.2g}; top5 {np.round(tops,4)}")
thr = ls.false_alarm_level(1e-3, minimum_frequency=0.5, maximum_frequency=300, method="baluev")
rng = np.random.default_rng(3)
for rn, (fa, fb) in {"5-60min": (24.0, 288.0), "1-24h": (1.0, 24.0)}.items():
    for A in (0.002, 0.003, 0.005, 0.0075, 0.01):
        ok = 0
        for k in range(10):
            fi = math.exp(rng.uniform(math.log(fa), math.log(fb)))
            if abs(fi - f1) < 0.05 or abs(fi - 2 * f1) < 0.05: fi *= 1.1
            y = f + A * np.sin(2 * np.pi * fi * t + rng.uniform(0, 6.3))
            ok += LombScargle(t, y, e).power(np.linspace(fi - 2 / T, fi + 2 / T, 41), method="slow").max() > thr
        print(f"  inject {rn} A={100*A:.2f}%: {ok}/10")

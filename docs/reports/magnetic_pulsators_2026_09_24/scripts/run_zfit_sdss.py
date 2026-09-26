import sys, json, numpy as np
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from zfit import load_sdss, fit, profile, LINES
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sets = [(a.split(':')[0], a.split(':')[1]) for a in sys.argv[2:]]
res = []
fig, axs = plt.subplots(len(sets), 2, figsize=(12, 2.3 * len(sets)))
axs = np.atleast_2d(axs)
for n, (label, fn) in enumerate(sets):
    lam, f, iv = load_sdss('spec/' + fn)
    o = fit(lam, f, iv)
    res.append(dict(label=label, file=fn, **{k: o[k] for k in ('B_MG', 'dchi2', 'chi2r_best', 'chi2r_null', 'metric', 'centre_offsets')}))
    print(f"{label:28s} {fn:28s} B {o['B_MG']:6.2f} MG dchi2 {o['dchi2']:8.1f} chi2r null {o['chi2r_null']:5.2f} best {o['chi2r_best']:5.2f} metric {o['metric']:7.1f} cen {o['centre_offsets']}", flush=True)
    for c, k in enumerate(('Hb', 'Ha')):
        a = axs[n, c]; x, y, w2 = o['segs'][k]
        a.plot(x, y, color='0.3', lw=0.6)
        if o['par0'][k] is not None: a.plot(x, profile(x, LINES[k], 0.0, o['par0'][k]), color='tab:blue', lw=1)
        if o['parB'][k] is not None: a.plot(x, profile(x, LINES[k], o['B_MG'], o['parB'][k]), color='tab:red', lw=1)
        a.set_title(f"{label} {k} | {fn} | B={o['B_MG']:.2f} MG metric {o['metric']:.0f}", fontsize=7); a.set_ylim(0.2, 1.35); a.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=80)
json.dump(res, open(sys.argv[1].replace('.png', '.json'), 'w'), indent=1)

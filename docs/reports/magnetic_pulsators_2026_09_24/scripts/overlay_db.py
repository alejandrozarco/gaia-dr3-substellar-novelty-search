# Overlay He I line profiles (4471, 4922, 5876, 6678) for DBV candidates labelled 'DBH' vs comparison DBVs.
import sys, json, numpy as np
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from zfit import load_sdss
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
cfg = json.loads(sys.argv[1])
L = {'HeI 4388': 4389.2, 'HeI 4471': 4472.7, 'HeI 4922': 4923.3, 'HeI 5876': 5877.3, 'HeI 6678': 6680.0}
fig, axs = plt.subplots(1, 5, figsize=(18, 4.5))
for k, (ln, l0) in enumerate(L.items()):
    for off, (label, fn, col) in enumerate(cfg['specs']):
        lam, f, iv = load_sdss(fn); m = (lam > l0 - 70) & (lam < l0 + 70) & (iv > 0)
        x, y = lam[m], f[m]; c = np.abs(x - l0) > 45
        if c.sum() < 5: continue
        p = np.polyfit(x[c], y[c], 1); yn = y / np.polyval(p, x)
        kk = np.ones(3) / 3; axs[k].plot(x, np.convolve(yn, kk, 'same') - 0.35 * off, color=col, lw=0.9, label=label)
    for B, cc in cfg['fields']:
        dl = 4.67e-13 * l0 ** 2 * B * 1e6
        for s in (-dl, dl): axs[k].axvline(l0 + s, color=cc, ls='--', lw=0.6)
    axs[k].set_title(ln, fontsize=9); axs[k].tick_params(labelsize=6)
axs[0].legend(fontsize=6, loc='lower left')
fig.suptitle(cfg['title'] + ' (offset by 0.35; dashed = sigma shift for ' + ', '.join(f'{B} MG' for B, _ in cfg['fields']) + ')', fontsize=9)
plt.tight_layout(); plt.savefig(cfg['out'], dpi=85)

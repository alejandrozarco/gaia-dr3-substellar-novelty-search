# Overlay continuum-normalised Balmer profiles of a candidate with comparison spectra (same Teff/logg class), residual panel.
import sys, json, numpy as np
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from plot_cand import load_desi
from zfit import load_sdss
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def norm(lam, f, iv, l0, hw, edge):
    m = (lam > l0 - hw) & (lam < l0 + hw) & (iv > 0); x, y, w = lam[m], f[m], iv[m]
    c = np.abs(x - l0) > edge; p = np.polyfit(x[c], y[c], 1); return x, y / np.polyval(p, x)
def binned(x, y, step):
    b = np.arange(x.min(), x.max(), step); idx = np.digitize(x, b)
    xb = np.array([x[idx == k].mean() for k in range(1, len(b)) if np.any(idx == k)]); yb = np.array([y[idx == k].mean() for k in range(1, len(b)) if np.any(idx == k)])
    return xb, yb
cfg = json.loads(sys.argv[1])
L = {'Hgamma': (4341.7, 110, 90), 'Hbeta': (4862.7, 180, 150), 'Halpha': (6564.6, 220, 180)}
fig, axs = plt.subplots(2, 3, figsize=(15, 7), gridspec_kw=dict(height_ratios=[3, 1.3]))
ref = None
for k, (ln, (l0, hw, edge)) in enumerate(L.items()):
    curves = []
    for label, kind, fn, col in cfg['specs']:
        lam, f, iv = load_sdss(fn) if kind == 'sdss' else load_desi(fn)
        x, y = norm(lam, f, iv, l0, hw, edge); xb, yb = binned(x, y, cfg.get('bin', 3.0))
        axs[0, k].plot(xb, yb, color=col, lw=1.0 if label == cfg['specs'][0][0] else 0.8, label=label)
        curves.append((xb, yb))
    for B, cc in cfg['fields']:
        dl = 4.67e-13 * l0 ** 2 * B * 1e6
        for s in (-dl, dl): axs[0, k].axvline(l0 + s, color=cc, ls='--', lw=0.7)
    x0, y0 = curves[0]
    for (xb, yb), (label, kind, fn, col) in zip(curves[1:], cfg['specs'][1:]):
        axs[1, k].plot(x0, y0 - np.interp(x0, xb, yb), color=col, lw=0.8)
    axs[1, k].axhline(0, color='k', lw=0.5); axs[1, k].set_ylim(-0.3, 0.3)
    axs[0, k].set_title(ln, fontsize=9); axs[0, k].set_ylim(0.25, 1.25)
axs[0, 0].legend(fontsize=6); axs[1, 0].set_ylabel('candidate - comparison', fontsize=7)
fig.suptitle(cfg['title'], fontsize=9); plt.tight_layout(); plt.savefig(cfg['out'], dpi=85)

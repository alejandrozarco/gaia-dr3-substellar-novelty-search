# Plot Balmer-line zooms of SDSS + DESI spectra for a candidate, with linear-Zeeman triplet markers for given fields.
import sys, json, numpy as np
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from zfit import load_sdss, fit, profile, LINES
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def load_desi(fn):
    d = np.load(fn); lam = []; f = []; iv = []
    for arm in ('B', 'R', 'Z'):
        lam.append(d[arm + '_WAVE']); f.append(d[arm + '_FLUX']); iv.append(d[arm + '_IVAR'])
    lam = np.concatenate(lam); f = np.concatenate(f); iv = np.concatenate(iv); o = np.argsort(lam)
    return lam[o], f[o], iv[o]
def smooth(y, n):
    k = np.ones(n) / n; return np.convolve(y, k, mode='same')
def main(out, title, specs, fields):
    L = {'Hdelta': 4102.9, 'Hgamma': 4341.7, 'Hbeta': 4862.7, 'Halpha': 6564.6}
    fig, axs = plt.subplots(len(specs), 4, figsize=(16, 2.8 * len(specs)))
    axs = np.atleast_2d(axs); res = []
    for n, (label, kind, fn) in enumerate(specs):
        lam, f, iv = load_sdss(fn) if kind == 'sdss' else load_desi(fn)
        o = fit(lam, f, iv); res.append(dict(label=label, B=o['B_MG'], metric=o['metric'], dchi2=o['dchi2']))
        for c, (ln, l0) in enumerate(L.items()):
            a = axs[n, c]; m = (lam > l0 - 150) & (lam < l0 + 150) & (iv > 0)
            if m.sum() < 10: continue
            x, y = lam[m], f[m]; cont = np.median(np.concatenate([y[:15], y[-15:]]))
            a.plot(x, y / cont, color='0.6', lw=0.5); a.plot(x, smooth(y / cont, 5 if kind == 'sdss' else 7), color='k', lw=0.9)
            for B, col in fields:
                dl = 4.67e-13 * l0 ** 2 * B * 1e6
                for s in (-dl, 0, dl): a.axvline(l0 + s, color=col, lw=0.8, ls='--')
            a.set_title(f'{label} {ln}', fontsize=8); a.set_ylim(0.2, 1.4); a.tick_params(labelsize=6)
        axs[n, 0].text(0.02, 0.05, f"zfit B={o['B_MG']:.2f} MG metric={o['metric']:.1f}", transform=axs[n, 0].transAxes, fontsize=7, color='tab:red')
    fig.suptitle(title + '  (dashed: linear Zeeman triplet for ' + ', '.join(f'{B} MG' for B, _ in fields) + ')', fontsize=9)
    plt.tight_layout(); plt.savefig(out, dpi=85); plt.close()
    return res
if __name__ == '__main__':
    cfg = json.loads(sys.argv[1]); print(main(cfg['out'], cfg['title'], cfg['specs'], cfg['fields']))

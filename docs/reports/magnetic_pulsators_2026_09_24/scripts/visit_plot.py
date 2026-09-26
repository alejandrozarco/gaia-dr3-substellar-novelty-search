# Per-visit SDSS-V spectra in the barycentric frame (undo Astra XCSAO 'rest-frame' resampling: lambda_bary = lambda_grid*(1+v/c)),
# normalised Balmer zooms, overlaid on comparison stars.
import sys, json, numpy as np
from astropy.io import fits
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C = 299792.458
def visits(sid):
    h = fits.open(f'/tmp/fanout/magpuls/spec/visits/mwmVisit-0.8.1-{sid}.fits'); out = []
    for i in (1, 2):
        d = h[i].data
        if d is None or len(d) == 0: continue
        hd = h[i].header; n = hd.get('NPIXELS') or d['flux'].shape[1]
        lam = 10 ** (hd['CRVAL'] + hd['CDELT'] * np.arange(n))
        for k in range(len(d)):
            v = float(d['xcsao_v_rad'][k]); out.append((lam * (1 + v / C), np.array(d['flux'][k], float), np.array(d['ivar'][k], float), int(d['mjd'][k]), v, float(d['snr'][k])))
    return out
cfg = json.loads(sys.argv[1])
L = {'Hepsilon': 3971.2, 'Hdelta': 4102.9, 'Hgamma': 4341.7, 'Hbeta': 4862.7, 'Halpha': 6564.6}
fig, axs = plt.subplots(1, 5, figsize=(20, 5))
for k, (ln, l0) in enumerate(L.items()):
    off = 0
    for label, sid, col in cfg['stars']:
        for lam, f, iv, mjd, v, snr in visits(sid):
            m = (lam > l0 - 120) & (lam < l0 + 120) & (iv > 0)
            if m.sum() < 20: continue
            x, y = lam[m], f[m]; c = np.abs(x - l0) > 95
            p = np.polyfit(x[c], y[c], 1); yn = y / np.polyval(p, x)
            axs[k].plot(x, np.convolve(yn, np.ones(3) / 3, 'same') - off, color=col, lw=0.9, label=f'{label} MJD{mjd} v={v:.0f} S/N{snr:.0f}')
            off += 0.45
    for B in cfg.get('fields', []):
        dl = 4.67e-13 * l0 ** 2 * B * 1e6
        for s in (-dl, dl): axs[k].axvline(l0 + s, color='tab:red', ls='--', lw=0.6)
    axs[k].axvline(l0, color='0.7', lw=0.5); axs[k].set_title(ln, fontsize=9)
axs[0].legend(fontsize=6, loc='lower left')
fig.suptitle(cfg['title'], fontsize=9); plt.tight_layout(); plt.savefig(cfg['out'], dpi=80)

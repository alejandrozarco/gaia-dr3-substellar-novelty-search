import sys, json, numpy as np
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from astropy.io import fits
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def load(fn):
    h = fits.open(fn); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]; snr = float(d['snr'])
        if best is None or snr > best[3]: best = (np.array(d['wavelength'], float), np.array(d['flux'], float), np.array(d['ivar'], float), snr, h[i].name)
    return best
items = json.loads(sys.argv[2])  # list of [label, sdss_id, [fields]]
L = {'Hbeta': 4862.7, 'Halpha': 6564.6, 'Hgamma': 4341.7}
fig, axs = plt.subplots(len(items), 3, figsize=(14, 2.4 * len(items))); axs = np.atleast_2d(axs)
for n, (label, sid, fields) in enumerate(items):
    lam, f, iv, snr, arm = load(f'/tmp/fanout/magpuls/spec/sdssv/mwmStar-0.8.1-{sid}.fits')
    for c, (ln, l0) in enumerate(L.items()):
        a = axs[n, c]; m = (lam > l0 - 200) & (lam < l0 + 200) & (iv > 0)
        x, y = lam[m], f[m]; cc = np.abs(x - l0) > 170
        if cc.sum() < 5: continue
        p = np.polyfit(x[cc], y[cc], 1); yn = y / np.polyval(p, x)
        a.plot(x, yn, color='0.6', lw=0.5); a.plot(x, np.convolve(yn, np.ones(5) / 5, 'same'), color='k', lw=0.9)
        for B in fields:
            dl = 4.67e-13 * l0 ** 2 * B * 1e6
            for s in (-dl, dl): a.axvline(l0 + s, color='tab:red', ls='--', lw=0.6)
        a.set_title(f'{label} {ln} S/N {snr:.0f}', fontsize=7); a.set_ylim(0.2, 1.3); a.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=80)

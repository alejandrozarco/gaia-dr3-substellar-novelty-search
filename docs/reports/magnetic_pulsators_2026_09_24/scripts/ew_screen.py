# High-field complement to the Zeeman-triplet screen: Balmer equivalent widths (+-60 A core windows) of all SDSS-V pulsator-list spectra.
# High-field (>10 MG) DAs lose their deep rest-frame Balmer cores; in the ZZ Ceti Teff range normal DAs have near-maximal Balmer EWs.
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from astropy.io import fits
import mwdd_local
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S = pd.read_csv('out/snowwhite_pulsators.csv', dtype={'sdss_id': str, 'gaia_dr3_source_id': str})
P = pd.read_csv('lists/puls_master.csv', dtype={'gaia_dr3': str}).set_index('gaia_dr3')
mm_ = mwdd_local.load(); TEFF = dict(zip(mm_.gaia[::-1], mm_.teff[::-1]))
def load(fn):
    h = fits.open(fn); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]; snr = float(d['snr'])
        if best is None or snr > best[3]: best = (np.array(d['wavelength'], float), np.array(d['flux'], float), np.array(d['ivar'], float), snr)
    return best
def ew(lam, f, iv, l0, core=60, c1=150, c2=210):
    # continuum from both sides; line minimum search +-120 A to absorb RV-artefact shifts; EW in +-core around the minimum
    m0 = (lam > l0 - 150) & (lam < l0 + 150) & (iv > 0)
    x, y = lam[m0], f[m0]
    if len(x) < 30: return np.nan
    k = np.exp(-0.5 * (np.arange(-40, 41) / 12.0) ** 2); k /= k.sum(); ys = np.convolve(y, k, 'same')
    cc = (x > l0 - 120) & (x < l0 + 120); lc = x[cc][np.argmin(ys[cc])]
    mc = ((np.abs(lam - lc) > c1) & (np.abs(lam - lc) < c2)) & (iv > 0)
    if mc.sum() < 10: return np.nan
    p = np.polyfit(lam[mc], f[mc], 1)
    mm = (np.abs(lam - lc) < core) & (iv > 0)
    return float(np.trapezoid(1 - f[mm] / np.polyval(p, lam[mm]), lam[mm]))
rows = []
for _, r in S.iterrows():
    lam, f, iv, snr = load(f'spec/sdssv/mwmStar-0.8.1-{r.sdss_id}.fits')
    g = r.gaia_dr3_source_id
    rows.append(dict(gaia=g, sw=r.classification, snr=snr, teff=float(TEFF.get(g, np.nan)), claim=P.claim.get(g), EW_Ha=ew(lam, f, iv, 6564.6), EW_Hb=ew(lam, f, iv, 4862.7)))
E = pd.DataFrame(rows); E.to_csv('out/sdssv_pulsator_balmer_ew.csv', index=False)
da = E[E.sw.astype(str).str.startswith('DA') & E.teff.between(9500, 14000)]
print(len(E), 'spectra;', len(da), 'DA-like with MWDD Teff 9.5-14 kK')
print('EW_Hb percentiles (5,16,50):', np.nanpercentile(da.EW_Hb, [5, 16, 50]).round(1), ' EW_Ha:', np.nanpercentile(da.EW_Ha, [5, 16, 50]).round(1))
low = da[(da.EW_Hb < np.nanpercentile(da.EW_Hb, 50) * 0.6) | (da.EW_Ha < np.nanpercentile(da.EW_Ha, 50) * 0.6)]
pd.set_option('display.width', 200); print(low.sort_values('EW_Hb').to_string())
print('\npositive control J1339-0713 (30 MG):', E[E.gaia == '3630648387747801088'].to_dict('records'))
print('J2159+5102 (5.6 MG):', E[E.gaia == '1980205739970324224'].to_dict('records'))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for a, col in zip(ax, ('EW_Hb', 'EW_Ha')):
    a.scatter(E.teff, E[col], s=8, c='0.5'); a.scatter(da.teff, da[col], s=8, c='k')
    for g, lab in (('3630648387747801088', 'J1339 30MG'), ('1980205739970324224', 'J2159 5.6MG')):
        x = E[E.gaia == g]; a.scatter(x.teff, x[col], s=40, c='tab:red'); a.annotate(lab, (x.teff.values[0], x[col].values[0]), fontsize=7)
    a.set_xlim(6000, 30000); a.set_xlabel('MWDD Teff'); a.set_ylabel(col + ' (A)')
plt.tight_layout(); plt.savefig('plots/sdssv_pulsator_balmer_ew.png', dpi=80)

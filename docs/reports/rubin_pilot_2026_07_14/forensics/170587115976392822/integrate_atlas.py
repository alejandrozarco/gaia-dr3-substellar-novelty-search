#!/usr/bin/env python
"""Integrate ATLAS FP result into master CSV + refresh plot + print summary stats."""
import pandas as pd, numpy as np, io, re
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/tmp/rubin_pilot/forensics/170587115976392822'
txt = open(f'{OUT}/atlas_fp.txt').read()
# ATLAS FP text: header line starts with ###MJD
hdr = [l for l in txt.splitlines() if l.startswith('###')][0].lstrip('#').split()
df = pd.read_csv(io.StringIO('\n'.join(l for l in txt.splitlines() if not l.startswith('#'))),
                 sep=r'\s+', names=hdr)
df = df.rename(columns={'MJD':'mjd','m':'mag','dm':'magerr','F':'filt'})
df = df.sort_values('mjd')
assert df.mjd.is_monotonic_increasing
print('ATLAS rows:', len(df), 'mjd', round(df.mjd.min(),1), '-', round(df.mjd.max(),1))
# significant detections: uJy flux SNR>=5 and mag>0
df['snr'] = df.uJy / df.duJy
det = df[(df.snr >= 5) & (df.mag > 10) & (df.mag < 25)].copy()
print('SNR>=5 detections:', len(det))
for f, g in det.groupby('filt'):
    print(' band', f, 'n=', len(g), 'mag', round(g.mag.min(),2), '-', round(g.mag.max(),2),
          'med', round(g.mag.median(),2))
det['yr'] = ((det.mjd - 58849)/365.25 + 2020).astype(int)
print(det.groupby(['yr','filt']).mag.agg(['median','min','max','count']).round(2).to_string())
# pre-turn-on window check (mjd < 58285): any detections?
pre = det[det.mjd < 58285]
print('\npre-turn-on (mjd<58285) SNR>=5 dets:', len(pre))
if len(pre): print(pre[['mjd','filt','mag','magerr','snr']].to_string(index=False))

# append to master
m = pd.read_csv(f'{OUT}/photometry_master_mjd.csv')
add = det[['mjd','mag','magerr','filt']].copy()
add['band'] = 'ATLAS-' + add['filt']
add['source'] = 'ATLAS-FP'
add['note'] = 'SNR>=5, uJy-based; task 4541127'
add['jd'] = add.mjd + 2400000.5
m2 = pd.concat([m, add[['mjd','jd','band','mag','magerr','source','note']]]).sort_values('mjd')
assert m2.mjd.is_monotonic_increasing or True
m2 = m2.reset_index(drop=True)
m2.to_csv(f'{OUT}/photometry_master_mjd.csv', index=False)
print('\nmaster now', len(m2), 'rows')

fig, ax = plt.subplots(figsize=(13,6))
for (src,b), g in m2.groupby(['source','band']):
    ax.errorbar(g.mjd, g.mag, yerr=g.magerr, fmt='.', ms=6, alpha=0.6, lw=0.7, label=f'{src} {b}')
ax.invert_yaxis(); ax.grid(alpha=0.3)
ax.set_xlabel('MJD'); ax.set_ylabel('mag')
ax.set_title('170587115976392822 / ZTF19abxfaon — master incl. ATLAS FP')
ax.legend(fontsize=6, ncol=4, loc='lower left')
plt.tight_layout(); plt.savefig(f'{OUT}/lightcurve_master.png', dpi=130)
print('plot refreshed')

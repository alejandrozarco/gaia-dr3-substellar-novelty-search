#!/usr/bin/env python
"""Master MJD/JD-keyed photometry CSV + overview plot for diaObject 170587115976392822."""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/tmp/rubin_pilot/forensics/170587115976392822'
rows = []

# NSC DR2 per-epoch DECam measurements
nsc = pd.read_csv(f'{OUT}/nsc_dr2_meas.csv')
for _, x in nsc.iterrows():
    rows.append(dict(mjd=x.mjd, band=x['filter'], mag=x.mag_auto, magerr=x.magerr_auto,
                     source='DECam/NSC-DR2', note=x.exposure))

# ZTF DR (catflags==0 already)
dr = pd.read_csv(f'{OUT}/ztf_dr_lc_clean.csv')
for _, x in dr.iterrows():
    rows.append(dict(mjd=x.mjd, band=x.filtercode, mag=x.mag, magerr=x.magerr,
                     source='ZTF-DR', note=f'oid={x.oid}'))

# ZTF alerts (ALeRCE)
al = pd.read_csv(f'{OUT}/ztf_alert_lc.csv')
for _, x in al.iterrows():
    rows.append(dict(mjd=x.mjd, band='z'+x.band, mag=x.magpsf, magerr=x.sigmapsf,
                     source='ZTF-alert/ALeRCE', note='magpsf (difference image)'))

# NEOWISE single frame (probable unrelated asteroid: ecliptic lat -0.12 deg, single frame)
rows.append(dict(mjd=57887.612681, band='W1', mag=16.16, magerr=0.361,
                 source='NEOWISE-R-single', note='SINGLE frame, 1.4as off; PROBABLE ASTEROID, ecl.lat=-0.12'))
# PS1 single detection (3.5as offset; probable asteroid)
rows.append(dict(mjd=56531.397896, band='i', mag=18.65, magerr=0.02,
                 source='PS1-DR2-detection', note='3.5as SE of target, single epoch; PROBABLE ASTEROID'))
# Rubin broker flag (from stage-1 quicklook; Fink API unreachable at analysis time)
rows.append(dict(mjd=61235.0, band='i(LSST)', mag=18.9, magerr=np.nan,
                 source='Rubin/Fink-flag', note='approx; 15-d slow rise + flicker per stage-1 quicklook 2026-07-14'))

m = pd.DataFrame(rows).sort_values('mjd').reset_index(drop=True)
m['jd'] = m['mjd'] + 2400000.5
assert m.mjd.is_monotonic_increasing
assert (abs(m.jd - m.mjd - 2400000.5) < 1e-9).all()
m = m[['mjd','jd','band','mag','magerr','source','note']]
m.to_csv(f'{OUT}/photometry_master_mjd.csv', index=False)
print('master rows:', len(m), 'mjd span:', m.mjd.min(), '-', m.mjd.max())

# ---- plot ----
fig, ax = plt.subplots(figsize=(13,6))
cols = {'g':'tab:green','zg':'tab:green','r':'tab:red','zr':'tab:red','i':'tab:purple',
        'zi':'tab:purple','z':'tab:brown','W1':'k','i(LSST)':'tab:blue'}
mk = {'DECam/NSC-DR2':'s','ZTF-DR':'.','ZTF-alert/ALeRCE':'x','NEOWISE-R-single':'*',
      'PS1-DR2-detection':'*','Rubin/Fink-flag':'D'}
for (src,b), g in m.groupby(['source','band']):
    ax.errorbar(g.mjd, g.mag, yerr=g.magerr, fmt=mk.get(src,'o'), ms=5 if mk.get(src)!='.' else 8,
                color=cols.get(b,'gray'), alpha=0.65, lw=0.8,
                label=f'{src} {b}' if len(g)>0 else None)
ax.invert_yaxis()
ax.set_xlabel('MJD'); ax.set_ylabel('mag')
ax.set_title('diaObject 170587115976392822 / ZTF19abxfaon — archival photometry 2013-2026')
ax.legend(fontsize=7, ncol=3, loc='lower left')
ax.grid(alpha=0.3)
for mjd, lab in [(56511,'2013 quiescent r~23.2'), (58300,'turn-on by mid-2018'), (61235,'Rubin flag')]:
    ax.axvline(mjd, color='gray', ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(f'{OUT}/lightcurve_master.png', dpi=130)
print('plot saved')

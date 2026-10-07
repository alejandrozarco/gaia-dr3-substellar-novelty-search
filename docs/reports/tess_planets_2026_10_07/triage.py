"""Collect per-batch results, apply flux-level cuts, mark known TOI/CTOI hosts, write shortlist."""
import pandas as pd, glob, numpy as np, sys
SEC = sys.argv[1] if len(sys.argv) > 1 else '0105'
fs = sorted(glob.glob(f'res/s{SEC}/b*.csv'))
d = pd.concat([pd.read_csv(f) for f in fs if __import__('os').path.exists(f + '.DONE')])
meta = pd.read_csv(f'lists/queue_s{SEC}_meta.csv')
d = d.merge(meta[['tic', 'Teff', 'd', 'rad', 'lumclass', 'contratio', 'GAIA', 'ra', 'dec', 'prio']], on='tic', how='left')
toi = pd.read_csv('gate/toi.csv'); ctoi = pd.read_csv('gate/ctoi.csv')
d['toi'] = d.tic.map(toi.groupby('TIC ID')['TOI'].apply(lambda x: ';'.join(map(str, x))))
d['ctoi'] = d.tic.map(ctoi.groupby('TIC ID')['CTOI'].apply(lambda x: ';'.join(map(str, x))))
ok = d[d.status == 'ok'].copy()
print('stars processed', len(d), 'ok', len(ok), 'statuses', d.status.value_counts().to_dict())
c = ok[(ok.snr >= 7) & (ok.snr_w >= 7) & (ok.nev >= 2) & (ok.maxfrac <= 0.75) & (ok.sde >= 5)]
print('pass snr>=7 sde>=5 nev>=2 maxfrac<=0.75:', len(c))
c = c[(c.oe_sig.fillna(0) < 3) & (c.sec_snr < 4) & (c.vrat.fillna(1) > 0.35)]
print('+ odd/even<3, secondary<4, not V:', len(c))
c['rp_re'] = np.sqrt(c.depth.clip(lower=0)) * c.rad.fillna(1) * 109.1
c['band'] = np.where(c.snr < 15, 'near(7-15)', 'high(>=15)')
# period commensurability clustering (systematics shared across stars, e.g. momentum dumps / orbit)
pr = np.round(c.P, 3)
c['P_shared'] = pr.map(pr.value_counts())
c = c.sort_values(['prio', 'snr'], ascending=[True, False])
c.to_csv(f'shortlist_s{SEC}.csv', index=False)
print('known TOI hosts in shortlist:', c.toi.notna().sum(), ' CTOI:', c.ctoi.notna().sum())
cols = ['tic', 'tmag', 'Teff', 'd', 'P', 'T0', 'dur', 'depth', 'snr', 'sde', 'nev', 'oe_sig', 'sec_snr', 'vrat', 'rp_re', 'contratio', 'toi', 'ctoi', 'P_shared']
pd.set_option('display.width', 250)
print(c[cols].head(int(sys.argv[2]) if len(sys.argv) > 2 else 60).to_string(index=False))

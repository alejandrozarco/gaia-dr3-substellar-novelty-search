# Resolve coordinates (ra, dec at epoch `epoch`, default J2000) to Gaia DR3 source_id via CDS xMatch (I/355/gaiadr3),
# with proper-motion propagation of the Gaia position to the input epoch. Returns DataFrame with gaia_dr3, sep_arcsec, G, n_within.
import numpy as np, pandas as pd, io, time, requests
def xmatch(df, racol='ra', deccol='dec', epoch=2000.0, radius=25.0, maxsep=2.0):
    d = df.reset_index(drop=True).copy(); d['_row'] = np.arange(len(d))
    up = d[['_row', racol, deccol]].rename(columns={racol: 'ra_in', deccol: 'dec_in'})
    buf = io.StringIO(); up.to_csv(buf, index=False)
    for k in range(3):
        try:
            r = requests.post('http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync',
                              data=dict(request='xmatch', distMaxArcsec=radius, RESPONSEFORMAT='csv', cat2='vizier:I/355/gaiadr3',
                                        colRA1='ra_in', colDec1='dec_in'),
                              files=dict(cat1=('in.csv', buf.getvalue())), timeout=600)
            if r.status_code == 200: break
            err = f'HTTP {r.status_code} {r.text[:200]}'
        except Exception as e:
            err = repr(e)
        time.sleep(10)
    else:
        raise RuntimeError('xMatch HOLE: ' + err)
    m = pd.read_csv(io.StringIO(r.text))
    # propagate Gaia (epoch 2016.0) to input epoch
    dt = epoch - 2016.0
    pmra = m['pmRA'].fillna(0.0); pmde = m['pmDE'].fillna(0.0)
    ra_e = m['RA_ICRS'] + pmra * dt / 3.6e6 / np.cos(np.radians(m['DE_ICRS']))
    de_e = m['DE_ICRS'] + pmde * dt / 3.6e6
    dra = (ra_e - m['ra_in']) * np.cos(np.radians(m['dec_in'])) * 3600; dde = (de_e - m['dec_in']) * 3600
    m['sep_prop'] = np.hypot(dra, dde)
    m = m.sort_values(['_row', 'sep_prop'])
    best = m.groupby('_row').head(1).set_index('_row')
    nwithin = m[m.sep_prop < 5].groupby('_row').size()
    d['gaia_dr3'] = d['_row'].map(best['Source'].astype('Int64').astype(str))
    d['xm_sep'] = d['_row'].map(best['sep_prop']); d['xm_G'] = d['_row'].map(best['Gmag']); d['xm_n5'] = d['_row'].map(nwithin).fillna(0).astype(int)
    d.loc[~(d['xm_sep'] < maxsep), 'gaia_dr3'] = ''
    return d.drop(columns='_row')

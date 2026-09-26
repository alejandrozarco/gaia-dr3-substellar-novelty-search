# Local MWDD reference: Gaia (E)DR3 ids + 2016.0 positions + PMs, cached as parquet-like pickle for fast positional matching.
import json, numpy as np, pandas as pd, os
from astropy.coordinates import SkyCoord
import astropy.units as u
CACHE = '/tmp/fanout/magpuls/raw/mwdd_ref.pkl'
def load():
    if os.path.exists(CACHE): return pd.read_pickle(CACHE)
    d = json.load(open('/tmp/mwd/mwdd/table.json'))['data']
    rows = []
    for r in d:
        rows.append(dict(gaia=r.get('gaiaedr3') or '', gaiadr2=r.get('gaiadr2') or '', wdid=r.get('wdid'), name=r.get('name'), spectype=r.get('spectype'),
                         ra_s=r.get('icrsra'), de_s=r.get('icrsdec'), pmra=r.get('pmra'), pmdec=r.get('pmdec'), G=r.get('G'), teff=r.get('teff'), logg=r.get('logg'),
                         mass=r.get('mass'), nper=r.get('number_periods'), var=r.get('variability'), ismag=r.get('ismag'), allnames=r.get('allnames'), binarity=r.get('binarity')))
    df = pd.DataFrame(rows)
    ok = df.ra_s.notna() & df.de_s.notna() & (df.ra_s != '') & (df.de_s != '')
    c = SkyCoord(df.loc[ok, 'ra_s'].values, df.loc[ok, 'de_s'].values, unit=(u.hourangle, u.deg))
    df['ra'] = np.nan; df['dec'] = np.nan
    df.loc[ok, 'ra'] = c.ra.deg; df.loc[ok, 'dec'] = c.dec.deg
    for k in ('pmra', 'pmdec', 'G', 'teff', 'logg', 'mass'): df[k] = pd.to_numeric(df[k], errors='coerce')
    df['nper'] = pd.to_numeric(df['nper'], errors='coerce').fillna(0).astype(int)
    df.to_pickle(CACHE); return df
def match(ra, dec, epoch=2000.0, maxsep=3.0):
    """Return list of (index into MWDD df, sep arcsec) nearest match for each input position (propagating MWDD 2016.0 -> epoch)."""
    df = load(); ok = df.ra.notna()
    ref = df[ok]; dt = epoch - 2016.0
    pmra = ref.pmra.fillna(0).values; pmde = ref.pmdec.fillna(0).values
    rae = ref.ra.values + pmra * dt / 3.6e6 / np.cos(np.radians(ref.dec.values)); dee = ref.dec.values + pmde * dt / 3.6e6
    cref = SkyCoord(rae * u.deg, dee * u.deg); cin = SkyCoord(np.asarray(ra) * u.deg, np.asarray(dec) * u.deg)
    idx, sep, _ = cin.match_to_catalog_sky(cref)
    out = []
    for i, s in zip(idx, sep.arcsec):
        out.append((ref.index[i], s) if s < maxsep else (None, s))
    return out
if __name__ == '__main__':
    df = load(); print(len(df), df.ra.notna().sum())

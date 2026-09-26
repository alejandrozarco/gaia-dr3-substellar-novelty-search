# Zeeman screen of SDSS-V (Astra 0.8.1 mwmStar coadd) spectra of every published pulsator / NOV with a SnowWhite row.
# Uses zfit (core+wing null vs triplet, line re-centring). DA-like classes only for the Balmer test; others recorded but flagged.
import sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/tmp/fanout/magpuls/scripts')
from astropy.io import fits
from zfit import fit
S = pd.read_csv('/tmp/fanout/magpuls/out/snowwhite_pulsators.csv', dtype={'sdss_id': str, 'gaia_dr3_source_id': str})
P = pd.read_csv('/tmp/fanout/magpuls/lists/puls_master.csv', dtype={'gaia_dr3': str}).set_index('gaia_dr3')
def load(fn):
    h = fits.open(fn); best = None
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        d = h[i].data[0]; snr = float(d['snr'])
        if best is None or snr > best[3]: best = (np.array(d['wavelength'], float), np.array(d['flux'], float), np.array(d['ivar'], float), snr, h[i].name)
    return best
out = []
for _, r in S.iterrows():
    fn = f"/tmp/fanout/magpuls/spec/sdssv/mwmStar-0.8.1-{r.sdss_id}.fits"
    try:
        lam, f, iv, snr, arm = load(fn); o = fit(lam, f, iv)
        rec = dict(gaia=r.gaia_dr3_source_id, sdss_id=r.sdss_id, sw=r.classification, snr=snr, arm=arm, claim=P.claim.get(r.gaia_dr3_source_id),
                   B=o['B_MG'], dchi2=o['dchi2'], chi2r_null=o['chi2r_null'], chi2r_best=o['chi2r_best'], metric=o['metric'], cen=o['centre_offsets'],
                   names=str(P.names.get(r.gaia_dr3_source_id))[:60])
    except Exception as e:
        rec = dict(gaia=r.gaia_dr3_source_id, sdss_id=r.sdss_id, sw=r.classification, error=str(e)[:100])
    out.append(rec)
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in rec.items() if k not in ('names',)}), flush=True)
json.dump(out, open('/tmp/fanout/magpuls/out/sdssv_pulsator_zeeman_screen.json', 'w'), indent=0, default=float)

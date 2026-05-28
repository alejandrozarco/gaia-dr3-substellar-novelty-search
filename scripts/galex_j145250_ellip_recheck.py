"""Sanity-check the 'TESS ellipsoidal 0.138%' claim for GALEX J145250-192225
(Gaia DR3 6281177228434199296). P_orb = 153.95 d -> ellipsoidal at P/2 = 77 d,
which is LONGER than a TESS sector (27 d): inter-sector systematics can fake it.
Test: is the folded amplitude at P/2 real (low permutation FAP vs random periods)
or just sector-systematic? Plus a Gaia blend check (RUWE=6.46 => likely double).
"""
import warnings, json, numpy as np
warnings.filterwarnings('ignore')
import lightkurve as lk
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.timeseries import LombScargle
from astroquery.gaia import Gaia

SID = 6281177228434199296
RA, DEC = 223.20970977619407, -19.373621697700553
P = 153.94723620655344
co = SkyCoord(RA*u.deg, DEC*u.deg)
out = {'P_orb_d': P, 'P_half_d': P/2, 'claimed_ellip_pct': 0.138}

# --- blend check: Gaia sources within 45" (~2 TESS px) ---
nb = Gaia.launch_job(
    "SELECT source_id, phot_g_mean_mag, DISTANCE(POINT(%f,%f),POINT(ra,dec))*3600 AS sep "
    "FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT(ra,dec),CIRCLE(%f,%f,0.0125)) "
    "ORDER BY phot_g_mean_mag" % (RA, DEC, RA, DEC)).get_results()
out['gaia_neighbors_45as'] = [{'sid': int(r['source_id']), 'G': round(float(r['phot_g_mean_mag']), 2),
                               'sep_as': round(float(r['sep']), 1)} for r in nb]

# --- TESS ---
out['authors'] = []
lcs = None
for auth in ['SPOC', 'TESS-SPOC', 'QLP']:
    s2 = lk.search_lightcurve(co, mission='TESS', author=auth)
    if s2 is not None and len(s2) > 0:
        out['authors'].append(f"{auth}:{len(s2)}")
        if lcs is None:
            try:
                lcs = s2.download_all(); out['used_author'] = auth; out['n_sectors'] = len(lcs)
            except Exception as ex:
                out[auth+'_err'] = str(ex)[:120]
if lcs is None:
    print(json.dumps(out, indent=1, default=str)); raise SystemExit

lc = lcs.stitch().remove_nans().remove_outliers(sigma=5)
t = np.asarray(lc.time.value, float); f = np.asarray(lc.flux.value, float)
e = np.asarray(lc.flux_err.value, float)
out['n_cadence'] = int(len(f)); out['baseline_d'] = float(t.max()-t.min())
out['per_cadence_relerr_median'] = float(np.nanmedian(e/f))
out['actual_coverage_d'] = float(len(np.unique(np.round(t))) )  # rough days-with-data

def foldP2P(Pf, nbins=40):
    ph = ((t-t.min())/Pf) % 1.0
    idx = np.clip((ph*nbins).astype(int), 0, nbins-1)
    bm = np.array([np.median(f[idx == b]) if np.any(idx == b) else np.nan for b in range(nbins)])
    return float(np.nanmax(bm)-np.nanmin(bm))

ampP = foldP2P(P); ampPh = foldP2P(P/2)
rng = np.random.default_rng(0)
ctrl = np.array([foldP2P(rng.uniform(20, 160)) for _ in range(400)])
out['foldP2P_at_Porb_pct'] = round(100*ampP, 4)
out['foldP2P_at_Phalf_pct'] = round(100*ampPh, 4)
out['random_period_P2P_pct_mean'] = round(100*float(ctrl.mean()), 4)
out['random_period_P2P_pct_p95'] = round(100*float(np.percentile(ctrl, 95)), 4)
out['Phalf_perm_FAP'] = float(np.mean(ctrl >= ampPh))
out['Porb_perm_FAP'] = float(np.mean(ctrl >= ampP))

# broad LS
ls = LombScargle(t, f, e)
freq, power = ls.autopower(minimum_frequency=1/250., maximum_frequency=1/0.4, samples_per_peak=6)
ip = int(np.argmax(power))
out['LS_peak_P_d'] = round(float(1/freq[ip]), 4)
out['LS_peak_FAP'] = float(ls.false_alarm_probability(power[ip]))

print(json.dumps(out, indent=1, default=str))
json.dump(out, open('/tmp/galex_j145250_ellip_recheck.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/galex_j145250_ellip_recheck.json')

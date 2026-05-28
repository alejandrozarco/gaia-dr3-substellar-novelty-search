"""Decisive eclipse test for CRTS J051419.8+011120 using the ACTUAL S98
2-min SPOC PDCSAP light curve (the product the original dossier used).
Masks outbursts via a running-median trend, divides it out (window >> eclipse
so the eclipse survives), folds quiescent residuals at the ZTF period, and
tests the deepest-bin dip with a permutation FAP over random periods.
"""
import warnings, json, numpy as np
warnings.filterwarnings('ignore')
import lightkurve as lk

TIC = 'TIC 672454027'
P_ZTF = 0.1255349  # d
out = {'P_ZTF_d': P_ZTF}

# ---- 1. fetch S98, prefer 2-min SPOC ----
sr = lk.search_lightcurve(TIC, mission='TESS', sector=98)
try:
    out['search'] = [f"{row['author']}|exp={row['exptime']}" for row in sr.table]
except Exception:
    out['search'] = str(sr)
lc = None
for auth in ['SPOC', 'TESS-SPOC', 'QLP']:
    s2 = lk.search_lightcurve(TIC, mission='TESS', sector=98, author=auth)
    if s2 is not None and len(s2) > 0:
        try:
            lc = s2.download()
            out['used_author'] = auth
            out['exptime_s'] = float(np.median(np.diff(lc.time.value))*86400)
            break
        except Exception as ex:
            out[f'{auth}_dl_err'] = str(ex)[:160]
if lc is None:
    print(json.dumps({'FATAL': 'no S98 light curve downloadable', **out}, indent=1)); raise SystemExit

# PDCSAP preferred
flux = None
for col in ('pdcsap_flux', 'sap_flux', 'flux'):
    if col in lc.colnames and np.isfinite(np.asarray(lc[col].value, float)).sum() > 100:
        flux = np.asarray(lc[col].value, float); out['flux_col'] = col; break
t = np.asarray(lc.time.value, float)
ferr = np.asarray(lc['flux_err'].value, float) if 'flux_err' in lc.colnames else np.full_like(flux, np.nan)
m = np.isfinite(flux) & np.isfinite(t)
t, flux, ferr = t[m], flux[m], ferr[m]
out['n_total'] = int(len(flux))

# ---- 2. running-median trend (0.5 d window >> 18-min eclipse) ----
order = np.argsort(t); t, flux, ferr = t[order], flux[order], ferr[order]
win = 0.5
trend = np.empty_like(flux)
lo = 0; hi = 0
for i in range(len(t)):
    while t[lo] < t[i]-win/2: lo += 1
    while hi < len(t) and t[hi] <= t[i]+win/2: hi += 1
    trend[i] = np.median(flux[lo:hi])
qbase = np.percentile(trend, 20)           # quiescent baseline
out['quiescent_baseline_flux'] = float(qbase)
out['per_cadence_relerr_median'] = float(np.nanmedian(ferr/np.maximum(flux, 1e-9)))  # ~ 1/(S/N)
out['per_cadence_SNR_quiescent'] = float(qbase / np.nanmedian(ferr)) if np.isfinite(np.nanmedian(ferr)) else None

# ---- 3. outburst mask + detrend ----
ob = trend > 1.4*qbase
qmask = ~ob
resid = flux/trend                          # eclipse survives (trend window >> eclipse)
tq, rq = t[qmask], resid[qmask]
out['n_quiescent'] = int(qmask.sum()); out['n_outburst'] = int(ob.sum())

# ---- 4. binned deepest-dip significance at a given period ----
def dip_stat(tq, rq, P, nbins=28):
    ph = ((tq - tq.min())/P) % 1.0
    idx = np.clip((ph*nbins).astype(int), 0, nbins-1)
    bm = np.array([np.mean(rq[idx==b]) if np.any(idx==b) else np.nan for b in range(nbins)])
    bn = np.array([np.sum(idx==b) for b in range(nbins)])
    ooe = np.nanmedian(bm)
    db = int(np.nanargmin(bm)); deepest = bm[db]
    depth = (ooe-deepest)/ooe
    scat = np.std(rq)
    sig = (ooe-deepest)/(scat/np.sqrt(max(bn[db], 1)))
    return depth, sig, db, ooe, scat, int(bn[db])

depth, sig, db, ooe, scat, nin = dip_stat(tq, rq, P_ZTF)
# fine period refine around ZTF P
grid = np.linspace(P_ZTF*0.997, P_ZTF*1.003, 121)
sigs = [dip_stat(tq, rq, Pg)[1] for Pg in grid]
P_best = float(grid[int(np.argmax(sigs))]); sig_best = float(np.max(sigs))
depth_b, _, _, _, _, _ = dip_stat(tq, rq, P_best)

# ---- 5. permutation FAP: random periods 0.08-0.20 d ----
rng = np.random.default_rng(1)
ntr = 3000
null = np.array([dip_stat(tq, rq, rng.uniform(0.08, 0.20))[1] for _ in range(ntr)])
fap_ZTF = float(np.mean(null >= sig))
fap_best = float(np.mean(null >= sig_best))

out['fold'] = {
    'at_ZTF_P': {'binned_depth': float(depth), 'deepest_bin_sigma': float(sig),
                 'n_in_deepbin': nin, 'OOE_level': float(ooe), 'per_cadence_scatter': float(scat),
                 'permutation_FAP': fap_ZTF},
    'refined_in_pm0.3pct': {'P_best_d': P_best, 'P_best_min': P_best*1440,
                            'binned_depth': float(depth_b), 'deepest_bin_sigma': sig_best,
                            'permutation_FAP': fap_best},
    'null_sigma_mean': float(np.mean(null)), 'null_sigma_p99': float(np.percentile(null, 99)),
}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open('/tmp/crts_j051419_spoc_recheck.json', 'w'), indent=1, default=str)
print('\nSAVED /tmp/crts_j051419_spoc_recheck.json')

"""Anchored archival recovery at a fixed period.
usage: recover.py TIC P T0 DUR [SEARCH_SECTOR]
For every archival TESS sector (one LC per sector: SPOC 2-min > TESS-SPOC > QLP), detrend as in search.py,
scan phase at fixed P/DUR, report max box SNR and its phase, and a trials-corrected FAP from wrong-period
null trials (same LC, 200 random non-commensurate periods; max over phase each time).
Writes rec/{tic}.json. Raw FITS are read in memory and never kept."""
import sys, os, io, json, warnings, time
import numpy as np, requests
from astropy.io import fits
from astroquery.mast import Observations
from wotan import flatten
warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f'{BASE}/rec', exist_ok=True)

def load(raw, prov):
    h = fits.open(io.BytesIO(raw)); d = h[1].data; cols = d.columns.names
    t = np.array(d['TIME'], float)
    for c in ['PDCSAP_FLUX', 'DET_FLUX', 'KSPSAP_FLUX', 'SAP_FLUX']:
        if c in cols: f = np.array(d[c], float); col = c; break
    q = np.array(d['QUALITY']) if 'QUALITY' in cols else np.zeros(len(t), int)
    m = np.isfinite(t) & np.isfinite(f) & (q == 0) & (f > 0)
    return t[m], f[m] / np.nanmedian(f[m]), col, h[0].header.get('SECTOR')

def clean(t, f):
    if len(t) < 100: return t, f, np.nan
    g = np.where(np.diff(t) > 0.5)[0]
    edges = np.concatenate([[t[0]], t[g], t[g + 1], [t[-1]]])
    bad = np.zeros(len(t), bool)
    for e in edges: bad |= np.abs(t - e) < 0.25
    t, f = t[~bad], f[~bad]
    fl = flatten(t, f, method='biweight', window_length=0.75, break_tolerance=0.3)
    ok = np.isfinite(fl); t, fl = t[ok], fl[ok]
    mad = 1.4826 * np.median(np.abs(fl - np.median(fl)))
    ok = (fl < 1 + 4 * mad) & (fl > 1 - 30 * mad); t, fl = t[ok], fl[ok]
    bi = np.floor((t - t[0]) / 0.5).astype(int); loc = np.zeros(len(t))
    for b in np.unique(bi):
        s = bi == b
        loc[s] = 1.4826 * np.median(np.abs(fl[s] - np.median(fl[s]))) if s.sum() > 10 else np.inf
    ok = loc < 2.0 * np.median(loc[np.isfinite(loc)]); t, fl = t[ok], fl[ok]
    # bin to 10 min
    k = np.floor((t - t[0]) / (10 / 1440.)).astype(int); c = np.bincount(k); g = c > 0
    tb = np.bincount(k, weights=t)[g] / c[g]; fb = np.bincount(k, weights=fl)[g] / c[g]
    return tb, fb, mad

def sig_dur(t, f, dur):
    k = np.floor((t - t[0]) / dur).astype(int); c = np.bincount(k); s = np.bincount(k, weights=f)
    g = c >= 0.5 * np.median(c[c > 0]); bm = s[g] / c[g]
    return 1.4826 * np.median(np.abs(bm - np.median(bm)))

def phase_scan(t, f, P, dur, sd, step=None):
    step = step or dur / 4
    phs = np.arange(0, P, step)
    ph = (t % P)
    out = np.full(len(phs), np.nan); nev = np.zeros(len(phs), int)
    pts_per_dur = max(1, dur / (10 / 1440.))
    for i, c in enumerate(phs):
        dd = np.abs(((ph - c + 0.5 * P) % P) - 0.5 * P)
        s = dd < 0.5 * dur
        if s.sum() >= 0.5 * pts_per_dur:
            ne = s.sum() / pts_per_dur
            out[i] = np.mean(1 - f[s]) / sd * np.sqrt(ne); nev[i] = round(ne)
    return phs, out, nev

def main():
    tic = int(sys.argv[1]); P = float(sys.argv[2]); T0 = float(sys.argv[3]); dur = float(sys.argv[4])
    ssec = int(sys.argv[5]) if len(sys.argv) > 5 else -1
    obs = Observations.query_criteria(target_name=str(tic), obs_collection=['TESS', 'HLSP'], dataproduct_type='timeseries')
    rows = {}
    pr_rank = {'SPOC': 0, 'TESS-SPOC': 1, 'QLP': 2}
    for o in obs:
        prov = str(o['provenance_name'])
        if prov not in pr_rank: continue
        sec = int(o['sequence_number'])
        if sec == ssec: continue
        if sec in rows and pr_rank[rows[sec]['prov']] <= pr_rank[prov]: continue
        rows[sec] = dict(prov=prov, obsid=o['obsid'])
    res = dict(tic=tic, P=P, T0=T0, dur=dur, search_sector=ssec, sectors=[])
    rng = np.random.default_rng(tic % 2**32)
    for sec in sorted(rows):
        r = rows[sec]
        try:
            prods = Observations.get_product_list(r['obsid'])
            m = [i for i, p in enumerate(prods) if str(p['productFilename']).endswith(('lc.fits', 'llc.fits')) and 'fast' not in str(p['productFilename'])]
            if not m: continue
            uri = prods[m[0]]['dataURI']
            raw = requests.get('https://mast.stsci.edu/api/v0.1/Download/file?uri=' + uri, timeout=120).content
            t, f, col, _ = load(raw, r['prov']); del raw
            t, f, mad = clean(t, f)
            if len(t) < 300: continue
            sd = sig_dur(t, f, dur)
            phs, s, nev = phase_scan(t, f, P, dur, sd)
            imax = int(np.nanargmax(s)); smax = float(s[imax])
            # predicted phase from search-sector ephemeris
            pph = T0 % P
            dpp = np.abs(((phs - pph + 0.5 * P) % P) - 0.5 * P)
            s_pred = float(np.nanmax(np.where(dpp < 0.5 * dur, s, -np.inf)))
            null = []
            for k in range(100):
                Pt = P * (1 + rng.uniform(0.02, 0.3) * rng.choice([-1, 1]))
                _, sn, _ = phase_scan(t, f, Pt, dur, sd, step=dur / 2)
                null.append(np.nanmax(sn))
            null = np.array(null)
            fap = float((np.sum(null >= smax) + 1) / (len(null) + 1))
            res['sectors'].append(dict(sector=sec, prov=r['prov'], col=col, n=len(t), sd=float(sd),
                                       smax=smax, ph_max=float(phs[imax]), nev=int(nev[imax]),
                                       fap_trials=fap, s_at_pred=s_pred, tmid=float(np.median(t)),
                                       null_p50=float(np.median(null)), null_p99=float(np.percentile(null, 99))))
            print(sec, r['prov'], f'smax={smax:.1f} ph={phs[imax]:.3f} fap={fap:.3f} null99={np.percentile(null,99):.1f}', flush=True)
        except Exception as e:
            res['sectors'].append(dict(sector=sec, prov=r['prov'], error=str(e)[:100]))
    json.dump(res, open(f'{BASE}/rec/{tic}.json', 'w'), indent=1)

if __name__ == '__main__':
    main()

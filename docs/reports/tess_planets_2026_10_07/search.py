"""Per-sector QLP BLS search, streamed in batches with DONE markers.
usage: search.py SECTOR QUEUE_FILE BATCH_INDEX_START BATCH_INDEX_STOP
QUEUE_FILE: csv with columns tic (ordered by priority). Batches of 200.
Output per batch: res/s{sec}/b{idx:05d}.csv (+ .DONE), candidate LCs to lc/s{sec}/{tic}.npz
Raw FITS are never kept on disk (read from memory)."""
import sys, os, io, time, warnings, json
import numpy as np, requests
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
from wotan import flatten
warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.abspath(__file__))
SEC = int(sys.argv[1]); QF = sys.argv[2]; B0 = int(sys.argv[3]); B1 = int(sys.argv[4])
NB = int(os.environ.get("NB", 200))
RES = f'{BASE}/res/s{SEC:04d}'; LCD = f'{BASE}/lc/s{SEC:04d}'
os.makedirs(RES, exist_ok=True); os.makedirs(LCD, exist_ok=True)
sess = requests.Session()

def url(tic, sec):
    t = f'{tic:016d}'
    return (f'https://archive.stsci.edu/hlsps/qlp/s{sec:04d}/{t[0:4]}/{t[4:8]}/{t[8:12]}/{t[12:16]}/'
            f'hlsp_qlp_tess_ffi_s{sec:04d}-{t}_tess_v01_llc.fits')

def fetch(tic):
    for k in range(3):
        try:
            r = sess.get(url(tic, SEC), timeout=60)
            if r.status_code == 200 and r.content[:6] == b'SIMPLE':
                return r.content
            if r.status_code == 404:
                return None
        except Exception:
            time.sleep(2)
    return 'ERR'

DURS = np.array([0.03, 0.045, 0.06, 0.08, 0.11, 0.15, 0.2])

def analyse(tic, raw, inj=None):
    h = fits.open(io.BytesIO(raw))
    hd = h[0].header; d = h[1].data
    t = np.array(d['TIME'], float); f = np.array(d['DET_FLUX'], float); q = np.array(d['QUALITY'])
    m = np.isfinite(t) & np.isfinite(f) & (q == 0) & (f > 0)
    t, f = t[m], f[m]
    if inj is not None:
        iP, iT0, idur, idep = inj
        ph_ = np.abs(((t - iT0 + 0.5 * iP) % iP) - 0.5 * iP)
        tau = 0.15 * idur  # ingress
        prof = np.clip((0.5 * idur - ph_) / tau, 0, 1)
        f = f * (1 - idep * prof)
    # drop 0.25 d after/before every gap > 0.5 d (ramps)
    if len(t) > 10:
        g = np.where(np.diff(t) > 0.5)[0]
        edges = np.concatenate([[t[0]], t[g], t[g + 1], [t[-1]]])
        bad = np.zeros(len(t), bool)
        for e in edges: bad |= np.abs(t - e) < 0.25
        t, f = t[~bad], f[~bad]
    if len(t) < 500: return dict(tic=tic, status='short', n=len(t)), None
    f = f / np.nanmedian(f)
    fl, tr = flatten(t, f, method='biweight', window_length=0.75, return_trend=True, break_tolerance=0.3)
    ok = np.isfinite(fl)
    t, fl = t[ok], fl[ok]
    # clip upward outliers and extreme downward single points
    mad = 1.4826 * np.nanmedian(np.abs(fl - np.nanmedian(fl)))
    ok = (fl < 1 + 4 * mad) & (fl > 1 - 30 * mad)
    t, fl = t[ok], fl[ok]
    # local scatter in 0.5-d bins; drop bins noisier than 2x the median bin scatter (scattered light)
    bi_ = np.floor((t - t[0]) / 0.5).astype(int)
    loc = np.zeros(len(t))
    for b_ in np.unique(bi_):
        s_ = bi_ == b_
        loc[s_] = 1.4826 * np.median(np.abs(fl[s_] - np.median(fl[s_]))) if s_.sum() > 20 else np.inf
    ok = loc < 2.0 * np.median(loc[np.isfinite(loc)])
    t, fl = t[ok], fl[ok]
    if len(t) < 500: return dict(tic=tic, status='short2', n=len(t)), None
    mad = 1.4826 * np.nanmedian(np.abs(fl - np.nanmedian(fl)))
    span = t.max() - t.min()
    pmax = min(20.0, span / 2.0)
    # 10-min bins for the search (QLP S105 cadence is 200 s)
    kb = np.floor((t - t[0]) / (10 / 1440.)).astype(int)
    cb = np.bincount(kb); gk = cb > 0
    tb_ = (np.bincount(kb, weights=t)[gk] / cb[gk]); fb_ = (np.bincount(kb, weights=fl)[gk] / cb[gk])
    bls = BoxLeastSquares(tb_, fb_, dy=mad / np.sqrt(cb[gk]))
    periods = np.exp(np.linspace(np.log(0.5), np.log(pmax), 9000))
    pw = np.zeros(len(periods)); bT0 = np.zeros(len(periods)); bdur = np.zeros(len(periods)); bdep = np.zeros(len(periods))
    for D in DURS:
        r_ = bls.power(periods, D, objective='likelihood')
        p_ = np.where(periods * 0.12 >= D, r_.power, 0)
        u_ = p_ > pw
        pw[u_] = p_[u_]; bT0[u_] = r_.transit_time[u_]; bdur[u_] = D; bdep[u_] = r_.depth[u_]
    class _G: pass
    pg = _G(); pg.period = periods; pg.transit_time = bT0; pg.duration = bdur; pg.depth = bdep
    from scipy.ndimage import median_filter, maximum_filter
    base = median_filter(pw, 301, mode='nearest'); resid = pw - base
    sd = np.std(resid); mu = np.mean(resid)
    loc = (resid == maximum_filter(resid, 15))
    cand = np.where(loc)[0]; cand = cand[np.argsort(-resid[cand])][:25]
    def events(P, T0, dur):
        ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P
        intr = np.abs(ph) < 0.5 * dur
        ep = np.round((t - T0) / P).astype(int)
        ev = []
        for e in np.unique(ep[intr]):
            s = intr & (ep == e)
            if s.sum() >= 3: ev.append((e, np.mean(1 - fl[s]), s.sum()))
        es = [d_ * np.sqrt(n_) / mad for e_, d_, n_ in ev]
        mf = (max(es) / np.sqrt(np.sum(np.square(es)))) if len(es) and np.sum(np.square(es)) > 0 else 1
        return ph, intr, ep, ev, mf
    i = None
    for j in cand:
        if pg.depth[j] <= 0: continue
        ph, intr, ep, ev_dep, maxfrac = events(pg.period[j], pg.transit_time[j], pg.duration[j])
        if len(ev_dep) >= 2 and maxfrac <= 0.8:
            i = j; break
    if i is None:
        return dict(tic=tic, status='nopeak', n=len(t), tmag=hd.get('TESSMAG'), mad=mad), None
    P, T0, dur, dep = pg.period[i], pg.transit_time[i], pg.duration[i], pg.depth[i]
    sde = (resid[i] - mu) / sd
    nin = intr.sum()
    nev = len(ev_dep)
    snr_w = dep / (mad / np.sqrt(max(nin, 1)))
    # red-noise aware: scatter of the out-of-transit LC binned at the transit duration
    oot = ~intr
    nb_ = np.floor((t[oot] - t[0]) / dur).astype(int)
    cnt = np.bincount(nb_); sm = np.bincount(nb_, weights=fl[oot])
    gb = cnt >= 0.5 * np.median(cnt[cnt > 0])
    bm = sm[gb] / cnt[gb]
    sig_d = 1.4826 * np.median(np.abs(bm - np.median(bm)))
    snr = dep / sig_d * np.sqrt(nev)
    nev = len(ev_dep)
    # odd/even
    odd = intr & (ep % 2 == 1); evn = intr & (ep % 2 == 0)
    def dd(s):
        return (np.mean(1 - fl[s]), mad / np.sqrt(s.sum())) if s.sum() > 2 else (np.nan, np.nan)
    do, eo = dd(odd); de, ee = dd(evn)
    oe_sig = abs(do - de) / np.hypot(eo, ee) if np.isfinite(do) and np.isfinite(de) else np.nan
    # secondary: best box depth over phase 0.3-0.7 at same duration
    phs = ((t - T0) / P) % 1
    best2 = 0; best2ph = np.nan
    for c in np.arange(0.3, 0.7, dur / P / 2):
        s = np.abs(phs - c) < 0.5 * dur / P
        if s.sum() > 3:
            v = np.mean(1 - fl[s]) / (mad / np.sqrt(s.sum()))
            if v > best2: best2, best2ph = v, c
    # V-shape: depth in central half vs edges of transit
    cen = np.abs(ph) < 0.25 * dur; edg = intr & ~cen
    vrat = (np.mean(1 - fl[edg]) / np.mean(1 - fl[cen])) if cen.sum() > 2 and edg.sum() > 2 else np.nan
    row = dict(tic=tic, status='ok', n=len(t), tmag=hd.get('TESSMAG'), teff=hd.get('TEFF'), rstar=hd.get('RADIUS'),
               cam=hd.get('CAMERA'), ccd=hd.get('CCD'), P=P, T0=T0, dur=dur, depth=dep, snr=snr, snr_w=snr_w, sde=sde,
               nev=nev, maxfrac=maxfrac, evtimes=';'.join(f'{T0+e_*P:.3f}' for e_,d_,n_ in ev_dep), oe_sig=oe_sig, sec_snr=best2, sec_ph=best2ph, vrat=vrat, mad=mad, span=span)
    keep = None
    if snr >= 6.5:
        b = 10. / 1440.; tb = np.floor(t / b)
        keep = dict(t=t.astype(np.float64), f=fl.astype(np.float32))
    return row, keep

def main():
    tics = np.loadtxt(QF, delimiter=',', skiprows=1, usecols=0, dtype=np.int64, ndmin=1)
    nbat = int(np.ceil(len(tics) / NB))
    pool = ThreadPoolExecutor(8)
    for bi in range(B0, min(B1, nbat)):
        out = f'{RES}/b{bi:05d}.csv'
        if os.path.exists(out + '.DONE'): continue
        batch = tics[bi * NB:(bi + 1) * NB]
        t0 = time.time(); rows = []
        for tic, raw in zip(batch, pool.map(fetch, batch)):
            if raw is None: rows.append(dict(tic=tic, status='404')); continue
            if raw == 'ERR': rows.append(dict(tic=tic, status='ERR')); continue
            try:
                row, keep = analyse(int(tic), raw)
            except Exception as e:
                row, keep = dict(tic=tic, status='EXC:' + str(e)[:60].replace(',', ';')), None
            rows.append(row)
            if keep is not None:
                np.savez_compressed(f'{LCD}/{tic}.npz', **keep)
            del raw
        import csv
        keys = ['tic','status','n','tmag','teff','rstar','cam','ccd','P','T0','dur','depth','snr','snr_w','sde','nev','maxfrac','evtimes',
                'oe_sig','sec_snr','sec_ph','vrat','mad','span']
        with open(out, 'w') as fh:
            w = csv.DictWriter(fh, keys, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
        open(out + '.DONE', 'w').write(f'{time.time()-t0:.1f}\n')
        with open(f'{BASE}/progress_s{SEC:04d}.log', 'a') as fh:
            nok = sum(r['status'] == 'ok' for r in rows)
            fh.write(f'{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} batch {bi}/{nbat} ok {nok}/{len(rows)} {time.time()-t0:.0f}s\n')

if __name__ == '__main__':
    main()

"""Multi-sector ephemeris + leave-one-sector-out prediction test for a recovered candidate.
usage: lsoo.py TIC P DUR    (uses all sectors incl. the search sector; LCs cached to lc_multi/{tic}.npz)"""
import sys, os, json, numpy as np, requests
sys.argv_ = sys.argv[:]
from recover import load, clean, sig_dur
from astroquery.mast import Observations
from astropy.timeseries import BoxLeastSquares
BASE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{BASE}/lc_multi', exist_ok=True)
tic = int(sys.argv[1]); P0 = float(sys.argv[2]); dur = float(sys.argv[3])
cache = f'{BASE}/lc_multi/{tic}.npz'
if os.path.exists(cache):
    z = np.load(cache); T, F, S = z['t'], z['f'], z['s']
else:
    obs = Observations.query_criteria(target_name=str(tic), obs_collection=['TESS', 'HLSP'], dataproduct_type='timeseries')
    rank = {'SPOC': 0, 'TESS-SPOC': 1, 'QLP': 2}; best = {}
    for o in obs:
        p = str(o['provenance_name']); s = int(o['sequence_number'])
        if p in rank and (s not in best or rank[p] < rank[best[s][0]]): best[s] = (p, o['obsid'])
    T, F, S = [], [], []
    for s in sorted(best):
        prods = Observations.get_product_list(best[s][1])
        m = [i for i, p in enumerate(prods) if str(p['productFilename']).endswith(('lc.fits', 'llc.fits')) and 'fast' not in str(p['productFilename'])]
        if not m: continue
        raw = requests.get('https://mast.stsci.edu/api/v0.1/Download/file?uri=' + prods[m[0]]['dataURI'], timeout=120).content
        t, f, col, _ = load(raw, best[s][0]); t, f, mad = clean(t, f)
        if len(t) < 300: continue
        T.append(t); F.append(f); S.append(np.full(len(t), s)); print('sector', s, best[s][0], len(t), flush=True)
    T, F, S = map(np.concatenate, (T, F, S)); np.savez_compressed(cache, t=T, f=F, s=S)

def fit(t, f, Pc):
    per = np.linspace(Pc * (1 - 0.003), Pc * (1 + 0.003), 6000)
    b = BoxLeastSquares(t, f); r = b.power(per, dur, objective='snr', oversample=20)
    i = np.argmax(r.power); return r.period[i], r.transit_time[i], r.depth[i], r.power[i]

secs = np.unique(S)
P, T0, dep, pw = fit(T, F, P0)
out = dict(tic=tic, P=P, T0=T0, depth=dep, snr_all=pw, sectors=[int(s) for s in secs], loo=[])
print(f'all-sector fit P={P:.6f} T0={T0:.5f} depth={dep*1e6:.0f} ppm snr={pw:.1f}')
rng = np.random.default_rng(1)
for s in secs:
    o = S != s; h = S == s
    if np.sum(o) < 300: continue
    Pf, T0f, df, _ = fit(T[o], F[o], P)
    th, fh = T[h], F[h]; sd = sig_dur(th, fh, dur)
    def box(c):
        ph = np.abs(((th - c + 0.5 * Pf) % Pf) - 0.5 * Pf); m = ph < 0.5 * dur
        n = m.sum() / max(1, dur / (np.median(np.diff(th))))
        return np.mean(1 - fh[m]) / sd * np.sqrt(max(n, 1e-9)) if m.sum() > 2 else np.nan, np.mean(1 - fh[m]) if m.sum() > 2 else np.nan
    spred, dpred = box(T0f)
    rnd = np.array([box(T0f + rng.uniform(1.5 * dur, Pf - 1.5 * dur))[0] for _ in range(300)])
    rnd = rnd[np.isfinite(rnd)]
    p = (np.sum(rnd >= spred) + 1) / (len(rnd) + 1)
    out['loo'].append(dict(sector=int(s), snr_pred=float(spred), depth_pred=float(dpred), p_random=float(p), dep_others=float(df)))
    print(f'held-out S{s}: SNR at predicted phase {spred:.1f}, depth {dpred*1e6:.0f} ppm (others {df*1e6:.0f}), p(random phase>=)={p:.3f}')
# odd/even + secondary on all data
ph = ((T - T0 + 0.5 * P) % P) - 0.5 * P; ep = np.round((T - T0) / P).astype(int); it = np.abs(ph) < 0.5 * dur
sdall = sig_dur(T, F, dur)
for nm, m in [('odd', it & (ep % 2 == 1)), ('even', it & (ep % 2 == 0))]:
    out[nm] = float(np.mean(1 - F[m])); print(nm, f'{out[nm]*1e6:.0f} ppm')
p2 = ((T - T0) / P) % 1; m2 = np.abs(p2 - 0.5) < 0.5 * dur / P
out['secondary'] = float(np.mean(1 - F[m2])); print('secondary at 0.5', f"{out['secondary']*1e6:.0f} ppm")
json.dump(out, open(f'{BASE}/rec/{tic}_lsoo.json', 'w'), indent=1)

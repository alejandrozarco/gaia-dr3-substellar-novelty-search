"""Extra flux-level vets on saved search-sector LCs for the shortlist.
anti: SNR of the BRIGHTENING at phase 0.5 (sinusoid signature); oot_amp: amplitude of a 1st-harmonic sinusoid fit
to out-of-transit flux at P relative to depth; half: depth in first vs second orbit (TESS orbit halves);
emom: fraction of in-transit points within 0.3 d after a gap (momentum dump/orbit start)."""
import pandas as pd, numpy as np, os, sys
SEC = sys.argv[1] if len(sys.argv) > 1 else '0105'
c = pd.read_csv(f'shortlist_s{SEC}.csv')
rows = []
for _, r in c.iterrows():
    fn = f'lc/s{SEC}/{int(r.tic)}.npz'
    if not os.path.exists(fn): continue
    z = np.load(fn); t, f = z['t'], z['f'].astype(float)
    P, T0, dur = r.P, r.T0, r.dur
    ph = ((t - T0 + 0.5 * P) % P) - 0.5 * P; it = np.abs(ph) < 0.5 * dur
    mad = 1.4826 * np.median(np.abs(f - np.median(f)))
    a = np.abs(np.abs(ph) - 0.5 * P) < 0.5 * dur
    anti = (np.mean(f[a]) - 1) / (mad / np.sqrt(max(a.sum(), 1))) if a.sum() > 2 else np.nan
    x = 2 * np.pi * ph / P; o = ~it
    A = np.vstack([np.ones(o.sum()), np.cos(x[o]), np.sin(x[o])]).T
    cf = np.linalg.lstsq(A, f[o], rcond=None)[0]
    amp = np.hypot(cf[1], cf[2])
    mid = np.median(t)
    d1 = np.mean(1 - f[it & (t < mid)]) if (it & (t < mid)).sum() > 2 else np.nan
    d2 = np.mean(1 - f[it & (t >= mid)]) if (it & (t >= mid)).sum() > 2 else np.nan
    g = np.where(np.diff(t) > 0.1)[0]; gaps_end = t[g + 1]
    near = np.array([np.any((tt - gaps_end > 0) & (tt - gaps_end < 0.3)) for tt in t[it]]) if it.sum() else np.array([])
    rows.append(dict(tic=int(r.tic), anti=anti, oot_amp_rel=amp / max(r.depth, 1e-9), d1=d1, d2=d2,
                     half_ratio=(min(d1, d2) / max(d1, d2)) if np.isfinite(d1) and np.isfinite(d2) and max(d1, d2) > 0 else np.nan,
                     frac_after_gap=near.mean() if len(near) else np.nan))
v = pd.DataFrame(rows)
c = c.drop(columns=[x for x in v.columns if x != 'tic' and x in c.columns]).merge(v, on='tic', how='left')
c['sinusoid'] = (c.anti > 3) | (c.oot_amp_rel > 0.5)
c['half_bad'] = c.half_ratio < 0.3
c.to_csv(f'shortlist_s{SEC}_vet.csv', index=False)
print(len(c), 'sinusoid flagged', int(c.sinusoid.sum()), 'half-inconsistent', int(c.half_bad.sum()))
pd.set_option('display.width', 250)
print(c[c.toi.isna()][['tic', 'P', 'depth', 'snr', 'anti', 'oot_amp_rel', 'half_ratio', 'frac_after_gap', 'sinusoid']].to_string(index=False))

"""Outburst detector for ZTF alert light curves (ALeRCE detections).
Apparent magnitude = magpsf_corr when the object has a reference counterpart (corrected), else magpsf (the source is
absent from the reference image, so every detection is an excess over a quiescent level fainter than the reference).
Per band: quiescent level q = 80th percentile of magnitudes (faint end, robust to outbursts) for corrected objects, or
the median image limit (diffmaglim) for uncorrected ones. Outburst points: brighter than q - AMP (default 1.2 mag),
real-bogus drb >= 0.5 where available, not dubious. Episodes: outburst points grouped with gaps <= 15 d; an episode needs
>= 2 points. Output per object: n_episodes, max amplitude, median episode length, g-r at peak, n points, corrected flag.
Usage: python outburst.py <lcdir> <objects.csv> <out.csv>"""
import sys, os, numpy as np, pandas as pd
AMP = float(os.environ.get("AMP", 1.2)); GAP = 15.0
def analyse(f, G=np.nan):
    """Brightening relative to Gaia G when available (a ZTF reference that underestimates the star makes every visit a false brightening), else relative to the reference image. Corrected objects: F_ref = F_corr - F_diff for positive differences,
    delta = 2.5 log10(F_corr / F_ref). Objects without a reference counterpart: delta = G(Gaia) - magpsf (lower bound when G
    is missing: 21.0 - magpsf). Only positive-difference detections count; real-bogus: drb >= 0.5, or rb >= 0.25 when drb is absent/zero."""
    d = pd.read_csv(f)
    if d.empty: return dict(npts=0)
    ok = (d.drb >= 0.5) | (((d.drb.isna()) | (d.drb == 0)) & (d.rb >= 0.25))
    d = d[ok & (d.dubious != True)]
    corr = bool(d.corrected.fillna(False).astype(bool).mean() > 0.5) if len(d) else False
    if corr: d = d[(d.magpsf_corr < 90) | d.magpsf_corr.isna()]   # 100 = placeholder for an undefined corrected magnitude
    neg_frac = float((d.isdiffpos == -1).mean()) if len(d) else np.nan
    pos = d[d.isdiffpos == 1].copy()
    if pos.empty: return dict(npts=len(d), n_pos=0, corrected=corr)
    if corr and np.isfinite(G):
        pos["delta"] = G - pos.magpsf_corr; pos["m"] = pos.magpsf_corr   # external quiescent level: Gaia G (the ZTF reference can be biased faint)
    elif corr:
        Fc = 10 ** (-0.4 * pos.magpsf_corr); Fd = 10 ** (-0.4 * pos.magpsf); Fr = Fc - Fd
        pos["delta"] = 2.5 * np.log10(Fc / Fr.where(Fr > 0))   # reference flux <= 0 -> undefined, dropped
        pos["m"] = pos.magpsf_corr
    else:
        q = G if np.isfinite(G) else 21.0
        pos["delta"] = q - pos.magpsf; pos["m"] = pos.magpsf
    pos = pos.replace([np.inf, -np.inf], np.nan).dropna(subset=["m", "delta"])
    if pos.empty: return dict(npts=len(d), n_pos=0, corrected=corr)
    ob = pos[pos.delta >= AMP].sort_values("mjd")
    eps = []
    if len(ob):
        grp = (ob.mjd.diff() > GAP).cumsum()
        for _, e in ob.groupby(grp):
            if len(e) >= 2: eps.append((e.mjd.min(), e.mjd.max(), e.m.min()))
    gr = np.nan
    if len(ob):
        pk = ob.loc[ob.m.idxmin()]; near = ob[np.abs(ob.mjd - pk.mjd) < 1.0]
        if {1, 2} <= set(near.fid): gr = near[near.fid == 1].m.min() - near[near.fid == 2].m.min()
    return dict(npts=len(d), n_pos=len(pos), neg_frac=round(neg_frac, 3), corrected=corr, amp_max=round(float(pos.delta.max()), 2), n_ob_pts=len(ob), n_ep=len(eps),
                ep_len_med=round(np.median([b - a for a, b, _ in eps]), 1) if eps else np.nan, gr_peak=round(gr, 2) if np.isfinite(gr) else np.nan,
                peak_mag=round(float(ob.m.min()), 2) if len(ob) else np.nan, span_d=round(d.mjd.max() - d.mjd.min(), 0), first_ep=round(eps[0][0], 1) if eps else np.nan)
if __name__ == "__main__":
    L, O, OUT = sys.argv[1:4]; ob = pd.read_csv(O); rows = []
    for oid, G in zip(ob.oid, ob.G if "G" in ob else [np.nan] * len(ob)):
        f = f"{L}/{oid}.csv"
        rows.append(dict(oid=oid, **(analyse(f, G) if os.path.exists(f) else dict(npts=-1))))
    R = pd.DataFrame(rows); R.to_csv(OUT, index=False); print(len(R), "analysed")

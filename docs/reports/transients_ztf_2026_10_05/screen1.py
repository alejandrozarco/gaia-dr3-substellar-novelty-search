"""Screen 1 (2026-10-01): per fresh ALeRCE object, positive detections with drb >= 0.8; time span; motion (arcsec/hr) from the
earliest-latest positive detections; prior alert history (mjdstarthist vs firstmjd). Output: screen1.csv"""
import pandas as pd, numpy as np
D = pd.read_csv("dets_all.csv"); O = pd.read_csv("alerce_fresh.csv").set_index("oid")
D["pos"] = D.isdiffpos.astype(str).isin(["1", "t", "True"]); P = D[D.pos & (D.drb >= 0.8)].sort_values("mjd"); rows = []
for o, x in P.groupby("oid"):
    if len(x) < 2: continue
    a, b = x.iloc[0], x.iloc[-1]; dt = (b.mjd - a.mjd) * 24
    sep = np.hypot((b.ra - a.ra) * np.cos(np.radians(a.dec)), b.dec - a.dec) * 3600
    rmsra = (x.ra - x.ra.mean()).std() * np.cos(np.radians(a.dec)) * 3600; rmsde = (x.dec - x.dec.mean()).std() * 3600
    nights = np.unique(np.floor(x.mjd)).size; o_ = O.loc[o]
    rows.append(dict(oid=o, ra=x.ra.mean(), dec=x.dec.mean(), npos=len(x), nights=nights, span_h=dt, sep_as=sep, rate_ash=sep / dt if dt > 0 else np.nan,
                     rms_as=float(np.hypot(rmsra, rmsde)), first=a.mjd, mag_first=a.magpsf, fid_first=int(a.fid), magmin=x.magpsf.min(), magmax=x.magpsf.max(),
                     distnr_med=x.distnr.median(), drb_med=x.drb.median(), firstmjd=o_.firstmjd, mjdstarthist=o_.mjdstarthist, ndethist=o_.ndethist,
                     hist_prior_d=o_.firstmjd - o_.mjdstarthist, nneg=int((~D[D.oid == o].pos).sum())))
S = pd.DataFrame(rows); S.to_csv("screen1.csv", index=False)
print(len(S)); print("nights>=2:", (S.nights >= 2).sum(), "span>0.5h:", (S.span_h > 0.5).sum())
print("pairs-only (span<0.1h) rate pct:", np.nanpercentile(S[S.span_h < 0.1].rate_ash, [10, 25, 50, 75, 90]).round(1))
print("span>0.5h rate pct:", np.nanpercentile(S[S.span_h > 0.5].rate_ash, [10, 25, 50, 75, 90]).round(2))
print("hist prior >30d:", (S.hist_prior_d > 30).sum())

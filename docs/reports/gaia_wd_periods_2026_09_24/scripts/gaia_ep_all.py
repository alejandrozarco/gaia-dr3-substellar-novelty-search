# Gaia DR3 epoch photometry (VizieR I/355/epphot) for the unconfirmed candidates: power and sinusoid amplitude/phase at the Gaia GLS
# frequency in G, BP, RP (rejected transits removed); permutation p of the G power (1000 shuffles).
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astroquery.vizier import Vizier
from astropy.timeseries import LombScargle
u = pd.read_csv("unconfirmed.csv", dtype={"source_id": str}); V = Vizier(columns=["**"], row_limit=-1); rng = np.random.default_rng(5); rows = []
for _, r in u.iterrows():
    try: t = V.query_constraints(catalog="I/355/epphot", Source=r.source_id)[0].to_pandas()
    except Exception as e: print(r.source_id, "no epphot", str(e)[:60]); continue
    t.to_csv(f"epphot_{r.source_id}.csv", index=False); f = r.gls_freq_g_fov; out = dict(source_id=r.source_id, f=f)
    for b, tc, fc, ec, fl in (("G", "TimeG", "FG", "e_FG", "GrVFlag"), ("BP", "TimeBP", "FBP", "e_FBP", "BPrVFlag"), ("RP", "TimeRP", "FRP", "e_FRP", "RPrVFlag")):
        s = t[(t[fl] == 0) & np.isfinite(t[fc]) & np.isfinite(t[tc])]
        if len(s) < 8: continue
        x = s[tc].values + 2455197.5; y = s[fc].values / np.median(s[fc]) - 1; e = s[ec].values / np.median(s[fc])
        X = np.vstack([np.ones_like(x), np.sin(2*np.pi*f*(x-2458000)), np.cos(2*np.pi*f*(x-2458000))]).T; W = 1/e**2
        p = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*y)); C = np.linalg.inv(X.T @ (X*W[:, None])); c2 = max(np.sum(W*(y-X@p)**2)/(len(x)-3), 1)
        pw = LombScargle(x, y, e).power(np.array([f]))[0]
        out[f"{b}_n"] = len(x); out[f"{b}_amp"] = round(np.hypot(p[1], p[2]), 4); out[f"{b}_eamp"] = round(np.sqrt(c2*(C[1,1]+C[2,2])/2), 4)
        out[f"{b}_ph"] = round(np.degrees(np.arctan2(p[1], p[2])) % 360); out[f"{b}_pow"] = round(pw, 3)
        if b == "G": out["G_perm_p"] = np.mean([LombScargle(x, rng.permutation(y), e).power(np.array([f]))[0] >= pw for _ in range(1000)])
    rows.append(out); print(out, flush=True)
pd.DataFrame(rows).to_csv("gaia_ep_check.csv", index=False)

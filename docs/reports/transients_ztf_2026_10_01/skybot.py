"""SkyBoT cone (radius 15 arcsec, observatory I41 = ZTF Palomar) at the first drb>=0.8 detection epoch for screen1 objects with
span > 0.5 h, or pair-only with sep < 0.3 arcsec (2026-10-01). Positive control first: the fastest-moving pair object.
Output: skybot.csv (oid, n_known, nearest name, nearest sep arcsec, V) ; 'HOLE' if no valid reply."""
import requests, time, pandas as pd, numpy as np, io
from concurrent.futures import ThreadPoolExecutor
S = pd.read_csv("screen1.csv"); U = "https://ssp.imcce.fr/webservices/skybot/api/conesearch.php"
sel = S[(S.span_h > 0.5) | ((S.span_h < 0.1) & (S.sep_as < 0.3))]
def q(r):
    for k in range(4):
        try:
            x = requests.get(U, params={"-ep": r.first + 2400000.5, "-ra": r.ra, "-dec": r.dec, "-rd": 15 / 3600, "-mime": "text", "-output": "basic", "-loc": "I41", "-filter": "0", "-objFilter": "111", "-refsys": "EQJ2000", "-from": "hobby"}, timeout=90)
            t = x.text
            if x.ok and ("No solar system object" in t or "Num | Name" in t or "# Num" in t):
                L = [l for l in t.splitlines() if l and not l.startswith("#")]
                if not L or "No solar system" in t: return dict(oid=r.oid, n_known=0)
                best = None
                for l in L:
                    f = [s.strip() for s in l.split("|")]
                    # basic: Num | Name | RA | DE | Class | Mv | Err | d
                    try: d = float(f[7]); best = min(best or (1e9, ""), (d, f[1] + " V" + f[5]))
                    except Exception: pass
                return dict(oid=r.oid, n_known=len(L), nearest=best[1] if best else "", sep_as=best[0] if best else np.nan)
            if k == 3: return dict(oid=r.oid, n_known="HOLE", raw=t[:200])
        except Exception as ex:
            if k == 3: return dict(oid=r.oid, n_known="HOLE", raw=repr(ex)[:200])
        time.sleep(5 * (k + 1))
ctrl = S[S.span_h < 0.1].sort_values("rate_ash").iloc[-50]; print("control", ctrl.oid, ctrl.rate_ash, q(ctrl), flush=True)
with ThreadPoolExecutor(4) as ex: R = list(ex.map(q, [r for r in sel.itertuples()]))
R = pd.DataFrame(R); R.to_csv("skybot.csv", index=False); print(len(R), R.n_known.astype(str).value_counts().to_dict())

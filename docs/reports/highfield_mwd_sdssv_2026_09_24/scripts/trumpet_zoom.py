# Zoomed trumpet diagram (linear B axis) under the visit-coadd spectrum. usage: python trumpet_zoom.py sid Bmin Bmax [tag]
import sys, numpy as np, spec as S, plots as P
sid = int(sys.argv[1]); Bmin, Bmax = float(sys.argv[2]), float(sys.argv[3]); tag = sys.argv[4] if len(sys.argv) > 4 else ""
V = [v for v in S.load_visits(sid) if v["snr"] >= 6]
lam = V[0]["lam"]; num = np.zeros_like(lam); den = np.zeros_like(lam)
for v in V:
    f = np.interp(lam, v["lam"], v["flux"]); iv = np.interp(lam, v["lam"], v["ivar"]); num += f * iv; den += iv
fco = np.where(den > 0, num / np.where(den > 0, den, 1), 0)
import matplotlib; matplotlib.use("Agg")
mt = P.trumpet(lam, fco, den, f"plots/trumpetzoom_{sid}{tag}.png", title=f"sdss_id {sid}: visit coadd (XCSAO undone), B {Bmin}-{Bmax} MG", Bmax=Bmax, logB=False, visits=V[:4], Bmin=Bmin)
import matplotlib.pyplot as plt
print("ok")

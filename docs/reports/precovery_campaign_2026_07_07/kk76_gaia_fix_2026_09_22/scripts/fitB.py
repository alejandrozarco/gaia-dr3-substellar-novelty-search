import sys; sys.path.insert(0, "/tmp/kk76_fix")
from fitlib import *
P6 = pickle.load(open("/tmp/kk76_fix/pos2006.pkl", "rb"))
R06 = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq"]
R10 = ["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"]
os.makedirs("/tmp/kk76_fix/fits", exist_ok=True)
# Fit D: ground only
write_obs("/tmp/kk76_fix/fits/D.obs", [])
D = run_fo("/tmp/kk76_fix/fits/D.obs", "/tmp/kk76_fix/fits/D")
# Fit B: ground + my Gaia-anchored 2006 (sigma 0.03")
rows = [(r, P6[r]["ra"], P6[r]["dec"], 0.03, 0.03) for r in R06]
write_obs("/tmp/kk76_fix/fits/B.obs", rows)
B = run_fo("/tmp/kk76_fix/fits/B.obs", "/tmp/kk76_fix/fits/B")
for name, F in (("D ground only", D), ("B ground+2006", B)):
    e = F["elements"]
    print(f"Fit {name}: a={e['a']:.5f} e={e['e']:.6f} i={e['i']:.5f} node={e['asc_node']:.4f} peri={e['arg_per']:.3f} "
          f"rms={e['rms_residual']:.3f}\" n_obs={F['observations']['used']}/{F['observations']['count']}")
# residuals of the 2006 HST points in fit B
for r in F["observations"]["residuals"] if False else B["observations"]["residuals"]:
    if r["obscode"] == "250": print(f"   B resid 250 {r['iso date']}  dRA={r['dRA']:+.3f}\" dDec={r['dDec']:+.3f}\"")
# predictions at 2006 (from D) and 2010 (from D and B), HST-centric, via Horizons with the fit's elements
jd06 = [HV[r]["jd"] for r in R06]; jd10 = [HV[r]["jd"] for r in R10]
pD06 = horizons_pred(D, jd06); pD10 = horizons_pred(D, jd10); pB10 = horizons_pred(B, jd10)
print("\nFit D (ground only) predicted 2006 minus MY measured 2006 [pred - meas, arcsec]:")
for r, p in zip(R06, pD06):
    dx, dy = offset_arcsec(p[0], p[1], P6[r]["ra"], P6[r]["dec"]); print(f"   {r}: ({dx:+.3f}, {dy:+.3f})")
pickle.dump(dict(D=D, B=B, pD06=pD06, pD10=pD10, pB10=pB10), open("/tmp/kk76_fix/fits/fitB.pkl", "wb"))
print("\nBlind 2010 predictions (HST-centric) from Fit B:")
for r, p, q in zip(R10, pB10, pD10):
    dx, dy = offset_arcsec(q[0], q[1], p[0], p[1])
    print(f"   {r} {HV[r]['isot']}  B: {p[0]:.7f} {p[1]:+.7f}   (D minus B: {dx:+.2f}, {dy:+.2f}\")")

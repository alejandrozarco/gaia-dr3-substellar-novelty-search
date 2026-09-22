import sys, csv; sys.path.insert(0, "/tmp/kk76_fix")
from fitlib import *
P6 = pickle.load(open("pos2006.pkl", "rb")); P10 = pickle.load(open("pos2010.pkl", "rb"))
R06 = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq"]
R10 = ["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"]
REF = {r["frame"].lower(): (float(r["RA_deg"]), float(r["Dec_deg"])) for r in csv.DictReader(l for l in open("/tmp/kk76_referee/referee_astrometry_kk76.csv") if not l.startswith("#"))}
POS = {**P6, **P10}
print("MY Gaia-anchored positions vs the REFEREE's (mine minus referee, arcsec):")
worst = 0
for r in R06 + R10:
    o = offset_arcsec(POS[r]["ra"], POS[r]["dec"], *REF[r]); worst = max(worst, np.hypot(*o))
    print(f"   {r}: ({o[0]:+.3f}, {o[1]:+.3f})  |d|={np.hypot(*o):.3f}")
print(f"   worst |d| = {worst:.3f}\"   (referee's reproduction target: <= 0.03\")")
SIG = {r: (0.04 if r in R10[4:] else 0.03) for r in R06 + R10}
row = lambda r: (r, POS[r]["ra"], POS[r]["dec"], SIG[r], SIG[r])
write_obs("/tmp/kk76_fix/fits/E.obs", [row(r) for r in R10]); E = run_fo("/tmp/kk76_fix/fits/E.obs", "/tmp/kk76_fix/fits/E")
write_obs("/tmp/kk76_fix/fits/C.obs", [row(r) for r in R06 + R10]); C = run_fo("/tmp/kk76_fix/fits/C.obs", "/tmp/kk76_fix/fits/C")
for name, F in (("E ground+2010", E), ("C all", C)):
    e = F["elements"]
    print(f"\nFit {name}: a={e['a']:.4f} e={e['e']:.6f} q={e['q']:.4f} i={e['i']:.5f} node={e['asc_node']:.4f} peri={e['arg_per']:.3f} "
          f"rms={e['rms_residual']:.3f}\" used {F['observations']['used']}/{F['observations']['count']}")
hst = [x for x in C["observations"]["residuals"] if x["obscode"] == "250"]
print("Fit C residuals of the 12 HST points (arcsec):", " ".join(f"({x['dRA']:+.3f},{x['dDec']:+.3f})" for x in hst))
print("   max |HST residual| =", f"{max(np.hypot(x['dRA'], x['dDec']) for x in hst):.3f}\"")
gr = [x for x in C["observations"]["residuals"] if x["obscode"] != "250"]
print("   ground rms RA/Dec =", f"{np.sqrt(np.mean([x['dRA']**2 for x in gr])):.3f} / {np.sqrt(np.mean([x['dDec']**2 for x in gr])):.3f}\"")
# cross-prediction: fit E (ground + 2010) predicts 2006
pE06 = horizons_pred(E, [HV[r]["jd"] for r in R06])
print("\nFit E (ground+2010) predicted 2006 minus my measured 2006:")
for r, p in zip(R06, pE06):
    o = offset_arcsec(p[0], p[1], POS[r]["ra"], POS[r]["dec"]); print(f"   {r}: ({o[0]:+.3f}, {o[1]:+.3f})")
pickle.dump(dict(C=C, E=E, pE06=pE06, POS=POS, SIG=SIG), open("/tmp/kk76_fix/fits/fitCE.pkl", "wb"))

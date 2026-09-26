# ZTF DR light curves (IRSA API, 2.5" cone) of Gaia DR3 3290180587821828480: catflags == 0, magerr < 0.2; per-band median subtracted;
# Lomb-Scargle 0.05-300 c/d (step 0.1/baseline); 50-shuffle permutation null of the highest peak (magnitude-error pairs shuffled within band).
import io, requests, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
ra, de = 75.028716, 8.045709
r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {de} 0.000694", BANDNAME="g,r", FORMAT="csv"), timeout=300)
d = pd.read_csv(io.StringIO(r.text)); print("ZTF rows", len(d), d.groupby("filtercode").size().to_dict() if len(d) else "", flush=True)
d = d[(d.catflags == 0) & (d.magerr < 0.2)]; T, Y, E, B = [], [], [], []
for f, s in d.groupby("filtercode"):
    m = s.mag - s.mag.median(); T.append(s.hjd.values); Y.append(m.values); E.append(s.magerr.values); B.append(np.full(len(s), f))
    print(f"  {f}: n {len(s)}, median {s.mag.median():.2f}, rms {m.std():.3f}, median err {s.magerr.median():.3f}", flush=True)
t, y, e, b = np.concatenate(T), np.concatenate(Y), np.concatenate(E), np.concatenate(B)
fr = np.arange(0.05, 300, 0.1 / (t.max() - t.min())); P = LombScargle(t, y, e).power(fr, method="fast"); k = np.argmax(P)
top = []
for i in np.argsort(P)[::-1]:
    if all(abs(fr[i] - q) > 0.01 for q in top): top.append(fr[i])
    if len(top) == 5: break
rng = np.random.default_rng(3); null = []
for it in range(50):
    yy, ee = y.copy(), e.copy()
    for f in np.unique(b):
        m = b == f; idx = rng.permutation(m.sum()); yy[m] = y[m][idx]; ee[m] = e[m][idx]
    null.append(LombScargle(t, yy, ee).power(fr, method="fast").max())
print(f"combined n {len(t)}, span {t.max()-t.min():.0f} d, {len(fr)} freqs: top {fr[k]:.5f} c/d (P = {24/fr[k]:.4f} h) power {P[k]:.4f}; permutation p = {np.mean(np.array(null) >= P[k]):.2f} (null max {max(null):.4f}); next {[round(x, 4) for x in top[1:]]}", flush=True)

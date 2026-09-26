# Completeness test of the DAHe bump screen: inject linear-Zeeman Balmer emission triplets (pi at rest, sigma+- at +-dlam,
# dlam = 4.67e-13 lambda^2 B[G]) as Gaussians (FWHM 20 A at H-alpha, 14 A at H-beta) with relative peak amplitude A (of the local
# continuum, same A for H-alpha and H-beta) into real SDSS-V locus spectra, rerun the identical metric + control statistic, and count
# recoveries under the visual-inspection selection used on the real data: score>2 or sHa>3 or sHb>3 (score = sqrt(sHa*sHb)).
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import best_star; from emis2 import metric, metric_ctrl
from scipy.ndimage import median_filter
rng = np.random.default_rng(42)
d = pd.read_pickle("/tmp/fanout/exotic_atm/screen2_scored.pkl")
base = d[(d.score < 1.2) & (d.snr > 12)].sample(150, random_state=1)
def gauss(w, c, fwhm): s = fwhm / 2.355; return np.exp(-0.5 * ((w - c) / s) ** 2)
res = []
for _, r in base.iterrows():
    fn = f"/tmp/fanout/exotic_atm/spec/mwmStar-0.8.1-{r.sdss_id}.fits"
    try: hdu, w, f, iv, snr = best_star(fn)
    except Exception: continue
    ok = np.isfinite(f) & (iv > 0)
    cont = median_filter(np.where(ok, f, np.nanmedian(f)), size=301, mode="nearest")
    for B in (5e6, 10e6, 15e6):
        for A in (0.03, 0.05, 0.08, 0.12):
            add = np.zeros_like(f)
            for l0, fw in ((6564.61, 20.0), (4862.68, 14.0)):
                dl = 4.67e-13 * l0 ** 2 * B
                add += A * (gauss(w, l0, fw) + gauss(w, l0 - dl, fw) + gauss(w, l0 + dl, fw))
            fi = f + add * cont
            m = metric(w, fi, iv); c = max(metric_ctrl(w, fi, iv), 3.0)
            sHa, sHb = m["Ha_sig"] / c, m["Hb_sig"] / c; score = np.sqrt(max(sHa, 0) * max(sHb, 0))
            res.append(dict(sdss_id=r.sdss_id, snr=snr, B=B / 1e6, A=A, sHa=sHa, sHb=sHb, score=score, rec=bool(score > 2 or sHa > 3 or sHb > 3)))
R = pd.DataFrame(res); R.to_csv("/tmp/fanout/exotic_atm/injection_results_v2.csv", index=False)
print(R.groupby(["B", "A"]).rec.mean().unstack().round(2))
R["snrbin"] = pd.cut(R.snr, [0, 20, 40, 1000])
print(R[R.B == 10].groupby(["snrbin", "A"]).rec.mean().unstack().round(2))

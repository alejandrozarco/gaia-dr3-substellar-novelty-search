"""ZTF24abfojgu (2026-09-29): refine each alias frequency on low+high data combined (detrended residuals as in abfojgu_highstate.py),
then fit a sinusoid separately to the low and high states at that frequency and compare amplitude (mag and flux) and phase of
maximum light. Phase errors from 500 bootstrap resamples over nights. Output: abfojgu_phase.json."""
import numpy as np, json, os
from astropy.timeseries import LombScargle
H = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(H, "abfojgu_highstate.py")).read().split("fr = np.linspace")[0])
L, Hh = dataset("low"), dataset("high"); A = __import__("pandas").concat([L, Hh])
def sinefit(t, y, e, f):
    X = np.vstack([np.ones_like(t), np.cos(2 * np.pi * f * t), np.sin(2 * np.pi * f * t)]).T; w = 1 / e
    c = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)[0]; amp = np.hypot(c[1], c[2]); ph = (np.arctan2(-c[2], -c[1]) / (2 * np.pi)) % 1  # phase of maximum light (minimum magnitude)
    return amp, ph
rng = np.random.default_rng(4); out = {}; t0 = 2460000.0
for f0 in (17.8592, 18.8619, 19.8647):
    fr = np.linspace(f0 - 0.003, f0 + 0.003, 6001); p = LombScargle(A.t, A.res, np.clip(A.e, 0.01, None)).power(fr); f = float(fr[np.argmax(p)])
    res = {"f": f, "P_min": 1440 / f, "power_all": float(p.max())}
    for nm, D in (("low", L), ("high", Hh)):
        t, y, e = D.t.values - t0, D.res.values, np.clip(D.e.values, 0.01, None); amp, ph = sinefit(t, y, e, f)
        nights = np.floor(t); un = np.unique(nights); bs = []
        for s in range(500):
            pick = rng.choice(un, len(un)); idx = np.concatenate([np.where(nights == k)[0] for k in pick]); bs.append(sinefit(t[idx], y[idx], e[idx], f))
        bs = np.array(bs); dph = ((bs[:, 1] - ph + 0.5) % 1) - 0.5
        res[nm] = dict(semi_amp_mag=float(amp), e_amp=float(bs[:, 0].std()), phase_max=float(ph), e_phase=float(dph.std()))
    dphase = ((res["high"]["phase_max"] - res["low"]["phase_max"] + 0.5) % 1) - 0.5
    res["phase_difference"] = float(dphase); res["e_phase_difference"] = float(np.hypot(res["low"]["e_phase"], res["high"]["e_phase"]))
    out[f"{f0}"] = res
    print(f"alias {f0}: combined f {f:.6f} c/d (P {1440/f:.4f} min, power {p.max():.3f}); low amp {res['low']['semi_amp_mag']:.3f}+-{res['low']['e_amp']:.3f} mag, "
          f"high amp {res['high']['semi_amp_mag']:.3f}+-{res['high']['e_amp']:.3f} mag; phase(high)-phase(low) {dphase:+.3f} +- {res['e_phase_difference']:.3f}")
json.dump(out, open(os.path.join(H, f"abfojgu_phase{TAG}.json"), "w"), indent=1)

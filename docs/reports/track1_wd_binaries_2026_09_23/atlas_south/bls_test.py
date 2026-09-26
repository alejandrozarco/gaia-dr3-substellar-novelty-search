# positive control for the ATLAS BLS stage: 4731701084150029824 (known eclipse P = 0.14786971 d, 10.6 min) on a fine uniform
# frequency grid (1-20 c/d, df = 2.5e-5 c/d ~ duty cycle / baseline).
import numpy as np, time
exec(open("bls_all.py").read().split("periods = ")[0])
from astropy.timeseries import BoxLeastSquares
D = load("atlas_raw/4731701084150029824.txt"); freq = np.arange(1.0, 20.0, 2.5e-5); periods = 1 / freq; durations = np.array([5, 10, 20, 40]) / 1440.
for b, (t, f, e) in D.items():
    t0 = time.time(); pw = BoxLeastSquares(t, f, dy=e).power(periods, durations, objective="likelihood"); p = pw.power
    i = np.argmax(p); sde = (p[i] - np.median(p)) / (1.4826 * np.median(np.abs(p - np.median(p))))
    top = np.argsort(p)[::-1][:5]
    print(b, f"{time.time()-t0:.0f} s; best P {periods[i]:.7f} d SDE(robust) {sde:.1f} depth {pw.depth[i]:.1f} dur {pw.duration[i]*1440:.0f} min; top5 P:", [round(periods[k], 6) for k in top])

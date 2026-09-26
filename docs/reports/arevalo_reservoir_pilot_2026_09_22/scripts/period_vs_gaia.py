import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import BoxLeastSquares
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
L = {k.strip(): v for k, v in json.load(open(f"{A}/lc_cache.json")).items()}
cases = {"AREV_2484_000431_zg_c01_q1": (1.243326, 2.545907, "Gaia DR3 4353463277400908160"),
         "AREV_1861_000407_zg_c15_q1": (1.53733, 2.734521, "Gaia DR3 3233615666672318336"),
         "AREV_711_000456_zg_c11_q3": (2.912971, 2.784238, "Gaia DR3 3283967904744688768")}
fig, ax = plt.subplots(3, 3, figsize=(15, 9))
for i, (sid, (Pz, Pg, name)) in enumerate(cases.items()):
    rows = L[sid]; t = np.array([float(x["hjd"]) for x in rows]); m = np.array([float(x["mag"]) for x in rows])
    o = np.array([x["oid"] for x in rows]); b = np.array([x["filtercode"] for x in rows])
    for q in set(o): m[o == q] -= np.median(m[o == q])
    fl = 10 ** (-0.4 * m); bls = BoxLeastSquares(t, fl)
    out = []
    for j, (P, lab) in enumerate(((Pz, "ours"), (2 * Pz, "ours x2"), (Pg, "Gaia DR3 / VSX"))):
        grid = P * (1 + np.linspace(-3e-4, 3e-4, 601))
        res = bls.power(grid, np.array([0.01, 0.02, 0.04, 0.06]) * P, objective="snr")
        k = int(np.argmax(res.power)); t0 = float(res.transit_time[k]); Pb = float(res.period[k])
        ph = ((t - t0) / Pb + 0.25) % 1.0 - 0.25
        # in-eclipse coherence: fraction of points within the BLS box that are > 3 sigma below baseline
        dur = float(res.duration[k]); inb = np.abs(((t - t0) / Pb + 0.5) % 1.0 - 0.5) < dur / Pb / 2
        sc = 1.4826 * np.median(np.abs(m[~inb]))
        frac = float((m[inb] > 3 * sc).mean()) if inb.sum() else float("nan")
        out.append(f"{lab} P={Pb:.6f} BLS-snr={res.power[k]:.1f} in-box n={inb.sum()} deep-frac={frac:.2f}")
        for band, col in (("zg", "tab:green"), ("zr", "tab:red"), ("zi", "tab:purple")):
            s = b == band; ax[i, j].plot(ph[s], m[s], ".", ms=2, color=col, alpha=0.5)
        ax[i, j].invert_yaxis(); ax[i, j].set_ylim(0.6, -0.2); ax[i, j].set_xlim(-0.25, 0.75)
        ax[i, j].set_title(f"{name}\n{lab}: P = {Pb:.6f} d, BLS snr {res.power[k]:.0f}", fontsize=8)
    print(sid, name); [print("   ", x) for x in out]
fig.tight_layout(); fig.savefig(f"{A}/known_eb_period_check.png", dpi=100); print("saved")

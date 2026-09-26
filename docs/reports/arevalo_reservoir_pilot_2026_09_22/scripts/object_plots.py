import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
L = {k.strip(): v for k, v in json.load(open(f"{A}/lc_cache.json")).items()}
F = json.load(open(f"{A}/eclipse_fit.json"))
objs = [("AREV_747_000417_zg_c05_q1", "Gaia DR3 3828306424841718656"), ("AREV_1918_000493_zg_c16_q4", "Gaia DR3 1738942132557316864"),
        ("AREV_990_000495_zg_c14_q3", "Gaia DR3 2709405317531811840")]
for sid, name in objs:
    E = F[sid]; P = E["P"]; t0 = E["T0_HJD"]
    rows = L[sid]; t = np.array([float(x["hjd"]) for x in rows]); m = np.array([float(x["mag"]) for x in rows])
    o = np.array([x["oid"] for x in rows]); b = np.array([x["filtercode"] for x in rows])
    # per-OID offsets onto the band's main OID zero point (keep real magnitudes)
    for band in set(b):
        s = b == band; oids = [q for q in set(o[s])]; main = max(oids, key=lambda q: (o[s] == q).sum())
        ref = np.median(m[s & (o == main)])
        for q in oids: m[s & (o == q)] += ref - np.median(m[s & (o == q)])
    periods = [(P, "P")] + ([(2 * P, "2P")] if sid.startswith("AREV_747") else [])
    fig, axes = plt.subplots(1, len(periods), figsize=(7.5 * len(periods), 4.4), squeeze=False)
    for ax, (PP, lab) in zip(axes[0], periods):
        ph = ((t - t0) / PP) % 1.0
        for band, col, nm in (("zg", "tab:green", "ZTF g"), ("zr", "tab:red", "ZTF r"), ("zi", "tab:purple", "ZTF i")):
            s = b == band
            if not s.any(): continue
            for sh in (-1, 0, 1):
                p = ph[s] + sh; k = (p >= -0.25) & (p <= 1.25)
                ax.plot(p[k], m[s][k], ".", ms=2.5, color=col, alpha=0.55, label=f"{nm} ({s.sum()})" if sh == 0 else None)
        ax.invert_yaxis(); ax.set_xlim(-0.25, 1.25); ax.set_xlabel("phase"); ax.set_ylabel("magnitude")
        ax.set_title(f"{name}\nP = {PP:.6f} d, epoch HJD {t0:.4f}" + ("   (alternative: 2P)" if lab == "2P" else ""), fontsize=9)
        ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout(); fn = f"{A}/fold_{name.split()[-1]}.png"; fig.savefig(fn, dpi=120); print("saved", fn)

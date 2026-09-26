import os
# Figure for the J1226-2304 (Gaia DR3 3513017956589117056) deep dive, 2026-09-23. Inputs: j1226_deep_results.json,
# j1226_2p_results.json (this folder), PS1/SkyMapper epochs as in j1226_deep.py. Ephemeris P = 0.07968185682 d,
# W1 maximum T0 = BJD_TDB 2459999.9469779.
import json, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P, T0 = 0.07968185682, 2459999.9469779
R = json.load(open("../data/j1226_deep_results.json")); Q = json.load(open("../data/j1226_2p_results.json"))
S = pd.DataFrame(R["wise_seasons"])
fig, ax = plt.subplots(2, 2, figsize=(12, 8.5))
a = ax[0, 0]
a.errorbar(S.year, S.W1_mean_mJy, S.W1_emean, fmt="o", color="tab:red", ms=4, label="W1 mean flux")
a.errorbar(S.year, S.W1_semiamp_mJy, S.W1_esemiamp, fmt="s", color="tab:red", mfc="none", ms=5, label="W1 semi-amplitude")
a.errorbar(S.year + 0.05, S.W2_mean_mJy, S.W2_emean, fmt="o", color="tab:orange", ms=4, label="W2 mean flux")
a.errorbar(S.year + 0.05, S.W2_semiamp_mJy, S.W2_esemiamp, fmt="s", color="tab:orange", mfc="none", ms=5, label="W2 semi-amplitude")
a.set_ylabel("flux density (mJy)"); a.set_xlabel("year"); a.set_ylim(0, 0.62); a.legend(fontsize=7, ncol=2, loc="upper right")
a.set_title("WISE per visit: modulated flux fell ~3x while the mean stayed flat", fontsize=9)
a = ax[0, 1]
ph = S.W1_phase_of_max.values.copy(); ph[ph > 0.5] -= 1
a.errorbar(S.year, ph, np.maximum(S.W1_ephase, 0.005), fmt="o", color="k", ms=4)
a.axhline(0, color="gray", lw=0.8); a.set_ylim(-0.25, 0.25); a.set_xlabel("year"); a.set_ylabel("phase of W1 maximum (cycles)")
tm = R["timing"]; a.set_title(f"phase of maximum stable over ~62,000 cycles; Pdot = ({tm['Pdot']*1e10:.1f} +- {tm['Pdot_err']*1e10:.1f}) x 1e-10", fontsize=9)
a = ax[1, 0]
REF = os.path.expanduser("~/claude_projects/gaia_local_notes/2026-09-23/j1226_referee")
ps1 = pd.read_csv(f"{REF}/ps1_det_clean.csv"); ps1["ph"] = ((ps1.bjd - T0) / P) % 1
off = {"g": -1.2, "r": -0.6, "i": 0.0, "z": 0.6, "y": 1.2}; col = {"g": "tab:green", "r": "tab:red", "i": "tab:brown", "z": "tab:purple", "y": "k"}
for b in "grizy":
    s = ps1[ps1.band == b]
    for k in (0, 1):
        a.errorbar(s.ph + k, s.mag - np.median(s.mag) + off[b], s.err, fmt="o", ms=3, color=col[b], label=f"PS1 {b} ({off[b]:+.1f})" if k == 0 else None)
sm = R["skymapper"]
for b, o in (("i", 1.8), ("z", 2.4)):
    rows = np.array(sm[b]["rows"])
    if len(rows):
        for k in (0, 1):
            a.errorbar(rows[:, 0] + k, rows[:, 1] - np.median(rows[:, 1]) + o, rows[:, 2], fmt="^", ms=4, color="tab:blue", label=f"SkyMapper {b} ({o:+.1f})" if (k == 0) else None)
a.invert_yaxis(); a.set_xlabel("phase (0 = W1 maximum)"); a.set_ylabel("mag - median + offset"); a.legend(fontsize=6, ncol=2)
a.set_title("red optical 2010-2020 folded on the WISE ephemeris: no coherent modulation", fontsize=9)
a = ax[1, 1]
fA = np.array(Q["field_A"]); a.hist(fA, bins=30, color="gray", alpha=0.7, label=f"field stars (n={Q['field_n']})")
a.axvline(Q["target"]["dchi2_A"], color="tab:red", lw=2, label=f"J1226: {Q['target']['dchi2_A']:.1f} (simulation p = {Q['p_sim_A']:.2f})")
a.axvline(Q["sim_A_pcts"][2], color="tab:blue", ls="--", label="simulations 99th pct")
a.set_xlabel("delta chi2 of a coherent odd/even term at 2P (W1)"); a.set_ylabel("N"); a.legend(fontsize=7)
a.set_title("P vs 2P: no significant coherent odd/even difference", fontsize=9)
fig.suptitle("J1226-2304 = Gaia DR3 3513017956589117056: deep dive (WISE 2010-2024, PS1 2010-14, SkyMapper 2016-20)", fontsize=10)
plt.tight_layout(); plt.savefig("../figures/j1226_deep_dive.png", dpi=120); print("saved")

"""Per-visit Ca II triplet emission EW for every stored SDSS-V DR20 spectrum with 2 or more visits (store from gasdisc_screen.py),
normalised as in gas_disc_epochs.norm; flags stars whose EW changes between visits: max - min > 5 sigma (formal error with a
10% + 1 A floor) and max EW > 5 A. Output sdssv_visit_ew.csv (one row per star)."""
import sys, glob, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
import gas_disc_epochs as GE
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); m = (GRID > 8250) & (GRID < 8950); W = GRID[m]
rows = []
for fn in glob.glob("/tmp/hotdq/lane_gasdisc/store/*/*.npz"):
    d = np.load(fn)
    if d["vf_8250"].shape[0] < 2: continue
    ews = []
    for vf, viv, mj in zip(d["vf_8250"], d["viv_8250"], d["mjd"]):
        ok = (viv > 0) & np.isfinite(vf)
        if ok.sum() < 300: continue
        try:
            n, v = GE.norm(W, vf.astype(float), viv.astype(float)); okn = (v > 0) & np.isfinite(n)
            snr = float(np.median(np.sqrt(v[okn])))
            if snr < 5: continue
            ew, e, _, _ = GE.measure(n, v, np.zeros(len(GE.W))); ews.append((int(mj), ew, float(np.hypot(e, np.hypot(0.1 * abs(ew), 1.0))), snr))
        except Exception: continue
    if len(ews) < 2: continue
    a = np.array(ews); i, j = int(np.argmin(a[:, 1])), int(np.argmax(a[:, 1]))
    sig = (a[j, 1] - a[i, 1]) / np.hypot(a[i, 2], a[j, 2])
    rows.append(dict(sdss_id=os.path.basename(fn)[:-4], nvis=len(a), ew_min=round(a[i, 1], 2), mjd_min=int(a[i, 0]), ew_max=round(a[j, 1], 2), mjd_max=int(a[j, 0]),
                     sig=round(sig, 2), ews="/".join(f"{x:.1f}" for x in a[:, 1]), mjds="/".join(str(int(x)) for x in a[:, 0])))
pd.DataFrame(rows).to_csv("sdssv_visit_ew.csv", index=False); print(len(rows), "stars with 2+ usable visits")

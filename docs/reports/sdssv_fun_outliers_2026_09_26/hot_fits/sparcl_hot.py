import os
import sys, time, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
h = pd.read_csv("/tmp/hotdq/hot_lum.csv", dtype=str).set_index("sdss_id")
for s in "100568930 74510696 80998734 73346836 99327334 109787602 86483251".split():
    sp = None
    for k in range(4):
        try: sp = GE.sparcl_spectra(float(h.loc[s].ra), float(h.loc[s].dec)); break
        except Exception as e: err = e; time.sleep(20)
    print(s, "HOLE " + repr(err)[:80] if sp is None else [(x["dataset"], x["date"]) for x in sp], flush=True)

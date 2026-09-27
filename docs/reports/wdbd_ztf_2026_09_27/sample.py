"""Sample for wdbd_ztf.py: GF21 white dwarfs (Pwd > 0.75) with a Gaia DR3 vari_spurious_signals GLS frequency 3-40 c/d (FAP < 0.05), Dec > -28."""
import os, pandas as pd
X = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(f"{X}/../gaia_wd_periods_2026_09_24/data/wd_vspur_gf21.csv", dtype={"source_id": str})
s = d[(d.Pwd > 0.75) & (d.gls_freq_fap_g_fov < 0.05) & (d.gls_freq_g_fov > 3) & (d.gls_freq_g_fov < 40) & (d.dec > -28)]
s.to_csv(f"{X}/sample.csv", index=False); print(len(s))

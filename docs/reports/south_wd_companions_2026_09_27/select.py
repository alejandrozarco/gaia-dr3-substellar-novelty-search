"""sample.csv: GF21 white dwarfs (Pwd > 0.75) with Gaia DR3 vari_spurious_signals GLS frequency 3-40 c/d, FAP < 1e-3, Dec < -28 (south of ZTF),
from ../gaia_wd_periods_2026_09_24/data/wd_vspur_gf21.csv."""
import pandas as pd
d = pd.read_csv("../gaia_wd_periods_2026_09_24/data/wd_vspur_gf21.csv", dtype={"source_id": str})
d[(d.Pwd > 0.75) & (d.dec < -28) & (d.gls_freq_g_fov > 3) & (d.gls_freq_g_fov < 40) & (d.gls_freq_fap_g_fov < 1e-3)].to_csv("sample.csv", index=False)

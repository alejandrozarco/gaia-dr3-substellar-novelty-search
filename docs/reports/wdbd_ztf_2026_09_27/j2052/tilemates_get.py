"""Tile 20836 petal 8 (J2052's DESI exposure, night 20210523): retrieve DESI DR1 spectra of all tile-mates via SPARCL (by TARGETID) and
save the 6500-6640 A region, for a test of flux-calibration residuals at H-alpha."""
import numpy as np, pandas as pd
from sparcl.client import SparclClient
t = pd.read_csv("tilemates.csv"); ids = [int(x) for x in t.targetid]
c = SparclClient(); out = {}
for k in range(0, len(ids), 100):
    r = c.retrieve_by_specid(specid_list=ids[k:k + 100], include=["specid", "wavelength", "flux", "ivar", "redshift", "spectype", "data_release"], dataset_list=["DESI-DR1"])
    for x in r.records:
        w = np.array(x.wavelength); m = (w > 6480) & (w < 6660)
        out[str(x.specid)] = dict(w=w[m], f=np.array(x.flux)[m], iv=np.array(x.ivar)[m], z=x.redshift, t=x.spectype)
np.save("tilemates_ha.npy", out, allow_pickle=True); print(len(out))

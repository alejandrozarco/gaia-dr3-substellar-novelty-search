# Gaia DR3 epoch photometry of 6021870154194477312 from VizieR I/355/epphot (DataLink is 503); GLS and a sinusoid at 13.929771 c/d.
import warnings; warnings.filterwarnings("ignore"); import numpy as np
from astroquery.vizier import Vizier
from astropy.timeseries import LombScargle
V = Vizier(columns=["**"], row_limit=-1)
t = V.query_constraints(catalog="I/355/epphot", Source="6021870154194477312")[0]
print(t.colnames); print(len(t))
np.save("gaia_ep_cols.npy", np.array(t.colnames))
t.write("gaia_epphot_6021.csv", format="csv", overwrite=True)

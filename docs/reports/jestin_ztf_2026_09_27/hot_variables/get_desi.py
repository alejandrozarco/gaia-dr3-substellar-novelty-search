import numpy as np
from sparcl.client import SparclClient
c = SparclClient(connect_timeout=30, read_timeout=300)
r = c.retrieve_by_specid(specid_list=[39633426852088069, 39633279405524397], include=["specid", "wavelength", "flux", "ivar", "model"], dataset_list=["DESI-DR1"])
for x in r.records: np.savez(f"desi_{x.specid}.npz", w=np.array(x.wavelength), f=np.array(x.flux), iv=np.array(x.ivar)); print(x.specid, len(x.wavelength))

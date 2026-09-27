import numpy as np
from sparcl.client import SparclClient
c = SparclClient()
r = c.retrieve(uuid_list=["f17139b9-87ed-11ef-a64e-525400f334e1"], include=["wavelength", "flux", "ivar", "model", "specid", "data_release", "targetid"] if False else ["wavelength", "flux", "ivar", "model", "specid", "data_release"])
x = r.records[0]; np.savez("desi_dr1.npz", w=np.array(x.wavelength), f=np.array(x.flux), iv=np.array(x.ivar), m=np.array(x.model)); print(x.specid, len(x.wavelength))

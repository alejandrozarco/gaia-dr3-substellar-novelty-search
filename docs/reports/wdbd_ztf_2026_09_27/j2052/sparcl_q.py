from sparcl.client import SparclClient
c = SparclClient()
r = c.find(outfields=["sparcl_id", "specid", "data_release", "ra", "dec", "spectype", "redshift"], constraints={"ra": [313.20, 313.211], "dec": [-3.411, -3.400]}, limit=20)
for x in r.records: print(x)

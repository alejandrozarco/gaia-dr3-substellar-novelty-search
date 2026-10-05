import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
import numpy as np
v=Vizier(columns=['GaiaEDR3','WDJname','RA_ICRS','DE_ICRS','Plx','Pwd','pmRA','pmDE','Gmag','BPmag','RPmag','TeffH','loggH'],row_limit=-1,timeout=600)
m=v.query_constraints(catalog='J/MNRAS/508/3877/maincat',Gmag='<19.5',Pwd='>0.75',DE_ICRS='>-5')[0]
print(len(m))
c=m['BPmag']-m['RPmag']
s=m[(c>=0.45)&(c<=0.65)]
print(len(s))
s.write('gf21_ctrl_pool.ecsv',overwrite=True)

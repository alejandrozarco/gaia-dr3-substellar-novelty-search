import pyvo
from astroquery.vizier import Vizier
s=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
t=s.search("select table_name,description from TAP_SCHEMA.tables where table_name like '%506/2269%' or table_name like '%MNRAS/506/22%'").to_table(); print(t)
cs=Vizier.find_catalogs('El-Badry wide binaries Gaia')
for k,v in cs.items(): print(k,'|',v.description)
cs=Vizier.find_catalogs('J/MNRAS/506/2269')
for k,v in cs.items(): print('ID query ->',k,'|',v.description)

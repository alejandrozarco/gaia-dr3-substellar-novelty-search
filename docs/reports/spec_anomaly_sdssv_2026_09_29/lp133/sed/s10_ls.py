import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np, json
s=pyvo.dal.TAPService('https://datalab.noirlab.edu/tap')
g=json.load(open('gaia.json'))
for sch in ['ls_dr9','ls_dr10','ls_dr11']:
    try:
        tabs=s.search(f"SELECT table_name FROM tap_schema.tables WHERE schema_name='{sch}'").to_table()
        print(sch,[x for x in tabs['table_name'] if 'tractor' in x])
    except Exception as e: print(sch,'ERR',e)

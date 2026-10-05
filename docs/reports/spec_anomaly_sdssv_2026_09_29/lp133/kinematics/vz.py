import pyvo
s=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
t=s.search("select table_name,description from TAP_SCHEMA.tables where table_name like 'J/MNRAS/506/2269%'").to_table(); print(t)
for tn in t['table_name']:
    cols=s.search(f"select column_name from TAP_SCHEMA.columns where table_name='{tn}'").to_table()
    print(tn,list(cols['column_name']))

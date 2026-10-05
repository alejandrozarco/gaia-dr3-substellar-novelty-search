import pyvo
s=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
tn='"J/MNRAS/506/2269/catalog"'
cols=s.search("select column_name,description from TAP_SCHEMA.columns where table_name='\"J/MNRAS/506/2269/catalog\"'").to_table()
print([ (c,d[:30]) for c,d in zip(cols['column_name'],cols['description'])])
print('rows:',s.search(f'select count(*) as n from {tn}').to_table())

import pyvo
s=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
tn='"J/MNRAS/506/2269/catalog"'
sid=1609392862209121664
r=s.search(f'select "Source1","Source2","theta","sepAU","R","BinType" from {tn} where "Source1"={sid} or "Source2"={sid}').to_table(); print('target rows:',len(r)); print(r)
# positive control: a pair within 3 deg of target, then re-query by id
r2=s.search(f'select top 20 "Source1","Source2","RA_ICRS","DE_ICRS","Plx1","sepAU","R" from {tn} where 1=CONTAINS(POINT(\'ICRS\',"RA_ICRS","DE_ICRS"),CIRCLE(\'ICRS\',211.793,55.158,3))').to_table()
print('pairs with primary within 3 deg:',len(r2)); print(r2[:10])
if len(r2):
    c=int(r2['Source2'][0]); r3=s.search(f'select "Source1","Source2" from {tn} where "Source1"={c} or "Source2"={c}').to_table(); print('control id query rows:',len(r3))
# pairs with primary within 1.2 deg & plx 15-23
r4=s.search(f'select "Source1","Source2","Plx1","Plx2","sepAU" from {tn} where 1=CONTAINS(POINT(\'ICRS\',"RA_ICRS","DE_ICRS"),CIRCLE(\'ICRS\',211.793,55.158,1.2)) and "Plx1">14').to_table(); print('pairs within 1.2 deg with plx1>14:',len(r4)); print(r4)

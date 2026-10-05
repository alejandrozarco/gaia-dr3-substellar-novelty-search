import re, glob, pandas as pd, numpy as np
from astropy.coordinates import SkyCoord; import astropy.units as u
rows=[]
for f in sorted(glob.glob('ews/*.html')):
    h=open(f).read()
    if 'ogle' in f:
        for m in re.finditer(r'>(\d{4}-BLG-\d{3,4})</A>\s*<TD>[^<]*<TD[^>]*>[^<]*<TD>\s*(\d\d:\d\d:\d\d\.\d+)\s*<TD>\s*(-?\d\d:\d\d:\d\d\.\d+)',h):
            rows.append(('OGLE-'+m.group(1),m.group(2),m.group(3)))
    else:
        for m in re.finditer(r"(KMT-\d{4}-BLG-\d{4})</a>.*?</tr>",h,re.S):
            c=re.findall(r'([-+]?\d\d:\d\d:\d\d\.\d+)',m.group(0))
            if len(c)>=2: rows.append((m.group(1),c[0],c[1]))
d=pd.DataFrame(rows,columns=['event','ra','dec']).drop_duplicates('event')
print(d.event.str[:9].value_counts().sort_index().to_dict())
d.to_csv('ews_all.csv',index=False)
t=pd.read_csv('targets.csv')
C=SkyCoord(d.ra.values,d.dec.values,unit=(u.hourangle,u.deg)); T=SkyCoord(t.RAdeg.values*u.deg,t.DEdeg.values*u.deg)
i,s,_=T.match_to_catalog_sky(C)
t['ml_list_match']=np.where(s.arcsec<2,d.event.values[i],''); t['ml_list_sep']=s.arcsec
t['kmt']='';print(t[t.ml_list_sep<10][['Name','ml_list_match','ml_list_sep','Comment']].to_string())
# control: OGLE-2024-BLG-0001 own coords
t[['Name','ml_list_match','ml_list_sep']].to_csv('ml_lists.csv',index=False)
inb=(np.abs(T.galactic.b.deg)<12)&((T.galactic.l.deg<20)|(T.galactic.l.deg>340)); print('targets in bulge window',inb.sum())
# all matches within 2" (both OGLE and KMT)
out=[]
for j,r in t.iterrows():
    sep=SkyCoord(r.RAdeg*u.deg,r.DEdeg*u.deg).separation(C).arcsec
    out.append(';'.join(f'{e}({s:.2f})' for e,s in zip(d.event.values[sep<2],sep[sep<2])))
t['ml_all']=out; t[['Name','ml_all']].to_csv('ml_lists.csv',index=False)
print(t[t.ml_all!=''][['Name','ml_all']].to_string()); print('n matched',(t.ml_all!='').sum())
# control: an OGLE event matches its KMT counterpart
c=SkyCoord('17:52:03.98','-30:50:03.59',unit=(u.hourangle,u.deg)); print('ctrl OB240249 KMT match:', d.event.values[c.separation(C).arcsec<2])

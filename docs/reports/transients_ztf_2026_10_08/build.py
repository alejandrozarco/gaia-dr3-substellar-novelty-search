import pandas as pd, requests, json, time
from astropy.time import Time
OBJ=[('ZTF26acacbkk','05:11:09.70','-03:13:37.59','PSN'),('ZTF26acanyxu','07:20:12.81','+30:06:45.99','PSN'),('ZTF26acanjuf','04:52:34.96','-05:59:20.99','PSN'),
('ZTF26acahvhr','23:59:59.38','-20:42:30.97','PSN'),('ZTF26acahyno','23:37:46.18','+14:32:04.51','PSN'),('ZTF26acakche','02:41:02.87','-07:29:59.04','PSN'),
('ZTF26acafchj','20:42:04.89','-03:07:51.14','PSN'),('ZTF26acanfbi','04:33:19.48','-12:13:07.89','PSN'),('ZTF26abzxtvv','01:04:20.19','+17:28:51.19','PSN'),
('ZTF26acanfri','04:59:26.49','-05:23:40.92','PSN'),('ZTF26acaddnd','07:02:18.83','+18:04:51.73','PSN')]
F={1:'g',2:'r',3:'i'}; out=[]
iso=lambda m: Time(m,format='mjd').utc.iso[:19]
for oid,ra,de,t in OBJ:
    for a in range(3):
        try:
            d=pd.DataFrame(requests.get(f'https://api.alerce.online/ztf/v1/objects/{oid}/detections',timeout=60).json()); n=pd.DataFrame(requests.get(f'https://api.alerce.online/ztf/v1/objects/{oid}/non_detections',timeout=60).json()); break
        except Exception as e: time.sleep(10)
    d=d[(d.isdiffpos==1)].sort_values('mjd'); d1=d.iloc[0]; d2=d[d.mjd>d1.mjd+0.5].iloc[0]
    nd=n[(n.mjd<d1.mjd)&(n.diffmaglim>d1.magpsf)].sort_values('mjd')
    ndr=nd.iloc[-1] if len(nd) else None
    out.append(dict(oid=oid,ra=ra,dec=de,type=t,ndet=len(d),
      d1=dict(t=iso(d1.mjd),mag=round(d1.magpsf,2),err=round(d1.sigmapsf,2),f=F[d1.fid],mjd=d1.mjd),
      d2=dict(t=iso(d2.mjd),mag=round(d2.magpsf,2),err=round(d2.sigmapsf,2),f=F[d2.fid]),
      nd=None if ndr is None else dict(t=iso(ndr.mjd),lim=round(ndr.diffmaglim,2),f=F[ndr.fid])))
    print(json.dumps(out[-1]))
json.dump(out,open('filing.json','w'),indent=1)

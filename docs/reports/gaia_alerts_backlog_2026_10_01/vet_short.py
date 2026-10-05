import io, time, json, requests, pandas as pd, numpy as np, datetime
s=pd.read_csv('short.csv')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (research script)'
def vsx(a,d,r=30):
    for k in range(4):
        try:
            t=S.get('https://www.aavso.org/vsx/index.php',params=dict(view='api.list',ra=a,dec=d,radius=r/3600,format='json'),timeout=90)
            if t.ok and t.text.startswith('{'):
                it=t.json().get('VSXObjects',{}); it=it.get('VSXObject',[]) if isinstance(it,dict) else []
                return it if isinstance(it,list) else [it]
        except Exception: pass
        time.sleep(5)
    return None
def ztf(a,d):
    for k in range(3):
        try:
            q=requests.get('https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves',params=dict(POS=f'CIRCLE {a} {d} 0.00042',BANDNAME='g,r',FORMAT='csv'),timeout=300)
            if q.ok: return q.text
        except Exception: time.sleep(10)
    return None
print('VSX control:', vsx(325.67854,43.58617)[0]['Name'])
c=ztf(325.67854,43.58617); print('ZTF control SS Cyg rows:', c.count('\n') if c else None)
rows=[]
for r in s.itertuples():
    ts=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%MZ')
    v=vsx(r.RAdeg,r.DEdeg)
    res=dict(Name=r.Name,vsx_ts=ts,vsx='FAIL' if v is None else json.dumps([(x.get('Name'),x.get('VariabilityType'),round(3600*np.hypot((float(x['RA2000'])-r.RAdeg)*np.cos(np.radians(r.DEdeg)),float(x['Declination2000'])-r.DEdeg),1)) for x in v]))
    if r.DEdeg>-31:
        t=ztf(r.RAdeg,r.DEdeg)
        if t is None: res['ztf']='HOLE'
        else:
            d=pd.read_csv(io.StringIO(t)) if t.count('\n')>1 else pd.DataFrame()
            if len(d)==0: res['ztf']='EMPTY(header-only)'
            else:
                d=d[(d.catflags==0)&(d.magerr<0.3)]; d.to_csv(f'ztf/{r.Name}.csv',index=False)
                for b in ('zg','zr'):
                    x=d[d.filtercode==b]
                    if len(x): res.update({f'{b}_n':len(x),f'{b}_min':round(x.mag.min(),2),f'{b}_med':round(x.mag.median(),2),f'{b}_max':round(x.mag.max(),2)})
                res['ztf']='ok'
    else: res['ztf']='south'
    print(res,flush=True); rows.append(res); time.sleep(1)
pd.DataFrame(rows).to_csv('vet_short.csv',index=False)

import pandas as pd, numpy as np, os, glob
s=pd.read_csv('g2_novsxviz.csv').set_index('Name')
rows=[]
for f in sorted(glob.glob('glc/*.csv')):
    n=os.path.basename(f)[:-4]
    d=pd.read_csv(f,skiprows=1); d.columns=['date','jd','mag']
    d['mag']=pd.to_numeric(d.mag,errors='coerce'); d=d.dropna()
    if len(d)<5: rows.append(dict(Name=n,npt=len(d))); continue
    m=d.mag.values; t=d.jd.values
    base=np.median(m); lo=np.percentile(m,5); hi=np.percentile(m,95)
    # outburst episodes: points >1 mag brighter than median, grouped by gaps>30d
    ob=t[m<base-1.0]; eps=0 if len(ob)==0 else 1+np.sum(np.diff(np.sort(ob))>30)
    fd=t[m>base+1.0]; feps=0 if len(fd)==0 else 1+np.sum(np.diff(np.sort(fd))>30)
    frac_ob=np.mean(m<base-1.0)
    # long-term trend: median first third vs last third
    k=len(m)//3; trend=np.median(m[-k:])-np.median(m[:k])
    rows.append(dict(Name=n,npt=len(d),base=base,minmag=m.min(),maxmag=m.max(),rng=m.max()-m.min(),r90=hi-lo,
        ob_eps=eps,fade_eps=feps,frac_ob=frac_ob,trend=trend,span=t.max()-t.min()))
F=pd.DataFrame(rows).set_index('Name').join(s[['AlertMag','HistoricMag','amp','Comment','Source','RAdeg','DEdeg','Plx','RPlx','pmsig','Gmag','BPmag','RPmag','RUWE']])
F['bprp']=F.BPmag-F.RPmag
F['MG']=F.Gmag+5*np.log10(np.clip(F.Plx,1e-3,None)/100)
F.to_csv('glc_feat.csv')
print(len(F))

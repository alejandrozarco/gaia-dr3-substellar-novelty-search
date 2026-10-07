import pandas as pd, glob, sys
s=sys.argv[1]
d=pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f'lists/tic{s}/c*.csv'))])
d=d.drop_duplicates('ID')
dw=(d.lumclass=='DWARF')&(d.Teff<5300)&(d.d<100)
d['prio']=(~dw).astype(int)
d=d.sort_values(['prio','Tmag'])
d.rename(columns={'ID':'tic'}).to_csv(f'lists/queue_s{s}_meta.csv',index=False)
d[['ID']].rename(columns={'ID':'tic'}).to_csv(f'lists/queue_s{s}.csv',index=False)
print(len(d), dw.sum(), (d.Tmag<=9).sum())

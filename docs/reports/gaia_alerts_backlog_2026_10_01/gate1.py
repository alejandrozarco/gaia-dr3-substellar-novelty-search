import pandas as pd, numpy as np
A=pd.read_csv('alerts.csv',skipinitialspace=True); A.columns=[c.strip().lstrip('#') for c in A.columns]
u=A[A.Class=='unknown'].copy()
X=pd.read_csv('xm_gaia.csv').sort_values('angDist').drop_duplicates('Name')
print('alerts with DR3 within 1.5":',len(X))
X['pmsig']=np.hypot(X.pmRA/X.e_pmRA, X.pmDE/X.e_pmDE)
X['stellar']=(X.RPlx>3)|(X.pmsig>5)
X['Source']=X.Source.astype('int64')
m=u.merge(X[['Name','angDist','Source','RAdeg','DEdeg','Plx','e_Plx','RPlx','pmRA','pmDE','pmsig','RUWE','Gmag','BPmag','RPmag','stellar','VarFlag' if 'VarFlag' in X else 'Gmag']],on='Name',how='left')
print('stellar (plx/err>3 or pm>5sig):',m.stellar.fillna(False).sum())
s=m[m.stellar.fillna(False)].copy()
s['amp']=s.HistoricMag-s.AlertMag
print('of which HistoricMag present:',s.HistoricMag.notna().sum())
print('amp>0 brighten:',(s.amp>0).sum(),' fade:',(s.amp<0).sum())
s.to_csv('g1_stellar.csv',index=False)
print(s.amp.describe())

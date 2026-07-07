from astroquery.jplhorizons import Horizons
import warnings; warnings.filterwarnings('ignore')
# 2009 HW77 arc: 2002-2012. Scan archive epochs near opposition for each year 2005-2023.
# Use geocentric (500) for uncertainty ellipse. quantities 1(astrom RA/Dec),9(V mag),36(RA/Dec 3sig),37(SMAA/SMIA/PA 3sig)
epochs = {
 '2005-06-05':2453526.5,   # SDSS coverage present
 '2010-04-15':2455301.5,
 '2013-01-01':2456293.5,   # gate best epoch
 '2013-03-15':2456366.5,
 '2014-03-15':2456731.5,
 '2015-03-15':2457096.5,
 '2017-07-01':2457935.5,
 '2018-03-15':2458192.5,
 '2021-01-01':2459215.5,
}
obj = Horizons(id='2009 HW77', location='500', epochs=list(epochs.values()))
eph = obj.ephemerides(quantities='1,9,36,37')
print("COLNAMES:", eph.colnames)
print()
import csv
w=csv.writer(open('ephem_uncertainty.csv','w'))
w.writerow(['label','jd','RA_deg','Dec_deg','V','SMAA_3sig_as','SMIA_3sig_as','Theta_PA','RA_3sig_as','DEC_3sig_as'])
labels=list(epochs.keys())
for i,row in enumerate(eph):
    smaa=float(row['SMAA_3sigma']); smia=float(row['SMIA_3sigma'])
    v=row['V'] if 'V' in eph.colnames else 'NA'
    print(f"{labels[i]:12s} RA={float(row['RA']):.5f} Dec={float(row['DEC']):.5f} V={v} SMAA_3s={smaa:.2f}\" SMIA_3s={smia:.2f}\" PA={float(row['Theta_3sigma']):.1f}")
    w.writerow([labels[i],round(float(row['datetime_jd']),1),round(float(row['RA']),5),round(float(row['DEC']),5),v,round(smaa,3),round(smia,3),round(float(row['Theta_3sigma']),2),round(float(row['RA_3sigma']),3),round(float(row['DEC_3sigma']),3)])

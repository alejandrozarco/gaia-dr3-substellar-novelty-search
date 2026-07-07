from astroquery.jplhorizons import Horizons
import warnings; warnings.filterwarnings('ignore')
# Precise per-night predictions at the candidate same-night DECam epochs.
# JD at frame midtime. Geocentric 500 for uncertainty; also topocentric CTIO (807/W84) would shift <~1' but box already tiny.
# Using midtimes from SSOIS.
nights = {
 '2013-03-02T07:40':2456353.8194,
 '2014-06-27T01:49':2456835.5757,
 '2014-06-27T06:07':2456835.7549,
 '2014-06-29T02:10':2456837.5903,
 '2015-04-27T05:32':2457139.7306,
 '2015-05-20T10:20':2457162.9306,
 '2015-05-21T10:07':2457163.9215,
}
# use CTIO obs code 807 (CTIO) - actually DECam = W84. Use W84.
obj = Horizons(id='2009 HW77', location='W84', epochs=list(nights.values()))
eph = obj.ephemerides(quantities='1,9,36,37')
import csv
w=csv.writer(open('ephem_nights.csv','w'))
w.writerow(['night','jd','RA_deg','Dec_deg','V','SMAA_3s_as','SMIA_3s_as','PA','rate_as_hr'])
labels=list(nights.keys())
# also get rates via quantity 3
obj2=Horizons(id='2009 HW77',location='W84',epochs=list(nights.values()))
eph2=obj2.ephemerides(quantities='3')
for i,row in enumerate(eph):
    smaa=float(row['SMAA_3sigma']); smia=float(row['SMIA_3sigma'])
    ra_rate=float(eph2['RA_rate'][i]) if 'RA_rate' in eph2.colnames else 0
    dec_rate=float(eph2['DEC_rate'][i]) if 'DEC_rate' in eph2.colnames else 0
    import math
    rate=math.hypot(ra_rate,dec_rate)  # arcsec/hr
    print(f"{labels[i]:20s} RA={float(row['RA']):.5f} Dec={float(row['DEC']):.5f} V={row['V']:.2f} SMAA={smaa:.2f}\" SMIA={smia:.2f}\" PA={float(row['Theta_3sigma']):.0f} rate={rate:.1f}\"/hr")
    w.writerow([labels[i],round(float(row['datetime_jd']),4),round(float(row['RA']),5),round(float(row['DEC']),5),round(float(row['V']),2),round(smaa,3),round(smia,3),round(float(row['Theta_3sigma']),1),round(rate,2)])

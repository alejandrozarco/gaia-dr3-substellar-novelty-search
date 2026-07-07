from astroquery.jplhorizons import Horizons
import numpy as np, json

# Key DECam night epochs (midnight UT of each rich night) + a couple others.
# Use JD at the mean MJD of each cluster to match footprint times closely.
# We'll query at representative mid-night times.
epochs_mjd = {
 '2013-03-11': 56362.266,
 '2014-04-23': 56770.0,
 '2015-05-20': 57162.5,
 '2015-05-21': 57163.5,
 '2015-05-22': 57164.5,
 '2015-05-23': 57165.5,
 '2015-05-24': 57166.5,
 '2015-07-15': 57218.3,
 '2019-05-16': 58619.3,
 '2019-06-07': 58641.0,
}
jds = {k: v+2400000.5 for k,v in epochs_mjd.items()}

# Horizons small-body designation. 2001 KN76.
obj = Horizons(id='2001 KN76', location='807',  # CTIO 807 = Cerro Tololo (DECam)
               epochs=list(jds.values()))
eph = obj.ephemerides(quantities='1,9,36,37', extra_precision=True)
cols = ['datetime_str','RA','DEC','V','RA_3sigma','DEC_3sigma','SMAA_3sigma','SMIA_3sigma','Theta_3sigma','RA_rate','DEC_rate']
avail = [c for c in cols if c in eph.colnames]
print('Available cols:', eph.colnames)
print()
for row in eph:
    print({c: (float(row[c]) if isinstance(row[c],(int,float,np.floating)) else str(row[c])) for c in avail})

eph[avail].write('horizons_ephem.csv', format='csv', overwrite=True)
print("\nWrote horizons_ephem.csv")

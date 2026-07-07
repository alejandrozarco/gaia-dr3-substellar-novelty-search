from astroquery.jplhorizons import Horizons
# Use the same record and covariance. Query batch of epochs near opposition.
# 2001 QU297 = record 50003034
epochs = {
 '2003-08-20':2452871.5,
 '2010-08-20':2455428.5,
 '2014-08-20':2456889.5,
 '2022-08-20':2460176.5,  # note: report used 2460176.5 for 2023 row; use it
}
obj = Horizons(id='2001 QU297', location='500', epochs=list(epochs.values()))
eph = obj.ephemerides(quantities='1,9,36,37')
cols = ['datetime_jd','RA','DEC','V','RA_3sigma','DEC_3sigma','SMAA_3sigma','SMIA_3sigma','Theta_3sigma']
have = [c for c in cols if c in eph.colnames]
print("COLNAMES:", eph.colnames)
for row in eph:
    print(round(row['datetime_jd'],1), 'RA',round(float(row['RA']),4),'Dec',round(float(row['DEC']),4),
          'V', row['V'] if 'V' in eph.colnames else 'NA',
          'SMAA_as', row['SMAA_3sigma'] if 'SMAA_3sigma' in eph.colnames else 'NA',
          'SMIA_as', row['SMIA_3sigma'] if 'SMIA_3sigma' in eph.colnames else 'NA')

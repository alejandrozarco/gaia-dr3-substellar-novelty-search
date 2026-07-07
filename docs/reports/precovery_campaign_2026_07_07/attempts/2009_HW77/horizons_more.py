from astroquery.jplhorizons import Horizons
import warnings; warnings.filterwarnings('ignore')
nights = {
 '2016-08-11':2457611.7,
 '2019-05-16':2458619.8,
 '2019-06-07':2458641.8,
}
obj = Horizons(id='2009 HW77', location='W84', epochs=list(nights.values()))
eph = obj.ephemerides(quantities='1,9,36,37')
labels=list(nights.keys())
for i,row in enumerate(eph):
    print(f"{labels[i]} RA={float(row['RA']):.5f} Dec={float(row['DEC']):.5f} V={row['V']:.2f} SMAA={float(row['SMAA_3sigma']):.2f} SMIA={float(row['SMIA_3sigma']):.2f}")

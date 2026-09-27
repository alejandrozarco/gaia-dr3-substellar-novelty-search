"""CRTS periodic-variable catalogues x Gentile Fusillo+2021 white dwarfs (CDS XMatch, 2"): Drake+2014 CSS (J/ApJS/213/9/table3) and
Drake+2017 SSS (J/MNRAS/469/3688/table4)."""
import astropy.units as u
from astroquery.xmatch import XMatch
for cat, out in [("vizier:J/ApJS/213/9/table3", "css_x_gf21.csv"), ("vizier:J/MNRAS/469/3688/table4", "sss_x_gf21.csv")]:
    XMatch.query(cat1=cat, cat2="vizier:J/MNRAS/508/3877/maincat", max_distance=2 * u.arcsec).write(out, format="csv", overwrite=True)

"""Chen+2020 ZTF periodic catalogue (J/ApJS/249/18/table2, 781,602 variables) x Gentile Fusillo+2021 Gaia EDR3 white dwarfs (J/MNRAS/508/3877/maincat), 1.5"."""
import astropy.units as u, warnings; warnings.filterwarnings("ignore")
from astroquery.xmatch import XMatch
r = XMatch.query(cat1="vizier:J/ApJS/249/18/table2", cat2="vizier:J/MNRAS/508/3877/maincat", max_distance=1.5 * u.arcsec)
print(len(r)); r.write("chen_x_gf21.csv", format="csv", overwrite=True)

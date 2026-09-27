"""Gaia DR3 vari_short_timescale (VizieR I/358/vst) x Gentile Fusillo+2021 (J/MNRAS/508/3877/maincat), 1": vst_x_gf21.csv.
vst_new.csv: Pwd > 0.5, characteristic period 20-200 min, not examined in the earlier period lanes (see RESEARCH_LOG)."""
import astropy.units as u
from astroquery.xmatch import XMatch
XMatch.query(cat1="vizier:I/358/vst", cat2="vizier:J/MNRAS/508/3877/maincat", max_distance=1 * u.arcsec).write("vst_x_gf21.csv", format="csv", overwrite=True)

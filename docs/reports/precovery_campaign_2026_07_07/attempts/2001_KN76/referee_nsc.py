import numpy as np
from astroquery.utils.tap.core import TapPlus

tap = TapPlus(url="https://datalab.noirlab.edu/tap")

def cone_objects(ra, dec, rad_as, label):
    r = rad_as/3600.0
    q = f"""SELECT id, ra, dec, ndet, nphot, mjd_first, mjd_last, deltamjd,
            gmag, rmag, imag, class_star, flags
            FROM nsc_dr2.object
            WHERE q3c_radial_query(ra,dec,{ra},{dec},{r})"""
    j = tap.launch_job(q)
    t = j.get_results()
    print(f"\n=== {label}: NSC objects within {rad_as}\" of ({ra},{dec}) ===")
    print(f"  {len(t)} objects")
    for row in t:
        dra=(row['ra']-ra)*3600*np.cos(np.radians(dec)); ddec=(row['dec']-dec)*3600
        sep=np.hypot(dra,ddec)
        print(f"  id={row['id']} sep={sep:.2f}\" ndet={row['ndet']} deltamjd={row['deltamjd']:.1f} "
              f"rmag={row['rmag']:.2f} class_star={row['class_star']:.2f} mjd_first={row['mjd_first']:.2f} mjd_last={row['mjd_last']:.2f}")
    return t

# Candidate 1 position (2013)
cone_objects(228.8012259, -20.8267668, 5.0, "CAND1 2013 tight 5\"")
cone_objects(228.8012259, -20.8267668, 15.0, "CAND1 2013 wide 15\"")
# Candidate 2 position (2015)
cone_objects(229.7975068, -21.0925405, 5.0, "CAND2 2015 tight 5\"")
cone_objects(229.7975068, -21.0925405, 15.0, "CAND2 2015 wide 15\"")

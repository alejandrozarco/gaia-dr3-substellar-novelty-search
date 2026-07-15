import requests, json, io, sys
RA, DEC = 306.74802, -11.81856
out = {}

def tap(url, q, name, timeout=90):
    try:
        r = requests.get(url, params={"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}, timeout=timeout)
        out[name] = {"status": r.status_code, "csv": r.text[:20000]}
        print(f"--- {name} [{r.status_code}] ---")
        print(r.text[:3000])
    except Exception as e:
        out[name] = {"error": str(e)}
        print(f"--- {name} FAILED: {e}")

# Gaia DR3 within 10"
tap("https://gea.esac.esa.int/tap-server/tap/sync",
    f"""SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec, phot_g_mean_mag,
    phot_bp_mean_mag, phot_rp_mean_mag, phot_variable_flag, ruwe,
    DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{RA},{DEC}))*3600 AS sep_as
    FROM gaiadr3.gaia_source
    WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.002778))=1
    ORDER BY sep_as""", "gaia_dr3")

# NOIRLab Data Lab: NSC DR2 objects within 10"
tap("https://datalab.noirlab.edu/tap/sync",
    f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, ndet, nphot, deltamjd, mjd, variable10,
    q3c_dist(ra,dec,{RA},{DEC})*3600 AS sep_as
    FROM nsc_dr2.object WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.002778)
    ORDER BY sep_as""", "nsc_dr2")

# Legacy Survey DR10 tractor within 10"
tap("https://datalab.noirlab.edu/tap/sync",
    f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2,
    q3c_dist(ra,dec,{RA},{DEC})*3600 AS sep_as
    FROM ls_dr10.tractor WHERE q3c_radial_query(ra,dec,{RA},{DEC},0.002778)
    ORDER BY sep_as""", "ls_dr10")

json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones1.json","w"), indent=1)

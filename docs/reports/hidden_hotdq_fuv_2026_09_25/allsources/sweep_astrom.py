"""All-catalogue astrometric sweep for the two hot DQ white dwarfs.
Gaia DR2/EDR3/DR3 PM consistency; VizieR astrometric catalogues (position at catalogue
epoch vs Gaia DR3 linear prediction; catalogue PM vs Gaia PM); Gaia DR3 wide-companion
search (1 pc projected, parallax and PM consistent) + El-Badry+2021 wide-binary table."""
import numpy as np, pyvo, warnings, json
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
warnings.filterwarnings("ignore")
tap = pyvo.dal.TAPService("https://gea.esac.esa.int/tap-server/tap")
OBJ = {"5208047381438507520":"J0735-7944","6886051830805052288":"J2051-1617"}
ids = ",".join(OBJ)
g3 = tap.search(f"select source_id,ra,dec,parallax,parallax_error,pmra,pmra_error,pmdec,pmdec_error,ruwe,astrometric_excess_noise,astrometric_excess_noise_sig,phot_g_mean_mag from gaiadr3.gaia_source where source_id in ({ids})").to_table()
g2 = tap.search(f"select n.dr3_source_id as source_id, g.parallax,g.parallax_error,g.pmra,g.pmra_error,g.pmdec,g.pmdec_error from gaiadr3.dr2_neighbourhood n join gaiadr2.gaia_source g on g.source_id=n.dr2_source_id where n.dr3_source_id in ({ids})").to_table()
out = {}
V = Vizier(columns=["**","_RAJ2000","_DEJ2000"], row_limit=50)
CATS = {  # catalogue: (label, epoch column or fixed epoch, pm cols)
 "I/322A/out":"UCAC4","I/340/ucac5":"UCAC5","I/317/sample":"PPMXL","I/339/hsoy":"HSOY","I/297/out":"NOMAD1",
 "I/284/out":"USNO-B1","I/320/spm4":"SPM4","I/353/gsc242":"GSC2.4.2","I/305/out":"GSC2.3","I/329/urat1":"URAT1",
 "I/344/upcs":"UPC-south","I/331/apop":"APOP","I/319/xpm":"XPM","I/343/gps1":"GPS1","I/351/gps1_p":"GPS1+",
 "II/246/out":"2MASS","II/328/allwise":"AllWISE","II/365/catwise":"CatWISE2020","II/363/unwise":"unWISE",
 "II/349/ps1":"PS1-DR1","II/358/smss":"SkyMapper-DR1.1","B/denis/denis":"DENIS","I/252/out":"USNO-A2",
 "II/367/vhs_dr5":"VHS-DR5","I/259/tyc2":"Tycho-2","I/311/hip2":"HIP2","J/ApJS/254/42/hgca_edr3":"HGCA",
 "I/315/out":"UCAC3","I/289/out":"UCAC2","I/327/cmc15":"CMC15","I/312/sample":"PPMX","I/280B/ascc":"ASCC-2.5",
 "J/MNRAS/508/3877/maincat":"GF21-WD","I/360/syntphot":"GaiaSynPhot",
}
for sid, name in OBJ.items():
    r3 = g3[g3["source_id"]==int(sid)][0]; r2 = g2[g2["source_id"]==int(sid)]
    res = {"gaia_dr3": {k: float(r3[k]) for k in ("parallax","parallax_error","pmra","pmra_error","pmdec","pmdec_error","ruwe","astrometric_excess_noise","astrometric_excess_noise_sig","phot_g_mean_mag")}}
    if len(r2):
        r2 = r2[0]; d_ra = r3["pmra"]-r2["pmra"]; d_de = r3["pmdec"]-r2["pmdec"]
        s_ra = np.hypot(r3["pmra_error"], r2["pmra_error"]); s_de = np.hypot(r3["pmdec_error"], r2["pmdec_error"])
        res["dr2_vs_dr3_pm"] = dict(dpmra=float(d_ra), dpmdec=float(d_de), sig_ra=float(d_ra/s_ra), sig_de=float(d_de/s_de),
                                     dr2_plx=float(r2["parallax"]), dr2_plx_err=float(r2["parallax_error"]))
    c = SkyCoord(float(r3["ra"])*u.deg, float(r3["dec"])*u.deg)  # epoch 2016.0
    rows = []
    for cat, lab in CATS.items():
        try:
            tl = V.query_region(c, radius=12*u.arcsec, catalog=cat)
        except Exception as e:
            rows.append(dict(cat=lab, vizier=cat, status=f"ERROR {type(e).__name__}")); continue
        if len(tl)==0:
            rows.append(dict(cat=lab, vizier=cat, status="no source within 12 arcsec")); continue
        t = tl[0]
        # nearest row to Gaia position (catalogue coordinates as served at J2000 equinox; epoch varies)
        cc = SkyCoord(t["_RAJ2000"], t["_DEJ2000"], unit="deg")
        sep = c.separation(cc).arcsec; i = int(np.argmin(sep))
        row = dict(cat=lab, vizier=cat, status="match", n_within_12=int(len(t)), sep_arcsec=round(float(sep[i]),2))
        cols = t.colnames
        for pmc in (("pmRA","pmDE"),("pmra","pmdec"),("pmRAcosDE","pmDE"),("pmR","pmD")):
            if pmc[0] in cols and pmc[1] in cols and not np.ma.is_masked(t[pmc[0]][i]):
                row["pmra"]=float(t[pmc[0]][i]); row["pmdec"]=float(t[pmc[1]][i]); break
        for ec in (("e_pmRA","e_pmDE"),("e_pmra","e_pmdec"),("e_pmR","e_pmD")):
            if ec[0] in cols and not np.ma.is_masked(t[ec[0]][i]):
                row["e_pmra"]=float(t[ec[0]][i]); row["e_pmdec"]=float(t[ec[1]][i]); break
        for ep in ("Epoch","EpRA","epoch","Ep","EpochRA","JD","MJD","Date"):
            if ep in cols and not np.ma.is_masked(t[ep][i]):
                row["epoch_col"]=ep; row["epoch_val"]=float(t[ep][i]); break
        for mc in ("Gmag","Vmag","f.mag","Jmag","W1mag","gmag","R1mag","Bmag","Fmag","Rmag","FUVmag","imag","rmag"):
            if mc in cols and not np.ma.is_masked(t[mc][i]):
                row["mag_"+mc]=float(t[mc][i]); break
        if "pmra" in row:
            row["dpm_total"] = float(np.hypot(row["pmra"]-r3["pmra"], row["pmdec"]-r3["pmdec"]))
        rows.append(row)
    res["catalogues"] = rows
    # wide companions: Gaia DR3 cone, 1 pc projected
    plx = float(r3["parallax"]); rad_deg = np.degrees(1.0/(1000.0/plx))
    q = f"""select source_id, ra, dec, parallax, parallax_error, pmra, pmdec, phot_g_mean_mag, bp_rp, ruwe,
      distance(point({float(r3['ra'])},{float(r3['dec'])}), point(ra,dec))*3600 as sep_arcsec
      from gaiadr3.gaia_source where 1=contains(point(ra,dec), circle({float(r3['ra'])},{float(r3['dec'])},{rad_deg}))
      and abs(parallax-{plx}) < 3*sqrt(parallax_error*parallax_error+{float(r3['parallax_error'])**2}) + 0.1*{plx}
      and parallax_over_error > 5 and source_id != {sid}"""
    cand = tap.search(q).to_table()
    comp = []
    for rr in cand:
        dpm = np.hypot(rr["pmra"]-r3["pmra"], rr["pmdec"]-r3["pmdec"])
        dv = 4.74047*dpm/plx
        sep_au = float(rr["sep_arcsec"])*1000/plx
        v_orb_max = 29.78*np.sqrt(2*2.5/sep_au)  # km/s, 2.5 Msun total, bound max
        comp.append(dict(source_id=str(rr["source_id"]), sep_arcsec=round(float(rr["sep_arcsec"]),1), sep_au=round(sep_au),
                         G=round(float(rr["phot_g_mean_mag"]),2), bp_rp=None if np.ma.is_masked(rr["bp_rp"]) else round(float(rr["bp_rp"]),2),
                         plx=round(float(rr["parallax"]),3), dv_tan_kms=round(float(dv),2), bound_ok=bool(dv < max(3.0, 2*v_orb_max))))
    res["wide_companion_search"] = dict(radius_deg=rad_deg, n_parallax_matched=len(comp),
                                        comoving=[x for x in comp if x["bound_ok"]], all_sorted=sorted(comp, key=lambda x: x["dv_tan_kms"])[:10])
    try:
        eb = V.query_constraints(catalog="J/MNRAS/506/2269/table", source_id1=sid)
        eb2 = V.query_constraints(catalog="J/MNRAS/506/2269/table", source_id2=sid)
        res["elbadry2021"] = f"{sum(len(x) for x in eb)+sum(len(x) for x in eb2)} rows (as primary {sum(len(x) for x in eb)}, secondary {sum(len(x) for x in eb2)})"
    except Exception as e:
        res["elbadry2021"] = f"ERROR {e}"
    out[sid] = res
    print(name, json.dumps(res, indent=0)[:200])
json.dump(out, open("astrom_sweep.json","w"), indent=1)
print("WRITTEN")

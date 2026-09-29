"""Catalogue fields for the seven VSX drafts (2026-09-29): Gaia DR3 astrometry, J2000 position (Gaia moved to epoch 2000.0),
constellation, VSX live API within 60 arcsec (positive control: AM Her), SIMBAD identifiers, eRASS1/eRASS:3 names (15 arcsec),
2MASS, AllWISE and Pan-STARRS DR1 (3 arcsec). Output: dn_fields.json."""
import json, requests, numpy as np
from astropy.coordinates import SkyCoord, get_constellation
import astropy.units as u
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astroquery.gaia import Gaia
IDS = ["6291945806661266560", "3082396190372984832", "5614298790271682688", "5701425912708783488", "3109248424693126400", "4308831935765230720", "5182404743053707904"]
g = Gaia.launch_job(f"SELECT source_id, ra, dec, pmra, pmdec, parallax, parallax_error, phot_g_mean_mag, bp_rp, ruwe, astrometric_params_solved FROM gaiadr3.gaia_source WHERE source_id IN ({','.join(IDS)})").get_results()
def vsx(ra, dec, r):
    j = requests.get(f"https://vsx.aavso.org/index.php?view=api.list&ra={ra}&dec={dec}&radius={r}&format=json", timeout=60).json()
    return (j.get("VSXObjects") or {}).get("VSXObject", []) or []
out = {"_control_AM_Her": len(vsx(274.0555, 49.8678, 0.01))}
for row in g:
    sid = str(row["source_id"]); ra, de = float(row["ra"]), float(row["dec"])
    pmra = float(row["pmra"]) if np.isfinite(row["pmra"]) else 0.0; pmde = float(row["pmdec"]) if np.isfinite(row["pmdec"]) else 0.0
    ra0 = ra - pmra * 16 / 3.6e6 / np.cos(np.radians(de)); de0 = de - pmde * 16 / 3.6e6; c = SkyCoord(ra0 * u.deg, de0 * u.deg)
    r = dict(pos_j2000=c.to_string("hmsdms", sep=" ", precision=2), ra2000=ra0, dec2000=de0, constellation=get_constellation(c), G=float(row["phot_g_mean_mag"]),
             bp_rp=float(row["bp_rp"]) if np.isfinite(row["bp_rp"]) else None, plx=float(row["parallax"]) if np.isfinite(row["parallax"]) else None,
             e_plx=float(row["parallax_error"]) if np.isfinite(row["parallax_error"]) else None, pmra=pmra, pmdec=pmde, ruwe=float(row["ruwe"]) if np.isfinite(row["ruwe"]) else None)
    r["vsx_60arcsec"] = [dict(Name=v.get("Name"), Type=v.get("VariabilityType"), OID=v.get("OID")) for v in vsx(ra0, de0, 1 / 60)]
    try:
        ids = Simbad.query_objectids(f"Gaia DR3 {sid}"); r["simbad_ids"] = [str(x) for x in ids[ids.colnames[0]]] if ids is not None else []
    except Exception as e: r["simbad_ids"] = f"HOLE {type(e).__name__}"
    for cat, key, rad, col in (("J/A+A/682/A34/erass1-m", "eRASS1", 15, "IAUName"), ("J/A+A/712/A171", "eRASS3", 15, "IAUName"),
                               ("II/246/out", "2MASS", 3, "2MASS"), ("II/328/allwise", "AllWISE", 3, "AllWISE"), ("II/349/ps1", "PS1", 3, "objID")):
        try:
            t = Vizier(columns=["**", "+_r"], row_limit=3).query_region(SkyCoord(ra * u.deg, de * u.deg), radius=rad * u.arcsec, catalog=cat)
            if len(t):
                tt = t[0]; cn = col if col in tt.colnames else [x for x in tt.colnames if "name" in x.lower() or x in ("1eRASS", "3eRASS", "Name")][:1]
                cn = cn if isinstance(cn, str) else (cn[0] if cn else tt.colnames[0])
                r[key] = dict(name=str(tt[cn][0]), sep=float(tt["_r"][0]), extra={k: str(tt[k][0]) for k in tt.colnames if k in ("gmag", "rmag", "imag", "Jmag", "Ksmag", "Kmag", "W1mag", "W2mag")})
            else: r[key] = "none"
        except Exception as e: r[key] = f"HOLE {type(e).__name__}: {e}"[:120]
    out[sid] = r
json.dump(out, open("dn_fields.json", "w"), indent=1, default=str)
for k, v in out.items():
    if k.startswith("_"): print(k, v); continue
    print(k, v["pos_j2000"], v["constellation"], "VSX60:", v["vsx_60arcsec"], "| SIMBAD", v["simbad_ids"], "|", {kk: (v[kk]["name"] + f" {v[kk]['sep']:.1f}\"" if isinstance(v[kk], dict) else v[kk]) for kk in ("eRASS1", "eRASS3", "2MASS", "AllWISE", "PS1")})

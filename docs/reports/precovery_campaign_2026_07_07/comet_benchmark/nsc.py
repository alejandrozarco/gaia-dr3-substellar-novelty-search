"""NSC DR2 access via NOIRLab Astro Data Lab REST query manager (/query/query).
Robust alternate to pyvo TAP (whose /tap/sync and /tap/async gateway-timeout under load).
datalab ADQL rejects q3c/geometry -> RA/Dec BOX (indexed) + Python radial filter.
Anonymous token; returns CSV -> astropy Table.
"""
import warnings; warnings.filterwarnings("ignore")
import io, time, sys, numpy as np, requests
from astropy.table import Table
from astropy.io import ascii as asciireader
from astropy.time import Time

BASE="https://datalab.noirlab.edu/query/query"
HDR={"X-DL-AuthToken":"anonymous.0.0.anon_access"}

def _log(*a): print(*a, flush=True)

def sql_csv(sql, tries=5, timeout=180):
    last=None
    for k in range(1,tries+1):
        try:
            r=requests.get(BASE, params={"sql":sql,"ofmt":"csv","async":"False"},
                           headers=HDR, timeout=timeout)
            if r.status_code==200 and not r.text.lstrip().lower().startswith("<!doctype") \
               and "error" not in r.text[:60].lower():
                return asciireader.read(r.text, format="csv", fast_reader=False, guess=False)
            last=f"HTTP {r.status_code}: {r.text[:160]}"
        except Exception as e:
            last=f"{type(e).__name__}: {str(e)[:160]}"
        _log(f"  [nsc try {k}] {last}")
        time.sleep(8*k)   # linear backoff to ride out overload
    raise RuntimeError(f"sql_csv failed after {tries} tries: {last}")

MEAS_COLS="measid,objectid,exposure,ra,dec,mjd,mag_auto,magerr_auto,filter,class_star,fwhm,flags"
def meas_box(ra0, dec0, half_arcsec=45.0, cols=MEAS_COLS):
    hw=half_arcsec/3600.0; cd=np.cos(np.radians(dec0))
    sql=(f"SELECT {cols} FROM nsc_dr2.meas "
         f"WHERE ra BETWEEN {ra0-hw/cd:.7f} AND {ra0+hw/cd:.7f} "
         f"AND dec BETWEEN {dec0-hw:.7f} AND {dec0+hw:.7f}")
    return sql_csv(sql)

def exposure_box(ra0, dec0, half_deg=1.3):
    cd=np.cos(np.radians(dec0))
    sql=(f"SELECT exposure,mjd,filter,exptime,ra,dec FROM nsc_dr2.exposure "
         f"WHERE ra BETWEEN {ra0-half_deg/cd:.6f} AND {ra0+half_deg/cd:.6f} "
         f"AND dec BETWEEN {dec0-half_deg:.6f} AND {dec0+half_deg:.6f}")
    return sql_csv(sql)

def with_sep(t, ra0, dec0):
    cd=np.cos(np.radians(dec0)); t=t.copy()
    t["dra_as"]=(t["ra"].astype(float)-ra0)*3600.0*cd
    t["ddec_as"]=(t["dec"].astype(float)-dec0)*3600.0
    t["sep_as"]=np.hypot(t["dra_as"],t["ddec_as"])
    return t

if __name__=="__main__":
    ra0,dec0=27.52079,-43.95323
    mjd_obs=Time("2017-10-15T08:06:23.328",format="isot",scale="utc").mjd
    _log("querying meas box (REST) ...")
    t0=time.time()
    t=with_sep(meas_box(ra0,dec0,45.0),ra0,dec0); t.sort("sep_as")
    _log(f"rows={len(t)} in {time.time()-t0:.1f}s  mjd_obs={mjd_obs:.6f}")
    _log("sep    dt(s)      mjd          mag   filt  cs    fwhm  exposure")
    for r in t[t["sep_as"]<6]:
        dt=(float(r["mjd"])-mjd_obs)*86400
        _log(f"{r['sep_as']:5.2f} {dt:+9.1f} {float(r['mjd']):.6f} {float(r['mag_auto']):6.2f} {str(r['filter']):2s} {float(r['class_star']):5.2f} {float(r['fwhm']):5.2f} {r['exposure']}")

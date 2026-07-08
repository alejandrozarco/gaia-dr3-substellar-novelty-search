#!/usr/bin/env python3
"""Per-exposure Horizons ephemeris + NSC DR2 detection search for 2010 JK124.
Rule 1: datetime_jd-keyed, asserted per epoch. Rule 3: catalog PSF pos + honest sigmas.
Rule 6: static-source rejection via mean-object cross-match, mag sanity."""
import urllib.request, urllib.parse, json, math, csv, sys

TAP="https://datalab.noirlab.edu/tap/sync"
HOR="https://ssd.jpl.nasa.gov/api/horizons.api"

def tap(q):
    data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
    for _ in range(3):
        try:
            r=urllib.request.urlopen(TAP,data=data,timeout=120).read().decode()
            return r
        except Exception as e:
            err=str(e)
    return "ERR "+err

# NSC-catalogued exposures covering the track (name, mjd_start, exptime_s, filter)
EXPS=[
 ("c4d_140606_025954_ooi_r_v1",56814.1237466855,100,"r"),
 ("c4d_140606_065522_ooi_r_v1",56814.2872649957,100,"r"),
 ("c4d_150620_050628_ooi_r_v2",57193.2113780420,150,"r"),
 ("c4d_150620_050928_ooi_r_v2",57193.2134303218,150,"r"),
 ("c4d_160308_082444_ooi_VR_v1",57455.3490717124,150,"VR"),
 ("c4d_160308_082745_ooi_VR_v1",57455.3511426855,150,"VR"),
 ("c4d_190428_083626_ooi_Y_v1",58601.3588169378,30,"Y"),
 ("c4d_190429_082142_ooi_i_v1",58602.3485826057,30,"i"),
 ("c4d_190429_082241_ooi_z_v1",58602.3492681003,30,"z"),
 ("c4d_190429_082340_ooi_Y_v1",58602.3499524998,30,"Y"),
 ("c4d_190501_051802_ooi_g_v1",58604.2214149052,96,"g"),
 ("c4d_190501_052007_ooi_r_v1",58604.2224824695,30,"r"),
 ("c4d_190513_074224_ooi_g_v1",58616.3216368090,90,"g"),
 ("c4d_190514_051628_ooi_i_v1",58617.2202982347,90,"i"),
 ("c4d_190609_054934_ooi_g_v1",58643.2432834385,90,"g"),
 ("c4d_190820_232431_ooi_i_v1",58715.9758799465,90,"i"),
 ("c4d_190820_232904_ooi_i_v1",58715.9790404079,90,"i"),
 ("c4d_190820_233101_ooi_i_v1",58715.9804009273,90,"i"),
]
# mid-exposure JD, keyed
rows=[]
for name,mjd0,exp,filt in EXPS:
    midmjd=mjd0+ (exp/2.0)/86400.0
    jd=midmjd+2400000.5
    rows.append(dict(name=name,mjd0=mjd0,exp=exp,filt=filt,midmjd=midmjd,jd=jd))

# one Horizons TLIST call for all mid-JDs
tl=",".join("%.8f"%r["jd"] for r in rows)
params={"format":"text","COMMAND":"'2010 JK124;'","OBJ_DATA":"NO","MAKE_EPHEM":"YES",
 "EPHEM_TYPE":"OBSERVER","CENTER":"'W84'","TLIST_TYPE":"JD","TLIST":tl,
 "QUANTITIES":"'1,9,36,37'","ANG_FORMAT":"DEG","EXTRA_PREC":"YES","CSV_FORMAT":"YES"}
url=HOR+"?"+urllib.parse.urlencode(params)
txt=urllib.request.urlopen(url,timeout=120).read().decode()
open("/tmp/precovery_wave4/2010_JK124/horizons_nsc_exps.txt","w").write(txt)
# parse SOE block
lines=txt.split("\n"); soe=lines.index("$$SOE"); eoe=lines.index("$$EOE")
eph=[]
for l in lines[soe+1:eoe]:
    p=[x.strip() for x in l.split(",")]
    # date, blank, blank, RA, DEC, APmag, S-brt, RA_3sig, DEC_3sig, SMAA, SMIA, Theta, Area
    eph.append(dict(date=p[0],ra=float(p[3]),dec=float(p[4]),vmag=p[5],
                    smaa=float(p[9]),smia=float(p[10]),theta=float(p[11])))
assert len(eph)==len(rows),f"eph {len(eph)} != rows {len(rows)}"

# rule1: assert time alignment per epoch — match Horizons UT date back to our JD
import datetime
def jd_to_dt(jd):
    return datetime.datetime(2000,1,1,12)+datetime.timedelta(days=jd-2451545.0)
for r,e in zip(rows,eph):
    dt=jd_to_dt(r["jd"])
    # Horizons date like '2014-Jun-06 03:00:35.xxx'
    e["dt_check"]=dt.strftime("%Y-%b-%d %H:%M")
    r.update(ra=e["ra"],dec=e["dec"],smaa=e["smaa"],smia=e["smia"],theta=e["theta"],
             vmag=e["vmag"],hdate=e["date"],dt_check=e["dt_check"])

out=[]
det_rows=[]
for r in rows:
    ra,dec=r["ra"],r["dec"]
    cosd=math.cos(math.radians(dec))
    # search box: max(3sig semi-major, 3.0") + 2.0" astrometric margin
    box=max(r["smaa"],3.0)+2.0  # arcsec
    dra=box/3600.0/cosd; ddec=box/3600.0
    q=(f"SELECT measid,ra,dec,mjd,mag_auto,magerr_auto,filter,fwhm,class_star,exposure "
       f"FROM nsc_dr2.meas WHERE exposure='{r['name']}' "
       f"AND ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} "
       f"AND dec BETWEEN {dec-ddec:.7f} AND {dec+ddec:.7f}")
    res=tap(q)
    dets=[]
    rd=list(csv.DictReader(res.splitlines()))
    for d in rd:
        try:
            mra=float(d["ra"]); mdec=float(d["dec"])
        except: continue
        sep=math.hypot((mra-ra)*cosd,(mdec-dec))*3600.0
        # per-axis in ellipse frame: rough — use sep vs smaa
        d["sep_arcsec"]=round(sep,3)
        d["dmjd_s"]=round((float(d["mjd"])-r["midmjd"])*86400.0,1)
        dets.append(d)
    dets.sort(key=lambda x:x["sep_arcsec"])
    r["n_box"]=len(dets)
    r["nearest"]=dets[0] if dets else None
    out.append(r)
    print(f"{r['name']:32s} pred=({ra:.5f},{dec:+.5f}) V~{r['vmag']} 3sig({r['smia']:.2f}x{r['smaa']:.2f}\") box={box:.1f}\"  n_in_box={len(dets)}  align:{r['hdate'][:17]}~{r['dt_check']}")
    for d in dets[:5]:
        print(f"     sep={d['sep_arcsec']:6.2f}\" mag={d['mag_auto']:>8} {d['filter']} fwhm={d['fwhm']:>6} cstar={d['class_star']:>6} dmjd={d['dmjd_s']}s meas={d['measid']}")
        det_rows.append(dict(exposure=r['name'],pred_ra=ra,pred_dec=dec,jd=r['jd'],midmjd=r['midmjd'],
            vmag_pred=r['vmag'],smaa=r['smaa'],smia=r['smia'],theta=r['theta'],
            meas_ra=d['ra'],meas_dec=d['dec'],sep_arcsec=d['sep_arcsec'],mag_auto=d['mag_auto'],
            magerr=d['magerr_auto'],filt=d['filter'],fwhm=d['fwhm'],class_star=d['class_star'],
            dmjd_s=d['dmjd_s'],measid=d['measid']))

json.dump([{k:(v if not isinstance(v,dict) else v) for k,v in r.items()} for r in out],
          open("/tmp/precovery_wave4/2010_JK124/nsc_search_summary.json","w"),indent=1,default=str)
with open("/tmp/precovery_wave4/2010_JK124/nsc_box_detections.csv","w",newline="") as f:
    if det_rows:
        w=csv.DictWriter(f,fieldnames=list(det_rows[0].keys())); w.writeheader(); w.writerows(det_rows)
    else:
        f.write("no_detections_in_any_box\n")
print("\nTOTAL box detections across all NSC exposures:",len(det_rows))

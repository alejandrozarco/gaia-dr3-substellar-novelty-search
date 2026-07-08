"""Blind same-frame re-measurement of C/2014 UN271 in NSC DR2 for selected W84 epochs.
Frame match uses AUTHORITATIVE nsc_dr2.exposure.mjd(start)+exptime/2 = midpoint (the c4d name
timestamp is unreliable, off by up to ~140 s). MPC obstime = exposure midpoint; assert |dt|<60s
(rule 1). Selection is BLIND: nearest detection to the HORIZONS prediction on the matching frame,
never using the published RA/Dec. Records our RA/Dec/mag/morphology + same-exposure stellar FWHM.
"""
import warnings; warnings.filterwarnings("ignore")
import csv, json, numpy as np
from astropy.time import Time
import nsc

SELECT_IDX=[0,2,8,14,16,18,23,25,28,29]

def main():
    hz={r["idx"]:r for r in csv.DictReader(open("raw/horizons_w84.csv"))}
    out=[]
    for idx in SELECT_IDX:
        r=hz[str(idx)]
        ra0,dec0=float(r["ra_hor"]),float(r["dec_hor"])
        tobs=Time(r["obstime"].replace("Z",""),format="isot",scale="utc"); mjd_obs=tobs.mjd
        band=r["band"].lower()
        print(f"\n=== idx {idx}  {r['obstime']}  band={band}  mag_pub={r['mag_pub']} ===",flush=True)
        meas=nsc.with_sep(nsc.meas_box(ra0,dec0,45.0),ra0,dec0)
        meas.write(f"raw/meas_idx{idx:02d}.csv",format="csv",overwrite=True)
        exp=nsc.exposure_box(ra0,dec0,1.3)
        expmap={str(e["exposure"]):(float(e["mjd"]),float(e["exptime"])) for e in exp}
        # candidate comet detections: near prediction + matching band
        near=(meas["sep_as"]<3.0)
        bandm=np.array([str(f).lower()==band for f in meas["filter"]])
        cand=meas[near&bandm]
        # frame midpoint per candidate (from exposure table), dt vs obstime
        rec=dict(idx=idx,obstime=r["obstime"],jd_utc=r["jd_utc"],mjd_obs=round(mjd_obs,6),band=band,
                 ra_hor=ra0,dec_hor=dec0,ra_pub=float(r["ra_pub"]),dec_pub=float(r["dec_pub"]),
                 mag_pub=r["mag_pub"],ra3sig=float(r["ra3sig"]),dec3sig=float(r["dec3sig"]),
                 smaa3=float(r["smaa3"]),smia3=float(r["smia3"]),theta3=float(r["theta3"]))
        best=None; bestdt=1e9
        for c in cand:
            en=str(c["exposure"])
            if en not in expmap: continue
            emjd,etime=expmap[en]; mid=emjd+etime/2/86400.0
            dt=(mid-mjd_obs)*86400.0
            if abs(dt)<abs(bestdt): bestdt=dt; best=(c,en,emjd,etime,mid)
        if best is None or abs(bestdt)>60:
            rec["status"]="NO_SAMEFRAME_CATALOG"; rec["n_near_band"]=int(len(cand))
            rec["best_dt_s"]=(None if best is None else round(bestdt,1))
            print(f"  NO same-frame catalog detection (best_dt={rec['best_dt_s']}s, n_near_band={len(cand)})")
        else:
            c,en,emjd,etime,mid=best
            same=meas[np.array([str(e)==en for e in meas["exposure"]])]
            stars=same[(same["class_star"].astype(float)>0.85)&(same["fwhm"].astype(float)>0)]
            comp=float(np.median(stars["fwhm"].astype(float))) if len(stars)>=3 else float("nan")
            cd=np.cos(np.radians(dec0))
            ra_o,dec_o=float(c["ra"]),float(c["dec"])
            rec.update(status="CATALOG", exposure=en, exptime=etime,
                exp_mid_mjd=round(mid,6), dt_frame_mid_s=round(bestdt,2),
                ra_ours=ra_o, dec_ours=dec_o, mag_ours=round(float(c["mag_auto"]),3),
                magerr_ours=round(float(c["magerr_auto"]),3), filt_ours=str(c["filter"]),
                fwhm_ours=round(float(c["fwhm"]),3), class_star_ours=round(float(c["class_star"]),3),
                flags_ours=int(c["flags"]) if "flags" in c.colnames else None,
                sep_pred_as=round(float(c["sep_as"]),3), measid=str(c["measid"]),
                comp_star_fwhm=round(comp,3), n_comp_stars=int(len(stars)), n_same_exposure=int(len(same)),
                dRA_ours_pub=round((ra_o-float(r["ra_pub"]))*3600*cd,4),
                dDec_ours_pub=round((dec_o-float(r["dec_pub"]))*3600,4),
                dRA_ours_hor=round((ra_o-ra0)*3600*cd,4),
                dDec_ours_hor=round((dec_o-dec0)*3600,4))
            print(f"  MATCH exp={en} exptime={etime} dt_mid={bestdt:+.2f}s sep_pred={c['sep_as']:.3f}\"")
            print(f"  ours {ra_o:.6f}/{dec_o:.6f} mag={float(c['mag_auto']):.2f} fwhm={float(c['fwhm']):.2f} cs={float(c['class_star']):.2f} comp*FWHM={comp:.2f}(n={len(stars)})")
            print(f"  ours-PUB dRA*cos={rec['dRA_ours_pub']:+.3f} dDec={rec['dDec_ours_pub']:+.3f}  |  ours-HOR dRA*cos={rec['dRA_ours_hor']:+.3f} dDec={rec['dDec_ours_hor']:+.3f}")
        out.append(rec)
    json.dump(out,open("raw/measured.json","w"),indent=1)
    nok=sum(1 for o in out if o["status"]=="CATALOG")
    print(f"\nsaved raw/measured.json  {len(out)} epochs; {nok} catalog, {len(out)-nok} miss")

if __name__=="__main__":
    main()

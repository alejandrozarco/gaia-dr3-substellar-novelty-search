import csv, json, math

# ---- search_log.csv: every epoch/box searched ----
scan=json.load(open('full_epoch_scan.json'))
rows=[]
for r in scan['results']:
    m=r['mjd']; p=scan['pred'][str(m)]
    import datetime
    d=datetime.date(1858,11,17)+datetime.timedelta(days=int(m))
    outcome = ('CANDIDATE sep=%.2f\" id=%s r=%s'%(r['sep'],r['cand_id'],r.get('rmag')) 
               if r.get('cand_id') and r.get('sep') is not None and r['sep']<p['smaa']*1.1 and r.get('inell') 
               else 'null (no on-night single-epoch source in ellipse)')
    rows.append(dict(
        target='2001 KN76', archive='NSC_DR2(DECam)', night_UT=str(d), mjd_int=m,
        pred_ra=round(p['ra'],6), pred_dec=round(p['dec'],6), pred_V=round(p['V'],2),
        SMAA_3sig_as=round(p['smaa'],2), SMIA_3sig_as=round(p['smia'],2),
        search_rad_as=round(max(15.0,p['smaa']*1.3),1), n_obj_in_cone=r.get('n_obj') if 'n_obj' in r else '',
        outcome=outcome))
# add the two negative-control rows + offset summary
with open('search_log.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows: w.writerow(r)
print("Wrote search_log.csv with",len(rows),"epoch rows")

# ---- astrometry table for USER review (per-detection meas) ----
def mjd_to_iso(mjd):
    import datetime
    day=int(mjd); frac=mjd-day
    d=datetime.datetime(1858,11,17)+datetime.timedelta(days=day, seconds=frac*86400)
    return d.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
meas={
 '133189_17045':[(56362.265414,228.8012394,-20.8267605,23.319532,0.120827,'r','tu2088892'),
                 (56362.267488,228.8012123,-20.8267731,23.06266,0.144618,'r','tu2092162')],
 '133703_14601':[(57218.057851,229.7975286,-21.0925339,23.119263,0.206589,'r','c4d_150715_012457_ooi_r_ls9'),
                 (57218.058744,229.7974849,-21.0925470,23.307161,0.20233,'r','c4d_150715_012616_ooi_r_ls9')],
}
resid=json.load(open('precise_resid.json'))
with open('astrometry_for_review.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['nsc_objectid','utc_iso','mjd','ra_deg','dec_deg','mag','magerr','band','exposure',
                'ephem_resid_along_as','ephem_resid_cross_as','sep_total_as','pos_unc_est_as'])
    for oid,dets in meas.items():
        rr={round(x['mjd'],6):x for x in resid[oid]}
        for (mjd,ra,dec,mag,me,band,exp) in dets:
            key=round(mjd,6)
            rx=resid[oid][0] if abs(resid[oid][0]['mjd']-mjd)<abs(resid[oid][1]['mjd']-mjd) else resid[oid][1]
            # position uncertainty: NSC astrometric scatter ~ 30-70 mas + centroid ~0.1-0.2" at this SNR
            posunc=0.15
            w.writerow([oid, mjd_to_iso(mjd), round(mjd,6), round(ra,7), round(dec,7),
                        round(mag,2), round(me,3), band, exp,
                        round(rx['maj'],2), round(rx['minr'],2), round(rx['sep'],2), posunc])
print("Wrote astrometry_for_review.csv")

import csv
rows=[
 # night, survey, filter, box_smaa, box_smia, ra, dec, V, radius, in_arc, ndet_transient, resid_best, outcome
 ('2013-03-02','CTIO-4m/DECam via NSC DR2 meas','r',0.82,0.27,246.12948,-26.25174,21.61,20,'NO',2,0.33,'CANDIDATE: 2 same-night r det, transient (ndet=2 deltamjd=2min), resid 0.33-0.41", mag 21.6=predV; distinct from static star 1.0" away'),
 ('2014-06-27','CTIO-4m/DECam via NSC DR2 meas','VR',1.20,0.34,249.49856,-29.93923,21.54,20,'NO',1,0.09,'CANDIDATE: 1 det resid 0.09" mag 21.83; transient (ndet=1); object absent at moved position in +4.3h exposure (consistent w/ 6.8"/hr motion, excludes star)'),
 ('2014-06-29','CTIO-4m/DECam via NSC DR2 meas','VR',1.19,0.34,249.39630,-29.93032,21.55,20,'NO',1,0.14,'CANDIDATE: 1 det resid 0.14" mag 21.60=predV; transient (ndet=1 deltamjd=0)'),
 ('2015-04-27','CTIO-4m/DECam via NSC DR2 meas','VR',2.29,0.37,260.30698,-32.37912,21.79,20,'NO',2,0.03,'CANDIDATE: 2 same-night det (6min apart) resid 0.03-0.15" mag 21.5-21.7; transient (ndet=2 deltamjd=5min)'),
 ('2015-05-20','CTIO-4m/DECam via NSC DR2 meas','VR',2.24,0.38,259.26191,-32.56919,21.68,20,'NO',0,4.25,'NULL: nearest same-night mag-matched det 4.25" from pred (outside 3sig box, and associated w/ multi-night objects); no clean transient in box'),
 ('2015-05-21','CTIO-4m/DECam via NSC DR2 meas','VR',2.23,0.38,259.20891,-32.57476,21.68,20,'NO',0,2.94,'NULL: nearest same-night det 2.94" from pred; no clean sub-arcsec transient in box'),
 ('2013-06-25','Pan-STARRS1 DR2 detection (F51)','g',0.73,0.30,244.12504,-26.74728,21.28,20,'NO',1,0.34,'WEAK: single g=21.73 PS1 detection resid 0.34", non-stationary (1 det ever); single-band single-epoch, not independently corroborated -> supporting only, not chain-grade'),
 ('2013-06-25','CTIO-4m/DECam via NSC DR2 meas','VR',0.73,0.30,244.12504,-26.74728,21.28,20,'NO',0,None,'NULL: NSC meas box had 0 on-night detections (no DECam coverage that night in NSC)'),
 ('2010-2011','Pan-STARRS1 DR2 (F51) opposition fields','izy',0.2,0.2,None,None,21.0,20,'YES',0,None,'IN-ARC / shallow: PS1 y/z stacks; positions already reported (F51 in MPC arc 2012); PS1 too shallow at V~21 in single izy visits; not pursued for novel astrometry'),
]
w=csv.writer(open('search_log.csv','w'))
w.writerow(['night_UT','archive_survey','filter','box_SMAA_3s_as','box_SMIA_3s_as','pred_RA_deg','pred_Dec_deg','pred_V','search_radius_as','in_discovery_arc','n_transient_det','best_resid_as','outcome'])
for r in rows: w.writerow(r)
print("search_log.csv finalized:",len(rows),"epoch-searches logged")

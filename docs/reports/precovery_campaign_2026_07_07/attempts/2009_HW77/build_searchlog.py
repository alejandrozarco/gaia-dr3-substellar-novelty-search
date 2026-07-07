import csv
# search_log columns: night_UT, archive/survey, filter, depth_note, box_SMAA_as, box_SMIA_as, pred_RA, pred_Dec, pred_V, search_radius_as, in_arc, outcome
rows = [
 # night, survey, filters, box_smaa, box_smia, ra, dec, v, radius, in_arc, outcome(placeholder)
 ('2013-03-02','CTIO-4m/DECam (NSC DR2 meas)','r',0.82,0.27,246.12940,-26.25166,21.61,30,'NO','PENDING'),
 ('2014-06-27','CTIO-4m/DECam (NSC DR2 meas)','VR',1.20,0.34,249.49856,-29.93923,21.54,30,'NO','PENDING'),
 ('2014-06-29','CTIO-4m/DECam (NSC DR2 meas)','VR',1.19,0.34,249.39630,-29.93032,21.55,30,'NO','PENDING'),
 ('2015-04-27','CTIO-4m/DECam (NSC DR2 meas)','VR',2.29,0.37,260.30698,-32.37912,21.79,30,'NO','PENDING'),
 ('2015-05-20','CTIO-4m/DECam (NSC DR2 meas)','VR',2.24,0.38,259.26191,-32.56919,21.68,30,'NO','PENDING'),
 ('2015-05-21','CTIO-4m/DECam (NSC DR2 meas)','VR',2.23,0.38,259.20891,-32.57476,21.68,30,'NO','PENDING'),
]
w=csv.writer(open('search_log.csv','w'))
w.writerow(['night_UT','archive_survey','filter','box_SMAA_3s_as','box_SMIA_3s_as','pred_RA_deg','pred_Dec_deg','pred_V','search_radius_as','in_discovery_arc','outcome'])
for r in rows: w.writerow(r)
print("search_log.csv scaffold written")

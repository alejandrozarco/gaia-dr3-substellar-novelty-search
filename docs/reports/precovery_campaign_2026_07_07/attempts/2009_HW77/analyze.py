import csv, math, glob, os

# Predicted positions (geocentric-derived, W84 topocentric) per night from ephem_nights.csv
preds = {
 '2013':  ('2013-03-02T07:40', 56353.319, 246.12940, -26.25166, 21.61, 0.82, 0.27, 3.0),
 '2014a': ('2014-06-27T01:49', 56835.076, 249.49856, -29.93923, 21.54, 1.20, 0.34, 6.8),
 '2014b': ('2014-06-29T02:10', 56837.090, 249.39630, -29.93032, 21.55, 1.19, 0.34, 6.7),
 '2015a': ('2015-04-27T05:32', 57139.231, 260.30698, -32.37912, 21.79, 2.29, 0.37, 4.8),
 '2015b': ('2015-05-20T10:20', 57162.431, 259.26191, -32.56919, 21.68, 2.24, 0.38, 6.8),
 '2015c': ('2015-05-21T10:07', 57163.421, 259.20891, -32.57476, 21.68, 2.23, 0.38, 6.9),
}
def sep(ra,dec,ra0,dec0):
    return math.hypot((ra-ra0)*math.cos(math.radians(dec0)), dec-dec0)*3600

print(f"{'tag':6s} {'night':18s} {'pred_V':6s} {'box(SMAA/SMIA)':14s} -> detections within box on-night")
print("="*100)
for tag,(night,pmjd,pra,pdec,pv,smaa,smia,rate) in preds.items():
    f=f'meas_{tag}.csv'
    if not os.path.exists(f) or os.path.getsize(f)<20:
        print(f"{tag}: NO DATA FILE"); continue
    rows=list(csv.DictReader(open(f)))
    # keep only same-night detections (|dt|<0.5 day)
    onnight=[r for r in rows if abs(float(r['mjd'])-pmjd)<0.5]
    print(f"\n{tag:6s} {night:18s} V~{pv:.1f} box SMAA={smaa}\"/SMIA={smia}\"  cone_total={len(rows)} on-night={len(onnight)}")
    for r in sorted(onnight, key=lambda x: sep(float(x['ra']),float(x['dec']),pra,pdec)):
        s=sep(float(r['ra']),float(r['dec']),pra,pdec)
        dt=(float(r['mjd'])-pmjd)*24
        # expected offset from motion over dt
        exp_off=abs(rate*dt)
        mag=float(r['mag_auto']); cs=float(r['class_star'])
        flag=''
        if s< max(3*smaa, 3.0)+exp_off+2: flag+='NEAR '
        if abs(mag-pv)<1.5: flag+='MAGOK '
        print(f"   sep={s:6.2f}\" dt={dt:+5.2f}h exp_mot={exp_off:4.1f}\" mag={mag:5.2f} filt={r['filter']} fwhm={float(r['fwhm']):.2f} cstar={cs:.2f} mjd={r['mjd']} {flag}")

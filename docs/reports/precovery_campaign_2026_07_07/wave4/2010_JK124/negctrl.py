#!/usr/bin/env python3
"""Negative controls (rule 6):
A) +1 deg Dec offset: re-run per-exposure ephemeris box search shifted +1 deg; a clean
   control yields no sub-arcsec mag-matched point source.
B) False-alarm density: on each chain exposure, count point sources (class_star>0.7) with
   mag within +/-0.5 of predicted, over a 90" radius -> surface density -> P(random match
   within observed sep)."""
import urllib.request, urllib.parse, csv, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def tap(q,retries=4):
    data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
    for i in range(retries):
        try: return urllib.request.urlopen(TAP,data=data,timeout=180).read().decode()
        except Exception as e: last=str(e); time.sleep(3)
    return "ERR "+last

# chain epochs: exposure, pred_ra, pred_dec, box_arcsec, pred_mag, obs_sep
CHAIN=[
 ("c4d_140606_065522_ooi_r_v1",243.477521,-29.543437,5.0,21.52,0.26),
 ("c4d_150620_050628_ooi_r_v2",244.744031,-29.394707,5.0,21.57,0.42),
 ("c4d_150620_050928_ooi_r_v2",244.743987,-29.394699,5.0,21.57,0.37),
 ("c4d_160308_082444_ooi_VR_v1",247.962213,-29.466620,5.0,21.70,0.97),
]
print("========== CONTROL A: +1 deg Dec offset per-exposure search ==========")
for name,ra,dec,box,pmag,osep in CHAIN:
    dec2=dec+1.0; cosd=math.cos(math.radians(dec2))
    dra=box/3600.0/cosd; ddec=box/3600.0
    q=(f"SELECT ra,dec,mag_auto,filter,class_star,fwhm FROM nsc_dr2.meas "
       f"WHERE exposure='{name}' AND ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} "
       f"AND dec BETWEEN {dec2-ddec:.7f} AND {dec2+ddec:.7f}")
    rows=list(csv.DictReader(tap(q).splitlines()))
    hits=[r for r in rows if r.get('mag_auto') and abs(float(r['mag_auto'])-pmag)<0.6]
    print(f"  {name}: sources_in_offset_box={len(rows)}  mag-matched(+/-0.6)={len(hits)}")
    for h in hits:
        s=math.hypot((float(h['ra'])-ra)*cosd,(float(h['dec'])-dec2))*3600
        print(f"     sep={s:.2f}\" mag={h['mag_auto']} {h['filter']} cstar={h['class_star']}")

print("\n========== CONTROL B: false-alarm density (90\" radius, mag +/-0.5, cstar>0.7) ==========")
for name,ra,dec,box,pmag,osep in CHAIN:
    cosd=math.cos(math.radians(dec)); R=90.0
    dra=R/3600.0/cosd; ddec=R/3600.0
    q=(f"SELECT ra,dec,mag_auto,class_star FROM nsc_dr2.meas WHERE exposure='{name}' "
       f"AND ra BETWEEN {ra-dra:.7f} AND {ra+dra:.7f} AND dec BETWEEN {dec-ddec:.7f} AND {dec+ddec:.7f}")
    rows=list(csv.DictReader(tap(q).splitlines()))
    pts=[r for r in rows if r.get('class_star') and float(r['class_star'])>0.7
         and r.get('mag_auto') and abs(float(r['mag_auto'])-pmag)<0.5]
    area=math.pi*R*R  # arcsec^2
    dens=len(pts)/area
    p_match=dens*math.pi*osep*osep  # expected count within observed sep
    print(f"  {name}: N_ptsrc(mag {pmag:.1f}+/-0.5)={len(pts)} in {R}\"R -> dens={dens*3600:.3f}/arcmin^2 "
          f"-> E[random within {osep}\"]={p_match:.4f}")

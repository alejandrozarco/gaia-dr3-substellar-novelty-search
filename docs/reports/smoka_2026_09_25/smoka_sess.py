import re, requests
INS = ['SUP','FCS','HDS','OHS','IRC','CIA','COM','CAC','MIR','MCS','K3D','HIC','FMS','HSC','CRS','IRD','SWS','MMZ','VMP','SCX','KCC','KCD','KWF','ISL','KLS','HID','OAS','CSD','MCT','MTA','MTO','HWP','HNR','NIC','KIF','TRC','GRA']
COLS = ['FRAMEID','DATE_OBS','FITS_SIZE','OBS_MODE','DATA_TYPE','OBJECT','FILTER','WVLEN','DISPERSER','RA2000','DEC2000','UT_START','EXPTIME','OBSERVER','EXP_ID']
def session():
    s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"; s.get("https://smoka.nao.ac.jp/fssearch.jsp", timeout=60); return s
def search(s, extra, ins=INS, radius="5.0", ascii=False):
    base = [("object",""),("resolver","SIMBAD"),("coordsys","Equatorial"),("equinox","J2000"),("fieldofview","auto"),("RadOrRec","radius"),("longitudeC",""),("latitudeC",""),("radius",radius),("longitudeF",""),("latitudeF",""),("longitudeT",""),("latitudeT",""),("date_obs",""),("exptime",""),("observer",""),("prop_id",""),("frameid",""),("exp_id",""),("dataset",""),("asciitable","Ascii" if ascii else "Table"),("frameorshot","Frame"),("action","Search")]
    keys = dict(extra); data = [(k, v) for k, v in base if k not in keys] + list(extra)
    data += [("instruments", i) for i in ins] + [("obs_mod", m) for m in ("IMAG","SPEC","IPOL")] + [("data_typ","OBJECT"),("obs_cat","Science Observation"),("bandwidth_type","FILTER"),("band",""),("wcs","0"),("request","0")]
    data += [("dispcol", c) for c in COLS] + [("orderby","FRAMEID")]*3 + [("diff","1000"),("output_equinox","J2000"),("from","0")]
    return s.post("https://smoka.nao.ac.jp/fssearch", data=data, timeout=300, headers={"Referer": "https://smoka.nao.ac.jp/fssearch.jsp"})
def text(r):
    t = re.sub(r"<[^>]+>", " ", r.text); return re.sub(r"\s+", " ", t)

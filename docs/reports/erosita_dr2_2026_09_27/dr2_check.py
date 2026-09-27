"""eROSITA DR2 (eRASS:1-3 cumulative; Ramos-Ceja+2026, VizieR J/A+A/712/A171) counterpart check of the project's X-ray-relevant
objects, superseding the eRASS1-only checks. Per object: galactic longitude (coverage: western/DE hemisphere, 179.9 < l < 359.9),
nearest DR2 source within 30 arcsec (separation, detection likelihood, 0.2-2.3 keV flux), and the nearest eRASS1 source
(J/A+A/682/A34) for comparison. Gaia DR3 positions (epoch 2016). A missing VizieR reply is recorded as ERR (a hole, not a null).
Usage: python dr2_check.py (writes dr2_check.csv)."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, os
from astroquery.vizier import Vizier; from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord; import astropy.units as u
H = os.path.dirname(os.path.abspath(__file__))
OBJ = {
 "3161546596480983040": "Object B (eRASS1 CV/MCV, Schwope+2026)", "3161546630842185984": "Object B neighbour (G dwarf, 4.76 arcsec)",
 "4731701084150029824": "2MASS J0353-5502 (eclipsing WD+dM)", "6470209729951480576": "CRTS J2054-5418 (He-emission DN)",
 "2002597083798483200": "J2257+5416 (CV)", "1977447164064222976": "J2133+4638 (CV cand)", "578709631539357440": "WD 0856+048 (gas disc)",
 "6914922055508553984": "WDJ2052-0324", "2191618770599895296": "WDJ2127+5937", "5503429908930455808": "WDJ0701-5348",
 "4844023064578952320": "WDJ0404-3950", "2249098833310553728": "WDJ1949+6730", "4705562733524591232": "WDJ0056-6617",
 "1420761029600606592": "WDJ1724+5620 (DAe)", "1337970174853051392": "WDJ1701+3435 (DAE)", "4409006786607484672": "WDJ1617+0158 (DAE)",
 "3717349170269867520": "WDJ1323+0559 (DAe)", "1769157090045264128": "WDJ2146+1431 (DAE)", "709815329316284928": "WDJ0835+3155 (DAE)",
 "926161868627454976": "WDJ0754+4423 (DAe)",
 "1038176780370360576": "WDJ0914+5812 (DO)", "1157401396015448960": "J1512+0651 (UHE DOZ)", "1879989790567353344": "WDJ2215+2530 (DOZ)",
 "920621124593362816": "KUV 07523+4017 (DOZ)", "953685015492787456": "WDJ0658+4414 (DO)", "5157333438398813824": "WDJ0256-1450 (hot DA)",
 "1415911839725510528": "WDJ1717+5158 (hot DA)", "2311285729210966144": "WDJ2349-3539 (DA)", "3365371721281530880": "WDJ0651+1852",
 "3230486971974872192": "WDJ0438+0031 (DO)", "1094376947131876352": "WDJ0800+6334 (DOA)", "6170660401283991680": "J1400-3302 (DO)",
 "5657176543986789248": "WDJ0948-2800 (DO)", "3842377248804727168": "SDSS J0917+0010 (DO)",
 "6021870154194477312": "GALEX J1618-3554 (103-min)", "5208047381438507520": "J0735-7944 (hot DQ)", "6886051830805052288": "J2051-1617 (hot DQ)",
 "1980205739970324224": "J2159+5102 (magnetic)", "3890059941364406144": "SDSS J1022+1611", "3107374277060584064": "WDJ0644-0045 (reflection)",
 "4711031463842628736": "EC 01395-6452 (UHE cand)", "4866851575967878144": "UHE cand 4866", "5671975077144346112": "UHE cand 5671",
 "4844689579080133248": "UHE cand 4844", "6644780943442193664": "UHE cand 6644", "3597350571454888448": "UHE cand 3597",
 "4749559145849819008": "UHE cand 4749", "1008280341952767232": "UHE cand 1008", "2120335400240968448": "GALEX J1833+4829 (UHE cand)",
 "303909583762954368": "UHE cand 0339",
}
ku = pd.read_csv(os.path.join(H, "..", "uhe_screen_sdssv_2026_09_26", "data", "known_uhe_all.csv"), dtype=str)
for _, r in ku.iterrows():
    OBJ.setdefault(str(r.gaia), f"{r['name']} (known UHE)")
ids = [i for i in OBJ if i.isdigit()]
g = Gaia.launch_job(f"SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE source_id IN ({','.join(ids)})").get_results()
pos = {str(x["source_id"]): (float(x["ra"]), float(x["dec"])) for x in g}
V = Vizier(columns=["**"], row_limit=10); V.TIMEOUT = 200; rows = []
for gid in ids:
    if gid not in pos: rows.append(dict(gaia=gid, label=OBJ[gid], status="NO_GAIA")); continue
    ra, dec = pos[gid]; c = SkyCoord(ra, dec, unit="deg"); l = c.galactic.l.deg
    d = dict(gaia=gid, label=OBJ[gid], ra=round(ra, 5), dec=round(dec, 5), gal_l=round(l, 1), covered=179.9 < l < 359.9)
    if d["covered"]:
        for cat, tag in (("J/A+A/712/A171", "dr2"), ("J/A+A/682/A34", "e1")):
            try:
                t = V.query_region(c, radius=30 * u.arcsec, catalog=cat)
                if len(t):
                    tt = t[0]
                    scol = [x for x in tt.colnames if x in ("_r", "rDist")]
                    tt.sort(scol[0]) if scol else None; b = tt[0]
                    d[f"{tag}_n30"] = len(tt); d[f"{tag}_sep"] = round(float(b[scol[0]]), 1) if scol else np.nan
                    for cn in tt.colnames:
                        if cn.lower() in ("det_like_0", "det_like", "ml_flux_0", "ml_flux", "fflux", "flux", "name", "iauname", "erass", "pos_err", "radecerr"):
                            d[f"{tag}_{cn}"] = b[cn]
                else: d[f"{tag}_n30"] = 0
            except Exception as ex: d[f"{tag}_n30"] = f"ERR {str(ex)[:40]}"
    rows.append(d); print({k: v for k, v in d.items() if k in ("gaia", "label", "covered", "dr2_n30", "dr2_sep", "e1_n30")}, flush=True)
pd.DataFrame(rows).to_csv(os.path.join(H, "dr2_check.csv"), index=False)

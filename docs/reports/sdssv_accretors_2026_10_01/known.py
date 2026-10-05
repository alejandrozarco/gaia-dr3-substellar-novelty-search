"""Front filter: match candidates (gaia id + ra/dec) against prior catalogues. Returns per-row semicolon list of hits.
Sources: Brink+2026 DR20 VAC (587, Gaia DR3), Inight+2025 (J/MNRAS/536/1057, 504), Inight+2026 DESI (arXiv:2607.22836 anc, 1029),
Inight+2023a (J/MNRAS/524/4867 t0+t1), Inight+2023b (J/MNRAS/525/3597), Han+2026 DESI DR1 (J/ApJS/282/26), SnowWhite CV lane 605
(docs/reports/cv_sdssv_2026_09_24, read only), SDSS-V targeting CV list mos_cataclysmic_variables (Gaia DR2 pos), Hernandez-Diaz+2026
Gaia ids, local known_objects store (VSX, Milliquas, RK, Downes, eRASS1 CV cats, Akras symbiotics; pulled May 2026).
Position match radius 3 arcsec (catalogue epochs differ; Gaia ids preferred)."""
import os, re, sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u
D = os.path.dirname(os.path.abspath(__file__)); LIT = os.path.join(D, "lit")
sys.path.insert(0, os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/scripts/gates")); import local_known
def sdssname(n):
    m = re.search(r"J(\d{2})(\d{2})(\d{2}\.\d+)([+-])(\d{2})(\d{2})(\d{2}\.?\d*)", str(n))
    if not m: return np.nan, np.nan
    h, mi, s, sg, d, dm, ds = m.groups(); ra = 15 * (int(h) + int(mi) / 60 + float(s) / 3600); de = int(d) + int(dm) / 60 + float(ds) / 3600
    return ra, (-de if sg == "-" else de)
def cats():
    C = []
    T = Table.read(os.path.join(LIT, "eROSITA_CVs_in_SDSS-1.0.0.fits"))
    g = [str(x) if x is not None and str(x) not in ("--", "") else "" for x in T["GAIA_DR3_ID"].astype("int64").filled(-1)] if hasattr(T["GAIA_DR3_ID"], "mask") else [str(x) for x in T["GAIA_DR3_ID"]]
    C.append(pd.DataFrame(dict(cat="Brink26", name=[str(x) for x in T["IAUNAME"]], gaia=g, ra=np.array(T["RA_GAIA_DR3"].filled(np.nan) if hasattr(T["RA_GAIA_DR3"], "mask") else T["RA_GAIA_DR3"], float), dec=np.array(T["DEC_GAIA_DR3"].filled(np.nan) if hasattr(T["DEC_GAIA_DR3"], "mask") else T["DEC_GAIA_DR3"], float))))
    C.append(pd.DataFrame(dict(cat="Brink26", name=[str(x) for x in T["IAUNAME"]], gaia="", ra=np.array(T["RA_ICRS"], float), dec=np.array(T["DE_ICRS"], float))))
    t = pd.read_csv(os.path.join(LIT, "J_MNRAS_536_1057_0.csv"), dtype={"GaiaEDR3": str}); r = [sdssname(x) for x in t.SDSS]
    C.append(pd.DataFrame(dict(cat="Inight25", name=t.SDSS, gaia=t.GaiaEDR3, ra=[x[0] for x in r], dec=[x[1] for x in r])))
    t = pd.read_csv(os.path.join(LIT, "src_2607.22836/anc/tabledata.csv"), dtype={"EDR3_source_id": str})
    C.append(pd.DataFrame(dict(cat="InightDESI26", name=t.Name, gaia=t.EDR3_source_id, ra=t.ra, dec=t.dec)))
    for f, k in (("J_MNRAS_524_4867_0.csv", "Inight23a"), ("J_MNRAS_524_4867_1.csv", "Inight23a_sp"), ("J_MNRAS_525_3597_0.csv", "Inight23b")):
        t = pd.read_csv(os.path.join(LIT, f), dtype={"GaiaEDR3": str}); r = [sdssname(x) for x in t.SDSS]
        C.append(pd.DataFrame(dict(cat=k, name=t.SDSS, gaia=t.GaiaEDR3 if "GaiaEDR3" in t else "", ra=[x[0] for x in r], dec=[x[1] for x in r])))
    t = pd.read_csv(os.path.join(LIT, "J_ApJS_282_26_0.csv"))
    C.append(pd.DataFrame(dict(cat="HanDESI26", name=t.Name, gaia="", ra=t.RAJ2000, dec=t.DEJ2000)))
    t = pd.read_csv(os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/cv_sdssv_2026_09_24/data/cv_lane_all605_disposition.csv"), dtype={"gaia_dr3_source_id": str})
    C.append(pd.DataFrame(dict(cat="SWlane605:" + t.disposition.astype(str), name="", gaia=t.gaia_dr3_source_id, ra=np.nan, dec=np.nan)))
    t = pd.read_csv(os.path.join(LIT, "mos_cv.csv"), skiprows=1)
    C.append(pd.DataFrame(dict(cat="SDSSV_CVtarget", name=t.ref_id.astype(str), gaia="", ra=t.ra, dec=t.dec)))
    hd = set(re.findall(r"\b\d{17,19}\b", open(os.path.join(LIT, "src_2607.27855/main.tex")).read()))
    C.append(pd.DataFrame(dict(cat="HernandezDiaz26", name="", gaia=sorted(hd), ra=np.nan, dec=np.nan)))
    return pd.concat(C, ignore_index=True)
def match(df, ra="ra", dec="dec", gaia="gaia", r_arcsec=3.0):
    K = cats(); hits = [[] for _ in range(len(df))]
    g2i = {}
    for i, g in enumerate(df[gaia].astype(str)): g2i.setdefault(g, []).append(i)
    for row in K[K.gaia.astype(str).str.len() > 10].itertuples():
        for i in g2i.get(str(row.gaia), []): hits[i].append(f"{row.cat}")
    P = K[np.isfinite(K.ra.astype(float)) & np.isfinite(K.dec.astype(float))]
    c1 = SkyCoord(df[ra].values * u.deg, df[dec].values * u.deg); c2 = SkyCoord(P.ra.values.astype(float) * u.deg, P.dec.values.astype(float) * u.deg)
    i1, i2, sep, _ = c1.search_around_sky(c2, r_arcsec * u.arcsec)
    for a, b, s in zip(i2, i1, sep.arcsec): hits[a].append(f"{P.cat.values[b]}({s:.1f}\")")
    lk = local_known.match(df.reset_index(drop=True), ra, dec, 5.0)
    for r in lk.itertuples():
        hits[int(r.idx)].append(f"{r.catalog}:{r.otype}:{r.name}({r.sep_arcsec:.1f}\")")
    return [";".join(sorted(set(h))) for h in hits]

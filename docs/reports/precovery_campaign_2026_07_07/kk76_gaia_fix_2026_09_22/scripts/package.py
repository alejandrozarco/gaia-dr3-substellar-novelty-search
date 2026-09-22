import sys, csv; sys.path.insert(0, "/tmp/kk76_fix")
from fitlib import *
from common import load, background, tangent, untangent
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F = pickle.load(open("fits/fitCE.pkl", "rb")); POS, SIG, C = F["POS"], F["SIG"], F["C"]
FB = pickle.load(open("fits/fitB.pkl", "rb"))
R06 = ["j9fw91hpq", "j9fw91hqq", "j9fw91hrq", "j9fw91hsq"]
R10 = ["ib2k52cvq", "ib2k52cwq", "ib2k52cxq", "ib2k52cyq", "ib2k52czq", "ib2k52d0q", "ib2k52d2q", "ib2k52d3q"]
INST = {r: ("ACS/HRC", "CLEAR") for r in R06}
for r in R10:
    h = load(r)["h0"]; INST[r] = ("WFC3/" + h["DETECTOR"], h["FILTER"])
res = {x["iso date"][:19]: x for x in C["observations"]["residuals"] if x["obscode"] == "250"}
# ---- positions CSV
with open("kk76_positions_gaia_anchored.csv", "w") as f:
    f.write("# (88268) 2001 KK76 - HST positions re-anchored to Gaia DR3 (PM-propagated per frame), main-thread independent re-measurement 2026-09-22.\n")
    f.write("# DRAFT, NOT SUBMITTED. obsTime = mid-exposure UTC ((EXPSTART+EXPEND)/2). HST-centric astrometric positions. pos = HST geocentric ICRF (km, JPL Horizons -48).\n")
    f.write("# shift = Gaia minus header-WCS (arcsec, xi/eta), n = Gaia stars used, fitC = residual in the all-data find_orb fit (arcsec).\n")
    w = csv.writer(f)
    w.writerow(["rootname", "instrument", "filter", "obsTime_UTC", "RA_deg", "Dec_deg", "sigma_arcsec", "shift_xi", "shift_eta", "rms_xi", "rms_eta", "n_gaia",
                "fitC_dRA", "fitC_dDec", "pos1_km", "pos2_km", "pos3_km"])
    for r in R06 + R10:
        p = POS[r]; v = HV[r]; rr = min(res.values(), key=lambda x: abs(Time(x["iso date"][:23]).jd - v["jd"]))
        w.writerow([r.upper(), INST[r][0], INST[r][1], v["isot"][:23] + "Z", f"{p['ra']:.7f}", f"{p['dec']:.7f}", SIG[r], f"{p['shift_xi']:+.3f}", f"{p['shift_eta']:+.3f}",
                    f"{p['rms_xi']:.3f}", f"{p['rms_eta']:.3f}", p["nstar"], f"{rr['dRA']:+.3f}", f"{rr['dDec']:+.3f}", f"{v['X']:.4f}", f"{v['Y']:.4f}", f"{v['Z']:.4f}"])
# ---- ADES PSV draft (two obsBlocks: 2006 ACS/HRC, 2010 WFC3)
def block(rows, tel_name, prog, det_note):
    L = ["# version=2022", "# observatory", "! mpcCode 250", f"! name Hubble Space Telescope ({tel_name}, archival; {prog})",
         "# submitter", "! name A. Keur", "# observers", f"! name HST {prog} archival exposures (original observers not named in the archive)",
         "# measurers", "! name A. Keur", "# telescope", "! design reflector", "! aperture 2.4", "! detector CCD", f"! name HST {tel_name}",
         "# comment",
         "! line DRAFT - NOT SUBMITTED. Archival astrometry of (88268) 2001 KK76 from public HST frames (MAST).",
         "! line Each frame's header WCS was NOT used as an absolute reference: in these moving-target visits it",
         "! line is the uncorrected guide-star pointing (WCSNAME ...-HSC30 carries a null correction; checked in WCSCORR).",
         "! line Positions are tied directly to Gaia DR3 per frame (proper motions propagated to the epoch;",
         f"! line {det_note}). HST parallax: pos1-3 = geocentric ICRF position of HST (km) from JPL Horizons",
         "! line (body -48) at obsTime (mid-exposure UTC). Photometry omitted (non-standard HST bands).",
         "permID |mode|stn |sys     |ctr|pos1        |pos2        |pos3        |obsTime                  |ra           |dec          |rmsRA|rmsDec|astCat|remarks"]
    for r in rows:
        p = POS[r]; v = HV[r]
        L.append(f"88268  |CCD |250 |ICRF_KM |399|{v['X']:12.4f}|{v['Y']:12.4f}|{v['Z']:12.4f}|{v['isot'][:23]}Z |{p['ra']:12.7f} |{p['dec']:12.7f} | {SIG[r]:.2f}| {SIG[r]:.2f} |Gaia3 |HST {INST[r][0]} {INST[r][1]} {r.upper()}; {p['nstar']} Gaia DR3 stars")
    return L
nst06 = ", ".join(str(POS[r]["nstar"]) for r in R06)
out = block(R06, "ACS/HRC", "GO-10514", f"shift fit on {nst06} Gaia stars per frame, rms 0.02-0.03 arcsec")
out += [""] + block(R10, "WFC3 UVIS+IR", "GO-11644", "shift fit on 9-11 (UVIS) or ~475 (IR) Gaia stars per frame")
open("ades_draft_v2_88268_2001kk76.psv", "w").write("\n".join(out) + "\n")
print("\n".join(out[-10:]))

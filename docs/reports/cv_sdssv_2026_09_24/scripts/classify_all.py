# Final per-object disposition for all 605 SnowWhite CV-selection rows. Manual verdicts come from visual inspection of the
# in_stack-aware barycentric coadds (plots/final/, plots/spec_*.png, contact sheets plots/cs_*.png).
import pandas as pd, numpy as np, json
m = pd.read_csv("master.csv"); ga = pd.read_csv("gaia_alert_xmatch.csv")[["sdss_id", "gaia_alert"]]
m = m.merge(ga, on="sdss_id", how="left")
M = {  # gaia id -> (category, note)
 2002597083798483200: ("NEW_CV_CANDIDATE", "A1: quiescent DN spectrum (double-peaked Balmer, EW(Ha)=320 A, He I); 196 pc; ROSAT 2RXS 7.3\"; no outburst in ZTF 2018-25"),
 1977447164064222976: ("NEW_CV_CANDIDATE", "A12: broad double-peaked Ha/Hb (FWHM ~1650 km/s), weak He I, blue WD-like continuum; 341 pc; no eROSITA-DE coverage"),
 5362131777028219904: ("CV_LIKELY_IN_UNPUBLISHED_EROSITA_LISTS", "A3: DN-like, eRASS1+eRASS:3 source, erosita_compact cartons -> probably in Brink+2026 (catalogue not public)"),
 5568642355890359168: ("CV_LIKELY_IN_UNPUBLISHED_EROSITA_LISTS", "A4: WD-dominated DN-like (194 pc), eRASS1/eRASS:3/2RXS; probably in Brink+2026 and/or Hernandez-Diaz+2026 master table (not public)"),
 4679467096349698048: ("CV_LIKELY_IN_UNPUBLISHED_EROSITA_LISTS", "A11: broad Balmer + He I, eRASS1/eRASS:3; probably in Brink+2026 (not public)"),
 6703736482047069696: ("POSSIBLE_CV", "A14: blue continuum, Ha/Hb FWHM ~850 km/s, weak He II; parallax insignificant; Culpan+2022 hot-subdwarf photometric candidate; eROSITA non-detection"),
 6403339013297801216: ("POSSIBLE_ACCRETING_OR_IRRADIATED_WD_BINARY", "B4: narrow (FWHM~200 km/s) Balmer emission to H10, no He, blue continuum, constant RV (-40 km/s, 2 visits); eROSITA non-detection"),
 1822575389309423232: ("KNOWN_CV_NEW_SUBTYPE", "A8 = MGAB-V3675 (VSX 'CV'): He II/Hb=0.76, ZTF high/low states (~2 mag) and 2.19-2.20 h, ~1 mag modulation -> polar candidate"),
 4784897896243243392: ("KNOWN_CV_NEW_SUBTYPE", "A9 = VSX/Gaia DR3 CV candidate: He II/Hb=0.92 -> magnetic CV candidate; eRASS:3; probably also in Brink+2026"),
 5664935458242923392: ("KNOWN_CV_NEW_SUBTYPE", "A10 = VSX/Gaia DR3 CV candidate, SIMBAD 'QSO' (misclassified): He II/Hb=0.46, hard X-rays, ZTF 77.4 min (or 38.7 min harmonic) -> magnetic CV candidate"),
 3474010479490950656: ("KNOWN_VSX", "ASASSN-20aj UGWZ:"), 4514099864666967040: ("KNOWN_VSX", "PNV J18580379+1701265 UG"),
 5222246650697733248: ("KNOWN_VSX", "MASTER OT J085602.92-710244.7 UG; Gaia22czo"), 2079868802496867072: ("KNOWN_VSX", "MASTER OT J194054.30+450242.0 UG"),
 1815530332977204096: ("KNOWN_VSX", "ZTF18abiklve NL/VY"),
 1969629915562515072: ("NON_CV_NEBULAR_UNCLASSIFIED", "B10: compact blue source with broad (~900 km/s) [O III], He II, [S III], [Ar III]; possible nova remnant or young PN; no catalogue entry"),
 250765238990402304: ("LOW_SN_UNCLEAR", "A16: cool WD (118 pc) with narrow Ha emission at S/N~6; earlier 'double peak' was an in_stack artefact"),
 5931744839753122944: ("NON_CV_BINARY_CANDIDATE", "blue M_G=8.2 star with Balmer absorption + narrow Ha emission, Ha RV -8..+71 km/s over 30 d, Gaia VARIABLE: reflection-effect (sdB/WD+dM) candidate"),
 5519268034637572736: ("NON_CV_YSO", "B1: young M dwarf (gamma Vel/Pozzo 1 member, VSX YSO) caught in a flare (Balmer, He I, He II)"),
 50865027106484096: ("KNOWN_PN", "central star of PN Ba 1"), 6055200341668022400: ("KNOWN_PN", "RCW 69"), 5881838006914886784: ("KNOWN_PN", "PN Mz 1"),
 2164192930525717248: ("KNOWN_PN", "NGC 7048"),
 5350284676671985536: ("NEBULAR_CONTAMINATION", "Carina Nebula field"), 2014154398418935040: ("NEBULAR_CONTAMINATION", "DA WD + Bubble Nebula (NGC 7635) emission"),
 3377263626729615232: ("NEBULAR_CONTAMINATION", "hot WD + [N II]/[S II] diffuse emission"), 3377426255666376704: ("NEBULAR_CONTAMINATION", "same field as 3377263626729615232"),
 2081766701303858816: ("NEBULAR_CONTAMINATION", "[O II],[N II],[S II]"), 5350358614535904384: ("NEBULAR_CONTAMINATION", "H II region spectrum"),
 2071605220993676544: ("NEBULAR_CONTAMINATION", "narrow lines + [S II]"), 2162171748957864960: ("NEBULAR_CONTAMINATION", "[S II]"),
 5254269858168675456: ("NEBULAR_CONTAMINATION", "[S II],[O III]"), 2162192540899913600: ("NEBULAR_CONTAMINATION", "[O III]"),
 3101601493117089408: ("NEBULAR_CONTAMINATION_PROBABLE", "weak Ha+[N II] at b=-0.5"),
 618535179648391936: ("QSO", "Quaia z=1.23"), 2538934835738048640: ("QSO", "SIMBAD QSO; Mg II at 6550"), 2827641888836229120: ("QSO", "Quaia z=1.09"),
 3641295538659855232: ("QSO", "z~0.69 ([O II] 6305, Mg II 4735, [O III] 8470)"),
 6400035706707634944: ("ARTEFACT", "G=14 star, spiky 6350-6920 A structure in single visit; RUWE 12"),
 3006200992344544384: ("ARTEFACT_BOSS_RED_HUMP", "6000-7000 A hump (same morphology as DESI-disproved cases)"),
 6395747778861116544: ("ARTEFACT_BOSS_RED_HUMP", "6250-6900 A hump, SDSS pipeline 'QSO z=1.29'; same morphology as DESI-disproved cases"),
 183564978087998336: ("ARTEFACT_BOSS_RED_HUMP", "6000-7000 A hump"), 2155352131166620160: ("ARTEFACT_BOSS_RED_HUMP", "hump absent in DESI DR1 spectrum (targetid 39633375635443973)"),
 4421481501938647936: ("ARTEFACT_BOSS_RED_HUMP", "red-arm flux 6-14x DESI DR1 (targetid 39627824805450751)"),
 4519762315183631104: ("CONTAMINATED_BY_NEIGHBOUR", "DC WD + M-dwarf wide companion light"), 4864483640237316224: ("CONTAMINATED_BY_NEIGHBOUR", "DC WD + bright M dwarf companion"),
 1822474401747520128: ("NO_CV_SIGNATURE", "hot featureless (Culpan hot-SD candidate); weak He II bump not significant"),
 5860276034133376768: ("NON_CV_YSO_OR_EMISSION_GIANT", "B5: red giant-like continuum with broad Ha, mwm_yso carton"),
 639900580361748736: ("NO_CV_SIGNATURE", "DQ-like Swan bands"), 4840005414731428224: ("XCSAO_EXTREME", "xcsao_v_rad=101751 km/s; blue part lost in Astra grid"),
}
cat, note = [], []
allviz = json.load(open("allviz_v1.json"))
for _, r in m.iterrows():
    g = int(r.gaia_dr3_source_id)
    if g in M: c, n = M[g]
    elif r.prior: c, n = "KNOWN_CATALOGUE", (str(r.local_hits) if isinstance(r.local_hits, str) else "") + " " + (str(r.arx_hits) if isinstance(r.arx_hits, str) else "") + " " + str(r.simbad)
    else:
        em = (r.Ha_ew > 5) & (r.Ha_sig > 5)
        if em and r.redblue > 5: c, n = "MDWARF_OR_WDdM_CHROMOSPHERIC", "narrow Ha on M-dwarf-dominated spectrum"
        elif em and r.neb: c, n = "NEBULAR_CONTAMINATION_PROBABLE", "forbidden lines present"
        elif em and r.Ha_fwhm < 400: c, n = "NARROW_Ha_EMITTER_NONCV", "narrow Ha (M dwarf/PCEB/YSO/M33/nebular)"
        elif em: c, n = "WEAK_BROAD_Ha_UNCLEAR", "inspected: noise/M dwarf/low S/N"
        else: c, n = "NO_CV_SIGNATURE", "no significant emission (WD/DC/DA/DZ/M dwarf/low S/N)"
    cat.append(c); note.append(n.strip())
m["disposition"] = cat; m["disposition_note"] = note
cols = ["gaia_dr3_source_id", "sdss_id", "classification", "p_cv", "phot_g_mean_mag", "bp_rp", "parallax", "parallax_error", "min_mjd", "max_mjd", "n_vis",
        "snr_coadd", "Ha_ew", "Ha_sig", "Ha_fwhm", "Hb_ew", "HeI5876_ew", "HeI5876_sig", "HeII4686_ew", "HeII4686_sig", "heii_hb", "simbad", "gaia_alert", "disposition", "disposition_note"]
m[cols].to_csv("cv_lane_all605_disposition.csv", index=False)
print(m.disposition.value_counts().to_string())

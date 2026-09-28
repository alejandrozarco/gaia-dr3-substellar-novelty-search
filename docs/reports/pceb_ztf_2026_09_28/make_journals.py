"""Journals for the DESI WD+M ZTF detections without a matching catalogued period (pceb_candidates_enriched.csv + ads_hits.csv).
Per object: journal (scripts/journal/journal.py new), ledger rows for the ZTF detection, the per-star period gate, the ADS alias search
and the GF21/VSX cross-match, and a status entry. Existing journals get the ledger rows and entry only.
Usage: python make_journals.py [--dry]"""
import os, sys, subprocess, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, "..", "..", "..")
P = os.path.expanduser("~/claude_projects/ostinato/.venv/bin/python"); J = os.path.join(R, "scripts", "journal", "journal.py")
DRY = "--dry" in sys.argv
c = pd.read_csv(os.path.join(H, "pceb_candidates_enriched.csv"), dtype={"GaiaDR3": str})
a = pd.read_csv(os.path.join(H, "ads_hits.csv"), dtype={"GaiaDR3": str}).fillna("")
NOTES = {"2699750475864002176": "VSX lists PS1-3PI J213019.78+061204.6 as type RRC with P = 0.341167 d (Gavras+2023 carries the same value); that frequency has zero Lomb-Scargle power in ZTF g and r (FAP 1) while 3.8152 c/d has FAP 5e-89 in r: the RRc classification does not describe this star (revision candidate)",
         "3096525945581800576": "Ranaivomanana+2025 lists a 7.1-min Gaia period (0.00495 d; not seen in ZTF) and Morgan+2012 a separation-based orbital-period estimate of 10.15 d; VSX has a Gaia auto-entry of type WD without a period",
         "5187572001027818240": "VSX has a Gaia auto-entry of type WD without a period",
         "2864507860881192320": "Bravo+2025 (AJ 169, 100; arXiv:2412.04597) list WD J2339+2552 as an unresolved ultracool-companion candidate (infrared excess; spectral-binary fit to the Gaia XP spectrum: DA 7489 K, log g 6.88, plus an M7 companion); no period is given there, so the 2.89-h modulation would be the orbital period of that system",
         "756150707815989632": "ADS full-text hits under the SIMBAD name 'PB 302' are unrelated non-astronomy papers (name collision); no astronomical reference mentions the star"}
MORGAN = {"1241489468326857472": 3.23, "1554999648323842560": 3.71, "3092149541407880576": 0.09, "3719845611420268544": 4.58, "756150707815989632": 0.45}
GAVRAS = {"2714650400312838400", "4594856927813126528", "1102031472205224832"}
def run(args):
    if DRY: print(" ", " ".join(x if len(x) < 60 else x[:57] + "..." for x in args[2:])); return
    subprocess.run([P, J] + args, capture_output=True, text=True)
for _, r in c.iterrows():
    g = r.GaiaDR3; hits = a[(a.GaiaDR3 == g) & (a.bibcode.str.len() > 4)]
    holes = a[(a.GaiaDR3 == g) & (a.bibcode == "HOLE")]
    aliases = sorted(set(a[a.GaiaDR3 == g].alias))
    hit_txt = "; ".join(f"{b.bibcode} {b.title[:70]}" for _, b in hits.drop_duplicates("bibcode").iterrows()) or "no full-text hits for any alias"
    if len(holes): hit_txt += f" (HOLE for {len(holes)} alias queries)"
    gf = f"GF21 parallax {r.Plx} mas" + (f", H-atmosphere Teff {r.TeffH:.0f} K, {r.MassH:.2f} Msun" if pd.notna(r.TeffH) else ", H-atmosphere fit unavailable (composite WD+M colours)")
    alias_note = f" The 1-day alias of the top peak is the second-highest peak; the alias family is not resolved from ZTF alone." if r.f_top > 2 else ""
    klass = f"DESI DR1 {r.cls} white dwarf + M dwarf (Amorim+2026 class); G {r.G:.2f}; {gf}"
    extra = NOTES.get(g, "")
    if g in MORGAN: extra = (extra + "; " if extra else "") + f"Morgan+2012 list a separation-based orbital-period estimate of {MORGAN[g]} d (not a measured period)"
    if g in GAVRAS: extra = (extra + "; " if extra else "") + "Gavras+2023 list the star as a known variable without a period"
    status = f"candidate: new ZTF photometric period {r.P_h:.4f} h (reflection-effect signature: r/g semi-amplitude ratio {r.r_over_g:.2f}); no measured period in any catalogue" + (f"; {extra}" if extra else "")
    print(g, r.WDJname, f"P {r.P_h:.3f} h", "| ADS:", hit_txt[:90])
    if not os.path.exists(os.path.join(R, "docs", "object_journals", f"{g}.md")):
        run(["new", g, "--name", r.WDJname, "--klass", klass, "--status", status])
    run(["ledger", g, "--catalog", "ZTF DR light curve (IRSA, 1.5 arcsec, catflags 0, magerr < 0.25; joint g+r Lomb-Scargle 0.5-50 c/d, 1-day masks)",
         "--result", f"top peak f = {r.f_top:.5f} c/d (P {r.P_h:.4f} h), FAP {r.fap_top:.1e}; semi-amplitude g {r.A1_zg:.2f}%, r {r.A1_zr:.2f}% (r/g {r.r_over_g:.2f}); not in a frequency cluster; not a 1-day alias family member.{alias_note}",
         "--provenance", "docs/reports/pceb_ztf_2026_09_28/pceb_detections.csv"])
    run(["ledger", g, "--catalog", f"Per-star period gate: VizieR all-table cone 5 arcsec ({int(r.n_tables)} tables), Oliveira da Rosa+2024 by TIC, MWDD, SIMBAD",
         "--result", (f"period-like columns: {r.period_tables}" if isinstance(r.period_tables, str) and r.period_tables.strip() else "no period or frequency column in any matched table") + f"; MWDD: {r.mwdd}; SIMBAD: {r.simbad}" + (f"; {extra}" if extra else ""),
         "--provenance", "docs/reports/pceb_ztf_2026_09_28/pceb_gate.csv"])
    run(["ledger", g, "--catalog", f"ADS full-text search by alias ({', '.join(aliases)})", "--result", hit_txt, "--provenance", "docs/reports/pceb_ztf_2026_09_28/ads_hits.csv"])
    run(["ledger", g, "--catalog", "XMatch: GF21 (1.5 arcsec), VSX (5 arcsec)", "--result", gf + (f"; VSX {r.vsx_name} type {r.vsx_type} period {r.vsx_period}" if isinstance(r.vsx_name, str) else "; no VSX entry"),
         "--provenance", "docs/reports/pceb_ztf_2026_09_28/pceb_candidates_enriched.csv"])
    run(["entry", g, "--title", "DESI WD+M ZTF period search", "--did", "Blind ZTF period search of the DESI DR1 WD+M sample; per-star novelty gate; ADS alias search; GF21/VSX cross-match.",
         "--found", status, "--provenance", "docs/reports/pceb_ztf_2026_09_28/", "--status", "candidate"])

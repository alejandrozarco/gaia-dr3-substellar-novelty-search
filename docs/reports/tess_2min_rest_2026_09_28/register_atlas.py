"""Test every ATLAS result in <batchdir>/atlas at its TESS frequency with fold_at2.py (search within +-0.01 c/d of f, 2f and f/2;
false-alarm probability over that window). Corrected 2026-09-29: the first version folded at the exact single-sector TESS
frequency, which over a 10-year ATLAS baseline drifts by cycles and averaged real signals away (7 of 67 'flat' verdicts were wrong).
Detection = window FAP < 1e-4 in either band at f, 2f or f/2 -> printed as HIT for manual work. Flat cases: margin >= 3 ->
not attributable, else undetermined; journal.py register commands are printed. Skips gaia ids already in the register.
Usage: python register_atlas.py <batchdir>"""
import sys, os, re, subprocess, pandas as pd
S = os.path.dirname(os.path.abspath(__file__)); B = sys.argv[1]; R = "docs/reports"; P = sys.executable
c = pd.concat([pd.read_csv(f"{R}/{d}/candidates_retiered.csv", dtype={"gaia": str}).assign(src=d) for d in ("tess_2min_s70s106_2026_09_27", "tess_2min_rest_2026_09_28")] + [pd.read_csv(f"{R}/tess_2min_rest_2026_09_28/candidates_retiered_final_new.csv", dtype={"gaia": str}).assign(src="tess_2min_rest_2026_09_28")]).drop_duplicates("gaia").set_index("gaia")
reg = set(pd.read_csv("docs/object_journals/findings_register.csv", dtype=str).source_id) if not os.environ.get("IGNORE_REGISTER") else set()
NUM = r"([\d.eE+-]+)"
PAT = re.compile(r"  (\w): n (\d+)" + "".join(rf"; {lab}: best ([\d.]+) FAP {NUM} amp ([\d.]+)\+-([\d.]+) uJy \(([\d.]+)%\)" for lab in ("f", "2f", "f/2")))
for f in sorted(os.listdir(f"{B}/atlas")):
    g = f.replace(".txt", "")
    if g in reg or g not in c.index: continue
    r = c.loc[g]; out = subprocess.run([P, f"{S}/fold_at2.py", f"{B}/atlas/{f}", str(r.f), str(r.G)], capture_output=True, text=True).stdout
    bands = PAT.findall(out)
    if not bands: print("# NO PARSE", g, out[:200].replace("\n", " ")); continue
    # per band tuple: 0 band, 1 n, then for f: 2 best, 3 FAP, 4 amp, 5 err, 6 pct; 2f: 7-11; f/2: 12-16
    det = [b for b in bands if min(float(b[3]), float(b[8]), float(b[13])) < 1e-4]
    if det: print(f"# HIT {g} {r.WDJname} TESS f {r.f} amp {r.amp}: " + out.replace("\n", " | ")); continue
    lim = max(float(b[6]) * (1 + 2 * float(b[5]) / max(float(b[4]), 1e-6)) if float(b[4]) > 0 else 2 * float(b[5]) / (3631e6 * 10 ** (-0.4 * r.G)) * 100 for b in bands)
    margin = 100 * r.amp / lim if lim > 0 else 99
    txt = "; ".join(f"{b[0]} {b[6]}% at f, {b[11]}% at 2f, {b[16]}% at f/2 (window FAP {b[3]}/{b[8]}/{b[13]}; n {b[1]})" for b in bands)
    frac = f"; {100*r.crowdsap:.1f}% of the aperture flux is the target" if r.crowdsap < 0.05 else ""
    ns = len(str(r.sectors).split())
    cls = f"white dwarf (G {r.G:.2f}, TeffH {r.TeffH/1000:.1f} kK, {r.MassH:.2f} Msun) with a TESS 2-min aperture signal ({ns} sector{'s' if ns > 1 else ''}, CROWDSAP {r.crowdsap:.3f})"
    if margin >= 3: nov = f"TESS f = {r.f:.4f} c/d (P {r.P_h:.2f} h, PDCSAP semi-amplitude {100*r.amp:.1f}%{frac}) not attributable: ATLAS forced photometry at the star flat within +-0.01 c/d of f, 2f, f/2 ({txt}); margin {margin:.0f}x"; disp = "register (not attributable to the white dwarf)"
    else: nov = f"TESS f = {r.f:.4f} c/d (P {r.P_h:.2f} h, PDCSAP semi-amplitude {100*r.amp:.1f}%{frac}) undetermined: ATLAS flat within +-0.01 c/d but too shallow ({txt}); margin only {margin:.1f}x"; disp = "register (undetermined: ATLAS too shallow; DR4 test)"
    print(f'{P} scripts/journal/journal.py register {g} --name {r.WDJname} --lane tess_2min_reopened --classification "{cls}" --novelty "{nov}" --disposition "{disp}" --journal no --provenance "docs/reports/{r.src}/" --date "$(date -u +%Y-%m-%d)" >/dev/null')

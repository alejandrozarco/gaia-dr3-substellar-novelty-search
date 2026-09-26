# Extract object identifiers from arXiv sources of recent CV papers (not (yet) in VizieR) so they can be used as prior-art
# gates: 15-19 digit numbers (Gaia DR2/DR3 source_ids), full J-names (Jhhmmss.s+ddmmss) -> J2000 coordinates, eRASS names.
# Output: cat/arxiv_ids.csv (paper, kind, token, ra, dec). Short names (Jhhmm+ddmm) are kept as tokens only (too coarse).
import re, os, glob, csv, sys
import numpy as np

PAPERS = {"2607.27960": "Brink+2026 eROSITA CVs in SDSS-V DR20", "2607.22836": "Inight+2026 DESI 1000 CVs",
          "2607.28066": "Schwope+2026 eRASS1 new CVs", "2607.27855": "Hernandez-Diaz+2026 eROSITA period bouncers",
          "2607.28736": "Galiullin+2026 Gaia XP GEM CVs", "2608.04179": "Galiullin+2026 high-state AM CVn",
          "2609.21150": "Mendoza+2026 COPAS I P<83min", "2607.08727": "Kepler+2026 TESS CV periods",
          "2505.10337": "Schwope+2025 PolarCat", "2603.03539": "Dag+2026 TESS CV periods",
          "2509.17216": "Munoz-Giraldo+2026 eROSITA period bouncers", "2606.09627": "Hernandez-Diaz+2026 Balmer decrements",
          "2510.09165": "Hernandez-Diaz+2025 polars TESS", "2412.15153": "van Roestel+2025 cyclotron MWD PCEBs",
          "2505.10535": "Green+2025 ultracompact catalogue", "2505.10478": "Liu+2025 eRASS1 accreting binaries",
          "2503.12410": "Zhao+2025 LAMOST accreting binaries", "2412.06882": "Canbay+2025 CV kinematics",
          "2608.25439": "Hakala+2026 pre-polars II", "2601.02287": "Zhao+2026 high-velocity X-ray sources",
          "2504.10794": "Wang+2025 eROSITA-DE CV candidates", "2408.16053": "Rodriguez+2025 eROSITA CVs volume-limited"}

jfull = re.compile(r"J(\d{2})(\d{2})(\d{2}(?:\.\d+)?)\s*(?:\$?)([+\-−]|--|\$-\$|\$\+\$|\\textminus|\{-\})\s*(?:\$?)(\d{2})(\d{2})(\d{2}(?:\.\d+)?)")
gid = re.compile(r"(?<![\d.])(\d{15,19})(?![\d.])")
rows = []
for pid, lab in PAPERS.items():
    d = f"arx/x_{pid}"
    if not os.path.isdir(d):
        rows.append(dict(paper=pid, label=lab, kind="HOLE", token="source not downloaded/extracted", ra="", dec=""))
        continue
    files = [f for f in glob.glob(d + "/**/*", recursive=True) if os.path.isfile(f) and f.lower().endswith((".tex", ".csv", ".txt", ".dat", ".tab", ".bbl", ".mrt"))]
    seen = set(); nfile = len(files)
    for f in files:
        try:
            txt = open(f, errors="ignore").read()
        except Exception:
            continue
        # also catch names in figure file names
        for m in gid.finditer(txt):
            t = m.group(1)
            if t in seen: continue
            seen.add(t); rows.append(dict(paper=pid, label=lab, kind="gaia_like_id", token=t, ra="", dec=""))
        for m in jfull.finditer(txt):
            h, mi, s, sg, dd, dm, ds = m.groups()
            sign = -1 if sg in ("-", "−", "--", "$-$", "\\textminus", "{-}") else 1
            ra = 15 * (int(h) + int(mi) / 60 + float(s) / 3600); de = sign * (int(dd) + int(dm) / 60 + float(ds) / 3600)
            key = f"J{h}{mi}{s}{'+' if sign > 0 else '-'}{dd}{dm}{ds}"
            if key in seen: continue
            seen.add(key); rows.append(dict(paper=pid, label=lab, kind="Jname", token=key, ra=f"{ra:.5f}", dec=f"{de:.5f}"))
    # figure file names (e.g. Gaia ids in png names)
    for f in glob.glob(d + "/**/*", recursive=True):
        b = os.path.basename(f)
        for m in gid.finditer(b):
            t = m.group(1)
            if t not in seen:
                seen.add(t); rows.append(dict(paper=pid, label=lab, kind="gaia_like_id(fname)", token=t, ra="", dec=""))
        for m in jfull.finditer(b):
            h, mi, s, sg, dd, dm, ds = m.groups()
            sign = -1 if sg in ("-", "−", "--") else 1
            ra = 15 * (int(h) + int(mi) / 60 + float(s) / 3600); de = sign * (int(dd) + int(dm) / 60 + float(ds) / 3600)
            key = f"J{h}{mi}{s}{'+' if sign > 0 else '-'}{dd}{dm}{ds}"
            if key not in seen:
                seen.add(key); rows.append(dict(paper=pid, label=lab, kind="Jname(fname)", token=key, ra=f"{ra:.5f}", dec=f"{de:.5f}"))
    n_id = sum(1 for r in rows if r["paper"] == pid and r["kind"].startswith("gaia")); n_j = sum(1 for r in rows if r["paper"] == pid and r["kind"].startswith("Jname"))
    print(f"{pid} {lab:45s} files={nfile:3d} gaia-like={n_id:5d} Jnames={n_j:5d}")
w = csv.DictWriter(open("cat/arxiv_ids.csv", "w"), fieldnames=["paper", "label", "kind", "token", "ra", "dec"]); w.writeheader(); w.writerows(rows)
print("total rows", len(rows))

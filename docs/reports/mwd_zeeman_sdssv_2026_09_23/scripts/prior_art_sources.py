# Grep the arXiv source text of 18 white-dwarf catalogue papers for every candidate: Gaia DR3 id, short names Jhhmm+ddmm (also with
# LaTeX $+$), and hhmmss.s / hhmmss.ss strings from the 2016.0, 2006.0 and 2000.0 positions. Positive controls (known magnetic stars
# in the same SnowWhite sample) are included to show each full table is present in the source.
import json, glob, requests, numpy as np
from astropy.coordinates import SkyCoord; import astropy.units as u
papers = {"Kilic2020": "2006.00323", "Kilic2025": "2412.04611", "Caron2023": "2212.08014", "Jewett2024": "2407.04827", "Moss2025": "2507.06102",
          "Amorim2023": "2301.08862", "Hardy2023": "2301.06596", "Kulebi2009": "0907.2372", "Amorim2026a": "2603.20487", "Amorim2026b": "2607.00430",
          "Swan2026": "2609.04314", "Yu2026": "2603.11004", "GarciaZamora2026": "2605.16493", "Kawka2007": "astro-ph_0609273",
          "KawkaVennes2012": "1206.5113", "Koester2009SPY": "0908.2322", "Napiwotzki2020SPY": "1906.10977", "Vincent2020": "2010.02376"}
tex = {k: "\n".join(open(f, errors="ignore").read() for f in glob.glob(f"arx/{a}/*") if f.endswith((".tex", ".txt", ".dat", ".csv"))) for k, a in papers.items()}
ids = [l.split()[0] for f in ("vis_list.txt", "vis_list2.txt", "ctrl_list.txt") for l in open(f) if l.strip() and not l.startswith("#")]
q = "SELECT source_id, ra, dec, pmra, pmdec FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")"
g = requests.get("https://gea.esac.esa.int/tap-server/tap/sync", params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=120).json()
C = {str(r[0]): r[1:] for r in g["data"]}; out = {}
for gid in ids:
    ra, dec, pmra, pmdec = C[gid]; pats = {gid}
    for dt in (0, -10, -16):
        r2 = ra + pmra * dt / 3.6e6 / np.cos(np.radians(dec)); d2 = dec + pmdec * dt / 3.6e6; s = SkyCoord(r2 * u.deg, d2 * u.deg)
        h, m, sec = s.ra.hms; dd, dm, ds = np.abs(s.dec.dms); sg = "+" if d2 >= 0 else "-"
        pats |= {f"J{int(h):02d}{int(m):02d}{sg}{int(dd):02d}{int(abs(dm)):02d}", f"J{int(h):02d}{int(m):02d}${sg}${int(dd):02d}{int(abs(dm)):02d}",
                 f"{int(h):02d}{int(m):02d}{int(sec):02d}.{int((sec % 1) * 100):02d}", f"{int(h):02d}{int(m):02d}{int(sec):02d}.{int((sec % 1) * 10):01d}"}
    out[gid] = sorted({k for k, t in tex.items() for p in pats if len(p) >= 7 and p in t})
json.dump(dict(papers=papers, chars={k: len(t) for k, t in tex.items()}, matches=out), open("paper_source_matches.json", "w"), indent=1)
for gid in ids: print(gid, "CTRL" if gid in [l.strip() for l in open("ctrl_list.txt")] else "    ", out[gid])

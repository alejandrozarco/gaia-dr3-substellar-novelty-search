"""Orphaned-anomaly harvester, stage 1: download arXiv sources for the corpus (corpus.csv from ADS: refereed astronomy papers whose
full text contains a per-object notes section), extract the notes section(s) from the LaTeX, and split them into per-object
paragraphs. Polite to arXiv: one e-print request every 4 s, resumable (skips sources already on disk).
Writes notes/<arxiv>.json = [{"head": <paragraph label>, "text": <plain text>}, ...] and a summary line per paper in harvest.log.
Usage: python harvest.py [--limit N] [--years 2015-2026]"""
import os, re, io, sys, json, time, tarfile, gzip, argparse, requests, pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--years", default="2000-2026"); ap.add_argument("--reextract", action="store_true"); A = ap.parse_args()
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(H, "src"); NOTES = os.path.join(H, "notes"); os.makedirs(SRC, exist_ok=True); os.makedirs(NOTES, exist_ok=True)
y0, y1 = map(int, A.years.split("-"))
D = pd.read_csv(os.path.join(H, "corpus.csv"), dtype=str); D = D[(D.arxiv != "") & D.arxiv.notna()]; D = D[D.year.astype(int).between(y0, y1)]
if A.limit: D = D.head(A.limit)
HEAD = re.compile(r"\\((?:sub)*)section\*?\{[^}]*(?:individual|notes on|comments on|remarks on)[^}]*\}", re.I)
def next_re(level):  # stop only at a heading of the same or a higher level than the notes heading
    lv = {"": r"\\section", "sub": r"\\(?:sub)?section", "subsub": r"\\(?:sub){0,2}section"}.get(level, r"\\section")
    return re.compile(lv + r"\*?\{|\\begin\{thebibliography\}|\\bibliography\{|\\end\{document\}")
def detex(s):
    s = re.sub(r"%.*", "", s); s = re.sub(r"\\(?:object|textit|textbf|emph|text|mbox|nodata)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{[^}]*\}", "[ref]", s); s = re.sub(r"\\ref\{[^}]*\}|\\label\{[^}]*\}", "", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s); s = s.replace("\\,", " ").replace("~", " ").replace("--", "-").replace("\\&", "&")
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s); s = re.sub(r"[{}]", "", s); return re.sub(r"\s+", " ", s).strip()
def split_paras(sec):
    parts = re.split(r"(\\paragraph\*?\{[^}]*\}|\\(?:sub)+section\*?\{[^}]*\}|\\item\s*(?:\\textbf\{[^}]*\}|\\emph\{[^}]*\}|\{\\bf [^}]*\})?)", sec)
    out, head = [], ""
    for k, p in enumerate(parts):
        m = re.match(r"\\(?:paragraph|(?:sub)+section)\*?\{([^}]*)\}|\\item\s*(?:\\textbf\{([^}]*)\}|\\emph\{([^}]*)\}|\{\\bf ([^}]*)\})?", p)
        if m: head = detex(next((g for g in m.groups() if g), "")); continue
        t = detex(p)
        if len(t) > 80: out.append({"head": head, "text": t[:6000]})
    if not out:
        for blk in re.split(r"\n\s*\n", sec):
            t = detex(blk)
            if len(t) > 120: out.append({"head": "", "text": t[:6000]})
    return out
def fetch(arx):
    p = os.path.join(SRC, arx.replace("/", "_") + ".tar")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    for k in range(3):
        try:
            r = requests.get(f"https://arxiv.org/e-print/{arx}", timeout=120, headers={"User-Agent": "orphaned-anomalies-harvester (contact via ADS account)"})
            if r.status_code == 200 and len(r.content) > 1000: open(p, "wb").write(r.content); return p
            if r.status_code in (403, 429): time.sleep(60)
        except Exception: time.sleep(20)
    return None
def texts(p):
    raw = open(p, "rb").read(); out = []
    try:
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            for m in t.getmembers():
                if m.name.lower().endswith(".tex") and m.size < 5_000_000: out.append(t.extractfile(m).read().decode("utf-8", "ignore"))
    except tarfile.TarError:
        try: out.append(gzip.decompress(raw).decode("utf-8", "ignore"))
        except Exception: out.append(raw.decode("utf-8", "ignore"))
    return out
log = open(os.path.join(H, "harvest.log"), "a")
for n, (_, r) in enumerate(D.iterrows()):
    arx = r.arxiv; outp = os.path.join(NOTES, arx.replace("/", "_") + ".json")
    if os.path.exists(outp) and not A.reextract: continue
    p = fetch(arx)
    if p is None: print(r.bibcode, arx, "HOLE download", file=log, flush=True); time.sleep(4); continue
    paras = []
    for tx in texts(p):
        for m in HEAD.finditer(tx):
            rest = tx[m.end():]; e = next_re(m.group(1)).search(rest); sec = rest[:e.start()] if e else rest[:60000]
            paras += split_paras(sec)
    json.dump({"bibcode": r.bibcode, "arxiv": arx, "year": r.year, "title": r.title, "paras": paras}, open(outp, "w"))
    print(r.bibcode, arx, f"{len(paras)} paragraphs", file=log, flush=True)
    if n % 25 == 0: print(n, r.bibcode, len(paras), flush=True)
    if not (A.reextract and os.path.exists(os.path.join(SRC, arx.replace("/", "_") + ".tar"))): time.sleep(4)
print("HARVEST-DONE", file=log, flush=True)

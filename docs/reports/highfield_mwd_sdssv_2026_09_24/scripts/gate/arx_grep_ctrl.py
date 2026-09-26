# grep every downloaded arXiv source tree under /tmp/mwd/arx (incl. the lane-required Amorim+2023 2301.08862, Hardy+2023
# 2301.06596, Kulebi+2009 0907.2372, Amorim+2026 2603.20487, 2607.00430) for Gaia DR3/DR2 ids and short J-names
# (hhmm[+-]ddmm and hhmmss[+-]ddmmss, any LaTeX minus form), plus file names (DESI-targetid-named figures).
import os, re, json, sys
A = json.load(open("ads_ctrl_aliases.json")); root = "/tmp/mwd/arx"
files = []
for dp, dn, fn in os.walk(root):
    for f in fn: files.append(os.path.join(dp, f))
texts = {}
for f in files:
    try:
        b = open(f, "rb").read()
        if b[:4] == b"%PDF" or f.endswith((".png", ".jpg", ".jpeg", ".eps", ".pdf", ".gz")): texts[f] = ""
        else: texts[f] = b.decode("latin-1")
    except Exception: texts[f] = ""
print("files scanned:", len(files), "text files:", sum(1 for t in texts.values() if t))
res = {}
for g, v in A.items():
    pats = [re.escape(g)]
    for al in v["aliases"]:
        m = re.match(r"Gaia DR[23] (\d+)", al)
        if m: pats.append(re.escape(m.group(1)))
        m = re.match(r"J(\d{4})([+-])(\d{4})$", al)
        if m: pats.append(m.group(1) + r"(?:\.\d+)?\s*(?:\$?[-+−]\$?|\\?\$?-\$?|--|\{-\}|\+)\s*" + m.group(3))
        m = re.match(r"J(\d{6})([+-])(\d{6})$", al)
        if m: pats.append(m.group(1)[:6] + r"(?:\.\d+)?\s*(?:\$?[-+−]\$?|\\?\$?-\$?|--|\{-\}|\+)\s*" + m.group(3)[:5])
    rx = re.compile("|".join(pats))
    hits = []
    for f, t in texts.items():
        if rx.search(os.path.basename(f)): hits.append((f, "FILENAME"))
        if t:
            for mm in rx.finditer(t):
                hits.append((f, t[max(0, mm.start() - 60):mm.end() + 60].replace("\n", " ")))
    res[g] = hits
    print(g, "hits:", len(hits), [(h[0].replace(root + "/", ""), h[1][:100]) for h in hits[:5]])
json.dump(res, open("arx_grep_ctrl.json", "w"), indent=1)

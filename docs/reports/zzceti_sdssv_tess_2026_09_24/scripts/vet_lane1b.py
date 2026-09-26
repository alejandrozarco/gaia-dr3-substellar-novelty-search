# Vet lane-1 light-curve results: (1) per sector, find frequencies (0.01 c/d bins) that top-3 peaks of >= 3 different targets share
# -> instrumental list; (2) candidates = light curves whose best non-instrumental peak has S/N >= 5 and Baluev FAP < 1e-3;
# (3) per target: combine sectors (count detections, frequencies within 1% of each other); (4) front-filter against the 882-star
# known pulsator list (magpuls lane: SIMBAD Pu*, VSX ZZ*, MWDD periods, Romero+2019/2022/2025, Vincent+2020, Guidry+2021, ...),
# noting its NOV (non-variable) entries separately. Output lane1b_candidates.csv.
import json, csv, collections, numpy as np
R = [json.loads(l) for l in open("lane1b_lc_results.jsonl")]
ok = [r for r in R if r["status"] == "OK"]
print("light curves:", len(R), "OK:", len(ok), "holes/other:", collections.Counter(r["status"] for r in R if r["status"] != "OK"))
bins = collections.defaultdict(set)
for r in ok:
    for f, a, sn in r["peaks"][:3]:
        if sn >= 4: bins[(r["sector"], round(f, 2))].add(r["tic"])
instr = {k for k, v in bins.items() if len(v) >= 3}
print("instrumental (sector, freq) bins shared by >= 3 targets:", sorted(instr)[:30])
def is_instr(sec, f): return any((sec, round(f + d, 2)) in instr for d in (-0.01, 0, 0.01))
known = {r["gaia_dr3"]: r for r in csv.DictReader(open("/tmp/fanout/magpuls/lists/puls_master.csv"))}
cand = collections.defaultdict(list)
for r in ok:
    good = [(f, a, sn) for f, a, sn in r["peaks"] if not is_instr(r["sector"], f)]
    if good and good[0][2] >= 5 and r["fap_top"] < 1e-3:
        cand[r["gaia"]].append(dict(sector=r["sector"], freq=good[0][0], P_s=86400 / good[0][0], amp_ppt=good[0][1], sn=good[0][2], crowdsap=r["crowdsap"], G=r["G"], lane=r["lane"], tic=r["tic"],
                                    others=[(round(f, 3), round(sn, 1)) for f, a, sn in good[1:4] if sn >= 4.5]))
nsec = collections.Counter(r["gaia"] for r in ok)
rows = []
for g, dets in cand.items():
    k = known.get(g); status = "NEW" if k is None else ("KNOWN_NOV_OR_CANDIDATE" if (k.get("claim") or "").lower().startswith(("nov", "cand")) else "KNOWN")
    rows.append(dict(gaia=g, tic=dets[0]["tic"], lane=dets[0]["lane"], G=dets[0]["G"], n_sectors_analysed=nsec[g], n_sectors_detected=len(dets),
                     best_sn=max(d["sn"] for d in dets), periods_s=";".join(f"S{d['sector']}:{d['P_s']:.1f}s/{d['amp_ppt']:.1f}ppt/SN{d['sn']:.1f}" for d in sorted(dets, key=lambda d: d["sector"])),
                     crowdsap_min=min((d["crowdsap"] or 1) for d in dets), known_status=status, known_names=(k or {}).get("names", "")[:80], known_claim=(k or {}).get("claim", "")[:80]))
rows.sort(key=lambda r: (r["known_status"] != "NEW", -r["best_sn"]))
with open("lane1b_candidates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["gaia"]); w.writeheader(); w.writerows(rows)
print(f"targets with >= 1 detection (S/N >= 5, FAP < 1e-3, non-instrumental): {len(rows)}; NEW: {sum(r['known_status']=='NEW' for r in rows)}; known: {sum(r['known_status']!='NEW' for r in rows)}")
for r in rows[:40]: print(f"  {r['known_status'][:5]} {r['lane']} G {r['G']:.2f} Gaia {r['gaia']} TIC {r['tic']} det {r['n_sectors_detected']}/{r['n_sectors_analysed']} bestSN {r['best_sn']:.1f} crowd {r['crowdsap_min']} | {r['periods_s'][:150]} | {r['known_names'][:40]}")

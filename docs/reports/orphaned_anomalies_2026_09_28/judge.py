"""Orphaned-anomaly harvester, stage 2: the System One model (Jev) reads every per-object paragraph in notes/*.json and returns, per
paragraph, the probability that the object is described as unexplained/peculiar, that follow-up is called for, that the text itself
resolves it, a weirdness level (0-3) and a broad object kind. Up to 8 paragraphs of one paper share one request. Resumable: papers
already in judged.csv are skipped. Usage: python judge.py [--limit N]"""
import os, sys, json, glob, time, argparse, pandas as pd, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); A = ap.parse_args()
os.environ["TYPESAFE_API_KEY"] = open(os.path.expanduser("~/.config/typesafe/token")).read().strip()
from typesafe_sdk import TypeSafeClient
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "judged.csv")
done = set(pd.read_csv(OUT, dtype=str).bibcode) if os.path.exists(OUT) else set()
KIND = {"star_or_stellar_binary": "a star, stellar binary, white dwarf, brown dwarf or their variability",
        "compact_object_candidate": "a black hole, neutron star, or accreting/dark compact companion candidate",
        "galaxy_or_agn": "a galaxy, quasar, AGN or cluster", "transient_or_explosive": "a supernova, GRB, nova, tidal disruption or other transient",
        "solar_system_or_exoplanet": "a solar-system body or an exoplanet", "unclear": "cannot tell from the text"}
rows = []; t0 = time.time(); n = 0
files = sorted(glob.glob(os.path.join(H, "notes", "*.json")))
with TypeSafeClient() as client:
    for f in files:
        P = json.load(open(f))
        if P["bibcode"] in done or not P["paras"]: continue
        paras = [p for p in P["paras"] if len(p["text"]) > 150][:40]
        for b in range(0, len(paras), 8):
            chunk = paras[b:b + 8]
            state = {"paper": {"title": P["title"], "year": P["year"]}, "notes": [{"label": p["head"], "text": p["text"][:3500]} for p in chunk]}
            qs = {}
            for k in range(len(chunk)):
                qs[f"unexplained_{k}"] = {"type": "noul", "instructions": f"In `notes[{k}].text`, do the authors describe the object's nature, classification or an observed property as unexplained, peculiar, anomalous, puzzling, unusual or not understood?", "criteria": {"true": "the text explicitly flags something unexplained or unusual about the object", "false": "the object is described as understood or ordinary"}}
                qs[f"followup_{k}"] = {"type": "noul", "instructions": f"Does `notes[{k}].text` state or clearly imply that further observations, data or analysis are needed to settle the object's nature?", "criteria": {"true": "follow-up is stated as needed or the question is left open for future work", "false": "no follow-up is called for"}}
                qs[f"resolved_{k}"] = {"type": "noul", "instructions": f"Does `notes[{k}].text` itself resolve the object's peculiarity, e.g. by explaining it, attributing it to an artefact or contamination, or classifying the object confidently?", "criteria": {"true": "the text settles the matter", "false": "the matter is left open or no peculiarity is discussed"}}
                qs[f"physical_{k}"] = {"type": "noul", "instructions": f"In `notes[{k}].text`, does the unexplained or unusual aspect concern the object's own physical nature or an observed property of the object (its spectrum, light curve, kinematics, composition, environment), rather than a difficulty of the authors' analysis, fitting, data quality or instrumentation?", "criteria": {"true": "the object itself is physically peculiar or its observed property is unexplained", "false": "the difficulty is methodological (fit convergence, calibration, low signal, model limitations) or there is nothing unusual"}}
                qs[f"weird_{k}"] = {"type": "score", "instructions": f"How unusual is the object in `notes[{k}].text` according to the authors' own words?", "criteria": ["ordinary object, nothing unusual noted", "minor peculiarity or uncertainty noted", "clearly unusual property that the authors cannot explain", "exceptional case, possibly a new kind of object"]}
                qs[f"kind_{k}"] = {"type": "choice", "instructions": f"What kind of object is `notes[{k}].text` about?", "criteria": KIND}
            try:
                a = client.system_one(state=state, questions=qs)
                for k, p in enumerate(chunk):
                    rows.append(dict(bibcode=P["bibcode"], arxiv=P["arxiv"], year=P["year"], title=P["title"][:100], head=p["head"][:80],
                                     unexplained=round(a.nouls[f"unexplained_{k}"].noul, 3), followup=round(a.nouls[f"followup_{k}"].noul, 3), resolved=round(a.nouls[f"resolved_{k}"].noul, 3), physical=round(a.nouls[f"physical_{k}"].noul, 3),
                                     weird=round(float(a.scores[f"weird_{k}"].score), 2), kind=a.choices[f"kind_{k}"].choice, text=p["text"][:400]))
            except Exception as ex:
                rows.append(dict(bibcode=P["bibcode"], arxiv=P["arxiv"], year=P["year"], title=P["title"][:100], head="", unexplained=np.nan, followup=np.nan, resolved=np.nan, physical=np.nan, weird=np.nan, kind=f"ERR {type(ex).__name__}", text=""))
            time.sleep(0.2)
        n += 1
        if n % 20 == 0:
            print(n, "papers", f"{time.time() - t0:.0f}s", flush=True)
            pd.concat([pd.read_csv(OUT) if os.path.exists(OUT) else pd.DataFrame(), pd.DataFrame(rows)]).to_csv(OUT, index=False); rows = []
        if A.limit and n >= A.limit: break
if rows: pd.concat([pd.read_csv(OUT) if os.path.exists(OUT) else pd.DataFrame(), pd.DataFrame(rows)]).to_csv(OUT, index=False)
J = pd.read_csv(OUT); print("judged", len(J), "paragraphs from", J.bibcode.nunique(), "papers;", "flagged (unexplained>0.6 & followup>0.5 & resolved<0.4 & physical>0.6):", int(((J.unexplained > 0.6) & (J.followup > 0.5) & (J.resolved < 0.4) & (J.physical > 0.6)).sum()))

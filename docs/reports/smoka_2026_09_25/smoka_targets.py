"""Search SMOKA (public, session-based, instrument-FOV 'auto', 1 arcmin) at the position of every object in our current lanes."""
import os
import re, glob, pandas as pd, pyvo, json
from astropy.coordinates import SkyCoord
import astropy.units as u
from smoka_sess import *
ids = {}
T = os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/tables/")
for f, lab in (("magnetic_zeeman.csv","zeeman"),("carbon_white_dwarfs.csv","carbon"),("zz_ceti_objects.csv","zzceti"),("balmer_emission.csv","balmer"),("eclipsing_4731701084150029824.csv","eclipse"),("periodic_white_dwarfs.csv","periodic")):
    for g in pd.read_csv(T + f, dtype={"gaia_dr3": str}).gaia_dr3: ids.setdefault(g, lab)
extra = {"6021870154194477312":"periodic J1618","2076678981825545088":"carbon cand","4377432592229753472":"carbon cand",
         "1810475401285228928":"puls cand","6370863945235959680":"puls cand","6123269216744427008":"puls cand","4693541467955966848":"puls cand",
         "6121651418527918976":"puls cand","2317319612801004416":"puls cand","6869592141738355968":"puls cand","5386114565161537920":"puls cand",
         "5346312514819760896":"puls cand","4670655408301574144":"puls cand","5356171977349246464":"puls cand",
         "6492083311194727168":"zz lane1","6558472750993181568":"zz lane1","2908195134345338496":"zz lane1","4729763229265811328":"zz lane1","6472153670805656832":"zz lane1",
         "3161546596480983040":"Object B","4792264314911712512":"hot DQ cand","4883191104733786496":"open lead","1980205739970324224":"J2159"}
for k, v in extra.items(): ids.setdefault(k, v)
tap = pyvo.dal.TAPService("https://gea.esac.esa.int/tap-server/tap")
g = tap.search(f"select source_id, ra, dec, pmra, pmdec, phot_g_mean_mag from gaiadr3.gaia_source where source_id in ({','.join(ids)})").to_table().to_pandas()
s = session(); rows = []
for r in g.itertuples():
    c = SkyCoord(r.ra * u.deg, r.dec * u.deg)
    res = search(s, [("longitudeC", c.ra.to_string(u.hour, sep=":", precision=2)), ("latitudeC", c.dec.to_string(sep=":", precision=1, alwayssign=True)), ("radius", "1.0")])
    t = text(res); m = re.search(r"(\d+) frames are found", t)
    summ = re.search(r"Instrument Number of frames (.*?) Thumbnail", t)
    nz = " ".join(f"{a}:{b}" for a, b in re.findall(r"([A-Z]{3}) (\d+)", summ.group(1)) if b != "0") if summ else ""
    status = m.group(1) if m else ("0" if "No matching" in t else "ERROR")
    rows.append(dict(gaia=str(r.source_id), lane=ids[str(r.source_id)], G=round(r.phot_g_mean_mag, 2), ra=r.ra, dec=r.dec, n_frames=status, instruments=nz))
    if m: open(f"tgt_{r.source_id}.html", "w").write(res.text)
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("smoka_targets.csv", index=False); print("DONE", len(rows))

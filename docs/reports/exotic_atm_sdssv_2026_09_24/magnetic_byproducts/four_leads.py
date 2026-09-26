import os
# Coadd and per-visit Zeeman fits (public-repo zeeman_split.measure) for the four remaining magnetic by-products with inconsistent
# H-alpha/H-beta B_split in the coadd.
import sys; sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
from zeeman_split import measure
from sdssv import visits
for g, sid in [("2246631460497465472", "68942299"), ("3987356721738829184", "80729520"), ("6915353300288749440", "114797603"), ("4867935694432066304", "93212597")]:
    vs = visits(sid)
    for spec in ["coadd"] + [str(v["mjd"]) for v in vs]:
        try:
            r = measure(sid, spec)
            print(f"{g} {spec:>6s} S/N {r['snr']:5.1f}: Ha {r['B_split_Ha_MG']:.2f}+-{r['e_B_split_Ha_MG']:.2f} (shift {r['Ha_shift_A']:+.1f}, asym {r['Ha_asym_A']:+.1f}) | Hb {r['B_split_Hb_MG']:.2f}+-{r['e_B_split_Hb_MG']:.2f} (shift {r['Hb_shift_A']:+.1f}, asym {r['Hb_asym_A']:+.1f})", flush=True)
        except Exception as e: print(g, spec, "ERR", str(e)[:100], flush=True)

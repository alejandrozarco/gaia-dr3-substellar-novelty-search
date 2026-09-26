import os
# Generate VSX revision drafts for the four periodic white dwarfs from the public table (local notes only; the user files them).
import pandas as pd
t = pd.read_csv(os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/tables/periodic_white_dwarfs.csv"), dtype={"gaia_dr3": str})
S = pd.read_csv(os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/data/periodic_white_dwarfs_sources.csv"), dtype={"gaia_dr3": str}).set_index("gaia_dr3")
VSX = {"2883364038621038208": (4419226, "18.13-18.30 G"), "6456720612064924928": (7911266, "17.86-18.00 G"), "178685757799822080": (3015482, "18.06-18.21 G"), "2888030331609338240": (4338178, "17.68-17.78 G"), "3496637913394359680": (4990120, "17.98-18.09 G")}
GF = {"2883364038621038208": "8,373 K, log g 8.26, 0.76 Msun", "6456720612064924928": "8,484 K, log g 8.30, 0.79 Msun", "178685757799822080": "8,890 K, log g 8.28, 0.77 Msun", "437628614520520320": "8,307 K, log g 8.16, 0.69 Msun", "2888030331609338240": "9,691 K, log g 7.95, 0.57 Msun", "3496637913394359680": "7,874 K, log g 8.09, 0.65 Msun"}
out = ["# VSX revision drafts: white dwarfs with new periods (Gaia DR3 auto-ingested VSX entries without periods)", "",
       "Status: DRAFT, NOT FILED (the user files them through the star's VSX page, logged in). Drafted 2026-09-24.", "",
       "All exist in VSX as 'Gaia DR3 <id>' entries of type WD (auto-ingested from the Gaia DR3 variability classifier) with no period.",
       "A revision adds the period, epoch and remarks and keeps type WD, which VSX defines as 'binary systems with at least one white-dwarf",
       "component, or a single rotating white dwarf'. Alternative: ROT: (spotted white dwarf, uncertain). Reference option: the public repository",
       "https://github.com/alejandrozarco/sdssv-white-dwarfs-2026 (table tables/periodic_white_dwarfs.csv, figure figures/periodic_white_dwarfs.png).",
       "Citing it links your VSX identity to that account; the remarks are self-contained without it.", ""]
for gid, (oid, rng) in VSX.items():
    s = S.loc[gid]; g = t[t.gaia_dr3 == gid]; r = g[g.dataset == s.ground].iloc[0]; gg = g[g.dataset.str.startswith("Gaia")].iloc[0]
    P = 1 / r.frequency_cd; eP = r.e_frequency_cd / r.frequency_cd ** 2
    tess = g[g.dataset.str.startswith("TESS")]
    tess_txt = ("; TESS " + ", ".join(f"S{x.dataset.split()[1][1:]} (highest peak {x.peak_cd:.4f} c/d, FAP {x.peak_fap:.1g}, CROWDSAP {x.dataset.split('CROWDSAP ')[1].rstrip(')')})" for _, x in tess.iterrows())) if len(tess) else ""
    band = "c and o" if s.ground == "ATLAS" else "g and r"
    out += [f"## Gaia DR3 {gid} (VSX OID {oid}) = {s['name']}", "",
            f"| field | current | proposed |", "|---|---|---|",
            f"| Type | WD | WD (unchanged) |",
            f"| Period | none | **{P:.7f} d** (± {eP:.1e}) = {24 * P:.4f} h |",
            f"| Epoch (max) | none | **BJD_TDB {r.t_max_bjd:.4f}** (± {r.e_t_max_min / 1440:.4f}) |",
            f"| Range | {rng} | unchanged; {s.ground} semi-amplitude {100 * r.amplitude_frac:.1f} % |", "",
            f"Remarks: Period from {s.ground} ({band}, {int(r.n)} points, BJD {r.bjd_first:.0f}-{r.bjd_last:.0f}): highest peak 0.05-50 c/d at "
            f"{r.peak_cd:.5f} c/d (Baluev FAP {r.peak_fap:.1g}); sinusoid semi-amplitude {100 * r.amplitude_frac:.1f} ± {100 * r.e_amplitude_frac:.1f} %, first harmonic "
            f"{100 * r.harmonic2_frac:.1f} %. Same frequency as the Gaia DR3 GLS frequency ({s.gaia_gls_freq_cd:.5f} c/d, FAP {s.gaia_gls_fap:.1g}; Gaia G semi-amplitude "
            f"{100 * gg.amplitude_frac:.1f} % at the {s.ground} frequency){tess_txt}. Gentile Fusillo et al. (2021) H-atmosphere fit: {GF[gid]}; parallax "
            f"{s.parallax_mas:.2f} mas; Gaia XP spectral class DA (Vincent et al. 2024).", ""]
out += ["## Gaia DR3 437628614520520320 (VSX OID 2851498) = WDJ025503.24+475833.96", "", "PENDING: ZTF (367 points) gives 0.19834 c/d (P = 5.042 d, FAP 7e-46, 4.6 %), matching Gaia (0.19845 c/d), but the IRSA download for the public table failed tonight, so no epoch yet. Draft once the light curve is saved.", ""]
open(os.path.expanduser("~/claude_projects/gaia_local_notes/2026-09-24/vsx_revisions_periodic_white_dwarfs.md"), "w").write("\n".join(out)); print("written")

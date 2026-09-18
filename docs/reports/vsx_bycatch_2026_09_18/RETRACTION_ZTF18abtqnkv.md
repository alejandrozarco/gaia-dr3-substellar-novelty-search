# ZTF18abtqnkv — NOT SUBMITTABLE (retracted from the VSX queue, 2026-09-18)

Recorded on 2026-08-13 as an "uncatalogued low-amplitude variable, DR ptp ~0.8–0.9 mag in
gri over 8 yr". **Re-derivation from ZTF DR photometry does not support a variability
claim.**

| test | result |
|---|---|
| raw min–max (the basis of the original claim) | 0.94 (zg) / 0.85 (zr) / 0.82 (zi) mag |
| **robust range (95th–5th pct)** | **0.076 / 0.061 / 0.076 mag** |
| MAD | 0.021 / 0.016 / 0.018 mag |
| points >0.3 mag faint (zr) | **5 of 561** — the entire "amplitude" |
| same-night partner test on those 5 | **2 of 5 nights have normal points alongside the faint ones** (project rule 10 red flag) |
| Lomb–Scargle (zr) | best P = 0.997 d — a 1-day alias — FAP 1.2e-2, **not significant** |
| BLS | P = 0.2135 d, depth 0.015 mag — noise |

Gaia DR3 2647761374214436352: G = 15.990, BP−RP = 1.478, parallax 1.898 ± 0.055 mas,
RUWE = 0.87 (astrometrically well-behaved single star).

**Conclusion:** the object is uncatalogued but shows no demonstrated variability beyond
outlier-driven scatter; there is no period and no amplitude worth registering. Filing it
would put an unsupported record in VSX under the user's name. **Do not submit.** Reopen
only if an independent survey (ATLAS/ASAS-SN forced photometry) shows coherent variability.

**Root cause — the same trap twice:** min–max amplitude is outlier-dominated. It inflated
the state-cycler v1 candidate list (difference-image magnitudes) and it inflated this
object. Standing rule: **quote percentile-based amplitudes, never peak-to-peak.**

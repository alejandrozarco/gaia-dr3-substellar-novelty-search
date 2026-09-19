# Deep period search — 170587115976392822 = ZTF19abxfaon (2026-07-15, main thread)

**Data:** ZFPS req 479161, 2,354 quality epochs (g 906 / r 1,222 / i 423, MJD 58267–61234),
calibrated to uJy via per-epoch zpdiff; de-trended per (band, rfid) with a 15-d running
median (removes 5-mag state cycling + the two reference-frame offsets per band);
1,687 usable residual epochs.

## Results — NULL, with quantified sensitivity

1. **Lomb-Scargle, P = 30 min – 2 d** (600k frequencies, per band, global bootstrap
   99% thresholds from 100 shuffles): g and i all below threshold. r showed one
   marginal alias family at f = 30.890/d ± n·1.0027 (P = 46.6 min) at power 0.048 vs
   threshold 0.044 — **REFUTED by three independent tests**: (a) split-sample — each
   half peaks at a different frequency, both below their own thresholds (power at f0:
   0.029 / 0.070); (b) color — g-band power at f0 = 0.009 (nothing); (c) amplitude —
   fitted semi-amplitude 4.2 uJy, below the 5.0 uJy median per-epoch error. Standard
   marginal-peak non-replication; discarded (rule-10-style discipline).
2. **BLS eclipse search, P = 1.4–48 h** (durations 12–43 min): best power 229 vs
   bootstrap 99% = 1220 → no eclipses.
3. **Long-period nightly-median pass, P = 10–300 d:** broad weak power near ~200 d
   (0.11) — at most quasi-periodic state cycling, alias-prone; NOT claimed.
4. **Injection-recovery sensitivity (r band):** coherent semi-amplitude ≥5 uJy
   (≈0.06 mag at the r≈19 bright state) recovered 20/20 at P = 1.5 h and 4 h;
   13/20 at 8 h; ≥8 uJy recovered 20/20 everywhere. 3 uJy: 0/20.

## Interpretation

No coherent periodicity with semi-amplitude ≳0.06 mag at hour-scale periods, and no
eclipses. This EXCLUDES an eclipsing CV and high-amplitude superhumpers at these
periods over the 8-yr baseline. **CORRECTED 2026-09-19:** an earlier version read this
as "fully consistent with a low-inclination CV". That is a logical error — no eclipses were DETECTED under this sampling and these search assumptions. This does NOT establish low inclination — moderate inclinations can be non-eclipsing and narrow or shallow eclipses can be missed — and a photometrically aperiodic light curve does not imply the system lacks an orbital period. Orbital modulation below ~0.06 mag is common in CVs at a range of inclinations, so the
null constrains the searched amplitude/period space and nothing about geometry.
Spectroscopy remains the discriminator. VSX/AstroNote drafts updated to carry the
quantified null instead of "Lomb-Scargle null".

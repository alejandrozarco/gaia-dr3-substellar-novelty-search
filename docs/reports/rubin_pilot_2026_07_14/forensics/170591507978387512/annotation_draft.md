# Consumer package (DRAFT ONLY — user files) — diaObject 170591507978387512

## A. Annotation text (ready to paste; <= ~1200 chars for Lasair annotation / broker feedback)

> **Archival forensics, Rubin/LSST diaObject 170591507978387512** (RA 313.22651, Dec -14.84044;
> Fink ELEPHANT hostless candidate; not on TNS as of 2026-07-14).
> Rubin: 5 diaSources / 3 nights, MJD(TAI) 61218.270-61235.247; i: 22.01 -> 21.24 (rise 0.72 mag
> in 10.0 d, then flat 6.9 d); z: 22.27 -> 21.67; i-z ~ -0.4; reliability > 0.999, no pixel flags.
> Quiescent counterpart: LS DR10 PSF source ls_id 10995375804519828 at 0.48" (~2 sigma),
> g = 24.73 +/- 0.28, r = 23.72 +/- 0.15 (1-2 DECam exposures, ~2016); Rubin template i ~ 24.0,
> z ~ 23.6; amplitude ~2.9 mag. No Gaia DR3, CatWISE/unWISE, 2MASS, GALEX, VLASS/NVSS, SIMBAD,
> VSX within 10-15".
> **Precursor test (negative):** the two PS1 DR2 i-band catalog detections at the position
> (MJD 55089.312, i=21.6; MJD 56472.505, i=21.15) are masked-pixel artifacts: psfQfPerfect 0.64,
> junk-detection-rich skycell, and — decisively — no source in the same-night partner warps taken
> 7/16 min apart (SNR 2.3 / 0.9 where i=21.2 would give 5-8 sigma). No outburst history in PS1
> (2009-2014, 42 warps), DECam/NSC (2016), ZTF DRs + Lasair-ZTF alerts (2018-2026), ATLAS FP
> (2015-2026, limits ~19.5).
> **Assessment: real transient; archival history disfavors recurrent CV; consistent with a SN
> near peak (if Ia, z ~ 0.19; LS counterpart then a compact M_r ~ -16 dwarf host). "Hostless"
> flag resolved to "faint compact counterpart at 0.5"".**

## B. Concrete ingestion paths (in priority order)

1. **Fink team / ELEPHANT feedback (primary, zero-gate).** The ELEPHANT hostless stream is
   explicitly community-vetting-driven (arXiv:2605.22407). Send the annotation text + REPORT.md
   to the Fink team via contact@fink-broker.org or the Fink Slack #hostless channel, referencing
   diaObjectId 170591507978387512. This is the adoption loop the flag came from. Named credit
   is NOT guaranteed (known from community scan 2026-07-14: Fink files under its own name) —
   value here is candidate adoption + relationship capital.
2. **Lasair-LSST annotation topic (designed consumer; gated).** Lasair annotators attach external
   classifications queryable by all users. Gate (USER action): create Lasair-LSST account
   (lasair-ztf token does not transfer), then request an annotator topic (e.g.
   `archival_forensics`) from the Lasair team, then POST annotation via /api/annotate/ with
   classification=SN_candidate, explanation=text above. This lane scales to future objects.
3. **TNS AT report (optional; policy caveat).** Object is absent from TNS; an AT report would put
   it in front of classifiers. CAVEAT: TNS reports conventionally come from the data-owning
   survey/broker; a third-party report built on public Rubin alert data should state
   "data from Rubin/LSST public alerts via Fink" and may be better routed by asking the Fink team
   (path 1) to submit their own TNS report. Do NOT file without checking current TNS policy.
   USER decision.
4. **VSX: not applicable** (not a periodic variable; no confirmed CV outburst history).

## C. What would change the verdict

- Continued Rubin photometry: a slow multi-week decline ~= SN (settles it); a sharp >1 mag/2 d
  drop => rethink CV. Fink object URL: https://lsst.fink-portal.org (search diaObjectId).
- A spectrum (out of scope for this project's no-telescope rule).

DRAFT ONLY. Prepared 2026-07-14 by archival-forensics pilot; filing is the user's personal action.

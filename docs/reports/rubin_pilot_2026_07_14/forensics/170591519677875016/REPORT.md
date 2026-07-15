# Archival forensics: Rubin/LSST diaObject 170591519677875016 (Fink ELEPHANT hostless flag)

Finalized 2026-07-14 (UT), rank-2 pilot stage 2. All epochs JD/MJD-keyed (asserts in scripts).
Position: RA 306.74802, Dec -11.81856 (ICRS). Galactic l,b = 32.833, -26.498.
Ecliptic lat +7.13 deg. SFD E(B-V) = 0.048.
Provenance: integrates products of the earlier 2026-07-14 session in this directory (Fink/ALeRCE
alert pulls, ATLAS FP job 4539055) — ATLAS stacking and Rubin template fluxes were INDEPENDENTLY
re-derived this session from the raw files and agree; ZFPS was completed and downloaded this
session; PS1 artifact adjudication, VHS/SkyMapper/SIMBAD nulls, and the Lasair-LSST token gate
test are new this session.

## VERDICT: INTERESTING — real, month-long, TNS-unreported transient with ATLAS pre-discovery
## rise and a sub-archival (r~24.0) underlying source; "hostless" flag is depth-limited.

## 1. The event (all mjd-keyed; full series in photometry_mjd.csv)

- Rubin/LSST public alerts (via ALeRCE multisurvey API; Fink object record agrees, nDiaSources=4,
  is_sso=false): i=20.815+/-0.018 (MJD 61218.31581), i=21.198+/-0.020 (61228.32884),
  i=21.135+/-0.043 (61231.23473), r=21.122+/-0.016 (61233.30790). reliability 0.99999+,
  extendedness ~0, ssObjectId=0, positional scatter ~6 mas over 15 d -> stationary point source
  (excludes solar-system; ALeRCE-beta "asteroid" label wrong).
- ATLAS forced photometry (job 4539055; 4,579 epochs MJD 57227-61232; independently re-stacked
  this session, nightly inverse-variance stacks): PRE-DISCOVERY counterpart —
  o=36.6+/-7.1 uJy (20.0 AB, 5.1 sigma) MJD 61202.53; c=38.1+/-5.6 (19.95, 6.8 sig) 61207.51;
  c=33.1+/-4.9 (20.10, 6.8 sig) 61208.57; c=28.2+/-5.4 (20.27, 5.3 sig) 61214.48; plus 3-4 sigma
  nights 61198/61213/61216/61226/61228. Flux present in ALL exposures of each night across three
  ATLAS units (01a/03a/04a) -> stationary and real. Pre-event stacks 61150-61199 null except
  marginal 3.1-sigma 61198 -> ONSET MJD ~61198-61202, i.e. >=16 d before the first Rubin
  diaSource. Post 61229: below ATLAS depth, consistent with Rubin i~21.1.
- Timeline: rise ~61198-61202, ATLAS c/o ~19.9-20.3 through ~61216, Rubin i 20.8 fading to 21.1
  by 61231; event duration >=30 d; ATLAS c minus Rubin i ~ -0.7 mag -> blue.

## 2. Host / counterpart: hostless ONLY at archival depth

- Rubin deep-template forced flux at the position (from alert packets, verified from raw CSV):
  r = 944+/-46 nJy = 23.96+/-0.05 AB (20.6 sigma); i = 949-1107 nJy = 23.8-24.0 AB (8-10 sigma).
  A blue (r-i ~ 0) underlying source EXISTS at the position, below every archival catalog depth.
- Archival nulls at the position: LS DR10 tractor (i-only field; nearest source = unrelated PSF
  i=21.87 at 3.04"); NSC DR2 (nearest 2.97", single epoch MJD 58704.144); Gaia DR3 (nearest
  14.25"); PS1 DR2 stack (no object; r~23.2/i~23.1 depth); VHS DR5 J~20.3 and SkyMapper DR4
  (coverage verified via 60" field counts: 73 and 16 srcs); SDSS DR16; CatWISE2020/unWISE
  (nearest 11"); SIMBAD 0 in 30".

## 3. Precursor search 2010-2026: NULL (with two adjudications)

- PS1 DR2 (2010-2014): apparent y=18.67 at 0.84" on MJD 55765.44094 REJECTED as warp artifact —
  absent in the same-night partner exposure 17 min later (which reaches y~19.4), psfQfPerfect
  0.539, member of a ~15-detection low-Qf swarm around a G=14.8 star 20.6" away; SkyBoT 204.
- ATLAS 11 yr: two historical spikes rejected as non-stationary — MJD 59024.48297 (1336 uJy in
  ONE 30-s exposure, 7 uJy 2.6 min later; SkyBoT-negative at T05) and 57955.477-57955.486 (2
  consecutive exposures ~113 uJy, gone 25 min later; SkyBoT-negative). Historical nightly-stack
  false-positive rate: 2/~1090 nights, both mover/glint-consistent. No stationary precursor to
  o~20.2/c~20.7 (median nightly 3-sig stack limits).
- ZTF: no alert within 30" ever (Lasair-ZTF cone, token OK on ZTF instance); ZTF DR light curve
  empty; ZFPS req 479160 (registered account, completed 2026-07-14 08:32 UT, downloaded this
  session as zfps_fp_raw.txt): 22 usable g+r diff-image epochs MJD 60515.4-61148.5, zero SNR>3,
  median diffmaglim g=19.7/r=19.5; sparse field, no epochs during the event.
- DASCH: skipped, justified — no plausible epoch at V<15 (counterpart r~24; event peak ~19.9).

## 4. Classification

- Solar-system: excluded (15-d fixed position; SkyBoT-clean).
- AGN/TDE: disfavored — no IR counterpart, no prior variability in 11 yr, host would be the
  r~24.0 template source (very faint for AGN); not excluded at 100%.
- Orphan afterglow: excluded (>=30-d duration, slow decline).
- Dwarf nova: possible only as a large-amplitude (>=3.8 mag from r=23.96 quiescence to o~20.0),
  long (>=26 d) superoutburst — WZ Sge-like duration is compatible, though the decline
  (~0.02 mag/d in i during the Rubin window) is slow for a DN plateau.
- Supernova in a faint/dwarf host: most consistent — blue color near peak, ~30-d evolution;
  at z~0.1-0.15 peak M ~ -18, host M ~ -14.5 to -15 (dwarf). Template source = host, not
  quiescent counterpart, in this reading.
- Discriminator: continued Rubin photometry (terminal rapid drop => DN; smooth radioactive/
  plateau decline => SN) or one spectrum.

## 5. Gates and blocked lanes (honest accounting)

- Fink API: reachable earlier on 2026-07-14 (JSON products in this dir); TCP-unreachable from
  this network at ~19:30 UT re-test. ALeRCE multisurvey endpoint carried the alert data.
- Lasair-LSST GATE RESULT: instance = https://lasair.lsst.ac.uk; stored lasair-ztf token returns
  {"detail":"Invalid token."} -> token does NOT transfer; USER must re-login (prerequisite for
  the annotation path). Lasair-ZTF token still works on the ZTF instance.
- ZFPS GATE NOTE: dec -11.8 > -31 => eligible; requests must use the REGISTERED e-mail (gmail
  address rejected with "e-mail address is unknown"; registered address per prior-session log
  works). Completed, not skipped.
- Duplicate ATLAS task 4542360 queued by this session before the finished job 4539055 was found;
  its output (same position) is redundant — ignore or use as consistency check when it lands.
- Data Lab nsc_dr2.meas cone timed out (2 min); object-level null stands.

## 6. Deliverables in this directory

- photometry_mjd.csv — 1,142 rows, MJD-keyed: ATLAS nightly stacks (1,108), Rubin diff (4) +
  template (4), ZFPS epochs (22), PS1 (3, artifact flagged), NSC (1).
- consumer_package/ — annotation.txt (broker/ELEPHANT feedback text), tns_astronote_draft.md,
  lasair_annotation.json, INGESTION.md (three concrete paths + user actions). DRAFTS ONLY.
- atlas_fp_raw.txt, zfps_fp_raw.txt, fink_lsst_*.json, lsst_*_alerce.csv — raw archive returns.
- ls_dr10_cutout.jpg — 67"x67" LS DR10 cutout (empty at center).
- Session query products in /tmp/rubin_pilot/ (gaia_dr3.csv, ps1_dr2_detections_*.csv,
  atlas_nightly_stacks_verified.csv, zfps_epochs.csv, vhs/smss/catwise/unwise csv, scripts).

## 7. Checkable URLs

- ATLAS FP queue: https://fallingstar-data.com/forcedphot/queue/ (jobs 4539055, 4542360)
- ALeRCE: https://api.alerce.online (multisurvey LSST endpoints; object 170591519677875016)
- Lasair-ZTF cone: https://lasair-ztf.lsst.ac.uk/api/cone/  | Lasair-LSST: https://lasair.lsst.ac.uk
- Data Lab TAP: https://datalab.noirlab.edu/tap/sync (nsc_dr2.object, ls_dr10.tractor)
- Gaia TAP: https://gea.esac.esa.int/tap-server/tap/sync
- PS1: https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/{mean,detection}.csv
- SkyBoT: https://ssp.imcce.fr/webservices/skybot/api/conesearch.php (epochs JD 2455765.940945,
  2457955.977405, 2459024.982973 -> all 204/no match)
- ZFPS: https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi (req 479160)
- LS cutout: https://www.legacysurvey.org/viewer/cutout.jpg?ra=306.74802&dec=-11.81856&layer=ls-dr10
- IRSA dust: https://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr=306.74802+-11.81856+equ+j2000

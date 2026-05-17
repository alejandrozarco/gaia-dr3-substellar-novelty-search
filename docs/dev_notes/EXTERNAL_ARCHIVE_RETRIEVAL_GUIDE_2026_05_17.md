# External Archive Retrieval Guide

Walkthrough for the 8 archives that are NOT yet in the cascade's automatic
cross-match because they're not standard-TAP queryable. Ranked by likely
leverage for our 10 headline candidates.

Status legend:
- 🟢 Programmatically retrievable now (Python script can fetch data)
- 🟡 Programmatically retrievable but requires authentication
- 🔴 Web-form only (no public API), or proprietary

## 1. NEID at WIYN-3.5m (Kitt Peak) — HIGHEST LEVERAGE 🟡

**Why it matters most**: NEID is a NASA-NSF dedicated exoplanet RV
spectrograph commissioned 2020, achieving ~1-2 m/s precision (target 30
cm/s). The GTO sample includes bright FGK exoplanet hosts — exactly our
HD-class candidates at V=8.7-10.0.

**Likely candidate hits** (Dec > -25° for KP, V < 14 for usable NEID RV):

| Candidate | V | Dec | NEID-accessible? | Likely in GTO list? |
|---|---|---|---|---|
| HD 76078 | 8.7 | +53.1 | ✓ | Possible |
| HD 101767 | 8.9 | +56.9 | ✓ | Possible |
| BD+46 2473 | 9.0 | +46.4 | ✓ | Possible |
| BD+35 228 | 9.1 | +35.9 | ✓ | Possible |
| BD+56 1762 | 10.0 | +56.2 | ✓ | Possible |
| HD 140895 | 9.4 | -2.8 | ✓ | Possible |
| HD 104828 | 9.9 | -11.0 | ✓ | Possible |
| HD 140940 | 8.7 | -33.4 | ✗ (too south) | No |
| HIP 60865 | 12.1 | +28.2 | Faint but possible | M-dwarf, lower priority for NEID |
| HIP 20122 | 13.5 | -5.5 | Too faint for NEID | No |

7 of 10 are in NEID's accessibility window.

### Retrieval workflow

NEID has a NASA archive interface at `https://neid.ipac.caltech.edu/`,
and provides PyNEID (Python package) for programmatic access:

```bash
pip install pyneid
```

```python
from pyneid.neid import Neid
import os
os.environ['NEID_API_TOKEN'] = 'YOUR_TOKEN_HERE'  # request from neid-help@ipac.caltech.edu

# Search by coordinates
results = Neid.query_position(
    ra=134.05530, dec=53.05869,  # HD 76078
    radius=5.0,  # arcsec
    columns='all',
)
print(results)

# If hits found, download:
# Neid.download(id=<observation_id>, output_dir='./')
```

Alternative without PyNEID: the web search portal is at
`https://neid.ipac.caltech.edu/search.php`. Coordinate cone-search there
returns observation IDs and DRP (data reduction pipeline) RV values.

**Step-by-step for our candidates**:
1. Register for an IPAC account → get API token by emailing
   `neid-help@ipac.caltech.edu`
2. Install pyneid (`pip install pyneid`)
3. Loop over the 7 NEID-accessible candidates with `Neid.query_position`
4. For any hit: fetch the DRP RV time-series (`Neid.download_rv(id=...)`)
5. Fit Keplerian orbit at the Gaia NSS Orbital period; check
   consistency

**Expected outcome**: low (NEID's target list is biased toward known
planet-host systems; our candidates are uncatalogued, so unlikely
in GTO). But if any hit exists, NEID's 1-2 m/s precision would be
decisive.

## 2. MAROON-X at Gemini-N (Mauna Kea) — HIGH LEVERAGE 🟡

**Why it matters**: M-dwarf-optimized RV spectrograph commissioned 2020,
~30 cm/s target precision. Direct hit for our two M-dwarf candidates.

**Likely candidate hits**:

| Candidate | SpT | V | Dec | MAROON-X target? |
|---|---|---|---|---|
| HIP 60865 | M dwarf | 12.1 | +28.2 | **Yes — exactly the sample** |
| HIP 20122 | M2.0Ve | 13.5 | -5.5 | Possible (borderline N hemisphere) |

### Retrieval workflow

**Gemini Observatory Archive (GOA) now requires ORCID authentication**
due to AI-bot abuse:

```
"Login Required. Please visit https://archive.gemini.edu/login
[...] We recommend using the login via ORCID option."
```

Steps:

1. Register for ORCID at `https://orcid.org/register` (free, ~5 min)
2. Log in to `https://archive.gemini.edu/login` via ORCID
3. Authenticated session uses cookies; programmatic access via
   `astroquery.gemini`:

```python
from astroquery.gemini import Observations
Observations.login(orcid='your-ORCID-id')

# Cone search for HIP 60865
results = Observations.query_criteria(
    coordinates='12 28 43.46 +28 11 12.2',
    radius='0d0m20s',
    instrument='MAROON-X',
)
```

The Gemini archive's RESTful endpoints work after login:

```
https://archive.gemini.edu/jsonsummary/canonical/ra=187.18108/dec=28.18672/sr=60/instrument=MAROON-X
```

Public after a 12-18 month proprietary period. So observations from
~2023-2024 would be public now.

**Expected outcome**: medium. MAROON-X is a small instrument (~50
unique targets observed so far per Trifonov & Brahm 2025); HIP 60865
might be in the sample if anyone proposed for it.

## 3. LCO NRES (global 1m network) — MEDIUM LEVERAGE 🟢

**Why it matters**: Robotic Echelle Spectrographs at 6 LCO sites worldwide
(McDonald TX, CTIO, SAAO, SSO, Tenerife, Wise). 3-5 m/s precision,
ToO/queue scheduled. Easy access for any allocated program.

### Retrieval workflow

LCO Science Archive API at `https://archive-api.lco.global/frames/` is
**publicly accessible without authentication for public-data frames**
(12-month proprietary period).

**Working query syntax**:
```
https://archive-api.lco.global/frames/?covers=POINT(174.5 56.7)&public=true&instrument_id=en06&OBSTYPE=SPECTRUM&limit=100
```

Key parameter notes:
- `covers=POINT(RA DEC)` (WKT format, parentheses required)
- `instrument_id` for filtering: `en01`-`en12` are NRES units at
  different sites
- `OBSTYPE=SPECTRUM` to exclude calibration frames (BIAS, DARK, ARC,
  LAMPFLAT default to also match cone searches with WCS=0,0)
- `target_name` filter exists but case-sensitive Django-style:
  `target_name__icontains=HD%2076078`

```python
import urllib.request, urllib.parse, json
params = urllib.parse.urlencode({
    'covers': f'POINT({ra} {dec})',
    'OBSTYPE': 'SPECTRUM',
    'public': 'true',
    'limit': 50,
})
url = f"https://archive-api.lco.global/frames/?{params}"
resp = urllib.request.urlopen(url, timeout=30).read()
data = json.loads(resp)
```

**Caveat noted during this session**: bare `covers=POINT(...)` matches
many calibration frames with default WCS. ALWAYS filter
`OBSTYPE=SPECTRUM` to limit to real science frames, and check the
returned `OBJECT` and `target_name` fields for actual target identity.

**Expected outcome**: low-medium. NRES has hundreds of distinct
science targets observed since 2019; sample is heavy on
exoplanet-candidate stars from TESS, plus PI proposals. Our candidates
are unlikely to be in NRES's TOI follow-up sample but could be in a
brown-dwarf program.

## 4. SOPHIE at OHP-1.93m (France) — MEDIUM LEVERAGE 🔴

**Why it matters**: HE-mode 3 m/s precision; northern-hemisphere
exoplanet RV survey running since 2006. Wide-net "SP1" survey covers
~2000 bright FGK stars.

### Retrieval

OHP archive at `http://atlas.obs-hp.fr/sophie/` — **web-form only**, no
programmatic API. Manual workflow:

1. Go to `http://atlas.obs-hp.fr/sophie/`
2. Search by RA/Dec or target name
3. Filter for `program_id=SP1` (or your specific program of interest)
4. Download reduced RV table or raw FITS

For each of the 9 northern candidates (Dec > -10), execute the web
search and record hit count + observation epochs. ~5 minutes per
candidate manually.

**Alternative**: Cortés-Contreras et al. (the CARMENES team) have
parallel SOPHIE coverage of some M-dwarfs. Direct email to
mariano.cortes@iac.es could check whether any of HIP 60865 or HIP
20122 are in their unpublished SOPHIE archive.

**Expected outcome**: medium-low. SOPHIE's SP1 sample includes many
HD stars and BD stars; some of ours may be incidental observations.

## 5. Nordic Optical Telescope FIES — LOW LEVERAGE 🔴

**Why it matters**: 10-m/s precision Northern-hemisphere RV. Used
heavily for TESS follow-up.

### Retrieval

NOT data archive at `https://www.not.iac.es/observing/forms/datarequest/`.
**Web-form only, no programmatic API**.

Workflow:
1. Search the public archive for each candidate's coords
2. Note any FIES observations with their proposal IDs
3. Request raw FITS via the form (auto-approved for public data)

**Expected outcome**: low. FIES sample is heavy on TESS follow-up,
which we already know our candidates are absent from.

## 6. EXPRES at Lowell Discovery Telescope — LOW LEVERAGE 🔴

**Why it matters**: 30 cm/s precision but extremely narrow sample
(~100 stars, Petersburg+ 2020 + extensions).

### Retrieval

**No public archive.** Data is held by the EXPRES team. Direct PI
contact (e.g., `eblunt@yale.edu`, Debra Fischer) required for any
data inquiry.

**Expected outcome**: very low. EXPRES sample is narrowly curated
toward G-dwarf precision targets; our candidates are unlikely to be in
the sample.

## 7. Subaru HDS (SMOKA archive) — LOW LEVERAGE 🟡

**Why it matters**: Subaru High Dispersion Spectrograph, ~5-10 m/s
precision (not optimized for ultra-stable RV but achievable).
Northern-hemisphere accessible.

### Retrieval

SMOKA archive at `https://smoka.nao.ac.jp/` — has a web-form search
that returns metadata. Authenticated download of raw FITS via the same
interface (registration required).

```
https://smoka.nao.ac.jp/SMOKAsearch.jsp?TELESCOPE=Subaru&INSTRUMENT=HDS&RA1=11+22+26&DEC1=%2B56+51+02
```

The query is via HTML form POST, not a JSON API.

**Expected outcome**: low. HDS is primarily used for stellar parameters
not exoplanet RV; our candidates are unlikely to have been observed.

## 8. Coralie at Geneva (Euler 1.2m, La Silla) — NOT RETRIEVABLE 🔴

**Why it matters**: Southern-hemisphere ~3 m/s RV. Geneva planet-search
program since 1998.

### Retrieval

**No public archive.** Coralie data is proprietary to the Geneva
planet-search team. Direct PI contact (Stephane Udry / Damien Ségransan
at Geneva Observatory) required.

**Expected outcome**: zero unless we know there's a specific Coralie
program covering our candidates.

---

## Prioritized action plan

If pursuing additional archives is worthwhile, the order of effort
investment vs likely yield is:

1. **LCO archive (NRES) — easiest, free, programmatic.** 30 min to
   write and run a proper-filtered query for all 10 candidates.
2. **NEID via PyNEID — requires API token request.** 1-2 days for
   account setup, then 1 hour to query all 10 properly.
3. **Gemini Observatory Archive (MAROON-X) — requires ORCID login.**
   30 min ORCID setup, then `astroquery.gemini` query for HIP 60865 + HIP 20122.
4. **SOPHIE web-form manual search.** ~1 hour for all 10 candidates.
5. **FIES web-form manual search.** ~1 hour.
6. The rest (EXPRES, HDS, Coralie) require PI emails or have negligible
   probability of containing our targets.

The combined effort for #1-5 is ~1 day's work. Given the universal
negative result from the 22 catalogs already cross-matched
(`SURVEY_COVERAGE_AUDIT_2026_05_17.md`), the marginal probability of
finding archival RV data here is low — probably 10-20% across all
candidates. But the cost is also low.

## Most pragmatic single action

If you want to check ONE archive properly without spending a full day:

**Email Stéphane Udry (`stephane.udry@unige.ch`) and/or Trent
Dupuy (`tdupuy@roe.ac.uk`) directly with the 10-candidate list and
predicted K_1 amplitudes.** Both lead substellar-companion RV
surveys (Geneva/Coralie and MAROON-X-related respectively). A
2-minute email asking "are any of these in your unpublished
archive?" can settle the question without us querying.

This is the kind of PI-level information that no archive query can
reveal.

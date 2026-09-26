# mwcheck — master counterpart check

One command runs every catalogue in the registry around a position, each with a search radius suited to the
survey's resolution, and reports one verdict per catalogue:

| verdict | meaning |
|---|---|
| MATCH | rows within the search radius (nearest separation given) |
| ABSENT | no row within the radius, while the catalogue has rows in the coverage cone around the position |
| NO_COVER | no rows in the coverage cone either: the survey does not cover this position, so absence says nothing |
| HOLE | the query failed |

```
python scripts/mwcheck/mwcheck.py --gaia 6315134987927550592 [--json out.json]
python scripts/mwcheck/mwcheck.py --ra 231.5622 --dec -11.2241
python scripts/mwcheck/mwcheck.py --selftest
```

With `--gaia`, the position is moved to epoch 2000.0 with the Gaia proper motion.

Registry (search radius): radio NVSS (30″), FIRST (5″), VLASS QL epoch 1 (5″), RACS-low (15″), SUMSS (30″),
TGSS (25″), GLEAM (90″), LoTSS-DR2 (10″), ATNF pulsars (60″); X-ray ROSAT 2RXS (30″), eRASS1 (15″), eRASS:3 (15″),
4XMM-DR13 (10″), 2SXPS (10″), CSC2 (5″); gamma 4FGL-DR4 (10′); UV GALEX AIS and GR5 (5″); variability VSX (10″),
Gaia DR3 vclassre (3″), Chen+2020 ZTF (5″), ATLAS (5″), ASAS-SN bare `II/366` (10″), Gavras+2023 (5″); CVs
Ritter–Kolb, Downes, Rodriguez+2025, eRASS1 CV catalogue (10″); white dwarfs Gentile Fusillo+2021 (5″).

`--selftest` queries known sources (3C 273, PKS 0521−36, 3C 295, PSR J0437−4715, a VSX polar, AM Her and a
catalogued VLASS source) and fails if any catalogue does not return them. Run it after editing the registry.
Two handles found to return false nulls are deliberately not used: `J/ApJS/260/53` (use `IX/72` for 4FGL) and
`II/366/catalog` (use the bare `II/366`).

This complements, and does not replace, the all-table VizieR cone (every VizieR table at 6″) and the
known-object store in `scripts/known_objects/`.

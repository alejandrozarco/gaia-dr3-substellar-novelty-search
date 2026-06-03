# Object journal — Gaia DR3 &lt;SOURCE_ID&gt;

<!-- Scaffold: python scripts/journal/journal.py new <SOURCE_ID> --name "<NAME>" --klass "<CLASS>" --dossier <PATH> -->

| field | value |
|---|---|
| Canonical key | **Gaia DR3 &lt;SOURCE_ID&gt;** |
| Aliases / names | &lt;NAME(s)&gt; |
| Current class | &lt;e.g. DA WD + dark companion (cool WD or dormant NS)&gt; |
| Current status | **&lt;CANDIDATE / CONFIRMED / DEMOTED / RETRACTED / PARKED&gt;** (as of &lt;DATE&gt;) |
| Dossier | `docs/dossiers/<...>.md` |
| CANDIDATES.md | &lt;section / line&gt; |
| In DR4 pre-registration | &lt;yes / no&gt; |

## Cross-check ledger
*Append-only. The anti-confabulation table — read this before asserting any prior result. Record every catalog/method ever checked, with the result (including NULL / NOT-IN) and where it's sourced.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|
| &lt;DATE&gt; | &lt;e.g. Shahaf+2023 (J/MNRAS/518/2991)&gt; | &lt;by source_id + 5" cone&gt; | **&lt;IN / NOT IN / value&gt;** | &lt;dossier §, CANDIDATES.md:line, script, task #&gt; |

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| &lt;DATE&gt; | &lt;status&gt; | &lt;reason&gt; | &lt;task #, session, dossier&gt; |

## Entry log
*Append-only, chronological.*

### &lt;DATE&gt; — &lt;short title&gt;
- **Did:** &lt;query / analysis / cross-check&gt;
- **Found:** &lt;result, including nulls and superseded values&gt;
- **Provenance:** &lt;script path, task #, agent, dossier, /tmp output&gt;

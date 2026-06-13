# Research Checklist

Field checklist for gap analysis (SKILL.md Step 5). This is the built-in default note schema; a user-supplied template overrides it (SKILL.md Step 2).

## Frontmatter Fields

| Key | Priority | Research target |
| --- | -------- | --------------- |
| `title` | Required | Full legal or trade name |
| `aliases` | Required | All name variants: legal entity name, trade name, abbreviations, former names |
| `type` | Required | Org category: startup, corporation, law-firm, government, nonprofit, think-tank, university |
| `hq` | Required | City, province/state, country of headquarters |
| `website` | Required | Primary domain URL |
| `sector` | Required | Industry or practice domain (e.g. Legal technology, FinTech, Administrative law) |
| `summary` | Required | One-sentence description: what org does + distinguishing characteristic |
| `founded` | Important | Founding year; approximate decade acceptable if exact year unavailable |
| `ownership` | Important | public / private / state-owned / nonprofit / partnership |
| `linkedin` | Important | LinkedIn company page URL |
| `size` | Important | Headcount range or named tier (e.g. 1-10, 11-50, 51-200, 200+) |
| `crunchbase` | Optional | Crunchbase profile URL; primarily for startups and VC-backed companies |
| `ticker` | Optional | Stock exchange ticker symbol for public companies |

## Body Sections

| Section | What to gather |
| ------- | -------------- |
| `## Context` | Narrative: what the org does, why it is in the user's notes, how it connects to the user's work |
| `## Profile` | Key identity fields table; then `### Milestones` chronological table: Year, Event. Oldest to newest. |
| `## Key People` | Table: Name (link to the person's profile note if one exists), Role, Note. Include founders, C-suite, key contacts. |
| `## Focus Areas` | Products, services, practice areas, or research themes; concrete list not generic marketing copy |
| `## Notable Affiliations` | Industry bodies, strategic partners, government relationships, accreditations, regulatory filings of note |
| `## Related` | 3-8 links to related notes (people, projects, news), if the user keeps a linked notes system |
| `## Notes` | Dated entry (`### YYYY-MM-DD`): connection context, deal notes, impressions, follow-up items |

## Gap Flag Definitions

| Flag | Meaning |
| ---- | ------- |
| `MISSING` | Field not found in any source consulted |
| `UNVERIFIED` | Inferred or indirect: headcount from job board density, founding year from earliest press mention |
| `PARTIAL` | Data found but incomplete: sector listed but no sub-domain, HQ known but no country |

## Common Sources by Field

Registry examples below are Canadian; substitute your jurisdiction's equivalents (e.g. Companies House, EDGAR, EU business registers).

| Field | Best sources |
| ----- | ------------ |
| Legal name, founding, ownership | Corporations Canada or your national/provincial business registry (SEDAR+/EDGAR for public companies), company About page |
| HQ, office locations | Company website Contact or Locations page, LinkedIn company page |
| Key people | Company website Team or Leadership page, LinkedIn company page |
| Funding, valuation | Crunchbase, PitchBook, press releases, tech and business news outlets |
| Practice areas / products | Company website Services or Products page, case studies, press releases |
| Awards, rankings | Chambers & Partners, Legal 500, industry award sites |
| Regulatory or court involvement | Court and tribunal databases (e.g. CanLII), securities filings, news search |
| Strategic partnerships | Press releases, company news page, partner directories |

## Screenshot Asset Convention

Save logo and screenshots to:
```
<output-root>/organizations/assets/<org-slug>/
```

Embed logo in note immediately after frontmatter:
```markdown
![](assets/<org-slug>/logo.png)
```

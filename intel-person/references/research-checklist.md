# Research Checklist

Field checklist for gap analysis (SKILL.md Step 5). This is the built-in default note schema; a user-supplied template overrides it (SKILL.md Step 2).

## Frontmatter Fields

| Key | Priority | Research target |
| --- | -------- | --------------- |
| `title` | Required | Full legal name (not nickname or short name) |
| `aliases` | Required | All name variants: legal name, professional name, nicknames, maiden name |
| `occupation` | Required | Current role and title |
| `organization` | Required | Current employer or firm |
| `location` | Required | City, province/state, country |
| `website` | Required | Personal or professional site URL |
| `summary` | Required | One-sentence description: role + distinguishing trait |
| `email` | Important | Professional email; contact form URL if no direct email |
| `phone` | Optional | Rarely public; note if found |
| `linkedin` | Important | Personal LinkedIn URL (not company page) |
| `github` | Optional | GitHub profile if tech-adjacent |
| `birthday` | Optional | Day-month if available (no year required) |

## Body Sections

| Section | What to gather |
| ------- | -------------- |
| `## Context` | Narrative: who they are, professional identity, how they connect to the user; note name variants |
| `## Biographical Details` | Table: full name, professional name, education, professional qualifications (e.g. year of call for lawyers), location, heritage, languages, athletics/hobbies |
| `## Career Timeline` | Chronological table: Role, Organisation, Notes. Oldest to newest. |
| `## Practice Areas` / domain section | Expertise areas, focus topics, specialisations |
| `## Notable Affiliations & Roles` | Boards, associations, community roles, committee positions |
| `## Recognition & Awards` | Named awards with awarding body and citation phrase |
| `## Personal Brand & Positioning` | Analytical paragraph: how they position themselves, what distinguishes them from competitors |
| `## Interests & Topics` | Hobbies, domains, topics of public engagement |
| `## Related` | 3-8 links to related notes (same project or context, plus broader connections), if the user keeps a linked notes system |
| `## Notes` | Dated entry (`### YYYY-MM-DD`): connection context, first impression, things worth remembering |

## Gap Flag Definitions

| Flag | Meaning |
| ---- | ------- |
| `MISSING` | Field not found in any source consulted |
| `UNVERIFIED` | Inferred or indirect: heritage from org name, role from third-party description, not self-stated |
| `PARTIAL` | Data found but incomplete: career gap, no qualification year, city but not country |

## Common Sources by Field

| Field | Best sources |
| ----- | ------------ |
| Career timeline | Personal website bio, LinkedIn (URL only), firm/company team pages |
| Education | School profile pages, award citations (often mention alma mater), personal bio |
| Awards | Award-issuer websites, press releases, professional rankings profiles |
| Community roles | Organisation websites, professional and bar association directories |
| Personal interests | Personal website sections, interview articles, speaker bios at events |
| Contact info | Personal website Contact page, firm inquiry forms |
| Headshot | Personal website About/Bio page (highest fidelity); award-site profiles |

## Screenshot Asset Convention

Save headshots and screenshots to:
```
<output-root>/people/assets/<name-slug>/
```

Embed in note immediately after frontmatter:
```markdown
![](assets/<name-slug>/headshot.jpg)
```

# Workflow: from-web

URL-first: web search → URLs; browser scrape (if agent-browser installed) or direct fetch → content + headshots.

## Inputs

- Person name (required)
- Seed URL(s) — personal site, company bio, award profile (optional; discovered via search if not provided)
- Gap list from `from-local-notes.md` (optional; if running as supplemental pass)

## Steps

### 1. Web search phase

Run 2-3 web searches. Collect URLs before opening any pages.

```
Search 1: "<full name>" site:linkedin.com
Search 2: "<full name>" "<employer or role if known>"
Search 3: "<full name>" award OR interview OR speaker OR "most influential"
```

From results, classify URLs:

| Category | Action |
| -------- | ------ |
| Personal website | Browser scrape (Step 2); no browser → direct fetch |
| LinkedIn profile | Note URL only; do NOT scrape (auth required) |
| Award issuer page | Direct fetch or browser scrape |
| Org/firm team page | Direct fetch |
| Press / interview | Direct fetch |
| Social media (Instagram, Twitter/X) | Note URL only; do NOT scrape |

### 1a. Capture research log inputs

Record the following before moving to Step 2. Pass as a `### Research Log Inputs` block through to Step 4 handoff.

| Item | What to record |
| ---- | -------------- |
| Seed URLs | Any URL the user explicitly provided; any seed discovered before web search |
| Non-template searches | Any query beyond the 3 template strings above — note exact string |
| Registries / databases opened | None applicable for person research; leave blank |
| Date range filters | Any `after:` or `before:` operator appended to a search |
| LinkedIn URL | URL noted during classification; not scraped |

Omit any row with no value.

### 2. Construct agent inputs

From the Step 1 URL classification and any incoming gap list, assemble:

- `person_name`: Full display name as provided
- `name_slug`: Hyphenated lowercase slug (e.g. `jordan-lee`)
- `urls`: Personal site first, then award profiles and org bios in order of likely richness; exclude LinkedIn and social media
- `gap_list`: Forwarded from `from-local-notes.md` if this is a supplemental pass; empty if first-pass run
- `asset_base_path`: `<output-root>/people/assets/{name_slug}/` (default output root: `./intel/`)
- `browser_available`: whether the agent-browser CLI is installed (see SKILL.md Setup)

### 3. Run the researcher

If the host supports subagents, dispatch one using `agents/intel-person-researcher.md` as the template. Pass a structured prompt with all six inputs from Step 2; the agent receives no conversation history, so all context must be explicit in the prompt.

If the host does not support subagents, execute the process in `agents/intel-person-researcher.md` inline yourself with the same inputs.

Wait for the structured research brief before proceeding ⛔ BLOCKING (process gate; no user question).

### 4. Receive and forward brief

Pass the returned research brief to SKILL.md Step 5 (gap analysis).

Include the `### Assets` block from the brief in the handoff so gap analysis can reference screenshots and headshot paths without re-deriving them.

If brief status is `partial` or `failed`, include the `### Gap Flags` block in the handoff so Step 5 can record unresolved fields.

Include the `### Research Log Inputs` block from Step 1a in the handoff to SKILL.md Step 7.

# Workflow: from-web

URL-first: web search → URLs; browser scrape (if agent-browser installed) or direct fetch → page content; direct fetch → discovered JSON/API endpoints only.

## Inputs

- Org name (required)
- Org type hint (startup, law-firm, government body, etc.) — informs search strategy
- Seed URL(s) — company website, Crunchbase, registry profile (optional; discovered via search if not provided)
- Gap list from `from-local-notes.md` (optional; if running as supplemental pass)

## Steps

### 1. Web search phase

Run 3-4 web searches depending on org type. Collect URLs before opening any pages.

**Core searches (all org types):**
```
Search 1: "<org name>" site:linkedin.com/company
Search 2: "<org name>" about OR leadership OR "founded" OR "our team"
Search 3: "<org name>" news OR "press release" OR announcement
```

**Type-specific additions:**

| Org type | Add search |
| -------- | ---------- |
| Startup / VC-backed | `"<org name>" crunchbase OR funding OR "series A/B/C"` |
| Public company | `"<org name>" securities filings OR "annual report" OR ticker` |
| Law firm | `"<org name>" chambers OR "legal 500" OR rankings` |
| Government body | `"<org name>" official site OR "annual report"` |
| Nonprofit / NGO | `"<org name>" "charitable registration" OR "board of directors"` |

From results, classify URLs:

| Category | Action |
| -------- | ------ |
| Company website (About, Team, Services, Press) | Browser scrape (Step 2); no browser → direct fetch |
| Crunchbase / PitchBook / data platforms | Browser → inspect network requests → fetch discovered API endpoint; no browser → direct fetch, record blocks as gaps |
| Business registry / securities filings | Browser → inspect network requests → fetch discovered API endpoint if available; else extract from page; no browser → direct fetch |
| News / press release / rankings | Browser scrape or direct fetch |
| LinkedIn company page | Note URL only; do NOT scrape (auth required) |
| Social media (Twitter/X, Instagram, Facebook) | Note URL only; do NOT scrape |

### 1a. Capture research log inputs

Record the following before moving to Step 2. Pass as a `### Research Log Inputs` block through to Step 4 handoff.

| Item | What to record |
| ---- | -------------- |
| Seed URLs | Any URL the user explicitly provided; any seed discovered before web search |
| Non-template searches | Any query beyond the 3-4 template strings above — note exact string |
| Registries / databases opened | Any business registry, securities filings database, charity registry, or rankings directory actually opened |
| Date range filters | Any `after:` or `before:` operator appended to a search |
| LinkedIn URL | URL noted during classification; not scraped |

Omit any row with no value.

### 2. Construct agent inputs

From Step 1 URL classification and any incoming gap list, assemble:

- `org_name`: Full display name as provided
- `org_slug`: Hyphenated lowercase slug (e.g. `counsel-pro-law`)
- `org_type`: Type hint from user or inferred from search results
- `urls`: Company website first (About, Team, Services, Press pages), then ranking profiles and registry pages in order of likely richness; exclude LinkedIn and social media
- `gap_list`: Forwarded from `from-local-notes.md` if supplemental pass; empty if first-pass run
- `asset_base_path`: `<output-root>/organizations/assets/{org_slug}/` (default output root: `./intel/`)
- `browser_available`: whether the agent-browser CLI is installed (see SKILL.md Setup)

### 3. Run the researcher

If the host supports subagents, dispatch one using `agents/intel-org-researcher.md` as the template. Pass a structured prompt with all inputs from Step 2; the agent receives no conversation history, so all context must be explicit in the prompt.

If the host does not support subagents, execute the process in `agents/intel-org-researcher.md` inline yourself with the same inputs.

Wait for the structured research brief before proceeding ⛔ BLOCKING (process gate; no user question).

### 4. Receive and forward brief

Pass the returned research brief to SKILL.md Step 5 (gap analysis).

Include the `### Assets` block from the brief so gap analysis can reference logo and screenshot paths.

If brief status is `partial` or `failed`, include the `### Gap Flags` block so Step 5 can record unresolved fields.

Include the `### Research Log Inputs` block from Step 1a in the handoff to SKILL.md Step 7.

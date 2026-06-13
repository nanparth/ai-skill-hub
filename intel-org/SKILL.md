---
name: intel-org
version: '1.1.1'
description: 'Use when researching an organization to build a persistent, structured profile note via web research, registry lookups, and gap analysis. Accepts seed URLs, existing note paths, or pasted content. Trigger on: "intel on [org/company]", "org profile for", "company intel", "build org profile", "profile this firm", "research this company".'
argument-hint: '<org-name> [<url>] [--source-note <path>]'
---

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick.

# intel-org

## Setup — optional browser tooling

Browser automation is optional. If the agent-browser CLI is installed (see https://github.com/vercel-labs/agent-browser), browser-based steps are available: scraping JS-rendered sites, screenshots, logo capture, network-request inspection. If it is not installed, all research still runs: fetch page content directly instead, skip screenshot and logo capture, and record the skipped assets as gap flags.

## Reference Loading Map

| Need | Reference |
| ---- | --------- |
| Field checklist, gap analysis spec | `references/research-checklist.md` |
| URL-first research with screenshots | `workflows/from-web.md` |
| Existing-notes-first extraction | `workflows/from-local-notes.md` |

## Workflow

### Step 1 — Parse inputs

Determine what the user provided:

- **Name** (required): the organization to research
- **URL(s)**: company website, Crunchbase profile, registry page, rankings profile
- **Note path(s)**: existing notes about or referencing the org
- **Pasted text**: About page copy, press release, or bio text passed inline
- **Type hint**: startup, law-firm, government body, etc. (inferred from name or context if not stated)

### Step 2 — Load checklist and template schema

1. Load `references/research-checklist.md`. Its frontmatter field list is the default note schema.
2. If the user supplies their own org-note template, read it and use its frontmatter keys instead. Do NOT hardcode; read live; schemas evolve.

### Step 3 — Relationship context ⛔ BLOCKING

Full relationship set: client, partner, employer, competitor, target, regulator, community (mapping table below). Ask the user: "What is your relationship to this organization?" Options: Client / Partner / Competitor / Employer (no recommended option; factual, no defensible default); "Other" captures regulator, target, community. Present as a structured choice if the host supports it; otherwise numbered options in plain text. Stop and wait for the reply. Map answer to relationship tag:

| Answer | Tag |
| ------ | --- |
| Current or former client | `org-client` |
| Strategic partner or collaborator | `org-partner` |
| Current or former employer | `org-employer` |
| Competitor to user or user's org | `org-competitor` |
| Acquisition or deal target | `org-target` |
| Regulatory or oversight body | `org-regulator` |
| Professional association / community | `org-community` |

### Step 4 — Research routing

| Inputs available | Route |
| ---------------- | ----- |
| URL(s) only | Load `workflows/from-web.md` |
| Note path(s) only | Load `workflows/from-local-notes.md` |
| Both | Run from-local-notes first; pass gap list to from-web |
| Pasted text | Extract inline; run from-web for supplemental |
| Neither | Run from-local-notes auto-discovery first; if insufficient, ask for a seed URL ⛔ BLOCKING (open ask) |

### Step 5 — Gap analysis ⚠️ REQUIRED

Compare gathered fields vs. checklist. Flag:

- `MISSING` — not found in any source
- `UNVERIFIED` — inferred or indirect (e.g. headcount from job board density, founding year from earliest press mention)
- `PARTIAL` — data found but incomplete (HQ city known, country unknown; sector listed, no sub-domain)

Present the gap summary; get a verdict from the user ⛔ BLOCKING (options: Proceed (Recommended) / Address gaps first; structured choice if supported, else numbered text options). Required fields MISSING → ask again before assembling the note ⛔ BLOCKING (options: Proceed with gaps (Recommended) / Supply missing values); batch both questions together when both apply.

### Step 6 — Set verification tag

- Core fields (name, type, HQ, sector, focus areas) from first-party sources (company website, registry) → `intel/quality/verified`; incidental UNVERIFIED fields don't downgrade.
- Core fields inferred or sourced from third-party only → `intel/quality/unverified`. Upgrade when first-party confirmed.

### Step 7 — Assemble the profile note

If a note-authoring skill is installed, route there with the payload below; otherwise write the note directly, following the checklist's frontmatter schema and body sections. Payload:

- Full research brief (all gathered text, keyed by source)
- Template schema (from Step 2)
- Gap flags
- Relationship tag (from Step 3)
- Org type tag (from research)
- Asset paths for any saved logo / screenshots
- Research Log Inputs (from Step 1a of `workflows/from-web.md`, if web research was run)
- Destination: `<output-root>/organizations/<org-slug>.md` (default output root: `./intel/`)
- Confirm the destination and write authorization with the user before writing ⛔ BLOCKING (options: Authorize write / Cancel; no recommended option, explicit authorization required; structured choice if supported, else numbered text options).

Append a collapsed Research Log callout as the absolute last block in the note, after `## Notes`. Use Research Log Inputs from Step 1a. Normalize Research Log URLs per the URL rule below. The callout uses Obsidian-style syntax; if the user's note app doesn't render callouts, write a plain `## Research Log` section with the same field lines. Template:

    > [!note]- Research Log
    > **Last updated:** YYYY-MM-DD
    > **Seed URLs:** [Label](https://url), ...
    > **Key searches:** `"org name" site:chambers.com`, `"org name" "series A" crunchbase`
    > **Registries / databases:** business registries, securities filings databases
    > **Date range filter:** after:2022-01-01
    > **LinkedIn:** noted only — https://linkedin.com/company/...

Replace `YYYY-MM-DD` with today's date at write time. Omit any line with no value.

Normalize every external URL to `[label](https://full-url)` before writing. Bare URLs only when standalone in a table cell or on their own line. Never inside backticks. Never partial paths in prose.

---
name: intel-person
version: '1.1.1'
description: 'Use when researching an individual to build a persistent, structured profile note via web research, scraping, and gap analysis. Accepts seed URLs, existing note paths, or pasted bio text. Trigger on: "intel on", "gather intel on", "make intel note for", "build profile for", "add to intel", "create person profile".'
argument-hint: '<name> [<url>] [--source-note <path>]'
---

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick.

# intel-person

## Setup — optional browser tooling

Browser automation is optional. If the agent-browser CLI is installed (see https://github.com/vercel-labs/agent-browser), browser-based steps are available: scraping JS-rendered sites, screenshots, headshot capture. If it is not installed, all research still runs: fetch page content directly instead, skip screenshot and headshot capture, and record the skipped assets as gap flags.

## Reference Loading Map

| Need | Reference |
| ---- | --------- |
| Field checklist, gap analysis spec | `references/research-checklist.md` |
| URL-first research with screenshots | `workflows/from-web.md` |
| Existing-notes-first extraction | `workflows/from-local-notes.md` |

## Workflow

### Step 1 — Parse inputs

Determine what the user provided:

- **Name** (required): the person to research
- **URL(s)**: personal site, company bio, award profile
- **Note path(s)**: existing notes containing intel
- **Pasted bio text**: raw text passed inline

### Step 2 — Load checklist and template schema

1. Load `references/research-checklist.md`. Its frontmatter field list is the default note schema.
2. If the user supplies their own person-note template, read it and use its frontmatter keys instead. Do NOT hardcode; read live; schemas evolve.

### Step 3 — Relationship context ⛔ BLOCKING

Full relationship set: friend, acquaintance, professional peer, mentor, client, family (mapping table below). Ask the user: "How do you know this person?" Options: Friend / Professional peer / Client / Family (no recommended option; factual, no defensible default); "Other" captures acquaintance, mentor. Present as a structured choice if the host supports it; otherwise numbered options in plain text. Stop and wait for the reply. Map answer to `ppl-*` tag:

| Answer | Tag |
| ------ | --- |
| Friend | `ppl-friend` |
| Acquaintance / panel / event | `ppl-acquaintance` |
| Professional peer / collaborator | `ppl-colleague` |
| Mentor | `ppl-mentor` |
| Client | `ppl-client` |
| Family | `ppl-family` |

### Step 4 — Research routing

| Inputs available | Route |
| ---------------- | ----- |
| URL(s) only | Load `workflows/from-web.md` |
| Note path(s) only | Load `workflows/from-local-notes.md` |
| Both | Run from-local-notes first; pass gap list to from-web |
| Pasted bio text | Extract inline; run from-web for supplemental |
| Neither | Ask the user for a seed URL before proceeding ⛔ BLOCKING (open ask) |

### Step 5 — Gap analysis ⚠️ REQUIRED

Compare gathered fields vs. checklist. Flag:

- `MISSING` — not found in any source
- `UNVERIFIED` — inferred or indirect (e.g. heritage from org affiliations, not stated)
- `PARTIAL` — data found but incomplete

Present the gap summary; get a verdict from the user ⛔ BLOCKING (options: Proceed (Recommended) / Address gaps first; structured choice if supported, else numbered text options). Critical fields MISSING → ask again before assembling the note ⛔ BLOCKING (options: Proceed with gaps (Recommended) / Supply missing values); batch both questions together when both apply.

### Step 6 — Set verification tag

- Core fields (name, role, org, career) from first-party → `intel-verified`; incidental UNVERIFIED don't downgrade.
- Core fields inferred or basis = third-party → `intel-unverified`. Upgrade when first-party found.

### Step 7 — Assemble the profile note

If a note-authoring skill is installed, route there with the payload below; otherwise write the note directly, following the checklist's frontmatter schema and body sections. Payload:

- Full research brief (all gathered text, keyed by source)
- Template schema (from Step 2)
- Gap flags
- Relationship tag (from Step 3)
- Asset paths for any saved screenshots/headshots
- Research Log Inputs (from Step 1a of `workflows/from-web.md`, if web research was run)
- Destination: `<output-root>/people/<name-slug>.md` (default output root: `./intel/`)
- Confirm the destination and write authorization with the user before writing ⛔ BLOCKING (options: Authorize write / Cancel; no recommended option, explicit authorization required; structured choice if supported, else numbered text options).

Append a collapsed Research Log callout as the absolute last block in the note, after `## Notes`. Use Research Log Inputs from Step 1a. Omit any line whose value is empty or not applicable. The callout uses Obsidian-style syntax; if the user's note app doesn't render callouts, write a plain `## Research Log` section with the same field lines. Template (indented = literal callout block):

    > [!note]- Research Log
    > **Last updated:** YYYY-MM-DD
    > **Seed URLs:** [Label](https://url), ...
    > **Key searches:** `"name" award OR interview site:example.com`
    > **Date range filter:** after:2022-01-01
    > **LinkedIn:** noted only — https://linkedin.com/in/...

Omit `> **Registries / databases:**` — not applicable for person profiles. Replace `YYYY-MM-DD` with today's date at write time.

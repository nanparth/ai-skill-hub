# Workflow: from-local-notes

Notes-first: extract org data from the user's existing notes before going online.

## Inputs

- Org name (required)
- Note path(s) — direct notes about the org (optional; auto-discovered if not provided)
- Gap list from prior research pass (optional; if running as supplemental pass)

## Steps

### 1. Auto-discover note references

If no note path is provided, search the user's notes folder with whatever search the environment provides: the note app's built-in search, semantic search if available, or recursive text search (e.g. `rg "<org name>"`). Run four discovery passes:

**Pass A — Direct org notes:** search for the org name; look for existing org profile notes with a matching title or alias.

**Pass B — People notes cross-reference:** find person profile notes whose `organization:` frontmatter (or body text) matches the org. These reveal key people and relationship context without web research.

**Pass C — News and events cross-reference:** search for news, event, or happenings notes tagged with the org (e.g. `intel/org/<org-slug>`) or containing the org name.

**Pass D — Project and knowledge notes:** search project folders and knowledge-base notes for the org name. These often carry deal context, meeting notes, or analytical commentary not present in the org's own public materials.

### 2. Read discovered notes

Read each discovered note. Extract:

| Field group | What to pull |
| ----------- | ------------ |
| Frontmatter | `type`, `hq`, `website`, `founded`, `sector`, `size`, `ownership`, `ticker`, `summary` |
| Key people | Names, roles, links from any `organization:` person notes |
| Milestones | Dated events mentioned across project and news notes |
| Focus areas | Practice areas, products, or services mentioned in context |
| Affiliations | Partner orgs, regulatory references, industry body memberships |
| Context | How the org connects to the user's work; deal or relationship history |

### 3. Build extraction map

Compile a flat extraction map keyed by checklist field:

```
title:        [source note path]
hq:           [source note path]
key_people:   [{name, role, note_path}]
milestones:   [{year, event, source}]
...
```

Flag each field as `FOUND`, `PARTIAL`, or `MISSING` against the research-checklist.

### 4. Generate gap list

All `MISSING` and `PARTIAL` fields become the gap list passed to `from-web.md` for supplemental research.

### 5. Return

Return extraction map + gap list to SKILL.md Step 5 (gap analysis).

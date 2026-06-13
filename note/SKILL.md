---
name: note
version: '1.1.2'
description: 'Markdown note gateway — create, write, save, rewrite, reformat, merge notes. Use any time note content needs writing, saving, or output to .md. Trigger on: "write to [folder]", "save to [path]", "reformat", "output to", "draft", "jot down", "save as .md", "rewrite", "merge notes", "process source into notes".'
argument-hint: "<action> <file.md>"
---

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick. Artifact >40 lines (plan, change list, draft) → artifact message ends the turn; raise the choice next turn with a ≤5-line digest.

# note

Unified skill for markdown note operations. Targets Obsidian-flavoured markdown; works with any plain-markdown notes folder, with Obsidian-specific features (wikilinks, callouts, properties) documented as extensions in `references/obsidian-syntax.md`.

## Routing

Understand user intent, then load exactly one corresponding workflow file in this table:

| Intent / Signal | Route | Policy / Notes |
| --- | --- | --- |
| Meaning-preserving formatting/layout cleanup, markdown syntax normalization, conversion artefact cleanup | `workflows/reformat-note.md` | Load syntax reference: yes. No paraphrase; wording preserved. |
| User explicitly says `no paraphrase` or requires verbatim language preservation | `workflows/reformat-note.md` | Override: force reformat route even if readability is requested. |
| Content change with wording/structure transformation for clarity, tone, concision, or substantiation | `workflows/rewrite-note.md` | Load syntax reference: yes. Preserve requirements unless explicitly authorized to change. |
| Merge two or more notes into one; combine files; consolidate notes; absorb one file into another | `workflows/merge-note.md` | Load syntax reference: yes. Accepts 2+ source paths + optional destination. Output is organic synthesis, not concatenation. |
| Create/draft a new note | `workflows/new-note.md` | Load syntax reference: yes. |
| Process source material into atomic knowledge notes | `workflows/process-source.md` | Load syntax reference: yes. |

If still unclear after routing table, ask one clarifying question.

## Syntax Loading Policy

Load `references/obsidian-syntax.md` before any write-path workflow runs (all workflows in this skill are write-path).

## Shared Conventions

All workflows in this skill follow these rules:

- Match the user's writing conventions and language; if none stated, mirror the target note's existing style.
- Use `[[wikilinks]]` for internal note references when the user's note app supports them; otherwise use relative markdown links.
- Use this YAML frontmatter contract with exact quoting rules:
  ```yaml
  ---
  title:
  created at:
  tags:
    -
    -
  summary:
  ---
  ```
  **Quoting rules:** All scalar field values must be double-quoted; each `tags` list item must be individually quoted.
- Lowercase-hyphenated filenames for new files. Exception: filenames containing CJK characters (Chinese, Japanese, Korean) do not require hyphen separators.
- Date format: `YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM` (ISO 8601 with timezone offset).
- Multi-part works (book chapters, course modules, multi-part reports): apply the series conventions in `references/multipart-series.md` (extended frontmatter, `<slug>-NN-<topic>` filenames, Prev/Next nav footer, `series/<slug>` tag). `rewrite-note.md` and `reformat-note.md` load it conditionally.
- Ignore root `readme.md`/`README.md` by default; operate on them only when explicitly asked.
- Mermaid diagram creation: thumb test first — "Reader must draw this to track it?" Yes → author a fenced ```mermaid block with the inferred type and embed it inline. Consider drawing if content has ANY: directed flow with decisions/loops/branches; multi-actor message exchange; schema or typed entity relationships; state lifecycle/transitions; non-trivial hierarchy (2+ levels); temporal ordering with deps or concurrency; volumetric/proportional breakdown; causal structure. Skip if: flat list or plain enumeration; argumentative/analytical/narrative prose; single concept being defined; linear A→B→C with no branching; diagram would restate one sentence.
- In `rewrite-note` and `reformat-note`, run a mandatory readability feature review for callouts:
  - record per section/chunk decision: `add`, `convert`, or `no-change`, with reason
  - apply callouts conservatively (avoid overuse, avoid adjacent stacking unless justified, no nested callouts by default)
  - keep policy-specific behavior in each workflow (`reformat` structure-only; `rewrite` meaning-preserving paraphrase allowed)

## Property Operations

Updating a scalar property on an existing note:

1. Obsidian CLI installed → `obsidian property:set path="<path>" name="<key>" value="<val>"` for scalar values; verify with `property:read`.
2. CLI unavailable, or list-type property (tags, aliases) → read the file and edit the YAML directly.

Applies only to property updates on existing notes. New creation, rewrites, reformats unaffected.

## Long-File Conventions

For rewrite/reformat/merge operations, apply this mode switch before any mutation:

- `LONG_FILE_THRESHOLD_LINES = 500` (long mode when `line_count > 500`)
- `LONG_FILE_PREVIEW_LINES = 200`
- `LONG_FILE_TARGET_CHUNK_LINES = 250` (fallback window size)
- `LONG_FILE_CHUNKER = semantic-line` (default; `legacy` available for debug/fallback)
- `LONG_FILE_CHUNKER_CONFIG` defaults:
  - `search_back_lines = 80`
  - `search_forward_lines = 25`
  - `min_chunk_lines = 120`
  - `max_overshoot_lines = 60`
  - `tail_merge_lines = 80`
  - `decay = 0.7`
  - `distance_power = 2.0`
- Long mode runs the chunked protocol: preflight -> plan approval -> chunked execution with checkpoints -> final integrity pass.
  - Host supports subagents → dispatch one chunked operator per the workflow's invocation contract; the operator handles checkpoint reporting.
  - No subagent support → run the same protocol inline yourself: generate the preflight with the planner script below, get plan approval, execute chunk by chunk, checkpoint after each chunk.
- Preflight planner: `python "<skill-dir>/shared/text/scripts/long_file_plan.py" --file "<target>"` (or `--request-file`/`--output-file` JSON mode for non-ASCII paths).
- Don't load the full file by default in long mode; use preflight metadata and chunked reads.
- Long-mode preflight output must include: `chunking_mode`, `algorithm_version`, `chunk_stats`, `session_id`, `source_hash`, `plan_hash`.
- Long-mode execution/resume requires stable identifiers: `session_id` + `plan_hash`.
- PDF/DOCX-source artefact strippers (run in execute mode, not plan mode):
  - PUA citation artefacts: `<skill-dir>/shared/text/scripts/strip_pua_artifacts.py`
  - HTML `<details>` / `<summary>` wrappers: `<skill-dir>/shared/text/scripts/strip_html_artefacts.py`
  - Dead image embeds: `<skill-dir>/shared/text/scripts/check_dead_embeds.py`

## Output Path Policy

- Default destination for notes created or persisted by these workflows is `./notes/outputs/` under the user's notes root; confirm or adjust with the user on first write of a session.
- User-provided destination folder in current request → honour that override.
- **Merge override:** `workflows/merge-note.md` overrides this default. New-file → primary source's folder; absorb → in-place to host; `into <path>` wins. See `workflows/merge-note.md` § Output Path Override.
- Promotion from the outputs folder to long-term folders = separate explicit triage step.

## Pre-Delivery Checklist

Before saving any note, verify:

- [ ] Frontmatter complete: `title`, `created at`, `tags` (list), `summary`
- [ ] Internal links use a consistent syntax (wikilinks or relative markdown links)
- [ ] Language conventions consistent; no em dashes if the user's style bans them
- [ ] No placeholder text remains (TODO, FIXME, TBD)
- [ ] Filename: lowercase-hyphenated `.md` (exception: CJK filenames do not require hyphens)

## Delegation Guards

- Long-file operator delegation: long mode only, to one matching chunked operator per workflow.
- Never chain note operators or recurse (`note → operator → note` and `operator → operator` are disallowed).
- If user says `no` to save, terminate with chat-only output.

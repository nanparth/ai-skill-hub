# Reformat Note Workflow

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick. Artifact >40 lines → artifact message ends the turn; raise the choice next turn with a ≤5-line digest.

Reformat markdown file in place for legibility w/o changing substantive content.

## Usage

`note reformat <file-path>`

## Long-File Operator Invocation Contract

Long mode: if the host supports subagents, dispatch a chunked reformat operator with this payload shape; otherwise run the same protocol inline yourself (preflight via `<skill-dir>/shared/text/scripts/long_file_plan.py`, plan approval, chunk-by-chunk execution with checkpoints).

```json
{
  "mode": "plan|execute|resume",
  "target_path": "path relative to notes root",
  "workflow": "reformat-note",
  "line_threshold": 500,
  "preview_lines": 200,
  "chunk_lines": 250,
  "chunker": "semantic-line",
  "chunker_config": {
    "search_back_lines": 80,
    "search_forward_lines": 25,
    "min_chunk_lines": 120,
    "max_overshoot_lines": 60,
    "tail_merge_lines": 80,
    "decay": 0.7,
    "distance_power": 2.0
  },
  "intent": "formatting-only reformat",
  "constraints": ["no substantive edits"],
  "feature_review": { "callouts": "required" },
  "callout_policy": "reformat-structure-only",
  "session_id": "required for execute/resume",
  "plan_hash": "required for execute/resume"
}
```

## Instructions

- [ ] Step 0: Load formatting authority first REQUIRED
 - [ ] 0.1 Load references/obsidian-syntax.md before any other workflow action.

- [ ] Step 1: Resolve target and mode ⛔ BLOCKING
 - [ ] 1.1 User must provide an explicit file path.
 - [ ] 1.2 Determine line count before loading the file body.
 - [ ] 1.3 Apply mode switch:
 - [ ] `line_count <= 500`: normal mode. Read file in full before changes.
 - [ ] `line_count > 500`: long mode. Don't load full file; run preflight (`mode = plan`, `chunker = semantic-line`) per the invocation contract above.
 - [ ] 1.4 Multi-part series detection: if this file is one part of a multi-part work processed as a series, load `references/multipart-series.md`. Reformat may add the additive series scaffolding (extended frontmatter keys, Prev/Next nav footer, `series/<slug>` tag, filename rename); it must NOT rewrite prose.

- [ ] Step 3: Analyse and build change list ⛔ BLOCKING
 - [ ] 3.1 Normal mode: prepare one change list across all categories.
 - [ ] 3.2 Evaluate callout opportunities per section/chunk; record one decision: `add`, `convert`, or `no-change`, with reason.
 - [ ] 3.3 Callout edits are structure-only in this workflow:
 - [ ] preserve source wording verbatim inside callouts except already-allowed whitespace/punctuation normalization
 - [ ] do not introduce new claims, requirements, or interpretation in callout titles or body text
 - [ ] copy callout titles from nearby text or use neutral labels only
 - [ ] 3.4 Apply callout heuristics conservatively:
 - [ ] favour callouts for key takeaway, caveat/risk, decision, action checklist, and definition/context blocks
 - [ ] avoid callouts for dense citation-only blocks, footnotes, and purely narrative continuity where callouts reduce flow
 - [ ] avoid adjacent callout stacking unless clearly justified
 - [ ] do not nest callouts by default
 - [ ] 3.5 Long mode: prepare semantic chunk plan and formatting-only change list.
 - [ ] 3.6 PUA artifact pre-strip (run before all other analysis)
 - [ ] Run `python "<skill-dir>/shared/text/scripts/strip_pua_artifacts.py" "<file-path>" --fix` and capture JSON output.
 - [ ] If `total_artifacts > 0`: report counts by type (`cite_removed`, `entity_replaced`, `unknown_stripped`) and surface any `unknown_samples` to user before continuing.
 - [ ] If `unknown_stripped > 0`: pause and show samples ⛔ BLOCKING. Present a structured choice (never free text): "Stripping correct?" options: Confirm (Recommended) / Review samples (fallback: numbered text options).
 - [ ] Zero cost when clean (exit 0, `total: 0`).
 - [ ] Long-mode: plan must NOT run this strip (hash capture). Defer to execute Step 3, before first chunk.
 - [ ] 3.6b HTML artefact check (PDF/DOCX-source `<details>`/`<summary>` wrappers)
 - [ ] Trigger: `source_type: "pdf"` or `source_type: "docx"` in frontmatter.
 - [ ] Run `python "<skill-dir>/shared/text/scripts/strip_html_artefacts.py" "<file-path>" --check` and capture JSON output.
 - [ ] Exit 0 / `total_artefacts: 0`: silent pass, continue. No user mention.
 - [ ] Exit 2 / `total_artefacts > 0`: surface counts + up to 5 `samples` ⛔ BLOCKING. Present a structured choice: "Apply `--fix` or leave as-is?" options: Apply --fix (Recommended) / Leave as-is (fallback: numbered text options). Honour answer.
 - [ ] On user approval, re-run with `--fix`; capture JSON and include counts in change list.
 - [ ] On user decline, proceed without mutation.
 - [ ] Rationale: stripper deletes wrapper tags, preserves inner content. Some converters normalize upstream; hand-authored collapsibles may want wrappers preserved; human decides.
 - [ ] Zero-cost when file is clean.
 - [ ] Long-mode: `--check` OK in plan (read-only); `--fix` defers to execute pre-first-chunk after approval.
 - [ ] 3.7 External media stripping (run after PUA pre-strip, before formatting categories)
 - [ ] Strip externally-linked images: `![...](https://...)`, `![...](data:image/...)`, `![...](data:image/svg+xml,...)`.
 - [ ] Strip HTML media tags: `<video ...>...</video>`, `<audio ...>...</audio>`, `<iframe ...>...</iframe>`.
 - [ ] Preserve local embeds: `![[...]]` syntax untouched — **except** dead embeds caught in Step 3.7a.
 - [ ] Captions: keep informational (attribution, figure descriptions, source citations); strip decorative-only (bare "Image", "Photo", empty alt-text).
 - [ ] Clean orphaned blank lines left by removed media (collapse to single blank).
 - [ ] 3.7a Dead wikilink embed check (run after external strip, before formatting categories)
 - [ ] Run `python "<skill-dir>/shared/text/scripts/check_dead_embeds.py" "<file-path>" --check` and capture JSON output.
 - [ ] Exit 0 / `total_dead: 0`: silent pass, continue.
 - [ ] Exit 2 / `total_dead > 0`: surface paths in plan table as `dead_wikilinks_detected`; strip in execute preamble.
 - [ ] Long-mode: `--check` plan mode only; `--fix` deferred to execute preamble (same pattern as `strip_pua_artifacts.py`).
 - [ ] Report `dead_wikilinks_detected` count in plan; `dead_wikilinks_stripped` count in execute checkpoint.
 - [ ] 3.8 Cover these formatting categories:
 - [ ] encoding and conversion artefact cleanup
 - [ ] heading/footnote/blockquote structure normalization
 - [ ] spacing and typographic consistency
 - [ ] frontmatter contract normalization w/o changing classification tags
 - [ ] paragraph text reflow: join hard-wrapped continuation lines within prose paragraphs
 - [ ] shadow tag escape: wrap bare `#WORD` tokens (Excel errors, preprocessor directives, developer markers) in backtick inline code. Skip frontmatter, code fences, existing inline code. Preserve intentional tags.
 - [ ] conversion artefact reunification: remove spurious blank lines and merge split heading+citation pairs in converted sources
 - [ ] frontmatter metadata enrichment: enrich tags and summary from body text where thin or missing
 - [ ] filename normalization: if filename contains uppercase or spaces, propose rename to lowercase-kebab
 - [ ] mermaid block syntax: validate + fix existing blocks only; no new blocks
 - [ ] math block normalization: fix `$$` at end of prose line; remove blank lines inside `$$` blocks
 - [ ] inline HTML block normalization: detect block-level HTML not at line start; convert or move to own line
 - [ ] 3.9 Conversion artefact reunification
 - [ ] Trigger: `source_type: "pdf"` or `source_type: "docx"` in frontmatter. Run before paragraph reflow (3.13).
 - [ ] 3.9a Spurious blank line removal. Single blank line between two non-empty body lines is artefact if ALL:
 - Preceding line lacks terminal punctuation (`.` `?` `!` `:`)
 - Preceding line not block-level marker (heading, list, blockquote, code fence, horizontal rule, table row, footnote def)
 - Following line not block-level marker
 - Following line not itself blank (single blank only, not double+)
 - Neither line inside code fence
 - [ ] Action: remove blank line. Subsequent reflow (3.13) joins resulting adjacent lines.
 - [ ] Preserved: blank lines after terminal punctuation (real paragraph breaks), adjacent to block markers, double+ blanks.
 - [ ] 3.9b Heading citation reunification. H3 followed by blank line + H4 matching citation pattern (`\d{4}\s+[A-Z]{2,}.*\d+` or `\[\d{4}\]`): merge into single H3 with comma separator. Remove H4 and intervening blank.
 - [ ] 3.10 Frontmatter metadata enrichment
 - [ ] Scope: `summary` and `tags`. No external lookups.
 - [ ] Summary: missing/empty/duplicated from another field → generate from body. Reasonable summary exists → no-change.
 - [ ] Tags: thin or missing → derive from body (user's tag-taxonomy file vocabulary preferred when one exists).
 - [ ] Guardrail: descriptive labelling only. No claims, interpretations, or classifications unsupported by body text.
 - [ ] 3.11 Long-mode plan table must include:
 - [ ] `chunk id`
 - [ ] `source line range`
 - [ ] `callout_decision` (`add|convert|no-change`)
 - [ ] `callout_reason`
 - [ ] `callout_scope` (heading/block target)
 - [ ] `reflow_detected` (true/false)
 - [ ] `reflow_line_count` (estimated number of continuation lines to join)
 - [ ] `boundary_type`
 - [ ] `boundary_score`
 - [ ] `boundary_note`
 - [ ] `formatting actions only`
 - [ ] `artefact_blank_lines_removed` (count)
 - [ ] `heading_citations_merged` (count)
 - [ ] `metadata_enrichment` (`summary-added`|`no-change`)
 - [ ] `external_media_stripped` (count)
 - [ ] `dead_wikilinks_detected` (count; 0 if none)
 - [ ] `math_blocks_normalized` (count; 0 if none)
 - [ ] `html_blocks_converted` (count; 0 if none)
 - [ ] `hierarchy_audit` (`flat|ok`; mandatory for all files)
 - [ ] `related_section` (`missing|already-present`)
 - [ ] 3.12 Long-mode metadata must be visible in plan:
   - [ ] `chunking_mode = semantic-line`
   - [ ] `algorithm_version`
   - [ ] `chunk_stats`
   - [ ] `session_id`
   - [ ] `source_hash`
   - [ ] `plan_hash`
   - [ ] `planner_invocation_strategy`
   - [ ] `planning_quality`
   - [ ] `planner_elapsed_ms`
   - [ ] `fallback_used`
   - [ ] `fallback_reason` when relevant
 - [ ] 3.13 Paragraph reflow rules
 - [ ] Trigger: `source_type: "pdf"` or `"docx"` in frontmatter; or scan: lines ending mid-clause (no `.` `?` `!` `:`) with non-blank continuation are >10% of body → apply.
 - [ ] A line is a hard-wrapped continuation if ALL of:
 - It is non-empty
 - Preceding line non-empty, no terminal punctuation (`.` `?` `!` `:`)
 - Neither line starts a block-level marker: heading (`#`), list (`-` `*` `+` `1.`), blockquote (`>`), code fence (` ``` `), horizontal rule (`---`/`***`), table row (`|`), footnote definition (`[^`)
 - No blank line separates the two lines
 - [ ] Do NOT join across blank lines (paragraph boundaries).
 - [ ] Do NOT join lines inside code fences.
 - [ ] Do NOT join blockquote lines (separate quoted units); reflow only if `>` lines are mid-sentence hard-wraps within a single blockquote paragraph.
 - [ ] Do NOT join intentional formal enumeration. Signals:
 - Preceding line ends with `;` (clause enumeration in contracts, statutes, formal instruments)
 - Current line begins with sub-clause marker: `(a)`, `(i)`, `a.`, `(1)`, `1.`, or similar legal numbering
 - [ ] Join by replacing the hard newline with a single space. Do not alter wording.
 - [ ] 3.14 Heading hierarchy audit (all files)
 - [ ] Trigger: unconditional — run heading inventory on every file.
 - [ ] Flat test: `h1_count > 1`.
 - [ ] Flat detected → build `global_demotion_map`: `[{line, heading_text, current_level, target_level}]`. title → H1; `# N` → H2; `# N.M` → H3; `# N.M.K` → H4; non-numbered back-matter → H2. Apply from map only; never compute level shifts chunk-by-chunk.
 - [ ] Flag broken headings: single-word lowercase (OCR), `# <digits>$` (bare page numbers), duplicates at same level (PDF artefacts) → remove or demote.
 - [ ] Normal mode: apply inline during execution.
 - [ ] Long mode: include `hierarchy_audit` + `global_demotion_map` in plan payload; apply during chunk execution.
 - [ ] 3.14a Plan-mode hierarchy_audit disclosure (long mode) ⛔ BLOCKING
 - [ ] Plan payload MUST include a `hierarchy_audit` block containing:
 - `heading_counts`: `{h1: N, h2: N, h3: N}`
 - `flat_detected`: `true|false`
 - `global_demotion_map`: `[{line, heading_text, current_level, target_level}]` — required when `flat_detected: true`; omit when false
 - [ ] `flat_detected: true` + `hierarchy_audit` absent → plan **INVALID**.
 - [ ] `h1_count == 1` → emit `hierarchy_audit: {flat_detected: false}`.

 - [ ] 3.15 Related section check
 - [ ] Scan file for an existing `## Related` section.
 - [ ] Present: flag `related_section = already-present`; no further action.
 - [ ] Absent: flag `related_section = missing`. Optionally add at Step 5.5 after write completes — do NOT attempt link resolution here.

 - [ ] 3.16 Math block normalization
 - [ ] Scan body (skip code fences): `$$` preceded by non-whitespace on same line → split; place `$$` on own line.
 - [ ] Scan body: blank line between `$$` opener and `$$` closer → remove blank.
 - [ ] Report `math_blocks_normalized` (0 if clean). Do NOT fix in plan mode; defer to execute pre-chunk.

 - [ ] 3.17 HTML inline block detection
 - [ ] Scan body (skip code fences + backticks): `<table`, `<div`, `<details`, `<summary` not at line start → flag.
 - [ ] Simple table (no `rowspan`/`colspan` attrs): convert to markdown table.
 - [ ] Complex table or other tag: move opening tag to own line (block-level HTML); preserve inner content.
 - [ ] Report `html_blocks_converted` (→ markdown), `html_blocks_moved` (→ own line). Do NOT fix in plan mode.

- [ ] Step 4: Confirm change list with user ⛔ BLOCKING
  - [ ] 4.1 Present full change list (incl. callout decisions + proposed summary); verdict via structured choice (never free text): "Proceed with this change list?" options: Proceed (Recommended) / Adjust. Fallback (no structured choice support): numbered options in plain text; wait for reply. Long mode: no chunk write before approval. Change list >40 lines → list message ends the turn; raise the choice next turn with ≤5-line digest.
  - [ ] 4.2 For files in user-designated read-only folders, explicitly note the user-requested override in confirmation.
  - [ ] 4.3 Confirm proposed callout decisions (`add|convert|no-change`) before execution (same structured-choice call as 4.1).
  - [ ] 4.6 Show proposed summary text before applying.
  - [ ] 4.4 Long-mode approval output must visibly disclose planning method and quality:
    - [ ] `planner_invocation_strategy = python-cli | manual-fallback`
    - [ ] `planning_quality = full-scored | reduced-fallback`
    - [ ] `planner_elapsed_ms`
    - [ ] `fallback_used`
    - [ ] `fallback_reason` when relevant
  - [ ] 4.5 If fallback used: state chunk plan safe but less optimized than scored planner output.
- [ ] Step 5: Execute reformat
 - [ ] 5.1 Normal mode: apply formatting in-place.
 - [ ] If filename rename was confirmed: Obsidian CLI installed → `obsidian rename` after content edits (auto-updates wikilinks); else rename the file and check inbound links from sibling notes.
  - [ ] 5.2 Long mode:
    - [ ] execute with `mode = execute`, `session_id`, and `plan_hash` (operator dispatch or inline)
    - [ ] execute chunk-by-chunk in deterministic order
    - [ ] emit checkpoint after each chunk: `status`, `completed_chunks`, `next_chunk`, `total_chunks`, `notes`, `plan_hash`, `source_hash`, `staging_output_path`, `updated_at`, `callout_actions_applied`, `callout_actions_remaining`, `dead_wikilinks_stripped`, `planner_invocation_strategy`, `planning_quality`, `planner_exit_code`, `planner_stderr_excerpt`, `planner_elapsed_ms`, `non_ascii_target_path`, `fallback_used`, `fallback_reason`
    - [ ] continue automatically unless anomaly/conflict blocks progress
 - [ ] 5.3 If interrupted, resume with `mode = resume` using the same `session_id` and `plan_hash`.
 - [ ] 5.4 If hash mismatch is returned (`source_changed_replan_required`), re-run plan mode before continuing.
 - [ ] 5.5 If `related_section = missing`: optionally append a `## Related` section linking existing related notes (user-named or found in the note's folder). Never fabricate links to non-existent notes; skip silently if none known.
 - [ ] 5.6 Tag refresh: derive tags from final content (user's taxonomy vocabulary preferred when a taxonomy file exists); replace `tags:` in frontmatter.

- [ ] Step 6: Final integrity pass
 - [ ] 6.1 Confirm frontmatter minimum keys and quoting are valid.
 - [ ] 6.2 Confirm heading sequence and block structure are valid markdown.
 - [ ] 6.3 Validate callout syntax where callouts are added/converted.
 - [ ] 6.4 Confirm no substantive text edits were introduced.
 - [ ] 6.5 PUA residual: run `strip_pua_artifacts.py "<path>" --check`. Exit 0 = pass. Exit 2 = fail; re-run `--fix`.
 - [ ] 6.6 Confirm no bare shadow tags in body (`#WORD` outside frontmatter, code blocks, backtick spans).
 - [ ] 6.7 Report `callout_verbatim_preservation` pass/fail (callout bodies keep source wording except allowed formatting normalization).
 - [ ] 6.8 Confirm summary factual.
 - [ ] 6.9 Confirm filename is lowercase-kebab; if rename was applied, verify the file exists at the new path.
 - [ ] 6.10 Confirm no external media embeds remain (scan for `![...](https://`, `data:image/`, `<video`, `<audio`, `<iframe`).
 - [ ] 6.11 HTML artefact residual: run `strip_html_artefacts.py "<path>" --check`. Exit 0 = pass. Exit 2 = report counts; do not auto-fix. Non-blocking.
 - [ ] 6.12 Heading hierarchy sanity:
 - [ ] File has exactly one H1.
 - [ ] No heading is a single lowercase word (OCR prose-fragment guard).
 - [ ] No heading matches `# Figure \d` or `# Table \d` (caption guard).
 - [ ] No heading matches `^# \d+$` (bare page-number guard).
 - [ ] No duplicate section headings at the same level (PDF page-header artefact guard).
 - [ ] 6.13 Note `related_section` status (`already-present` or `missing`). Do not fail integrity pass on `missing`.

- [ ] Step 7: Report changes
 - [ ] 7.1 Group report by category with counts.
 - [ ] 7.2 In long mode, include checkpoint progression summary and resume/replan notes.
 - [ ] 7.3 Include callout outcome summary (`add|convert|no-change`) with reasons.
 - [ ] 7.4 Report metadata enrichment with before/after summary.
 - [ ] 7.5 Report external media stripped count (images, video, audio, iframes) and captions kept/stripped.
 - [ ] 7.6 Report `related_section` status and tag update outcome.
 - [ ] 7.7 Report `math_blocks_normalized` count.
 - [ ] 7.8 Report `html_blocks_converted` + `html_blocks_moved` counts.

## Guardrails

- No substantive edits. Do not alter meaning, claims, arguments, or evidence.
- No new mermaid blocks — content change, out of scope. Fix syntax of existing blocks only (Step 3.8).
- Not this workflow: paraphrasing, sentence rewrites for clarity/tone, or requirement reframing.
- Reformat may add or convert callouts only as presentation containers.
- Preserve source wording verbatim inside callouts except already-allowed whitespace/punctuation normalization.
- Never introduce new claims, requirements, or interpretation in callout titles/body text.
- Preserve file in place. Do not move, rename, or copy (confirmed lowercase-kebab rename excepted).
- Files in user-designated read-only folders are allowed only when user explicitly requests reformat.
- Never create new notes; modify one existing file per invocation.
- Never treat root `readme.md`/`README.md` as reformat targets unless explicitly requested.

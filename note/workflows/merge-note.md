# Merge Note Workflow

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick. Artifact >40 lines → artifact message ends the turn; raise the choice next turn with a ≤5-line digest.

Merge 2+ notes: new-file mode (new synthesised file) or absorb mode (foreign into host). Output = organically coherent; transformation varies by theme.

## Usage

`note merge <source1> <source2> [... sourceN] [into <destination>]`

## Organic Synthesis Principle

Merged **output** = organically coherent: unified voice, theme-driven structure, no source-tagged sections. Path ≠ uniform heavy rewriting. When one source expresses a theme well, preserve verbatim. Mix across sources — some sections intact, others synthesised, as content demands.

Per theme, judge the transformation needed:

| Situation | Action |
|---|---|
| Dominant source covers the theme well; foreign sources add nothing new | Keep dominant prose verbatim. Audit foreign coverage as "subsumed". |
| Dominant source covers the theme; foreign material extends it | Preserve dominant prose; weave foreign material in at natural insertion points; light rewriting only for voice continuity. |
| Dominant source covers the theme; foreign material contradicts or updates it | Rewrite the passage to integrate the correction; preserve voice where possible. |
| Multiple sources cover the theme with partial, complementary content | Synthesise heavily into unified prose. |
| Multiple sources cover the theme with overlapping content | Unify; drop redundant expression; preserve the strongest phrasing. |
| One source has a structurally excellent section; others do not touch it | Preserve verbatim. |
| Structurally strong section with minor updates from another source | Preserve structure and most prose; rewrite selectively. |

Framing: ask "what transformation does this theme need?" — not "should I rewrite everything?" Preservation = valid default when prose works.

## Long-File Operator Invocation Contract

Long mode: if the host supports subagents, dispatch a chunked merge operator with this payload shape; otherwise run the same protocol inline yourself (preflight via `<skill-dir>/shared/text/scripts/long_file_plan.py`, plan approval, chunk-by-chunk execution with checkpoints).

```json
{
  "mode": "plan|execute|resume",
  "source_paths": ["path", "path"],
  "destination_path": "path",
  "merge_mode": "new-file|absorb",
  "workflow": "merge-note",
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
  "theme_outline": "theme-driven output outline with per-theme transformation decisions",
  "source_coverage": "audit mapping: which source passages each theme must cover",
  "intent": "merge summary",
  "constraints": ["merge guardrails"],
  "session_id": "required for execute/resume",
  "plan_hash": "required for execute/resume"
}
```

## Output Path Override

Merge overrides the SKILL.md Output Path Policy. The default outputs folder does NOT apply — merges consolidate in project context.

- **Default destination (new-file mode):** same folder as the first-listed source file.
- **Explicit:** `note merge <A> <B> into <path>` — overrides everything.
- **Absorb:** destination = host file in place; `into <path>` invalid.

## Long-File Gate Estimation

The gate triggers when any single source exceeds 500 lines OR the estimated combined output exceeds 500 lines. Estimation heuristics:

- **New-file merge:** sum of all source line counts (upper bound; synthesis typically reduces).
- **Absorb merge:** host line count + sum of foreign source line counts.

## Instructions

- [ ] Step 0: Load formatting authority ⚠️ REQUIRED
  - [ ] 0.1 Load `references/obsidian-syntax.md` before any other workflow action.

- [ ] Step 1: Resolve sources and merge mode ⛔ BLOCKING
  - [ ] 1.1 Require 2+ explicit file paths; if fewer: "merge requires 2+ sources; use the rewrite workflow for single-file."
  - [ ] 1.2 Verify sources exist and are readable. Reject files in user-designated read-only folders and `readme.md`/`README.md` unless user requests.
  - [ ] 1.3 Read all sources: frontmatter (title, created at, tags, summary), line count, word count, H1, H2 inventory.
  - [ ] 1.4 Auto-detect merge mode:
    - [ ] One source ≥ 3x longer (by word count) than the sum of all other sources → suggest absorb (that source as host).
    - [ ] Otherwise → suggest new-file merge.
  - [ ] 1.5 Confirm merge mode ⛔ BLOCKING. Present a structured choice; never present these options as free text. question: "Merge as new file or absorb into host?" options: New file / Absorb into host. Auto-detected mode from 1.4 first, labelled "(Recommended)". Absorb: confirm host in same call; "Other" captures different host (fallback: numbered text options).
  - [ ] 1.6 Resolve destination path:
    - [ ] Explicit `into <path>` provided (new-file mode only) → use that path.
    - [ ] New-file w/o explicit destination → first-listed source folder; derive filename in Step 2.
    - [ ] Absorb mode → destination is the host file path (in-place modification).
  - [ ] 1.7 Long-file gate check per estimation heuristics above.
    - [ ] `estimated_output <= 500`: normal mode.
    - [ ] `estimated_output > 500`: long mode. Run preflight (`mode = plan`) per the invocation contract (see Step 3.6).

- [ ] Step 2: Frontmatter reconciliation plan ⛔ BLOCKING
  - [ ] 2.1 Collect all source frontmatter.
  - [ ] 2.2 Compute `tags` union (deduplicated, alphabetically ordered).
  - [ ] 2.3 If the user maintains a tag-taxonomy file, read it and validate all union tags exist; flag any unknown tags to the user. No taxonomy file → skip validation.
  - [ ] 2.4 Merged scope introduces new concept → propose tag (lowercase, hyphenated) with one-line description.
  - [ ] 2.5 Confirm final tag set ⛔ BLOCKING. Present a structured choice: "Apply this merged tag set?" options: Confirm (Recommended) / Adjust. "Other" captures edits (fallback: numbered text options).
  - [ ] 2.6 Derive `title`:
    - [ ] Explicit destination filename provided → derive title from filename.
    - [ ] New-file w/o explicit destination → combine key nouns from H1 titles; propose filename (lowercase-hyphenated) + title.
    - [ ] Absorb mode → preserve host's existing title unless user requests change.
    - [ ] Confirm title and filename ⛔ BLOCKING: batch into same structured-choice call as 2.5. options: Confirm (Recommended) / Adjust. "Other" captures alternative title/filename (fallback: numbered text options).
  - [ ] 2.7 Select earliest `created at` across all sources (preserves provenance).
  - [ ] 2.8 Draft `summary` covering the merged scope. Never concatenate source summaries; write a genuine synthesis.

- [ ] Step 3: Build theme-driven output outline with per-theme transformation decisions ⛔ BLOCKING
  - [ ] 3.1 Identify shared themes (heading overlap, topical clustering, content similarity). Themes ≠ source boundaries.
  - [ ] 3.2 Build the outline:
    - [ ] New-file mode: order themes for narrative coherence; structure emerges from shared themes, not from source order.
    - [ ] Absorb: anchor outline to host's heading structure; map foreign material to host themes or propose new themes for foreign-only material.
  - [ ] 3.3 Per theme, record transformation decision per Organic Synthesis table: `preserve_verbatim`, `preserve_with_light_edit`, `integrate_foreign`, `synthesise_heavily`, `unify_overlap`, or `rewrite_with_correction`.
  - [ ] 3.4 Build source-coverage audit: map every source passage to covering themes. Split across themes (rare) or mark `dropped_with_reason` (justify to user). Unmapped passages = planning bug; fix before proceeding.
  - [ ] 3.5 Merge `## Related` sections from all sources: collect links, deduplicate by target path (normalise display text differences). If the combined set exceeds 8, curate down with user confirmation.
  - [ ] 3.6 Long mode: run preflight (`mode = plan`). Returns chunk plan, theme_outline, source_coverage, session_id, source_hash, plan_hash. Use for Step 4.
  - [ ] 3.7 Long-mode plan output must include: `chunking_mode`, `algorithm_version`, `chunk_stats`, `session_id`, `source_hash`, `plan_hash`, `planner_invocation_strategy`, `planning_quality`.

- [ ] Step 4: Confirm plan with user ⛔ BLOCKING
  - [ ] 4.1 Present to user:
    - [ ] merge mode (new-file vs absorb) and destination path
    - [ ] reconciled frontmatter (title, tags, created at, summary)
    - [ ] theme outline with per-theme transformation decisions
    - [ ] source coverage audit (which source passages each theme covers; any passages marked `dropped_with_reason` with justification)
    - [ ] merged `## Related` links
  - [ ] 4.2 Do not mutate any file before user approval. Verdict via structured choice (never free text): "Proceed with this merge plan?" options: Proceed (Recommended) / Adjust. Fallback (no structured choice support): numbered options in plain text; wait for reply. Plan >40 lines (typical for merges) → plan message ends the turn; raise the choice next turn with ≤5-line digest.
  - [ ] 4.3 User may adjust transformation decisions ("keep this section verbatim; synthesise that one heavily"), reorder themes, or change coverage.
  - [ ] 4.4 Long mode: explicitly confirm the chunk plan in addition to the theme outline (same structured-choice call).

- [ ] Step 5: Execute merge following approved transformation decisions
  - [ ] 5.1 Normal/new-file mode: create the new file at the destination path. For each theme, follow its `transformation_decision`:
    - [ ] `preserve_verbatim`: copy the designated source passage unchanged.
    - [ ] `preserve_with_light_edit`: copy source passage; edit only for voice continuity at entry and exit transitions.
    - [ ] `integrate_foreign`: weave material from multiple sources into unified prose under the theme.
    - [ ] `synthesise_heavily`: write new prose that integrates material from all covering sources; do not copy source phrasing.
    - [ ] `unify_overlap`: drop redundant expression; preserve the strongest phrasing.
    - [ ] `rewrite_with_correction`: rewrite the passage to integrate the correction; preserve voice where possible.
  - [ ] 5.2 Normal/absorb: rewrite host in place. Host voice = baseline; preserve host prose; integrate foreign under host themes per decisions; rewrite only where integration demands.
  - [ ] 5.3 Long mode: execute with `mode = execute`, `session_id`, `plan_hash`, `theme_outline`, `source_coverage` (operator dispatch or inline).
  - [ ] 5.4 Long mode: emit checkpoint after each chunk (fields per operator output contract).
  - [ ] 5.5 If interrupted in long mode, resume with `mode = resume` using same `session_id` and `plan_hash`.
  - [ ] 5.6 If hash mismatch returned (`source_changed_replan_required`), re-run Step 3 plan mode with fresh source reads.
  - [ ] 5.7 If new tags approved in Step 2 and the user maintains a tag-taxonomy file, append the new tags there.
  - [ ] 5.7a After content assembled: scan for process/architecture/workflow/state machine → author a fenced ```mermaid block; embed inline. Note in Step 7.
  - [ ] 5.8 Never delete source files; deletion is the caller's responsibility (Step 7 reports this explicitly).

- [ ] Step 6: Final integrity pass
  - [ ] 6.1 Validate frontmatter contract and quoting: all scalar values double-quoted; each `tags` list item individually quoted.
  - [ ] 6.2 Validate heading continuity and order.
  - [ ] 6.3 Validate link syntax in `## Related`.
  - [ ] 6.4 Every source passage represented (preserve/integrate/synthesise) or marked `dropped_with_reason`. Unaccounted = failure.
  - [ ] 6.5 Scan output for source-tagged markers ("from Source A", filenames inline). Fail if any found.
  - [ ] 6.6 Scan output for raw H1 concatenation (both source H1 titles appearing verbatim in output). Fail if detected.
  - [ ] 6.7 Confirm no duplicated section blocks from sources.
  - [ ] 6.8 Shadow tag scan: no bare `#WORD` tokens outside frontmatter, code blocks, or backtick spans.
  - [ ] 6.9 Confirm output organically coherent: unified voice, no voice-shift attribution to single source, overlapping content unified.
  - [ ] 6.10 Confirm source files untouched (all in new-file mode; foreign in absorb mode).
  - [ ] 6.11 Flag merged file >800 lines (not failure; review over-consolidation).

- [ ] Step 7: Report
  - [ ] 7.1 List sources merged, destination path, merge mode used.
  - [ ] 7.2 Summarise per-theme transformation decisions applied.
  - [ ] 7.3 Report any source passages marked `dropped_with_reason`.
  - [ ] 7.4 In long mode, include final checkpoint summary and any resume/replan events.
  - [ ] 7.5 State: source files NOT deleted. Cleanup = separate explicit step.

## Guardrails

- Never auto-detect which files to merge; sources must be explicitly provided.
- Never delete source files; caller's responsibility.
- Never execute w/o user confirmation on merge plan.
- Never concatenate source passages or produce source-tagged sections ("from Source A", filename inline markers).
- Never rewrite prose that already works; preservation = valid default.
- Preserve existing callouts; do not add new ones during merge (rewrite-workflow concern).
- Files in user-designated read-only folders are not permitted merge targets; redirect to new-note or process-source flow.
- Never treat root `readme.md`/`README.md` as merge sources unless user explicitly requests.
- Merge exactly the sources specified per invocation; never discover additional merge candidates.
- Wrap technical `#WORD` tokens in backtick inline code to prevent shadow tags.
- Output must be organically coherent per the Organic Synthesis Principle: unified voice, theme-driven structure, no reader-visible source boundaries.

## Conventions

- Keep frontmatter tags lowercase.
- Shadow tag prevention per `obsidian-syntax.md` Shadow Tag Hazards section.
- Match the user's language conventions; no em dashes if the user's style bans them.
- Check for existing notes on the same topic before creating the merged output (new-file mode only).

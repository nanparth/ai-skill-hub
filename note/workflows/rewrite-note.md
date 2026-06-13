# Rewrite Note Workflow

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick. Artifact >40 lines → artifact message ends the turn; raise the choice next turn with a ≤5-line digest.

Rewrite an existing note in place: structure, content, grouping, voice. Unlike `reformat-note.md` (formatting only), content-level edits expected.

## Usage

`note rewrite <file-path>`

## Long-File Operator Invocation Contract

Long mode: if the host supports subagents, dispatch a chunked rewrite operator with this payload shape; otherwise run the same protocol inline yourself (preflight via `<skill-dir>/shared/text/scripts/long_file_plan.py`, plan approval, chunk-by-chunk execution with checkpoints).

```json
{
  "mode": "plan|execute|resume",
  "target_path": "path relative to notes root",
  "workflow": "rewrite-note",
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
  "intent": "user-request summary",
  "constraints": ["rewrite guardrails"],
  "feature_review": { "callouts": "required" },
  "callout_policy": "rewrite-meaning-preserving",
  "session_id": "required for execute/resume",
  "plan_hash": "required for execute/resume"
}
```

## Instructions

- [ ] Step 0: Load formatting authority first ⚠️ REQUIRED
 - [ ] 0.1 Load `references/obsidian-syntax.md` before any other workflow action.

- [ ] Step 1: Resolve target and mode ⛔ BLOCKING
 - [ ] 1.1 User must provide an explicit file path or unambiguous reference.
 - [ ] 1.2 Determine line count before loading the file body.
 - [ ] 1.3 Apply mode switch:
 - [ ] `line_count <= 500`: normal mode. Read the file in full before drafting changes.
 - [ ] `line_count > 500`: long mode. Don't load full file; run preflight (`mode = plan`, `chunker = semantic-line`) per the invocation contract above.
 - [ ] 1.4 Identify what user wants changed: structure, voice, grouping, substantiation, or specific combination. Ask if unclear.
 - [ ] 1.5 Multi-part series detection: if this file is one part of a multi-part work (book chapter, course module, multi-part report) processed as a series, load `references/multipart-series.md` and apply its frontmatter, filename, nav-footer, and `series/<slug>` tag conventions. Batch orchestration across N files uses the wave pattern in that reference; each invocation still edits one file.

- [ ] Step 3: Build rewrite plan ⛔ BLOCKING
 - [ ] 3.0 PDF/DOCX-source artefact handling (trigger: `source_type: "pdf"` or `source_type: "docx"`)
 - [ ] PUA strip: run `python "<skill-dir>/shared/text/scripts/strip_pua_artifacts.py" "<path>" --fix` and capture JSON output. PUA tokens are unambiguous garbage; always fix.
 - [ ] HTML wrapper check: run `python "<skill-dir>/shared/text/scripts/strip_html_artefacts.py" "<path>" --check` and capture JSON output.
 - Exit 0 / `total_artefacts: 0`: silent pass, no user mention.
 - Exit 2 / `total_artefacts > 0`: surface counts + up to 5 `samples` ⛔ BLOCKING. Present a structured choice: "Apply `--fix` or leave as-is?" options: Apply --fix (Recommended) / Leave as-is (fallback: numbered text options). Re-run on approval.
 - Rationale: wrapper tags may carry semantic labels from upstream converters. Human decides; never auto-fix.
 - [ ] Report PUA counts (always) and HTML counts (if fixed) in change list.
 - [ ] Long-mode: plan must NOT run PUA `--fix` (hash capture). HTML `--check` read-only → OK in plan; HTML `--fix` defers to execute Step 5, before first chunk, after approval.
 - [ ] 3.0a External media stripping (run unconditionally, after 3.0)
   - [ ] Strip externally-linked images: `![...](https://...)`, `![...](data:image/...)`, `![...](data:image/svg+xml,...)`.
   - [ ] Strip HTML media tags: `<video ...>...</video>`, `<audio ...>...</audio>`, `<iframe ...>...</iframe>`.
   - [ ] Preserve local embeds: `![[...]]` syntax untouched — **except** dead embeds caught in 3.0b.
   - [ ] Captions: keep informational (attribution, figure descriptions, source citations); strip decorative-only (bare "Image", "Photo", empty alt-text).
   - [ ] Clean orphaned blank lines left by removed media (collapse to single blank).
 - [ ] 3.0b Dead wikilink embed check (run after 3.0a, before planning)
   - [ ] Run `python "<skill-dir>/shared/text/scripts/check_dead_embeds.py" "<file-path>" --check` and capture JSON output.
   - [ ] Exit 0 / `total_dead: 0`: silent pass, continue.
   - [ ] Exit 2 / `total_dead > 0`: surface paths in plan as `dead_wikilinks_detected`; strip in execute preamble.
   - [ ] Long-mode: `--check` plan mode only; `--fix` deferred to execute preamble.
   - [ ] Report `dead_wikilinks_detected` count in plan; `dead_wikilinks_stripped` count in execute checkpoint.
 - [ ] 3.1 Normal mode: prepare a rewrite plan covering structure, content, voice, readability features, frontmatter, tags, shadow tag escape, and filename.
 - [ ] 3.1a Diagram assessment: scan sections for process/architecture/data model/state machine/sequence → decide type + placement per section; record in plan. At Step 5, author a fenced ```mermaid block with the decided type. Embed inline.
 - [ ] 3.1b Heading hierarchy audit (PDF/DOCX sources)
 - [ ] Detect flat hierarchy: file has >1 H1, OR >10 H1s with zero H2/H3.
 - [ ] Demotion is parent-dependent, NOT flat regex. Walk top-down tracking region (front/body/appendix/biblio) + nearest parent. Hierarchy: Chapter=H2; Part=H3 (under Chapter); roman `i./ii.`=H4; lettered `(a)/(b)`=H5 under a roman, else H4 (avoids H3→H5 skip). A chapter's Conclusion + Appendix = H3 (subordinate to that chapter), not H2 siblings. Numbered `N.` under a chapter = H3. Biblio subsections = H3 under one `## Bibliography` H2. Figure/table captions + bare numbers → bold, not headings.
 - [ ] Flat demotion (`## N.`→`### N.` everywhere) is INSUFFICIENT: makes Parts siblings of Chapters, detaches chapter Conclusions/Appendices. Regex cannot see parent; observed failure mode on a converted book manuscript.
 - [ ] Flag broken-heading patterns: single-word lowercase headings, duplicate section titles at same level, bare page-number headings.
 - [ ] Normal mode: apply inline.
 - [ ] Long mode: include `hierarchy_audit` in plan payload; apply during chunk execution.
 - [ ] 3.1c Subheading augmentation: any section with 3+ consecutive paragraphs and no H3/H4 -> add subheadings by default. Skip only if user explicitly overrides.
 - [ ] 3.1d Wikilink format (when the note app supports wikilinks): `[[path/to/note|filename]]` — notes-root-relative, no `.md`; display = filename only. Heading-anchored: `[[path/to/note#Heading|filename]]`. Bare `[[note]]` not used. No wikilink support → relative markdown links.
 - [ ] 3.1e Footnote artefacts (PDF/DOCX). Extraction degrades footnotes: markers survive as mashed digits (`Canada's1`, `crisis".7`, `world.1002`); most defs lost; survivors may be concatenated. Plan multi-pass, not single.
 - [ ] Convert recoverable (marker has surviving def) to `[^N]`/`[^N]:`. A `[^N]:` def MUST start its own line or renderers ignore it; split concatenated defs.
 - [ ] Strip orphan markers (no def) only when CLEARLY a footnote: digit abutting word-end, sentence-end punctuation, or closing quote. SKIP if ambiguous.
 - [ ] Residual passes for classes one pass misses: closing-quote+digits (`".7`); full-word+3-4-digit (`world.103`), capping 4-digit below the doc's max footnote number so years (`.2018`) + DOIs (`fpsyg.2018`) survive; apostrophe-s+digit.
 - [ ] PRESERVE real numbers: years, decimals, percentages, `s. 96` sections, dollar amounts, bracketed judgment paragraphs (`[51]`).
 - [ ] Long mode: `footnote_audit` in plan; apply per chunk; controller re-runs residual passes + parity check post-execute (Step 6).
 - [ ] 3.2 Evaluate callout opportunities for readability in normal and long mode. For each section/chunk, record one explicit decision: `add`, `convert`, or `no-change`, with reason.
 - [ ] 3.3 Apply callout heuristics conservatively:
 - [ ] favour callouts for key takeaway, caveat/risk, decision, action checklist, and definition/context blocks
 - [ ] avoid callouts for dense citation-only blocks, footnotes, and purely narrative continuity where callouts reduce flow
 - [ ] avoid adjacent callout stacking unless clearly justified
 - [ ] do not nest callouts by default
 - [ ] 3.4 Long mode: use preflight output to prepare a section-level chunk plan table with:
 - [ ] `chunk id`
 - [ ] `anchor heading(s)`
 - [ ] `source line range`
 - [ ] `rewrite intent`
 - [ ] `callout_decision` (`add|convert|no-change`)
 - [ ] `callout_reason`
 - [ ] `callout_scope` (heading/block target)
 - [ ] `boundary_type`
 - [ ] `boundary_score`
 - [ ] `boundary_note`
 - [ ] `execution order`
 - [ ] `external_media_stripped` (count; 0 if none)
 - [ ] `dead_wikilinks_detected` (count; 0 if none)
 - [ ] `related_section` (`missing|already-present`)
  - [ ] 3.5 Long-mode metadata must be visible in plan:
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
 - [ ] 3.6 Frontmatter rules:
 - [ ] Preserve original `created at` value and quoting.
 - [ ] Update `title` and `summary` to reflect rewritten content.
 - [ ] Keep scalar values and each tag item double-quoted.
 - [ ] 3.7 If scope changes tags, flag changed tags for the tag refresh at Step 5.6.
 - [ ] 3.8 If filename is not lowercase-hyphenated, propose rename and confirm. Exception: filenames containing CJK characters (Chinese, Japanese, Korean) are valid as-is; do not propose rename.
 - [ ] "Rewrite in place" / "overwrite original" / "same path" instructions DO NOT exempt rename. In-place semantics refer to folder location and content overwrite, not to filename preservation. Filename convention still applies; propose rename and confirm even when user says "in place". CJK exception applies here too.
 - [ ] Rename after write completes: Obsidian CLI installed → `obsidian rename path="<old>" name="<new>"` (auto-updates internal wikilinks); else rename the file and update inbound links from sibling notes.
 - [ ] Long mode: flag rename to parent workflow; the operator must NOT auto-rename. Rename after execute succeeds (Step 5.1 post-write).
 - [ ] 3.9 Related section check
 - [ ] Scan file for an existing `## Related` section.
 - [ ] Present: flag `related_section = already-present`; no further action.
 - [ ] Absent: flag `related_section = missing`. Optionally add at Step 5.8 after write completes — do NOT attempt link resolution here.

- [ ] Step 4: Confirm plan with user ⛔ BLOCKING
  - [ ] 4.1 Do not mutate before user approval. Verdict via structured choice (never free text): "Proceed with this rewrite plan?" options: Proceed (Recommended) / Adjust. Fallback (no structured choice support): numbered options in plain text; wait for reply. Plan >40 lines → plan message ends the turn; raise the choice next turn with ≤5-line digest.
  - [ ] 4.2 Long mode must explicitly confirm semantic chunk plan before execution (same structured-choice call).
  - [ ] 4.3 Confirm proposed callout decisions (`add|convert|no-change`) before execution (same structured-choice call).
  - [ ] 4.4 Long-mode approval output must visibly disclose planning method and quality:
    - [ ] `planner_invocation_strategy = python-cli | manual-fallback`
    - [ ] `planning_quality = full-scored | reduced-fallback`
    - [ ] `planner_elapsed_ms`
    - [ ] `fallback_used`
    - [ ] `fallback_reason` when relevant
  - [ ] 4.5 If fallback used: state chunk plan safe but less optimized than scored planner output.
- [ ] Step 5: Execute rewrite
 - [ ] 5.1 Normal mode: rewrite in place and apply approved rename/tag updates.
  - [ ] 5.2 Long mode:
    - [ ] execute with `mode = execute`, `session_id`, and `plan_hash` (operator dispatch or inline)
    - [ ] write sequentially by chunk in deterministic order
    - [ ] emit checkpoint after each chunk: `status`, `completed_chunks`, `next_chunk`, `total_chunks`, `notes`, `plan_hash`, `source_hash`, `staging_output_path`, `updated_at`, `callout_actions_applied`, `callout_actions_remaining`, `dead_wikilinks_stripped`, `planner_invocation_strategy`, `planning_quality`, `planner_exit_code`, `planner_stderr_excerpt`, `planner_elapsed_ms`, `non_ascii_target_path`, `fallback_used`, `fallback_reason`
    - [ ] continue automatically unless blocked by anomaly/conflicting instruction
 - [ ] 5.3 If interrupted in long mode, resume with `mode = resume` using the same `session_id` and `plan_hash`.
 - [ ] 5.4 If hash mismatch is returned (`source_changed_replan_required`), re-run plan mode before continuing.
 - [ ] 5.5 If renamed, delete old file after successful write.
 - [ ] 5.6 Tag refresh: derive tags from rewritten content plus Step 3.7 flags (user's tag-taxonomy vocabulary preferred when a taxonomy file exists); replace `tags:` in frontmatter.
 - [ ] 5.7 Execute diagram placements from 3.1a → author fenced ```mermaid blocks; embed at planned locations. Note in Step 7.
 - [ ] 5.8 If `related_section = missing`: optionally append a `## Related` section linking existing related notes (user-named or found in the note's folder). Never fabricate links to non-existent notes; skip silently if none known.

- [ ] Step 6: Final integrity pass
 - [ ] 6.1 Validate frontmatter contract and quoting.
 - [ ] 6.2 Validate heading continuity and order.
 - [ ] 6.3 Validate callout syntax where callouts are added/converted.
 - [ ] 6.4 Confirm no duplicated section blocks.
 - [ ] 6.5 Confirm intent preserved after rewrite.
 - [ ] 6.6 Confirm no bare shadow tags in body (scan `#WORD` outside frontmatter, code blocks, backtick spans matching non-tag patterns).
 - [ ] 6.7 Report `callout_semantic_parity` pass/fail (callout edits preserve required constraints and requirements).
 - [ ] 6.8 PUA residual check: run `python "<skill-dir>/shared/text/scripts/strip_pua_artifacts.py" "<path>" --check`. Exit 0 = pass.
 - [ ] 6.9 HTML artefact residual: run `strip_html_artefacts.py "<path>" --check`. Exit 0 = pass. Exit 2 = report counts; do not auto-fix. Non-blocking.
 - [ ] 6.9a Confirm no external media embeds remain (scan for `![...](https://`, `data:image/`, `<video`, `<audio`, `<iframe`).
 - [ ] 6.10 Heading hierarchy sanity:
 - [ ] File has exactly one H1.
 - [ ] No heading is a single lowercase word.
 - [ ] No heading matches `# Figure \d` or `# Table \d`.
 - [ ] No heading matches `^# \d+$` (bare page-number).
 - [ ] No duplicate section headings at the same level.
 - [ ] Skip detector: no parent-to-child jump >1 level (flag H2→H4, H3→H5). Skip = nesting error from 3.1b.
 - [ ] 6.11 Note `related_section` status (`already-present` or `missing`). Do not fail integrity pass on `missing`.
 - [ ] 6.12 Post-operator verification (long mode) ⚠️ REQUIRED. Operator summary = INTENDED actions, not a verified diff; chunked execution drops edits inconsistently + over-reports (one observed run claimed 26 numbered H2→H3 demotions never applied). Never trust the summary. Verify the file directly: each claimed transformation landed (grep heading distribution), skip detector clean (6.10), footnote parity clean (6.13). Re-apply missed fixes before reporting done.
 - [ ] 6.13 Footnote parity (if footnotes): `[^N]` marker count vs `^[^N]:` def count; matched sets; zero dangling; every def line-start. Re-run residual passes (3.1e) for leftovers.

- [ ] Step 7: Report what changed
 - [ ] 7.1 Summarize by category: structure, content, voice, tags, filename.
 - [ ] 7.2 In long mode, include final checkpoint summary and any resume/replan events.
 - [ ] 7.3 Include callout outcome summary (`add|convert|no-change`) with reasons.
 - [ ] 7.4 Report `related_section` status and tag update outcome.
 - [ ] 7.5 Report external media stripped count (images, video, audio, iframes), captions kept/stripped, and dead wikilinks stripped count.

## Guardrails

- Substantive edits are expected in this workflow.
- Not this workflow: pure whitespace/markup normalization-only cleanup.
- Preserve substantive intent. Rewrite expression and structure, not the note's purpose.
- If user requires verbatim language preservation or "no paraphrase", redirect to reformat workflow.
- Rewrite may add or convert callouts when readability improves, and may rephrase text inside callouts.
- Never change requirements/constraints through callout edits unless user explicitly authorizes.
- Preserve in place unless user explicitly requests a move.
- Files in user-designated read-only folders are not permitted rewrite targets. Redirect to formatting-only or new-note flow.
- Never create additional notes; rewrite one existing file per invocation.
- Never treat root `readme.md`/`README.md` as rewrite targets unless explicitly requested.

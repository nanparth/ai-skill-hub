# note

A markdown note-management skill for AI assistants. It creates, rewrites, reformats, and merges notes in your notes folder, and turns source documents into atomic knowledge notes. Every change is planned first and shown to you for approval before anything is written.

## Part A — User Guide

### Who it's for

Anyone who keeps a folder of markdown notes: Obsidian users get full feature support (wikilinks, callouts, properties); plain-markdown users get everything except the Obsidian-specific rendering.

### What you need

- An AI assistant that supports folder-based skills (Claude Code is one example; any assistant with a skills folder works).
- File read/write access to your notes folder.
- Python 3.10+ — only needed for very long files (500+ lines) and for cleaning up PDF/Word-converted documents. Everyday note work runs without it.

### Quick start

1. Copy the whole `note` folder into your assistant's skills folder (for example `~/.claude/skills/note/` in Claude Code).
2. Ask your assistant something like:
   - "draft a note about the meeting takeaways"
   - "reformat notes/imported-chapter.md, no paraphrase"
   - "rewrite notes/draft.md for clarity"
   - "merge notes/ideas-a.md and notes/ideas-b.md"
   - "process this PDF extract into atomic notes"
3. Review the plan or change list the skill presents, answer its questions, and approve before it writes.

### What each mode does

- **New note**: drafts a note with clean frontmatter (title, date, tags, summary), saved where you choose.
- **Reformat**: layout and syntax cleanup only; your wording is preserved verbatim. Ideal for files converted from PDF or Word: it strips conversion garbage, fixes heading structure, rejoins broken paragraphs, and repairs footnotes.
- **Rewrite**: substantive editing for structure, clarity, tone, or grouping, while preserving the note's intent.
- **Merge**: combines 2+ notes into one coherent note, theme by theme; strong passages are preserved verbatim rather than blended into mush.
- **Process source**: reads source material and produces one small note per concept, each linked back to the source.

### Safety model

Nothing is written before you approve the plan. Long files (500+ lines) get a chunk-by-chunk execution plan with checkpoints, so an interrupted run can resume without data loss. Source files in a merge are never deleted. Folders you designate as read-only are refused as edit targets.

## Part B — Technical Reference

### Layout

```text
note/
  SKILL.md                          routing, shared conventions, long-file protocol,
                                    output policy, delegation guards
  PORTABILITY.md                    classification + dependency boundary
  note-readme.md                    this file
  workflows/
    new-note.md                     note creation
    rewrite-note.md                 substantive in-place rewriting
    reformat-note.md                formatting-only cleanup
    merge-note.md                   2+ note synthesis (new-file or absorb)
    process-source.md               source material → atomic notes
  references/
    obsidian-syntax.md              markdown + Obsidian syntax authority
    multipart-series.md             book-chapter / course-module series conventions
  shared/text/scripts/
    long_file_plan.py               deterministic chunk planner for 500+ line files
    strip_pua_artifacts.py          removes PUA-wrapped citation garbage (PDF/chat exports)
    strip_html_artefacts.py         removes <details>/<summary> wrappers (PDF/DOCX converts)
    check_dead_embeds.py            detects/removes dead ![[image]] embeds
  tests/
    run_merge_smoke.sh              merge smoke-test orchestrator (bash)
    verify_merge.py                 merge output verifier
    fixtures/merge/                 ten neutral test fixtures
```

### Design notes

- Long-file mode (>500 lines) never loads the whole file. The planner script produces a semantic chunk plan (`session_id`, `source_hash`, `plan_hash`); execution checkpoints after every chunk and resumes from interruption. Hosts with subagent support delegate chunks to an operator agent; hosts without run the identical protocol inline.
- The merge workflow plans theme-by-theme transformations (preserve verbatim / integrate / synthesise) with a source-coverage audit, so no passage silently disappears.
- All Python helpers are standard-library only; no pip installs.
- Every user decision is a hard stop: structured choice where the host supports it, numbered plain-text list where it doesn't. Plans longer than 40 lines are shown in their own message before the approval question.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| File read/write | All workflows | Required |
| Python 3.10+ | Long-file planner, PDF/DOCX artefact strippers | Short files unaffected; converted-source cleanup degrades to manual edits |
| Subagent dispatch | Chunked operators for long files | Same protocol executed inline |
| Obsidian CLI | Rename with automatic wikilink updates; scalar property edits | Direct file edits; manual inbound-link check after renames |
| Tag-taxonomy file | Controlled tag vocabulary | Tags derived from content |
| Obsidian app | Wikilink/callout/property rendering | Any markdown editor; files stay plain text |
| bash + sha256sum | Merge smoke tests | Tests skipped; skill unaffected |

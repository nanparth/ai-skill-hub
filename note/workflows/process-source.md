# Process Source Workflow

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick.

Process source material and produce atomic knowledge notes.

## Usage

`note <file-path-or-topic>`

## Instructions

0. Load references/obsidian-syntax.md first. REQUIRED

1. Resolve source input. ⛔ BLOCKING
   - If explicit file path(s) are provided, read those files directly.
   - Topic-only input → search the user's notes folder once for matching sources (note app's built-in search or recursive text search).
   - If nothing is found, ask user to specify source paths.

2. Analyze source content.
   - Identify key concepts, claims, evidence, and practical takeaways.
   - Identify related existing notes for possible connections.

3. Assign tags. ⛔ BLOCKING
   - If the user maintains a tag-taxonomy file, read it and select the most relevant tags for each note; otherwise derive lowercase hyphenated tags from the analysis.
   - No adequate tag → propose one (lowercase, hyphenated) with a one-line description.
   - Confirm proposed tags (existing and new) before proceeding ⛔ BLOCKING. Present as a structured choice (never free text): "Apply these tags?" options: Confirm (Recommended) / Adjust. "Other" captures changes (fallback: numbered text options).
   - On approval, append any new tags to the user's taxonomy file when one exists.

4. Create atomic knowledge notes.

```markdown
---
title: "[Concept Title]"
created at: "YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM"
tags:
  - [relevant tags]
source:
  - "[[path/to/source-file1]]"
  - "[[path/to/source-file2]]"
summary: "[One-sentence summary]"
---

# [Concept Title]

[Concise explanation]

## Key Points

- [essential point]

## Connections

- [[related-note-1]] -- [how it connects]

## Source

From [[source-file-name]]: [where this appears]
```

4.4 External URL citations: use `[label](https://full-url)` in prose. Bare URLs allowed only when standalone in a table cell or on their own line. Never inside backticks. Never partial paths in prose.

4.5 Per note: content has process/workflow/architecture/data model/state machine → author a fenced ```mermaid block; embed inline.

5. Resolve destination folder per Output Path Policy in SKILL.md.
6. Save all generated notes in the resolved destination with lowercase-hyphenated filenames.
7. Report files created with one-line summaries and include the final destination path used.

## Guardrails

- Search the user's notes at most once per invocation; never run repeated discovery passes.
- Keep one concept per note.
- Wrap technical `#WORD` tokens (e.g., `#REF!`, `#include`, `#define`, `#TODO`) in backtick code to prevent shadow tags.
- Never treat root `readme.md`/`README.md` as source input unless explicitly requested.

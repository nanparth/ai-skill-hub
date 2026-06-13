# New Note Workflow

> ⛔ GATE DISCIPLINE: user-decision gates = hard stops. Present options as a structured choice if the host supports it; otherwise as a numbered list in plain text. Stop and wait for the user's reply; never auto-pick.

Create a new note with proper formatting and placement.

## Usage

`note [optional title]`

## Instructions

0. Load references/obsidian-syntax.md first. REQUIRED

1. No title provided → ask user for one. ⛔ BLOCKING
2. Resolve destination folder per Output Path Policy in SKILL.md.
3. Identify 2–3 key topics from the note content; these drive tag selection at Step 5.5.

4. Before drafting: content has process/workflow/architecture/data model/state machine/sequence → author a fenced ```mermaid block with the inferred type; embed inline. Create note with frontmatter + body (diagrams inline):

```markdown
---
title: "FILE NAME"
created at: "YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM"
tags: []
summary: "SUMMARY"
---

# [Title]

[content]
```

5. Save with lowercase-hyphenated filename in the resolved destination folder. Exception: filenames containing CJK characters (Chinese, Japanese, Korean) do not require hyphen separators.
5.5 Derive 3-8 lowercase hyphenated tags from the content. If the user maintains a tag-taxonomy file, read it and prefer its vocabulary; flag any new tag proposals to the user. Insert the final `tags:` into frontmatter.
5.6 (optional) Append a `## Related` section: link existing related notes the user names, or notes found in the destination folder on the same topic. Skip silently if none known; never fabricate links to non-existent notes.
6. Report saved path and tags applied.

## Conventions

- Keep frontmatter tags lowercase.
- Wrap technical `#WORD` tokens (e.g., `#REF!`, `#include`, `#TODO`) in backtick code (see Shadow Tag Hazards in `obsidian-syntax.md`).
- Check for existing notes on same topic before creating a duplicate.
- Never create or edit root `readme.md`/`README.md` unless explicitly requested.

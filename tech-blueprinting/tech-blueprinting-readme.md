# tech-blueprinting

`tech-blueprinting` helps an AI assistant write technical specs, PRDs, RFCs, decision docs, implementation plans, and READMEs through a structured review workflow.

## Use This If

Use this skill when the main deliverable is a document, not code. It is especially useful when the document needs enough detail for another engineer or agent to act on it later.

## Dependencies

The core workflow has no runtime dependency beyond file read/write access.

The visual companion is optional and requires:

- Node.js.
- Shell support.
- A local browser.

## Main Workflow

1. Gather context and ask blocking setup questions.
2. Build the document section by section.
3. Run reader testing to catch gaps, ambiguity, and missing assumptions.
4. Save the final document to a user-selected path, usually `./docs/<document-name>.md`.

## Optional Visual Companion

The visual companion serves local HTML screens for mockups, diagrams, and visual comparisons.

```bash
<skill-dir>/scripts/start-server.sh --project-dir /path/to/project
<skill-dir>/scripts/stop-server.sh <session-dir>
```

Use it only when seeing the options would help more than reading a list.

## README Workflow

For README work, load `workflows/readme-write.md`. It reads the target source files first, drafts from `references/readme-template.md`, and checks the result with `references/readme-self-review.md`.

## Files To Copy

Copy the whole `tech-blueprinting/` folder. Required local files include `SKILL.md`, `workflows/`, `agents/`, `references/`, `shared/`, `scripts/`, and `PORTABILITY.md`.
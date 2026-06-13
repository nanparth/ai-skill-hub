# tech-blueprinting

A technical-document drafting skill for AI assistants. Give it a spec, PRD, RFC, design-doc, architecture, README, or dev-plan request, and it guides the work through context gathering, structured drafting, review, and reader testing.

## Part A — User Guide

### Who it's for

Engineers, technical leads, product builders, and maintainers who need clear technical documents that another person or implementation agent can use without shared conversation context.

### What you need

- An AI assistant that supports folder-based skills and can write Markdown to a user-selected path.
- Enough domain context to explain the feature, system, decision, or document goal.
- Optional: subagent support for spec self-review and reader testing.
- Optional: Node.js and a browser for the visual companion.
- Optional: an external converter if the final output must be `.docx`.

### Quick start

1. Copy the whole `tech-blueprinting` folder into your assistant's skills folder.
2. Ask your assistant something like:
   - "Write a technical spec for the new authentication service."
   - "Draft an RFC for this API migration."
   - "Create a dev plan for this feature."
   - "Write a README for this skill."
3. Answer the initial questions about audience, document type, desired impact, format, and constraints.
4. Provide context in whatever shape you have it.
5. Review structure options, then draft section by section.

### What you get back

- A Markdown document at the user-selected output path.
- A structure chosen deliberately for the audience and document type.
- Section drafts built from user-curated brainstorming.
- For implementation-oriented specs: commands, testing expectations, project structure, code style, git workflow, boundaries, and success criteria.
- A self-review pass and a reader-test pass before the document is considered ready.

### Modes

- **Structured blueprinting**: the three-stage flow for specs, PRDs, RFCs, design docs, decision docs, architecture docs, and dev plans.
- **README writing**: a dedicated workflow that reads source files and writes a Part A / Part B readme without the full collaborative drafting loop.
- **Visual companion**: optional local browser surface for mockups, layouts, and visual comparisons.
- **Freeform**: if the user declines the structured process, the assistant can draft normally.

## Part B — Technical Reference

### Layout

```text
tech-blueprinting/
  SKILL.md                         routing hub and three-stage workflow
  PORTABILITY.md                   standalone-with-optional-tools boundary
  tech-blueprinting-readme.md      this file
  workflows/
    visual-companion.md
    readme-write.md
  agents/
    spec-reviewer.md
    reader-tester.md
  references/
    readme-template.md
    readme-self-review.md
    plan-template.md
  shared/
    test-level-protocol.md
    code-organization.md
  scripts/
    server.cjs
    helper.js
    frame-template.html
    start-server.sh
    stop-server.sh
```

### Design notes

- The main workflow is three stages: context gathering, section-by-section refinement, and reader testing.
- Scope assessment happens before detailed questions so oversized requests can be split into separate documents.
- Implementation-oriented docs receive extra gates for commands, testing, structure, style, git workflow, boundaries, and success criteria.
- Subagents receive only the document content needed for their review, which makes self-review and reader testing less dependent on conversation memory.
- The visual companion is optional and offered separately so setup does not get buried inside other questions.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Host file writer | Markdown output | Present draft in chat and ask for a destination |
| Subagent support | Spec review and reader testing | Run the same checklists inline |
| Node.js | Visual companion server | Use Mermaid blocks or static Markdown instead |
| Browser access | Viewing visual companion | Skip visual companion |
| External converter | `.docx` output | Deliver Markdown first |

### Maintenance notes

- Keep `SKILL.md` routing maps in sync with moved or renamed workflows, agents, references, shared files, or scripts.
- README-writing rules live in `workflows/readme-write.md` plus `references/readme-template.md` and `references/readme-self-review.md`.
- Changes to `shared/test-level-protocol.md` affect `tech-implement` as well; update both skills' compressed gate summaries together.

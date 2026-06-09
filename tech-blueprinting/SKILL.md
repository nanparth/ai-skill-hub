---
name: tech-blueprinting
description: 'Use when the primary deliverable is a technical specification document produced through iterative drafting with user review gates, not for generating code. Trigger on: "write a spec", "spec this out", "draft a PRD", "write an RFC", "blueprint this", "decision doc", "dev plan", "write a README", "document this skill".'
argument-hint: '[spec|prd|rfc|design-doc|decision-doc|dev-plan|architecture|readme] [--title name]'
---

# Tech Blueprinting Workflow

A structured three-stage collaborative workflow for producing technical documents. Stages target predictable failure modes: missing context, disorganized drafting, and author blind spots.

## Dependencies

The core writing workflow needs only file read/write access in the user's chosen project or output folder. The visual companion is optional and requires Node.js, shell support, and a local browser.

## Loading Maps

| Resource | File | Load when |
| --- | --- | --- |
| Visual Companion | `workflows/visual-companion.md` | User accepts visual companion offer. |
| Spec Reviewer | `agents/spec-reviewer.md` | After near completion, before reader testing. |
| Reader Tester | `agents/reader-tester.md` | Stage 3 reader testing dispatch. |
| README Workflow | `workflows/readme-write.md` | User wants to write, update, or refresh a README. |
| README Template | `references/readme-template.md` | README workflow drafting. |
| README Self-Review | `references/readme-self-review.md` | README workflow quality check. |
| Plan Template | `references/plan-template.md` | Document type is an implementation plan. |
| Test Level Protocol | `shared/test-level-protocol.md` | Implementation assertions plus boundary signals. |
| Code Organization | `shared/code-organization.md` | Multi-file implementation or architecture spec. |

## Test Level Gate

Load `shared/test-level-protocol.md` and evaluate when any boundary signal is present in an implementation-oriented spec: subprocess spawn, IPC or HTTP boundary, filesystem state written then read, lock or PID coordination, external tool, cross-language boundary, CLI entrypoint, public schema, config, API payload, or file format change.

Skip when the work is a single module with pure logic and no I/O. Decide the test level before drafting and include the recommendation in the plan.

## Document Type Routing

Before offering the three-stage workflow, check for a specialized workflow match.

| Signal | Route | Why |
| --- | --- | --- |
| User mentions README, usage docs, refresh docs, or document this skill | Load `workflows/readme-write.md` | READMEs follow a fixed source-reading and template workflow. |
| User mentions implementation plan, dev plan, task breakdown, or execute-ready plan | Load `references/plan-template.md` before drafting | Plans need task shape, commands, boundaries, and TDD-ready steps. |

If the request is ambiguous, ask whether the user wants a README or a general technical document.

## Guiding Principles

- Keep it simple. Prefer clear, concrete prose over abstraction and jargon.
- Include only what is needed. Every section must serve the audience and purpose.
- Keep high cohesion and low coupling in implementation-oriented docs. Each component should own one responsibility and communicate through explicit boundaries.

## Stage 1: Context Gathering

Ask for meta-context before drafting:

1. What type of document is this?
2. Who is the primary audience?
3. What should change after someone reads it?
4. Is there a template or specific format to follow?
5. Are there constraints or context to know?

Never proceed until the user has answered these questions. The user can answer in shorthand or dump information however works for them.

For implementation-oriented documents, inspect the accessible codebase before drafting. Read project structure, recent Git history, key files, existing patterns, tests, and likely risks. Present a structured summary and ask whether it matches the user's understanding.

If visual content would help, offer the optional browser companion in its own message. If accepted, read `workflows/visual-companion.md` before the next visual question.

## Stage 2: Refinement and Structure

Build the document section by section.

For each section:

1. Ask clarifying questions.
2. Brainstorm possible content.
3. Ask the user what to keep, remove, or combine.
4. Check for gaps.
5. Draft the section in the document.
6. Refine through direct edits.

Do not draft from a brainstorm list until the user has curated it or clearly approved it.

For multi-file implementation specs, add a module or folder layout section and load `shared/code-organization.md`.

Implementation-oriented docs should cover exact commands, testing, project structure, code style, Git workflow, boundaries, and success criteria. Include "never commit secrets or API keys" unless the document is not for implementation work.

Ask the user where the document should be saved. If they have no preference, propose `./docs/<document-name>.md`.

For markdown output, create or edit the file using the host assistant's normal file-writing method. For DOCX output, draft markdown first and tell the user that conversion is outside this skill unless their environment provides a separate converter.

## Stage 3: Reader Testing

Test the document with a fresh reader perspective.

1. Predict 5-10 reader questions.
2. Dispatch `agents/reader-tester.md` if the host supports subagents. Pass only the document content and predicted questions.
3. Summarize what the reader got right or wrong.
4. Fix ambiguities, contradictions, or missing context.

If the host does not support subagents, do a manual reader test by answering the predicted questions from only the document text.

## Final Review

When reader testing passes, recommend a final user read-through, fact check, and link check. For specs, dev plans, or implementation plans with discrete tasks, mention that `tech-implement` can execute the plan if that skill is installed.
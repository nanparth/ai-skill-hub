---
name: tech-refactor
description: 'Use when a codebase has structural problems requiring systematic analysis before changes: competing implementations, god modules, unclear boundaries, or deep technical debt. Trigger on: "refactor this service", "overhaul this legacy system", "too much technical debt", "architectural migration". Not for tactical fixes or small cleanup.'
argument-hint: '<codebase-path> [--focus boundaries|duplication|legacy-paths]'
---

# tech-refactor

Architectural overhaul workflow for existing systems. It produces an execution-ready roadmap before any high-risk code changes.

Core principle: deletion is the proof of centralization. Adding a new abstraction is not enough. The old access path must be removed before centralization is complete.

Not for: surgical cleanup, single-function improvements, extract-and-rename tasks, or small formatting cleanup.

## Pipeline

```text
Phase 1: Understand -> confidence-rated behavioral inventory
Phase 2: Audit -> risk findings and additive-bias detection
Phase 3: Clarify -> targeted questions when needed
Phase 4: Design -> target architecture, migration strategy, retirement plan
Phase 5: Roadmap -> execution-ready task list
Approval gate -> optional execution with tech-implement or manual TDD workflow
```

## Workflow

### Phase 1: Understand

1. Read the target codebase: entrypoints, module structure, key files.
2. Produce a confidence-rated inventory: high, medium, low.
3. Include user-facing features, inputs, outputs, side effects, integrations, API shapes, wire formats, config keys, data models, duplicate implementations, tests, and protected behavior.
4. Present the inventory to the user before proceeding.

### Phase 2: Audit

Load `references/architectural-risk-audit.md`. Separate confirmed findings from plausible risks.

Check for additive refactor bias, competing sources of truth, partial refactor residue, runnable but wrong behavior, context drift, test coupling, unsafe operations, unused package dependencies, orphaned test infrastructure, and structure risks. Load `shared/code-organization.md` for structure risks.

Present findings to the user before design.

### Phase 3: Clarify

Skip this phase if Phases 1 and 2 left no open unknowns. Ask only about low-confidence behavior, ambiguous business rules, non-code constraints, deployment environment, rollback tolerance, team constraints, or compliance.

Do not ask questions that are answerable from the codebase.

### Phase 4: Design

Restate the inventory and audit findings before proposing a design.

1. Target architecture: propose module boundaries and canonical ownership of rules, schemas, config, integrations, and workflows. Use `shared/code-organization.md`.
2. Migration strategy: load `references/cross-boundary-refactoring.md`; design incremental migration while preserving public behavior, wire formats, CLI or API contracts, and config semantics.
3. Legacy path retirement plan: load `references/legacy-path-retirement.md`; classify symbols, map dependents, enumerate deletion list, plan test migration, and define guard tests.

Gate check: what old path does this retire, and what import or patch target becomes impossible? No answer means the plan is incomplete.

### Phase 5: Roadmap

Load `references/test-patterns.md` before specifying tests.

Produce an execution-ready task list. Each task specifies characterization tests, files and subsystems in scope, tests to write before the change, validation command, rollback anchor, type safety requirements at new boundaries, and hard stops that require explicit user confirmation.

Present the roadmap and wait for explicit user approval.

## Execution

If `tech-implement` is installed, hand off approved tasks to that skill one at a time. If it is not installed, stop after the execution-ready roadmap unless the user explicitly asks to execute manually.

Manual execution must still follow TDD, verification gates, and one coherent task at a time. Use Git worktree isolation when available. If worktrees are unavailable or the target is not a normal Git repository, ask before working directly in the current folder.

## Language Choice During Refactor

Refactor in the target project's existing language by default. Switch languages only when the domain clearly belongs elsewhere and the user approves the migration risk. Surface the trade-off during analysis. Never auto-port.

## Load Policy

| Need | Reference |
| --- | --- |
| Architectural risk inventory and additive-bias detection | `references/architectural-risk-audit.md` |
| Cross-boundary migration patterns | `references/cross-boundary-refactoring.md` |
| Legacy path retirement and guard test templates | `references/legacy-path-retirement.md` |
| Structure audit and relocation playbook | `shared/code-organization.md` |
| Characterization, migration, and guard test patterns | `references/test-patterns.md` |
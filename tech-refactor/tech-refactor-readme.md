# tech-refactor

An architectural-refactoring skill for AI assistants. Give it a codebase path with structural debt, and it inventories behaviour, audits architectural risk, designs a target architecture, plans legacy-path retirement, and produces an execution-ready migration roadmap.

## Part A — User Guide

### Who it's for

Engineers and maintainers facing deep technical debt: competing implementations, unclear boundaries, partial migrations, god modules, duplicated sources of truth, or architecture that no longer matches current product reality.

### What you need

- A user-selected codebase path.
- Read access to source files, tests, and relevant project configuration.
- Existing tests if execution is requested; missing tests become part of the roadmap.
- Optional: Git history for context.
- Optional: `tech-implement` when you want the approved roadmap executed task by task.

This skill is not for small cleanup. Use it for architectural overhaul, not isolated rename, extract, DRY, or formatting work.

### Quick start

1. Copy the whole `tech-refactor` folder into your assistant's skills folder.
2. Ask your assistant something like:
   - "Refactor this service architecture: `src/orders/`."
   - "Audit this legacy module and design a migration plan."
   - "This codebase has competing implementations; plan the refactor."
3. Review the behavioural inventory and risk audit.
4. Answer only the clarifying questions that remain after code inspection.
5. Approve or revise the target architecture and migration roadmap.

### What you get back

- A confidence-rated behavioural inventory.
- Confirmed and plausible architectural-risk findings.
- A target architecture with canonical ownership for rules, schemas, config, integrations, and workflows.
- An incremental migration strategy that preserves public behaviour.
- A legacy-path retirement plan: what old paths disappear, what imports become impossible, and what guard tests prevent regression.
- An execution-ready roadmap sized for sequential implementation tasks.

### Workflow phases

- **Phase 1: Understand**: read entry points, module structure, tests, integrations, data models, and current behaviour.
- **Phase 2: Audit**: load architectural-risk guidance and classify structural failure modes.
- **Phase 3: Clarify**: ask only about low-confidence behaviour or non-code constraints.
- **Phase 4: Design**: propose target architecture, migration strategy, and legacy-path retirement plan.
- **Phase 5: Roadmap**: specify characterization tests, TDD tasks, validation gates, rollback anchors, and hard stops.

### Execution boundary

The skill stops at the roadmap unless the user approves execution. If `tech-implement` is available, approved tasks can be dispatched sequentially. Parallel refactor execution is intentionally avoided.

## Part B — Technical Reference

### Layout

```text
tech-refactor/
  SKILL.md                         five-phase workflow and load policy
  PORTABILITY.md                   standalone classification
  tech-refactor-readme.md          this file
  references/
    architectural-risk-audit.md
    cross-boundary-refactoring.md
    legacy-path-retirement.md
    code-smells.md
    design-patterns.md
    parse-dont-validate.md
    test-patterns.md
  shared/
    code-organization.md
```

### Design notes

- Behaviour preservation is the constraint. Public behaviour, wire formats, CLI/API contracts, and config semantics must survive each migration task.
- Deletion proves centralization. A new abstraction is incomplete until the old access path is retired.
- Migration tasks execute sequentially because architectural changes have broad propagation surfaces.
- The core pipeline lives in `SKILL.md` because every invocation uses the same phases; references are loaded only when a phase needs them.
- The roadmap must answer: "What old path does this retire?" and "What import or patch target becomes impossible?"

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Host file read access | Analysis and roadmap | Required |
| Existing tests | Characterization and execution safety | Roadmap starts by adding tests |
| Git | History and safety review | Continue with source inspection only |
| `tech-implement` | Executing approved tasks | Stop at roadmap or execute manually with user approval |
| Test command | Verifying execution tasks | Do not claim completed execution |

### Maintenance notes

- Add new audit failure modes in `references/architectural-risk-audit.md` and update the load policy if needed.
- Keep `shared/code-organization.md` aligned with the structure checkpoint and design phases.
- Reference files are skill-local; do not introduce hard sibling-skill dependencies.

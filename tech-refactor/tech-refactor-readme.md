# tech-refactor

`tech-refactor` helps an AI assistant inspect a codebase with structural problems and produce an execution-ready refactor roadmap before changing code.

## Use This If

Use this skill for unclear module boundaries, duplicated implementations, partial migrations, risky legacy paths, god modules, or deep technical debt. Do not use it for small cleanup tasks.

## Dependencies

The analysis workflow needs only file read access. Git and test commands are useful when reviewing history or executing the roadmap, but they are not required to produce the roadmap.

## Main Workflow

1. Understand current behavior and produce a confidence-rated inventory.
2. Audit architectural risk and additive-refactor bias.
3. Ask only targeted questions that cannot be answered from the code.
4. Design the target architecture and migration strategy.
5. Produce a TDD-ready roadmap with characterization tests, validation gates, and rollback anchors.

## Execution

If `tech-implement` is installed, it can execute approved roadmap tasks one at a time. If it is not installed, `tech-refactor` stops after the roadmap unless the user explicitly asks for manual execution.

## Local References

- `references/architectural-risk-audit.md`
- `references/cross-boundary-refactoring.md`
- `references/legacy-path-retirement.md`
- `references/test-patterns.md`
- `shared/code-organization.md`

## Files To Copy

Copy the whole `tech-refactor/` folder. Required local files include `SKILL.md`, `references/`, `shared/`, `tech-refactor-readme.md`, and `PORTABILITY.md`.
# Code Organization Reference

Use this file when a skill needs to decide where code should live or how to move code without changing behavior.

## Concern Taxonomy

Prefer the project structure that already exists. When the project is unclear, group files by responsibility:

- `entrypoints`: commands, handlers, routes, or UI entry files that start a workflow.
- `core` or `domain`: rules, calculations, parsing, validation, and decisions with minimal I/O.
- `contracts` or `schemas`: public data shapes, API payloads, config schemas, events, and types.
- `adapters`: filesystem, database, HTTP, subprocess, browser, or third-party integrations.
- `workflows` or `services`: orchestration across core logic and adapters.
- `utils`: small reusable helpers with no hidden state and no domain ownership.
- `tests`: tests near the project convention.
- `docs`: user-facing or developer-facing documentation.

## Organize-On-Demand Threshold

Do not split a file just because a file is long. Split when one of these is true:

- A module owns more than one clear responsibility.
- Different parts of the file change for different reasons.
- Callers need only one part, but must import a large mixed module.
- Tests patch private details because boundaries are unclear.
- A folder has grown past roughly eight active files without meaningful grouping.

Below that threshold, prefer a clear file with well-named sections over premature folder churn.

## Placement Rules

1. Put new code beside the closest existing pattern.
2. Keep public entrypoints stable unless the task explicitly changes the public surface.
3. Keep generated, vendored, cache, and build output out of manual refactors.
4. Do not create single-file folders unless the project already uses that convention or more files are clearly coming in the same task.
5. When adding a boundary, define the owner and the contract. Avoid two modules owning the same rule.

## Behavior-Preserving Relocation Playbook

1. Add or identify tests that cover current observable behavior.
2. Choose the canonical owner for the code being moved.
3. Move the implementation in the smallest coherent group.
4. Update internal imports to the canonical owner.
5. Run the relevant tests after each group.
6. Retire old aliases, re-exports, and compatibility wrappers only when callers no longer need them.
7. Add guard tests or lint checks when old imports are likely to come back.

A relocation is not complete until the old access path is gone or explicitly documented as a supported compatibility path.
# Refactor Test Patterns

Use these patterns when turning a refactor roadmap into execution tasks.

## Characterization Tests

Before moving or deleting code, lock down current observable behavior.

- Use representative real inputs from fixtures or small synthetic examples.
- Assert outputs, side effects, errors, and public contract shapes.
- Do not assert private helper calls unless that private path is the thing being retired.
- Run the test against current code first. It must pass before migration starts.

## Migration Tests

For each migration task, specify the test that fails before the change and passes after it.

- `unit` for isolated pure logic.
- `integration` when moved code crosses filesystem, database, parser, subprocess, or service boundaries.
- `contract` when API payloads, config, CLI output, schemas, or file formats must stay stable.
- `smoke_e2e` when the risk is the workflow through the real entrypoint.

## Guard Tests

Add guard tests when old access paths are likely to return.

Examples:

- Assert callers import from the canonical module.
- Search source for retired import paths.
- Verify deprecated facades no longer expose private aliases.
- Verify generated docs or schemas point to the canonical owner.

## Task Test Block

Each roadmap task should include:

```text
Tests first:
- characterization: <existing behavior to lock down>
- migration: <failing test proving the intended change>
- guard: <old path that must become impossible>
Validation gate:
- <exact command>
```
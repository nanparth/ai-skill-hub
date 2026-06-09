# Test Level Protocol

Use this file before writing tests for implementation plans, bug fixes, or refactor roadmaps. The goal is the smallest test that catches the real failure.

## Test Levels

- `unit`: one function, class, or module with external I/O mocked or absent.
- `integration`: multiple local components working together, often with real filesystem, database, parser, or service boundaries.
- `contract`: verifies an API, schema, CLI output, file format, or event shape that other code depends on.
- `smoke_e2e`: runs the main user path through real entrypoints with lightweight fixtures.
- `full_e2e`: runs the production-like path across multiple real systems. Use only when cheaper tests cannot catch the risk.

## Strong Boundary Signals

Escalate beyond unit tests when the task includes two or more of these signals:

- Subprocess spawning or shell command orchestration.
- IPC, HTTP, WebSocket, database, queue, or browser boundary.
- Filesystem state written and later read by another component.
- Lock files, PID files, session state, caching, or cleanup coordination.
- External tools such as Git, package managers, document converters, or browsers.
- Cross-language boundary.
- CLI entrypoint driving a real workflow.
- Public schema, config, API payload, or file format change.

## Decision Steps

1. Name the failure the test must catch.
2. List boundary signals.
3. Pick the cheapest test level that observes the failure without over-mocking the boundary.
4. Add a contract test when a public shape changes.
5. Add a smoke test when the risk lives in orchestration rather than a single module.
6. State the chosen level and one sentence of rationale in the plan or review.

## Output Shape

```text
Test recommendation:
- level: unit | integration | contract | smoke_e2e | full_e2e
- signals: <short list>
- failure mode: <what this test would catch>
- command: <exact command when known>
```
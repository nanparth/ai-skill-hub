# TDD Protocol

Load when implementer agent dispatched, or when creating failing tests for bug fixes.
Prerequisite: test level should be decided before writing. If not done, load `../shared/test-level-protocol.md` first.

## Core Principle

Write test first. Watch it fail. Write minimal code to pass. Refactor.

If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating letter of rules = violating spirit of rules.**

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before test? Delete it. Start over.

**No ad-hoc exceptions.** One defined gate: see When to Use § Exceptions.
- Don't keep as "reference"
- Don't "adapt" while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Red-Green-Refactor

1. **RED**: write failing test
2. **Verify fails correctly**: run test, confirm it fails for the right reason (not a syntax error, not a missing import)
3. **GREEN**: minimal code to pass
4. **Verify passes**: run test, all green
5. **REFACTOR**: clean up; tests stay green
6. Next

## When to Use

Always:
- New features
- Bug fixes
- Refactoring
- Behavior changes

Exceptions (ask user):
- Throwaway prototypes
- Generated code
- Configuration files

Complexity gate (no user confirmation required): all conditions in `shared/test-level-protocol.md` § Skip Protocols met — single module, pure logic, no I/O, `model_tier = cheap`. Controller evaluates; implementer respects. When in doubt, write the test.

Thinking "skip TDD just this once"? Stop. Rationalization.

## Red Flags → STOP, Start Over

- Code before test
- "I already manually tested it"
- "Tests after achieve same purpose"
- "It's about spirit not ritual"
- "This is different because..."
- "Just one quick check first"
- "I'll write the test after confirming the fix"

All mean: delete code, start over with TDD.

## Rationalization Counters

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately proves nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "It's about spirit" | Spirit = tests-first. No shortcut honors spirit. |
| "Different because generated code" | Ask user before skipping. Default = test. |

## Bug-Fix TDD (critical)

Bug fix without a failing test first = bug returns later.

1. Reproduce bug
2. Write test that fails because of the bug
3. Verify test fails with current (broken) code
4. Fix the bug
5. Verify test passes
6. Revert the fix. Run test. MUST FAIL.
7. Restore fix. Run test. Passes. Commit.

Step 6 is non-negotiable. Without it, you don't know if your test catches the bug or something else.

## Bottom Line

Write the test. Watch it fail. Write minimal code. Watch it pass. Refactor.

If any step is skipped or out of order, the Iron Law was violated. Start over.

## Integration Test Pattern

Setup: temp dir or fake local dep (never mock integration target).

1. Arrange: create temp fixture (file, dir, DB, local server)
2. Act: call real interface (not a mock)
3. Assert: check resulting state
4. Teardown: clean up unconditionally (try/finally or fixture scope)

Key: mocking integration target = unit test, not integration.

## Contract Test Pattern

Schema IS the test. Neither producer nor consumer tests internal logic; both test boundary.

1. Define shared schema (JSON Schema, Pydantic model, TypeScript interface)
2. Producer: assert emitted payload validates against schema
3. Consumer: assert received payload validates against schema
4. Schema change → drift caught on either side

Key: no live service needed. Fixtures and schema validation suffice.

## Smoke E2E Pattern

One real flow, minimal setup, deterministic.

1. Create isolated temp workspace
2. Run the real CLI or trigger the real subprocess path
3. Assert one observable output (file exists, exit code 0, expected stdout)
4. Cleanup unconditionally

Rules: no sleeps/polling; use completion signals. One happy path; no edge cases. Containers/network → requires_user_gate = true.

## Full E2E Pattern

Rare: only when full user/system workflow = risk surface.

1. Seed deterministic fixtures (DB, auth state, queue)
2. Trigger user action
3. Assert persisted output and system state
4. Cleanup deterministically

Rules: requires user gate always. No flaky timing. No shared state between runs. Keep suite small.

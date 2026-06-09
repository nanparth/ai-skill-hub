# Systematic Debugging Workflow

Fires on test failures during execute-plan verification gate, or as bug-fix entry point.

## Core Principle

Find root cause before attempting fixes. Symptom fixes = failure.

**Violating letter of process = violating spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Phase 1 incomplete → cannot propose fixes.

## When to Use

Any technical issue: test failure, bug, unexpected behaviour, performance problem, build failure, integration issue.

Especially when:
- Under time pressure (emergencies tempt guessing)
- "Just one quick fix" seems obvious
- Multiple fixes already tried
- Previous fix didn't work
- Don't fully understand the issue

Don't skip when:
- Issue seems simple (simple bugs have root causes too)
- In a hurry (rushing guarantees rework)

## The Four Phases

Complete each phase before the next.

### Phase 1: Root Cause Investigation

Before attempting ANY fix:

1. **Read error messages carefully.** Don't skip errors or warnings. They often contain the exact solution. Read stack traces fully. Note line numbers, file paths, error codes.

2. **Reproduce consistently.** Can you trigger it reliably? Exact steps? Every time? Not reproducible → gather more data, don't guess.

3. **Check recent changes.** What changed that could cause this? Git diff, recent commits, new deps, config changes, environmental differences.

4. **Gather evidence in multi-component systems.** System has multiple components (CI → build → signing, API → service → db)? Before proposing fixes, add diagnostic instrumentation:

   For each component boundary:
   - Log data entering
   - Log data exiting
   - Verify env / config propagation
   - Check state at each layer

   Run once → gather evidence showing WHERE it breaks. Analyze. Identify failing component. Investigate that specific component.

   **Instrumentation output goes in temp dir, not committed.** Write logs to `.tmp/debug-<timestamp>.log`. See `references/worktree-setup.md` Scratch Files. Revert instrumentation added to production code before fix commit, unless it becomes permanent logging.

5. **Trace data flow.** Error deep in call stack? Quick version:
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until source found
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

Find the pattern before fixing:

1. **Find working examples.** Similar working code in same codebase? What works that resembles what's broken?
2. **Compare against references.** Implementing a pattern? Read reference implementation fully. Don't skim. Understand before applying.
3. **Identify differences.** Working vs broken: list every difference, however small. Don't assume "that can't matter."
4. **Understand dependencies.** What components, settings, config, env does this need? What assumptions does it make?

### Phase 3: Hypothesis and Testing

Scientific method:

1. **Form single hypothesis.** State clearly: "I think X is the root cause because Y." Write it. Be specific.
2. **Test minimally.** Smallest possible change to test hypothesis. One variable at a time. Don't fix multiple things at once.
3. **Verify before continuing.** Worked? → Phase 4. Didn't work? → form NEW hypothesis. DON'T stack fixes.
4. **When you don't know.** Say "I don't understand X." Don't pretend. Ask, research.

### Phase 4: Implementation

Fix root cause, not symptom. Re-enters per-task loop of `workflows/execute-plan.md` at Step 3.2:

1. **Create failing test case.** Simplest possible reproduction. Automated if possible. MUST have before fixing. Use `references/tdd-protocol.md` (red-green-refactor, including revert-and-verify-fails step).
2. **Implement single fix.** Address root cause. ONE change. No "while I'm here" improvements. No bundled refactoring.
3. **Verify fix.** Test passes now? No other tests broken? Issue actually resolved? Use `references/verification-protocol.md`.
4. **Fix doesn't work?** STOP. Count attempts.
   - < 3 → return to Phase 1, re-analyze with new info
   - ≥ 3 → STOP. Question architecture (step 5).
5. **3+ fixes failed = architectural problem.** Pattern:
   - Each fix reveals new shared state / coupling / problem elsewhere
   - Fixes require "massive refactoring"
   - Each fix creates new symptoms

   STOP. Question fundamentals: is this pattern sound? Are we sticking through inertia? Refactor architecture vs continue fixing symptoms?

   Discuss with user before more fixes. Not a failed hypothesis. A wrong architecture.

## Red Flags → STOP, Return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals new problem in different place

3+ fixes failed → question architecture per Phase 4.5.

## Rationalization Counters

| Excuse | Reality |
|---|---|
| "Issue is simple, don't need process" | Simple issues have root causes. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic is FASTER than guess-and-check thrashing. |
| "Just try this first, investigate later" | First fix sets pattern. Do it right from start. |
| "Test after confirming fix" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt pattern" | Partial understanding = guaranteed bugs. Read fully. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern. |

## When Process Reveals "No Root Cause"

Investigation reveals issue is truly environmental, timing-dependent, or external:

1. Document what was investigated
2. Implement appropriate handling (retry, timeout, error message)
3. Add monitoring / logging for future investigation

95% of "no root cause" cases = incomplete investigation.

## Integration

- Called by: `workflows/execute-plan.md` Step 3.8 (verification gate failed)
- Called by: `workflows/fix-bug.md` (bug-fix entry point)
- Re-enters: `workflows/execute-plan.md` Step 3 (per-task loop) for the fix implementation

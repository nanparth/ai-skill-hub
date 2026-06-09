# Verification Protocol

Load at verification checkpoints: after each implementer task, after each reviewer loop, at final review.

## Core Principle

Evidence before claims, always. Claiming work complete without fresh verification = dishonesty.

**Violating letter of this rule = violating spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Haven't run the verification command in this message → cannot claim pass.

## Gate Function

Before claiming status or expressing satisfaction:

1. IDENTIFY: what command proves the claim?
2. RUN: execute full command, fresh, complete
3. READ: full output, check exit code, count failures
4. VERIFY: does output confirm claim?
   - No → state actual status with evidence
   - Yes → state claim WITH evidence
5. ONLY THEN: make the claim

Skip any step = lying, not verifying.

## Claim → Evidence Required

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags → STOP

- "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired, wanting work over
- ANY wording implying success without having run verification

## Rationalization Counters

| Excuse | Reality |
|---|---|
| "Should work now" | Run the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD red-green):**
Follow `references/tdd-protocol.md` § Bug-Fix TDD exactly. The revert-verify step is non-negotiable; see that document for the full cycle.

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When to Apply

Always before:

- ANY variation of success/completion claim
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

Rule applies to: exact phrases, paraphrases and synonyms, implications of success, ANY communication suggesting completion or correctness.

## Bottom Line

Run the command. Read the output. THEN claim the result. Non-negotiable.

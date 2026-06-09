# Status Code Handling

Load when processing implementer agent responses. Implementer reports exactly one of four statuses.

## DONE

Implementer finished cleanly. No concerns.

Action: proceed to spec-reviewer dispatch.

## DONE_WITH_CONCERNS

Implementer completed the work but flagged doubts.

Action:
1. Read concerns before proceeding
2. Classify concerns:
   - **Correctness or scope doubts** → address before review (ask user, re-dispatch with guidance, or break task down)
   - **Observations** (e.g., "this file is getting large", "noticed existing coupling") → note for later, proceed to review
3. Never ignore a DONE_WITH_CONCERNS without reading and classifying

## NEEDS_CONTEXT

Implementer lacks information not provided in dispatch prompt.

Action:
1. Read what's missing
2. Provide the missing context
3. Re-dispatch same task with augmented prompt
4. Same model, same task text + added context

Don't skip to a different model; context problem ≠ capability problem.

## BLOCKED

Implementer cannot complete the task.

Action: assess blocker type, apply matching response:

| Blocker type | Response |
|---|---|
| Context problem (missing info from plan) | Provide context, re-dispatch same model |
| Capability (task needs more reasoning) | Re-dispatch with more capable model |
| Size (task too big) | Break into smaller pieces, update TodoWrite, re-dispatch sub-pieces |
| Plan wrong | Escalate to user; do not try to fix plan in-flight |

Never ignore escalation. Never force same model to retry with no changes. If implementer said stuck, something must change.

## Red Flags

- Implementer returned no status code → treat as BLOCKED, investigate
- Implementer reports DONE but VCS diff is empty → verification failure, re-dispatch
- Implementer reports DONE with test output in report → verify independently per `references/verification-protocol.md`
- DONE_WITH_CONCERNS about correctness treated as DONE → skipped classification step, start over
- Dispatching same model + same prompt for BLOCKED → violates "something must change" rule

## Decision Table

| Status | Controller reads | Controller does |
|---|---|---|
| DONE | Full report | Dispatch spec-reviewer |
| DONE_WITH_CONCERNS | Full report + classify concerns | Address correctness concerns → re-dispatch; else note + dispatch spec-reviewer |
| NEEDS_CONTEXT | What's missing | Provide context, re-dispatch same model |
| BLOCKED | Blocker type | Apply response from blocker table above |

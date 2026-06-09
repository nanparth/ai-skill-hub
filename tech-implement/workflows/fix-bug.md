# Fix Bug Workflow

Bug-fix entry point. Routes through systematic debugging first, then re-enters execute-plan for the actual fix.

## Preconditions

- User reported a bug, test failure, or unexpected behaviour
- No pre-existing plan file (this is the alternative to feature-from-plan entry)

## Checklist

- [ ] Step 1: Capture bug context ⛔ BLOCKING
  - [ ] 1.1 Ask user: symptom, reproduction steps, expected vs actual, affected area (files, components)
  - [ ] 1.2 Note environment: branch, commit, recent changes if known
  - [ ] 1.3 If user points to a failing test: run it, capture output verbatim
- [ ] Step 2: Worktree setup
  - [ ] 2.1 Load `references/worktree-setup.md`
  - [ ] 2.2 Preflight + confirm branch name (suggest `fix/<slug>`) ⛔ BLOCKING
  - [ ] 2.3 Create worktree, move into it
- [ ] Step 3: Systematic debugging ⛔ BLOCKING
  - [ ] 3.1 Load `workflows/systematic-debugging.md`
  - [ ] 3.2 Complete Phase 1 (root cause investigation)
  - [ ] 3.3 Complete Phase 2 (pattern analysis)
  - [ ] 3.4 Complete Phase 3 (hypothesis + minimal test)
  - [ ] 3.5 Present root-cause analysis to user; confirm before Phase 4 ⛔ BLOCKING
- [ ] Step 4: Fix as one-task implementation
  - [ ] 4.1 Construct a single-task spec from the root-cause analysis:
    - task_name: short fix description
    - task_text: "Fix [symptom]. Root cause = [cause from Phase 1]. Approach = [hypothesis from Phase 3]. Add failing regression test first, confirm it fails for the right reason, fix, confirm it passes, revert + confirm fails, restore + confirm passes."
    - context: affected files + surrounding architecture
  - [ ] 4.2 Re-enter `workflows/execute-plan.md` at Step 3 (per-task loop) with this synthetic task
  - [ ] 4.3 Implementer dispatch follows TDD per `references/tdd-protocol.md` with bug-fix red-green-revert-restore cycle
  - [ ] 4.4 Spec + quality review + verification gate run normally
- [ ] Step 5: Finish
  - [ ] 5.1 Hand off to `workflows/finish-branch.md`

## Red Flags

- Skipping systematic debugging phases "because the fix is obvious"
- Jumping to Phase 4 without Phase 1-3 evidence
- Writing fix code before the failing regression test
- Skipping the revert-and-verify-fails step in TDD (step 4.3)
- 3+ failed fix attempts without questioning architecture (see systematic-debugging.md Phase 4.5)

## Integration

- Called by: `SKILL.md` routing (bug-fix intent)
- Uses: `workflows/systematic-debugging.md` (Phases 1-3)
- Re-enters: `workflows/execute-plan.md` Step 3 (per-task loop)
- Hands off to: `workflows/finish-branch.md`

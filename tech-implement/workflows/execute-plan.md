# Execute Plan Workflow

Feature-from-plan entry. Takes an implementation plan, runs tasks via subagents with two-stage review, verifies, finishes.

## Preconditions

- User provided a plan file path, or output from `/tech-blueprinting`
- Plan contains discrete tasks (numbered, sectioned, or bulleted)
- Working directory = git repo (worktree setup handles the rest)

## Checklist

Copy this checklist and mark items as you complete them.

- [ ] Step 1: Read plan and extract tasks ⛔ BLOCKING
  - [ ] 1.1 Read plan file fully (controller reads, not subagents)
  - [ ] 1.2 Extract each task: full text + scene-setting context
  - [ ] 1.3 Identify model tier per task (cheap = 1-2 files clean spec; standard = multi-file integration; capable = architecture or judgment)
  - [ ] 1.4 Create TodoWrite checklist, one item per task
- [ ] Step 2: Worktree setup ⛔ BLOCKING
  - [ ] 2.1 Load `references/worktree-setup.md`
  - [ ] 2.2 Run preflight checks (git repo, clean state, existing worktrees)
  - [ ] 2.3 Propose branch name; confirm with user ⛔ BLOCKING
  - [ ] 2.4 Create worktree, move into it
- [ ] Step 3: Per-task loop
  - [ ] 3.1 Mark current task `in_progress` in TodoWrite
  - [ ] 3.2 Dispatch implementer via Agent tool using `agents/implementer.md`; pass full task_text + context + working_dir + model_tier
  - [ ] 3.3 Load `references/status-code-handling.md`, then handle implementer status:
    - DONE → continue
    - DONE_WITH_CONCERNS → classify, address correctness concerns, continue
    - NEEDS_CONTEXT → provide context, re-dispatch same model
    - BLOCKED → apply blocker-type response (context / capability / size / plan-wrong)
    - If report includes `Test recommendation:` field → append to running recommendations list; do not block current task
  - [ ] 3.4 Dispatch spec-reviewer via Agent tool using `agents/spec-reviewer.md`; pass task_text + implementer_report + working_dir + commits ⛔ BLOCKING
  - [ ] 3.5 Spec issues? → re-dispatch implementer with specific fix instructions; loop to 3.4 until Approved
  - [ ] 3.6 Dispatch quality-reviewer via `agents/quality-reviewer.md` (only after spec Approved)
  - [ ] 3.7 Critical / Important issues? → re-dispatch implementer; loop to 3.6 until Approved
  - [ ] 3.8 Verification gate ⛔ BLOCKING
    - Load `references/verification-protocol.md`
    - Controller runs test command in working_dir; reads fresh output
    - Controller runs build / linter if applicable; reads fresh output
    - Confirm exit codes and output match claims
    - Fail → treat as bug; either re-dispatch implementer or route to `workflows/systematic-debugging.md`
  - [ ] 3.9 Mark task `completed` in TodoWrite
  - [ ] 3.10 More tasks? → loop to 3.1. Else → Step 4.
- [ ] Step 4: Final review
  - [ ] 4.0 Surface accumulated test recommendations from Step 3 loop. For each, propose a follow-up implementation task to add the recommended test. User decides whether to include before final review.
  - [ ] 4.1 Dispatch quality-reviewer on the whole implementation (all commits since worktree branch started)
  - [ ] 4.2 Address Critical / Important findings; loop until Approved
- [ ] Step 5: Finish
  - [ ] 5.1 Load `workflows/finish-branch.md`; hand off

## Subagent Dispatch Rules ⛔ BLOCKING

- Agents get full task text inline. Never pass plan file path.
- Agents get zero conversation context. Fresh subagent per dispatch.
- Model tier = set per task per Step 1.3, not dynamically inherited.
- Never dispatch 2+ implementer subagents in parallel. Sequential only. (Conflicts + confusion.)
- Reviewer dispatches after implementer reports = mandatory. Never skip.
- Spec review before quality review. Never reversed. Never combined.

## Red Flags

- Starting implementation on main/master without explicit user consent
- Skipping spec review or quality review
- Proceeding with unfixed spec issues to quality review
- Proceeding with unfixed quality-Critical issues to verification
- Proceeding with failed verification to next task
- Letting implementer self-review replace actual reviewer dispatch
- Claiming task complete without running verification command fresh

## Integration

- Called by: `SKILL.md` routing (feature-from-plan intent)
- Re-entered by: `workflows/fix-bug.md` at Phase 4 (bug-fix implementation)
- Hands off to: `workflows/finish-branch.md`

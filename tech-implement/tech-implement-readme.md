# tech-implement

An implementation-control skill for AI assistants. Give it a technical plan or bug report, and it runs an end-to-end coding cycle: isolated work, TDD, implementation, spec review, quality review, verification, and final branch handling.

## Part A — User Guide

### Who it's for

Engineers and maintainers who want an assistant to execute a plan or fix a bug without skipping tests, overbuilding, or claiming completion before fresh verification.

### What you need

- A Git repository and a base branch.
- A technical plan with discrete tasks, or a concrete bug report.
- A runnable project test command such as `npm test`, `pytest`, `cargo test`, or `go test ./...`.
- Optional but recommended: `git worktree` support for isolated branches.
- Optional: subagent support for implementer, spec reviewer, and quality reviewer roles.
- Optional: GitHub CLI (`gh`) for automatic pull request creation.

### Quick start

1. Copy the whole `tech-implement` folder into your assistant's skills folder.
2. Ask your assistant something like:
   - "Implement this plan: `docs/plans/add-user-auth.md`."
   - "Build this feature with TDD."
   - "Fix this failing test."
   - "Root cause this bug before changing code."
   - "Finish this branch."
3. Confirm the proposed worktree or working mode.
4. Let the skill run one task at a time, with review and verification before moving on.
5. Choose what to do with the branch: merge, push a PR, keep it, or discard it.

### What you get back

- Working code tied to the approved task text.
- Tests written before implementation where the workflow requires TDD.
- A spec-compliance review before code-quality review.
- Fresh verification output from the controller, not just subagent claims.
- A final branch decision flow and optional documentation handoff to `tech-blueprinting`.

### Modes

- **Execute plan**: extracts tasks from a plan and runs the full implementation loop.
- **Fix bug**: captures symptoms, reproduces, runs systematic debugging, then creates a synthetic TDD task for the fix.
- **Systematic debugging**: investigates root cause and stops before implementation.
- **Finish branch**: verifies, identifies base branch, and presents merge / PR / keep / discard choices.

### Safety posture

The controller is the main assistant thread. It reads the plan, extracts task text, dispatches subagents with inline context, and runs verification itself. Subagents do not reinterpret the whole plan file. Worktree isolation is preferred; if worktrees are unavailable, the skill asks before working directly in the current folder.

## Part B — Technical Reference

### Layout

```text
tech-implement/
  SKILL.md                         routing, pipeline overview, loading maps
  PORTABILITY.md                   standalone-with-optional-tools boundary
  tech-implement-readme.md         this file
  workflows/
    execute-plan.md
    fix-bug.md
    systematic-debugging.md
    finish-branch.md
  agents/
    implementer.md
    spec-reviewer.md
    quality-reviewer.md
  references/
    verification-protocol.md
    tdd-protocol.md
    worktree-setup.md
    status-code-handling.md
  shared/
    test-level-protocol.md
    code-organization.md
  scripts/
```

### Design notes

- Work is sequential by design; parallel implementers create merge conflicts and context drift.
- Spec review and quality review are separate gates. Spec comes first so scope errors are fixed before style and structure review.
- Verification is controller-owned. The controller reruns the test command fresh before marking a task complete.
- Bug fixes use root-cause analysis and a red-green-revert-restore regression-test loop.
- The final documentation offer delegates to `tech-blueprinting` instead of duplicating README-writing logic.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Git | Branch and diff operations | Required for normal feature work |
| Test command | Completion verification | Ask user for one or stop before claiming done |
| `git worktree` | Isolated work directory | Ask before working in current folder |
| Subagent support | Implementer and two reviewers | Run the same roles sequentially in the main assistant |
| GitHub CLI (`gh`) | Push + PR option | Provide manual push/PR instructions |
| `tech-blueprinting` | Optional README/doc handoff | Skip documentation handoff |

### Maintenance notes

- Implementer status codes are a fixed contract: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`.
- Keep `references/status-code-handling.md` synchronized with implementer output format.
- Changes to `shared/test-level-protocol.md` affect `tech-blueprinting`; update both skills' summaries together.
- This skill intentionally has no deterministic scripts today; add scripts only for repeatable mechanical work.

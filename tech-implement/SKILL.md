---
name: tech-implement
description: 'Use when committing to a full implementation cycle: worktree isolation, TDD, subagent dispatch, and two-stage review. Trigger on: "implement this plan", "build this feature", "fix this bug", "root cause this", "implement with TDD", "subagent-driven development". Not for ad-hoc edits, writing specs, or architectural overhauls.'
argument-hint: '[plan.md] [--mode implement|debug]'
---

# tech-implement

Execute implementation plans or bug fixes with TDD, isolated work, subagent review, and verification gates.

## Required Dependencies

- Git.
- Shell access.
- A runnable project test command such as `pytest`, `npm test`, `cargo test`, or a user-provided command.
- Subagent support for the full pipeline. Without subagents, follow the checklists manually and do one task at a time.

Optional: GitHub CLI (`gh`) for pull request creation. If `gh` is unavailable, push the branch manually or provide PR instructions instead.

## Routing

| Intent | Action |
| --- | --- |
| User has a plan file or `tech-blueprinting` output to execute | Load `workflows/execute-plan.md` |
| User reports a bug or test failure needing a fix | Load `workflows/fix-bug.md` |
| User wants systematic debugging without committing to a fix | Load `workflows/systematic-debugging.md` |
| User wants to finish a branch already in progress | Load `workflows/finish-branch.md` |

If intent is ambiguous, ask whether this is a plan to execute, a bug to fix, or in-progress work to finish.

## Pipeline Overview

```text
Feature from plan:
  plan -> task extraction -> worktree -> per-task loop -> final review -> finish -> optional docs

Per-task loop:
  implementer subagent -> spec reviewer -> quality reviewer -> verification gate -> mark complete

Bug fix:
  bug report -> worktree -> systematic debugging -> synthetic task -> per-task loop -> finish
```

## Core Principles

- Agents receive full task text inline. They do not read the plan file.
- Fresh subagent per task. No conversation context is inherited.
- TDD is mandatory. No production code without a failing test first.
- Two-stage review is mandatory: spec compliance first, code quality second.
- Verification is a gate. Run commands, read output, and check exit codes before claiming completion.
- Implementer dispatches are sequential only.
- Worktree isolation is the default for normal Git repositories.
- One responsibility per module. Use explicit interfaces.

## Loading Maps

### Workflows

| Workflow | File | Load when |
| --- | --- | --- |
| Execute plan | `workflows/execute-plan.md` | User has a plan or spec to execute. |
| Fix bug | `workflows/fix-bug.md` | User reports a bug or test failure. |
| Systematic debugging | `workflows/systematic-debugging.md` | Verification fails, or bug-fix investigation starts. |
| Finish branch | `workflows/finish-branch.md` | All tasks complete and ready for merge, PR, or handoff. |

### Agents

| Agent | File | Purpose |
| --- | --- | --- |
| Implementer | `agents/implementer.md` | Implement one task with TDD, commit, self-review, and report status. |
| Spec Reviewer | `agents/spec-reviewer.md` | Verify the implementation matches the requested spec. |
| Quality Reviewer | `agents/quality-reviewer.md` | Review code quality after spec review passes. |

### References

| Need | Reference |
| --- | --- |
| Verification discipline and evidence-before-claims | `references/verification-protocol.md` |
| TDD red-green-refactor and bug-fix cycle | `references/tdd-protocol.md` |
| Git worktree commands, preflight checks, naming, and fallbacks | `references/worktree-setup.md` |
| Implementer statuses | `references/status-code-handling.md` |
| Test level decision | `shared/test-level-protocol.md` |
| Code organization | `shared/code-organization.md` |

## Test Level Gate

Load `shared/test-level-protocol.md` when any boundary signal is present in the plan: subprocess spawn, IPC or HTTP boundary, filesystem state written then read, lock or PID coordination, external tool, cross-language boundary, CLI entrypoint, public schema, config, API payload, or file format change.

Skip when the task is a single module with pure logic and no I/O. Decide the level, then use `references/tdd-protocol.md` for the red-green-refactor pattern.

## Fallbacks

- No `gh`: skip automated PR creation. Push with Git or report the branch and PR body for manual creation.
- No worktree support: ask before working directly in the current folder. Do not assume direct edits are acceptable.
- Target is not a normal Git repository: ask before working directly in the current folder, and explain what safety is lost.
- No subagent support: execute the same checklists manually, one task at a time, and run review passes yourself before verification.

## Optional Documentation Finish

At the end of a run, offer neutral documentation choices:

1. Update the project `README.md`.
2. Create `docs/<topic>.md`.
3. Skip documentation.

If `tech-blueprinting` is installed, it can help write those docs. Otherwise, write or skip them directly based on the user's choice.

## Portable Conventions

- Use the target project's language, style, and test conventions.
- Keep scratch files under `.tmp/` and do not commit them.
- Do not commit secrets, credentials, generated noise, or unrelated refactors.
- Task format in plans may use checkboxes, numbered lists, or clear section headings.
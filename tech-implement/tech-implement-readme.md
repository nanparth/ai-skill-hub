# tech-implement

`tech-implement` helps an AI assistant turn a plan or bug report into code changes using TDD, worktree isolation, verification gates, and review passes.

## Use This If

Use this skill when you are ready to build, fix, or finish code in a Git project. It is not meant for casual one-line edits or early architecture brainstorming.

## Required Dependencies

- Git.
- Shell access.
- A project-specific test command.
- Subagent support for the full pipeline.

Without subagents, use the same workflow manually and do one task at a time.

## Optional Dependencies

- Git worktrees for safer isolated work.
- GitHub CLI (`gh`) for pull request creation.
- `tech-blueprinting` for optional docs at the end.

## Main Workflows

- Execute a plan: `workflows/execute-plan.md`.
- Fix a bug: `workflows/fix-bug.md`.
- Investigate root cause: `workflows/systematic-debugging.md`.
- Finish a branch: `workflows/finish-branch.md`.

## Fallbacks

- No `gh`: push manually or provide PR text for the user.
- No worktree support: ask before editing the current folder directly.
- Not a normal Git repository: ask before editing and explain the safety trade-off.
- No test command: ask for one before claiming verification.

## Scratch Files

Use `.tmp/` for temporary logs, repro inputs, and debugging notes. Do not commit scratch files.

## Files To Copy

Copy the whole `tech-implement/` folder. Required local files include `SKILL.md`, `workflows/`, `agents/`, `references/`, `shared/`, and `PORTABILITY.md`.
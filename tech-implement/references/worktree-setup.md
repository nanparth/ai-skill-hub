# Worktree Setup

Use this reference before implementation or bug-fix work that changes a Git project.

## Required Preflight

1. Confirm the current folder is a Git repository: `git rev-parse --show-toplevel`.
2. Check status: `git status --short`.
3. If unrelated user changes exist, do not overwrite them. Ask before touching files that are already modified.
4. Identify the base branch: usually `main` or `master`, unless the user names another branch.
5. Run the current test command if the user provided one, or ask for it if unknown.

## Worktree Default

Use a Git worktree for feature work and bug fixes whenever possible.

Suggested branch names:

- `feature/<short-topic>` for planned feature work.
- `fix/<short-topic>` for bug fixes.
- `refactor/<short-topic>` for approved refactor tasks.

Typical commands:

```bash
git worktree add ../<repo-name>-<branch-slug> -b <branch-name>
cd ../<repo-name>-<branch-slug>
```

After moving into the worktree, run `git status --short` and the baseline test command again.

## Fallbacks

If worktrees are unavailable, ask before working directly in the current folder. Explain that direct edits make rollback and parallel work less safe.

If the target is not a normal Git repository, ask before editing. Confirm where backups, scratch files, and outputs should go.

If the current branch already contains user work, do not rebase, reset, stash, or overwrite it unless the user explicitly asks.

## Scratch Files

Keep temporary files under `.tmp/` inside the active worktree or project folder. Do not commit `.tmp/` contents.

Examples:

- `.tmp/debug-<timestamp>.log`
- `.tmp/repro-input.json`
- `.tmp/manual-check-notes.md`

Delete scratch files when they are no longer needed, or leave them ignored if they are useful for user review.

## Baseline Tests

Before making changes, record:

- Test command used.
- Whether it passed before changes.
- Any known pre-existing failures.
- Build or lint command if relevant.

Do not claim a new change broke or fixed something unless you have fresh command output.
# Finish Branch Workflow

End of run. Verify, present options, execute the user's choice, clean up when appropriate, and offer documentation.

## Preconditions

- All implementation tasks are complete.
- Final quality review passed.
- Worktree contains feature or fix commits.

## Checklist

- [ ] Step 1: Verify tests
  - [ ] 1.1 Run the full test suite in the worktree.
  - [ ] 1.2 Read output and confirm zero unexpected failures.
  - [ ] 1.3 Run build or linter if applicable.
  - [ ] 1.4 If tests fail, stop and present failures.

- [ ] Step 2: Determine base branch
  - [ ] 2.1 Try `main`, then `master`, unless the user named another base branch.
  - [ ] 2.2 If ambiguous, ask the user to confirm the base branch.

- [ ] Step 3: Present options

  ```text
  Implementation complete. What would you like to do?

  1. Merge back to <base-branch> locally
  2. Push and create a pull request
  3. Keep the branch as-is
  4. Discard this work

  Which option?
  ```

- [ ] Step 4: Execute choice
  - [ ] Option 1: merge locally, rerun tests on the merged result, then delete the feature branch only if tests pass.
  - [ ] Option 2: push the branch. If `gh` is available, create the pull request. If not, provide the branch name, PR title, PR body, and test plan for manual PR creation.
  - [ ] Option 3: keep the branch and worktree. Report their paths.
  - [ ] Option 4: require typed confirmation before deleting commits, branch, or worktree.

- [ ] Step 5: Cleanup worktree
  - [ ] Only clean up for Option 1 or confirmed Option 4.
  - [ ] Never auto-clean the worktree for pushed PRs or kept branches.

- [ ] Step 6: Offer documentation

  ```text
  Would you like to update docs for this work?

  1. Update the project README.md
  2. Create docs/<topic>.md
  3. Not now
  ```

  If the user chooses docs and `tech-blueprinting` is installed, use its README or technical-doc workflow. Otherwise write the selected doc directly.

## Red Flags

- Proceeding with failing tests.
- Merging without rerunning tests on the merged result.
- Deleting work without typed confirmation.
- Force-pushing without explicit user request.
- Auto-cleaning worktree for pushed PRs or kept branches.

## Integration

- Called by: `workflows/execute-plan.md` Step 5 and `workflows/fix-bug.md` Step 5.
- Optional docs handoff: `tech-blueprinting` if installed.
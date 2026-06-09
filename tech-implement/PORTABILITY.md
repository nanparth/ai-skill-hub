# Portability

Classification: standalone_with_optional_tools

This skill is self-contained. Required workflow, agent, reference, and shared guidance files live inside the skill folder.

## Required When Copying

Copy the entire `tech-implement/` folder, including:

- `SKILL.md`
- `PORTABILITY.md`
- `tech-implement-readme.md`
- `workflows/`
- `agents/`
- `references/`
- `shared/`

## Required Runtime Dependencies

- Git.
- Shell access.
- A runnable project test command supplied by the project or user.

## Optional Dependencies

- Git worktree support. If unavailable, ask before working directly in the current folder.
- Subagent support for the full implementer, spec reviewer, and quality reviewer pipeline. If unavailable, run the same steps manually.
- GitHub CLI (`gh`) for automatic pull request creation. If unavailable, provide branch and PR instructions for manual creation.
- `tech-blueprinting` for optional documentation handoff after implementation.

## No Vault Or Personal Path Dependencies

No vault or personal path dependencies. The skill works against the user's selected Git project. Scratch files should stay under `.tmp/` in the active project or worktree.
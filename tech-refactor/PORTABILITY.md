# Portability

Classification: standalone

This skill is self-contained. Required references and shared guidance live inside the skill folder.

## Required When Copying

Copy the entire `tech-refactor/` folder, including:

- `SKILL.md`
- `PORTABILITY.md`
- `tech-refactor-readme.md`
- `references/`
- `shared/`

## Required Runtime Dependencies

No runtime dependency is required for the analysis and roadmap workflow beyond the host assistant's normal ability to read project files.

## Optional Dependencies

- Git is useful for history review and change safety.
- Test commands are needed only if the user asks to execute the roadmap.
- `tech-implement` is optional for executing approved tasks. Without it, this skill stops after the execution-ready roadmap unless the user asks for manual execution.

## No Vault Or Personal Path Dependencies

No vault or personal path dependencies. The target codebase path is provided by the user at runtime, and all bundled guidance is skill-local.
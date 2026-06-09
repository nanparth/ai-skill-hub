# README Write Workflow

Produce clear README documentation for a skill folder or project component.

This workflow bypasses the full three-stage collaboration process. READMEs need thorough source reading, accurate structure, and a final quality check.

## Argument Parsing

Parse arguments at workflow start:

1. First positional argument: skill name, skill folder path, or component path.
2. `--type skill|component`: force target type.
3. `--output <path>`: explicit output path.
4. `--update`: update an existing README instead of creating from scratch.
5. If no arguments are provided, ask what to document.

## Output Path

If `--output` is not provided, ask the user where to save the README.

Neutral defaults:

- Skill folder: `<skill-folder>/<skill-name>-readme.md`.
- Project component: `docs/<component-name>-readme.md`.

If a README already exists at the output path and `--update` was not provided, ask whether to update or overwrite.

## Source Reading Protocol

Before drafting any README, complete the relevant reading pass.

### Skill Folder

1. List files inside the skill folder.
2. Read `SKILL.md` completely.
3. Read every referenced file in `references/`, `workflows/`, `agents/`, `scripts/`, `assets/`, and `shared/` that affects user-facing behavior.
4. Trace external dependencies. If a dependency is outside the skill folder, document it as external and ask before relying on it.
5. For scripts, read the code and capture CLI arguments, requirements, error handling, and output format.

### Project Component

1. Read the target file completely.
2. Scan imports and cross-file dependencies.
3. Read related modules, config files, tests, and public entrypoints.
4. For multi-file components, list the containing folder and read the files that define behavior.

Do not draft until reading is complete.

## Create README

1. Load `references/readme-template.md`.
2. Run the source reading protocol.
3. Decide whether a diagram would clarify workflows, routing, data flow, or state transitions.
4. Draft sections following the template.
5. Write the README to the selected output path using the host assistant's normal file-writing method.
6. Load `references/readme-self-review.md` and check the draft.
7. Fix failures before presenting the README.

## Update README

1. Read the existing README.
2. Run the source reading protocol.
3. Load `references/readme-template.md`.
4. Identify changed behavior, new files, removed files, new dependencies, and stale examples.
5. Update affected sections in place. Preserve user-edited content where intent is clear.
6. Load `references/readme-self-review.md` and check the update.
7. Fix failures before presenting the diff summary.

## Reference Loading Map

| Need | File |
| --- | --- |
| Section structure and writing guidance | `references/readme-template.md` |
| Quality gate before delivery | `references/readme-self-review.md` |

## Conventions

- Use the user's spelling and style conventions when known.
- Prefer concrete usage examples over abstract description.
- Do not hardcode machine-local paths.
- Do not require a separate private document app, document-conversion tool, or project-management tool.
- Filename convention: `<name>-readme.md`, lowercase and hyphen-separated, unless the project already uses another convention.
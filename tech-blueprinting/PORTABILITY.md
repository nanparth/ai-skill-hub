# Portability

Classification: standalone_with_optional_tools

This skill is self-contained. Required references live inside the skill folder under `workflows/`, `agents/`, `references/`, and `shared/`.

## Required When Copying

Copy the entire `tech-blueprinting/` folder, including:

- `SKILL.md`
- `PORTABILITY.md`
- `tech-blueprinting-readme.md`
- `workflows/`
- `agents/`
- `references/`
- `shared/`
- `scripts/`

## Required Runtime Dependencies

The core document workflow requires only the host assistant's normal ability to read and write files.

## Optional Dependencies

The visual companion is optional. It requires:

- Node.js to run `scripts/server.cjs`.
- Shell support to run `scripts/start-server.sh` and `scripts/stop-server.sh`.
- A local browser to view the generated URL.

Subagent support improves spec review and reader testing. If unavailable, run those checks manually from the same checklists.

## No Vault Or Personal Path Dependencies

No vault or personal path dependencies. Output should go to a user-selected path. If no path is provided, suggest `./docs/<document-name>.md`.

## Adapter Notes

DOCX conversion is not bundled. Draft markdown first, then use any external converter the user's environment provides if a Word file is needed.
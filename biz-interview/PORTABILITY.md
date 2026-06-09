# Portability

Classification: standalone_with_optional_tools

This skill runs from a copied folder with no machine-local paths, private project paths, or shared-folder dependencies.

## Required When Copying

Copy the entire `biz-interview/` folder, including:

- `SKILL.md`
- `PORTABILITY.md`
- `biz-interview-readme.md`
- `workflows/`
- `agents/`
- `references/`
- `scripts/`
- `requirements.txt`

## Required Runtime Dependencies

Core interview design, transcript cleanup, mock interview generation, and qualitative analysis workflows require only the host assistant's normal ability to read and write files.

## Optional Dependencies

- Python 3.9+ for spreadsheet helpers.
- `openpyxl` for `.xlsx` matrix and co-occurrence exports. Install with `pip install -r requirements.txt` from this skill folder.
- Subagent support improves mock interview generation and coding throughput, but small batches can be run manually by the host assistant.

## No Vault Or Personal Path Dependencies

No vault or personal path dependencies. User-generated outputs should be written to a user-selected project or output folder. If no location is provided, suggest `./outputs/biz-interview/customer-discovery/`.
# Portability

Classification: workbench_only_needs_refactor

This skill has a sanitized public entry surface, but the full folder should not be treated as plug-and-play until the internal workflows, scripts, tests, and examples complete a standalone portability pass.

## Portable Surface

The following files are intended to be safe public entry points:

- `SKILL.md`
- `life-jobapps-readme.md`
- `PORTABILITY.md`
- `workflows/` after internal review
- `references/voice-references.md`
- `assets/` law templates
- `scripts/` only after office helpers are bundled or documented as external

## Required When Copying

Do not copy this folder as a standalone public skill yet. If used inside this workbench, copy the whole $skill/ folder so internal references continue to resolve.

## Required Runtime Dependencies

- User-provided job posting or role description.
- User-provided source material such as resume, CV, content bank, past application examples, or experience notes.
- Host assistant file-writing ability for Markdown or plain-text outputs.

## Optional Dependencies

- Python 3 for bundled DOCX injection scripts.
- External office helper utilities for DOCX unpack/pack/validate, provided by `LIFE_JOBAPPS_OFFICE_DIR` or bundled later under `shared/office/`.
- Bundled law-specific DOCX templates in `assets/` for legal cover-letter and CV rendering.

## No Vault Or Personal Path Dependencies

The public README, SKILL.md, and this portability note use neutral paths and user-selected output locations. Remaining internals may still contain workbench-specific assumptions and must be audited before release.

## Required Before Public Release

- Bundle or remove the external office helper dependency.
- Add non-law template/script pairs or clearly label DOCX rendering as law-specific.
- Add synthetic examples and remove any remaining private application assumptions.
- Run script syntax checks and a copied-alone render smoke test.

## Adapter Notes

Classify the skill as standalone or standalone_with_optional_tools only after the internal scan is clean, every required file lives inside the skill folder, and a copied-alone smoke test passes.

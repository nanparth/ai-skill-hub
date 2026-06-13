# Portability

Classification: standalone_with_optional_tools

The copied folder works alone with any AI assistant that supports folder-based skills, file read/write, and shell access for the bundled Python helpers. It targets Obsidian-flavoured markdown but operates on any plain-markdown notes folder. Subagent dispatch, the Obsidian CLI, and a tag-taxonomy file improve results; every step that uses them carries a documented fallback.

## Portable Surface

- `SKILL.md` — routing, shared conventions, long-file protocol, output policy
- `workflows/` — new-note, rewrite-note, reformat-note, merge-note, process-source
- `references/obsidian-syntax.md` — markdown + Obsidian syntax authority
- `references/multipart-series.md` — multi-part series conventions
- `shared/text/scripts/` — `long_file_plan.py` (chunk planner), `strip_pua_artifacts.py`, `strip_html_artefacts.py`, `check_dead_embeds.py` (all stdlib-only Python 3.10+)
- `tests/` — merge smoke-test harness (`run_merge_smoke.sh`, `verify_merge.py`, fixtures)
- `note-readme.md` — user guide and technical reference

## Required When Copying

Copy the whole `note/` folder into the host assistant's skills folder (for example `~/.claude/skills/note/` in Claude Code; equivalent locations in other assistants).

## Required Runtime Dependencies

- File read/write on the user's notes folder
- Python 3.10+ for the long-file planner and artefact strippers (only needed for long files and PDF/DOCX-converted sources; short-file workflows run without Python)

## Optional Dependencies

- Subagent dispatch: chunked operators for long-file rewrite/reformat/merge. Fallback: run the same chunked protocol inline.
- Obsidian CLI: `rename` (auto-updates wikilinks) and scalar `property:set`. Fallback: direct file edits; manual inbound-link check after renames.
- A user-maintained tag-taxonomy file: controlled tag vocabulary. Fallback: derive tags from content.
- Obsidian (the app): renders wikilinks, callouts, embeds. Fallback: any markdown editor; outputs remain plain text.

## Adapter Notes

- User-decision gates expect a structured choice UI; every gate carries a plain-text numbered-list fallback. Artifacts >40 lines are presented in their own turn before the gate.
- Output default `./notes/outputs/` is user-adjustable; confirm on first write.
- Read-only source folders are user-designated; the workflows enforce whatever set the user names.
- Wikilink conventions apply when the note app supports them; otherwise use relative markdown links.
- Shell examples are POSIX-flavoured; the smoke-test harness requires bash and `sha256sum`.

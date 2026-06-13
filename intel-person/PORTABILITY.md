# Portability

Classification: standalone_with_optional_tools

The copied folder works alone with any AI assistant that supports folder-based skills, web search, and direct URL fetching. Browser automation (agent-browser) and a note-authoring skill improve results but are optional; every step that uses them carries a documented fallback.

## Portable Surface

- `SKILL.md` — entry point and core workflow
- `workflows/from-web.md` — URL-first research
- `workflows/from-local-notes.md` — existing-notes-first extraction
- `references/research-checklist.md` — built-in note schema and gap-analysis spec
- `agents/intel-person-researcher.md` — researcher process (subagent template or inline checklist)
- `intel-person-readme.md` — user guide and technical reference
- `PORTABILITY.md` — dependency and copy boundary

## Required When Copying

Copy the whole `intel-person/` folder into the host assistant's skills folder (for example `~/.claude/skills/intel-person/` in Claude Code; equivalent locations in other assistants).

## Required Runtime Dependencies

- Web search capability
- Direct URL fetching
- File read/write for the output note

## Optional Dependencies

- agent-browser CLI (https://github.com/vercel-labs/agent-browser): scraping JS-rendered sites, screenshots, headshot capture, network-request inspection. Fallback: direct page fetch; visual assets skipped and recorded as gap flags.
- A note-authoring skill: structured note creation. Fallback: write the note directly from the checklist schema.
- Obsidian-style callout rendering for the Research Log. Fallback: plain `## Research Log` section.

## No Vault Or Personal Path Dependencies

The skill does not require a private vault, sibling skill, or machine-local folder. Local-note inputs are user-selected files or folders, and generated profile notes are written only to the user-confirmed destination. The default output root is the neutral project path `./intel/`.

## Adapter Notes

- User-decision gates expect a structured choice UI; every gate carries a plain-text numbered-list fallback.
- The researcher runs as a subagent where the host supports dispatch; otherwise execute its process inline.
- Output root is user-selected; default `./intel/`.
- Shell examples are POSIX-flavoured (`mkdir -p`, `curl`, heredocs); adjust for other shells.

## Public Defaults

- The skill never auto-writes a profile note; it asks the user to confirm the destination first.
- LinkedIn and social media URLs are recorded only and are not scraped.
- Browser screenshots, headshot capture, and network inspection are opt-in through the optional browser tool; without it, the skill records those assets as skipped.
- Research output uses source labels and gap flags so users can distinguish verified, partial, and missing fields.

# intel-person

A research skill for AI assistants. Give it a person's name (and optionally a link to their site or bio), and it researches them online and in your existing notes, then builds a structured profile note: career timeline, education, awards, affiliations, interests, and a log of where every fact came from.

## Part A — User Guide

### Who it's for

Anyone who keeps notes on people they meet or work with: consultants, lawyers, founders, recruiters, event organizers, networkers.

### What you need

- An AI assistant that supports folder-based skills (Claude Code is one example; any assistant with a skills folder works).
- Web search and web access enabled in the assistant.

**Optional but recommended:** the agent-browser command-line tool. With it, the skill can read JavaScript-heavy websites, capture screenshots, and save a headshot from the person's bio page. Without it, the skill still works; it fetches pages directly and simply skips screenshots and headshot capture. To set it up, visit https://github.com/vercel-labs/agent-browser and follow the install instructions there.

### Quick start

1. Copy the whole `intel-person` folder into your assistant's skills folder (for example `~/.claude/skills/intel-person/` in Claude Code).
2. Ask your assistant something like:
   - "intel on Jordan Lee, here's their site: https://example.com"
   - "build profile for Jordan Lee"
   - "make intel note for Jordan Lee, I have notes at notes/panel-bios.md"
3. Answer the questions the skill asks (how you know the person, whether to proceed past any information gaps, and where to save the note).

### What you get back

A single markdown profile note saved where you choose (default `./intel/people/`), containing:

- Frontmatter fields: name, aliases, occupation, organization, location, website, contact details
- Biographical details and a chronological career timeline
- Practice/expertise areas, affiliations, awards, interests
- A short positioning analysis: how the person presents themselves publicly
- A verification tag showing whether facts came from first-party sources
- A collapsed Research Log recording the searches and seed links used

Headshots and screenshots (when browser tooling is available) are saved beside the note under `assets/`.

### Modes

- **Web-first**: you give a name and maybe a URL; the skill searches, reads pages, and compiles the profile.
- **Notes-first**: you point at existing notes (event bios, meeting notes); the skill extracts what you already have, then fills gaps from the web.
- **Pasted bio**: paste a speaker bio or similar text; the skill extracts from it and supplements online.

### Privacy posture

The skill researches public sources only. LinkedIn and social media are never scraped (authentication walls); their URLs are recorded for your reference. Profile notes stay on your machine in the folder you choose.

## Part B — Technical Reference

### Layout

```text
intel-person/
  SKILL.md                          entry point: input parsing, relationship gate,
                                    routing, gap analysis, note assembly
  PORTABILITY.md                    classification + dependency boundary
  intel-person-readme.md            this file
  workflows/
    from-web.md                     URL-first research pass
    from-local-notes.md             existing-notes-first extraction pass
  references/
    research-checklist.md           built-in note schema, gap flags, source map
  agents/
    intel-person-researcher.md      researcher process: scrape, headshot capture, brief
```

### Design notes

- The checklist in `references/research-checklist.md` is the default note schema; a user-supplied template overrides it at runtime.
- The researcher in `agents/` is written as a subagent template. Hosts without subagent support execute the same process inline.
- Every user-decision point is a hard stop: structured choice where the host supports it, numbered plain-text list where it doesn't.
- The headshot capture protocol screenshots the bio page first, then downloads the largest direct image URL; dynamic/blob images degrade to the screenshot.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Web search | Finding sources | Required; skill needs it for web-first mode |
| Direct URL fetch | Reading pages, API endpoints | Required for web research |
| agent-browser CLI (https://github.com/vercel-labs/agent-browser) | JS-rendered sites, screenshots, headshot capture, network inspection | Pages fetched directly; visual assets skipped and recorded as gap flags |
| Note-authoring skill | Structured note creation | Skill writes the note directly from the checklist schema |
| Subagent dispatch | Isolated researcher run | Researcher process executed inline |
| Obsidian-style callouts | Collapsed Research Log block | Plain `## Research Log` section |

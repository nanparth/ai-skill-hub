# intel-org

A research skill for AI assistants. Give it an organization's name (and optionally a website link), and it researches the organization online and in your existing notes, then builds a structured profile note: identity, key people, milestones, focus areas, and a log of where every fact came from.

## Part A — User Guide

### Who it's for

Anyone who keeps notes on companies, firms, agencies, or nonprofits they deal with: consultants, lawyers, founders, researchers, job seekers.

### What you need

- An AI assistant that supports folder-based skills (Claude Code is one example; any assistant with a skills folder works).
- Web search and web access enabled in the assistant.

**Optional but recommended:** the agent-browser command-line tool. With it, the skill can read JavaScript-heavy websites, capture screenshots, and save the organization's logo. Without it, the skill still works; it fetches pages directly and simply skips screenshots and logo capture. To set it up, visit https://github.com/vercel-labs/agent-browser and follow the install instructions there.

### Quick start

1. Copy the whole `intel-org` folder into your assistant's skills folder (for example `~/.claude/skills/intel-org/` in Claude Code).
2. Ask your assistant something like:
   - "intel on Acme Robotics"
   - "build org profile for Northwind Legal, here's their site: https://example.com"
   - "company intel on Fabrikam, I have an existing note at notes/fabrikam.md"
3. Answer the questions the skill asks (your relationship to the organization, whether to proceed past any information gaps, and where to save the note).

### What you get back

A single markdown profile note saved where you choose (default `./intel/organizations/`), containing:

- Frontmatter fields: name, aliases, type, headquarters, website, sector, size, founding year, and more
- A profile table and milestones timeline
- Key people, focus areas, and notable affiliations
- A verification tag showing whether facts came from first-party sources
- A collapsed Research Log recording the searches, seed links, and databases used

Logos and screenshots (when browser tooling is available) are saved beside the note under `assets/`.

### Modes

- **Web-first**: you give a name and maybe a URL; the skill searches, reads pages, and compiles the profile.
- **Notes-first**: you point at existing notes; the skill extracts what you already have, then fills gaps from the web.
- **Pasted text**: paste an About page or press release; the skill extracts from it and supplements online.

## Part B — Technical Reference

### Layout

```text
intel-org/
  SKILL.md                          entry point: input parsing, relationship gate,
                                    routing, gap analysis, note assembly
  PORTABILITY.md                    classification + dependency boundary
  intel-org-readme.md               this file
  workflows/
    from-web.md                     URL-first research pass
    from-local-notes.md             existing-notes-first extraction pass
  references/
    research-checklist.md           built-in note schema, gap flags, source map
  agents/
    intel-org-researcher.md         researcher process: scrape, logo capture, brief
```

### Design notes

- The checklist in `references/research-checklist.md` is the default note schema; a user-supplied template overrides it at runtime.
- The researcher in `agents/` is written as a subagent template. Hosts without subagent support execute the same process inline.
- Every user-decision point is a hard stop: structured choice where the host supports it, numbered plain-text list where it doesn't.
- LinkedIn and social media are never scraped (authentication walls); their URLs are recorded only.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Web search | Finding sources | Required; skill needs it for web-first mode |
| Direct URL fetch | Reading pages, API endpoints | Required for web research |
| agent-browser CLI (https://github.com/vercel-labs/agent-browser) | JS-rendered sites, screenshots, logo capture, network inspection | Pages fetched directly; visual assets skipped and recorded as gap flags |
| Note-authoring skill | Structured note creation | Skill writes the note directly from the checklist schema |
| Subagent dispatch | Isolated researcher run | Researcher process executed inline |
| Obsidian-style callouts | Collapsed Research Log block | Plain `## Research Log` section |

# CV / résumé tailoring workflow

Profession-agnostic. Bundled rendering scripts and DOCX templates are currently law-specific (see assets); workflow logic transfers to any profession (engineering, consulting, research, design, finance, government, …).

Tailor master CV for specific job application. Following from step zero compresses pass nine to pass one or two.

## When to load

- User asks to tailor CV/résumé to specific role
- User has posting and wants master CV reshaped for target
- User has draft CV and wants structural review against a sample

## Inputs ⛔ BLOCKING

- Job posting (link, file, or pasted text)
- Target employer name and role title
- Master CV path (default: `./job-applications/assets/master-cv.md`)
- Companion cover letter path if exists
- Sample CV in target firm's format if user has one (DOCX, PDF, or MD); see Stage 1.2

## Workflow

### Stage 1: Voice and structural reference load ⛔ BLOCKING

Step zero. Skipping produces credential-piling and structural drift from target-firm convention.

- [ ] 1.1 Read `references/voice-references.md` for voice. CV register differs from prose: telegraphic bullets, verb-forward, no em dashes, Canadian English, two spaces after sentence-ending periods, sentence case for headings.
- [ ] 1.2 ⚠️ STRUCTURAL REFERENCE: Read at least one well-formed CV in the target firm's format. Priority order: (a) sample CV provided by user from target firm, (b) past tailored CV from `./job-applications/materials/`, (c) master CV at `./job-applications/assets/master-cv.md`. Note structural moves: section divider style, section order, sub-header use, bullet density per sub-header, treatment of Education/Bar/Publication/Community/Skills/Languages/Interests.
- [ ] 1.3 Read `./job-applications/assets/content-bank.md` for closest positioning angle and unabridged experience inventory.
- [ ] 1.4 Note sample word-count baseline. Target ~1,350-1,750 words.

### Stage 2: Pillar and emphasis brainstorm ⛔ BLOCKING

User drives.

- [ ] 2.1 Read job posting carefully
- [ ] 2.2 Propose 3-4 capability pillars scaffolding the CV narrative for this role. Pillars drive section emphasis, sub-header naming, bullet selection.
- [ ] 2.3 ⚠️ REQUIRED: Confirm final pillar list with user before continuing

### Stage 3: Job-posting mapping ⛔ BLOCKING

- [ ] 3.1 List each posting Major Responsibility bullet
- [ ] 3.2 List each posting Knowledge and Skills item
- [ ] 3.3 Map each posting bullet to role/evidence on CV that serves it
- [ ] 3.4 Flag posting bullets not covered by current CV evidence. Decide: add detail from content bank, restructure, or accept gap.
- [ ] 3.5 ⚠️ REQUIRED: Present mapping table to user; confirm before drafting

### Stage 4: Section structure decision ⛔ BLOCKING

CV ordering is a user-driven judgment call, not auto-set. Two patterns work for this user:

**Pattern A — Capability-themed groups** (lets reader find target-relevant work fast):
- For law tech-trans: `## Tech transactions, IP, and commercial experience` (industry roles) then `## Legal experience` (court, firm, research).
- For product or engineering: `## Engineering and product experience` then `## Research and academic experience`.
- For consulting: `## Client consulting` then `## Internal operations`.
- Best when one capability cluster materially leads the pitch and standard reverse-chronological would bury the headline experience.

**Pattern B — Flat reverse-chronological** (single `## Experience`, most recent first):
- Best when all roles are uniformly role-relevant and chronology itself tells the story.

Within either pattern, **reverse chronological by end date within each group** is the default. Ongoing roles lead. Primary full-time current role above part-time advisory current role.

- [ ] 4.1 Propose Pattern A vs B with one-line rationale tied to pillars + posting
- [ ] 4.2 ⚠️ REQUIRED: User picks pattern and group labels (if Pattern A). User drives.

### Stage 5: Section reordering and evidence selection

- [ ] 5.1 Order experiences per chosen pattern
- [ ] 5.2 For each role, pick which sub-headers and bullets to keep from content bank; trim or omit content irrelevant to target
- [ ] 5.3 **Bullet density cap**: target 2-3 bullets per sub-header. Subsection running 7-10 bullets reads as a wall; split into more sub-headers or compress to 4-5 best bullets.
- [ ] 5.4 **RA / side-role compression**: don't list every PI or every side role. Pick the N most relevant to the target. For a law tech-trans role, prefer data-law and corporate-law RAs over admin-law. For a research role, prefer the closest subject-matter PIs. For a product role, prefer RAs with measurable shipped deliverables.
- [ ] 5.5 Decide what to demote or drop entirely. Past moves: drop off-pitch subject-matter RAs; drop pure-litigation bullets under tech-trans CV; compress clerkship bench-memo list to highest-signal subject areas; drop Publication section if no relevant papers; drop side roles that don't connect to the target capability cluster.

### Stage 6: Draft

Format conventions are sample-CV-aligned and have landed for this user.

- [ ] 6.1 **Header**: Name (H1), then single inline contact line: email | location | LSO licence #. No tagline paragraph. Cover letter carries the thesis; CV does not repeat.
- [ ] 6.2 **Section dividers**: HR `---` line before and after each major `##` heading. Mimics target's DOCX visual hierarchy.
- [ ] 6.3 **No org intro paragraphs** under role headings. "X is an AI startup building..." adds words without signal. Reader infers context from role title + bullets.
- [ ] 6.4 **Sub-headers inside roles**: bold colon labels (e.g. `**Commercial drafting and negotiation:**`), each carrying 2-3 bullets. Caps wall risk and groups evidence thematically.
- [ ] 6.5 **Professional licences and certifications folded into Education and Certification**, not standalone. Examples: Bar admission (LSO, LSBC, NY Bar), PEng, CFA, CPA, CISSP, AWS Solutions Architect, ISO 27001 Lead Auditor. Sub-heading `**[Licence Title] | [Issuing Body]**` with one short bullet or paragraph on call/issue date, licence number, and standing.
- [ ] 6.6 **Publication separate from Community Involvement**. Papers under `## Publication` (drop section entirely if no relevant papers). Panels, working groups, association memberships under `## Legal innovation and community involvement` (or equivalent label).
- [ ] 6.7 **Languages inline** as one semicolon-joined sentence under `## Languages`. Not a bulleted list.
- [ ] 6.8 **Interests section included** (sports, reading, gaming, music, volunteering). Common convention in Canadian professional-services CVs (Big Law, MBB consulting, in-house counsel); personality-fit signal. Adjust by market: US tech CVs often omit Interests; Asian markets often expect them. Default: include unless target convention drops them.
- [ ] 6.9 **Technical Skills as descriptive prose bullets, not enumeration dumps**. Each bullet: bold label + 20-40 word descriptive sentence carrying the depth claim. Pair any inventory with capability claim or relevance tie. Pattern: `**[Capability area]:** [Inventory of concrete tools, frameworks, or systems] paired with a descriptive sentence carrying the depth claim.` Law example: `**Tech-transactions drafting at depth:** MSA, OEM, Hosting Licence Agreement, EULA, DPA, NDA, IP assignment, SAFE, founders' agreement; counterparty experience against Dell, IBM, AT&T, Thomson Reuters, …`. Engineering example: `**Distributed systems engineering:** Production experience with Kubernetes, Kafka, Spanner, gRPC, Envoy; designed cell-based architectures handling 10k req/s with multi-region failover.`
- [ ] 6.10 **Concrete over abstract**. Prefer "Reviewed open-source dependencies before each release" over "Conducted open-source dependency due diligence on every release". Verb-forward, plain.
- [ ] 6.11 Write to `./job-applications/active/<role-slug>/candidate-cv.md`. If finalising a polished version separately from a working draft, suffix `-final.md`.
- [ ] 6.12 Add `## {Related}` block: job posting, companion cover letter, content bank, master CV, and any unabridged source notes.

### Stage 7: Self-review against anti-patterns ⚠️ REQUIRED

- [ ] Tagline paragraph between header and first section (move thesis to cover letter)
- [ ] Org intro paragraph under role heading ("X is a Vancouver-based software company...")
- [ ] Sub-header running 7+ bullets without further break (split or compress to 4-5)
- [ ] Bar admission as standalone `## Bar admission` section
- [ ] Publication bundled into "Selected publications and speaking" with community involvement
- [ ] Languages as bulleted list with one-line-per-language entries
- [ ] No Interests section
- [ ] Technical Skills as raw enumeration ("MSA, OEM, SLA, DPA, NDA, SAFE, SOW...") without descriptive sentence
- [ ] All 4 RAs listed when 2 would serve (or all side roles when target-relevant subset suffices)
- [ ] Roles or bullets that don't serve the target role
- [ ] Sub-header label that doesn't match the pillar driving the section
- [ ] Em dashes anywhere in bullets or headers
- [ ] Word count over ~1,800 (target 1,350-1,750)

### Stage 8: Deliver

- [ ] 8.1 Present draft to user
- [ ] 8.2 Note word count vs sample baseline and target range
- [ ] 8.3 Wait for feedback; iterate on flagged sections only

### Stage 9: Render to DOCX (optional, when employer requires Word and a profession-specific template is bundled)

Currently only the law CV template ships. For law applications, render the Markdown source into `<skill-dir>/assets/law-cv-injection-template.docx` via `scripts/inject-law-cv.py`. For other professions, build a paired `assets/<profession>-cv-template.docx` + `scripts/inject-<profession>-cv.py` per the law pattern.

- [ ] 9.1 Confirm Markdown matches the CV authoring contract (Stage 6 conventions). The injection script depends on this contract; deviations fall back to plain paragraph rendering and lose section structure.
- [ ] 9.2 Run the injection script:

```bash
python <skill-dir>/scripts/inject-law-cv.py \
  --source ./job-applications/active/<role-slug>/candidate-cv-final.md \
  --output ./job-applications/active/<role-slug>/candidate-cv-<year>.docx
```

- [ ] 9.3 Verify validation reports `All validations PASSED!`
- [ ] 9.4 Open the DOCX in Word (or LibreOffice) for visual sanity check before submitting

**Notes on the script:**

- Coupled to `law-cv-injection-template.docx`. Template carries name + contact in `header1.xml`; script body builds Experience through Interests.
- Underline runs continuously across the role-line tab gap (title|org left, date right) by setting `<w:u w:val="single"/>` on every run including the tab.
- Smart quotes applied by default. Use `--no-smart-quotes` when source is already clean.
- Section emission is order-faithful: sections appear in the order they appear in Markdown. Omit `## Publication` (or any section) entirely and it does not render.

**Markdown authoring contract** (any deviation downgrades to plain paragraph rendering):

- Frontmatter (between leading `---` lines): skipped.
- `# Name` (top H1): skipped. Name + contact live in template's header.
- Plain contact line after H1 (contains `@` or `LSO`): skipped.
- `---` standalone lines: HR separators, skipped.
- `## Section Heading`: section title (shaded title bar).
- `### Title  |  Organization`: role heading. Paired with the next italic-meta line for date.
- `*Date  |  Location  |  Time-commitment*` (immediately after a role H3): consumed by the preceding H3.
- `**Label:**` (ending in colon, no pipes): sub-header within role.
- `**Title | Institution | Date**` or `**Title | Org**  |  Date` or `**Title | Org**`: alternative entry-heading patterns for Community / Education sections.
- `- **Prefix** rest`: bullet with bold leading segment.
- `- text`: plain bullet.
- Other non-empty lines: plain paragraph (Languages, Interests, single-line Lawyer's Licence body).
- `## {Related}` (or `## Related`): stops parsing.

**Common Stage 9 failure modes:**

- Pack failure with `non-zero exit status 1` — output DOCX is open in Word (look for a `~$<filename>.docx` lock file in the same folder). Close Word and re-run, or write to a different output path (`-final.docx` works).
- Role heading renders as plain paragraph — H3 line has too many or too few pipes. Confirm `### Title  |  Organization` exactly. If date should appear on top-right, put it on the italic line below, not in the H3 line.
- Sub-header bold span absorbs the next colon — `**Label**:` outside the bold breaks pattern. Use `**Label:**` with the colon inside the bold.
- Bullet bold prefix missing — bold span needs to start at the bullet's first character: `- **Dr. Cheng** (date): text`. Whitespace before `**` breaks detection.

## Anti-patterns specific to this workflow

- Drafting before completing Stages 1-4 (especially skipping the structural reference at 1.2)
- Auto-setting flat reverse-chronological without offering Pattern A
- Treating master CV as drop-in for tailored CV (master is unabridged; tailored requires user-driven cuts)
- Listing every PI, every side role, every bullet from content bank
- Confusing line count with word count or with token reduction
- Repeatedly re-reading the same file instead of holding context

## Distilled principles (from past sessions)

These are the moves that landed for this user, regardless of target firm:

- **Voice reference + structural reference are both required at Stage 1.** Voice rules govern prose register; structural reference (sample CV from target firm) governs section order, header style, and bullet density.
- **Pattern A vs Pattern B is a user-driven choice, not a default.** Same content can land either way; user picks per role.
- **Reverse-chronological by end date within each group.** Ongoing roles first; primary current full-time above part-time advisory.
- **2-3 bullets per sub-header.** Anything more reads as a wall; split or compress.
- **Drop org intros.** Reader infers from role title + bullets.
- **No tagline paragraph.** Cover letter carries thesis.
- **Bold colon sub-headers.** Group bullets thematically inside roles.
- **Capability → Evidence → Relevance** at the bullet level mirrors the cover-letter three-beat structure.
- **Concrete over abstract verbs.** Plain-language verb-forward sentences beat consultant-register nominalizations.
- **Drop side roles or PIs that don't serve the target.** RAs compress to 2 of 4; off-pitch litigation bullets cut.
- **Publication is its own section when present; drop the section entirely when no relevant papers.**
- **Languages inline; Interests typically included** for Canadian professional-services targets (Big Law, MBB consulting, in-house). Adjust per market convention (US tech often omits Interests; Asian markets often expect them).
- **Technical Skills as descriptive sentences, not inventory dumps.** Bold label + 20-40 word capability claim.
- **Render to DOCX via injection script at Stage 9** when employer requires Word; close Word before re-running or write to alternate suffix.


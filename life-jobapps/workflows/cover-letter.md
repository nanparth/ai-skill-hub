# Cover letter workflow

Profession-agnostic. Bundled rendering scripts and DOCX templates are currently law-specific (see assets); workflow logic transfers to any profession (engineering, consulting, research, design, finance, government, …).

Tailor new cover letter for specific job application. Following from step zero compresses pass nine to pass one or two.

## When to load

- User asks to draft or tailor a cover letter
- "Write a cover letter for [employer]" or "tailor my cover letter to [role]"
- User has job posting and wants application materials

## Inputs ⛔ BLOCKING

- Job posting (link, file, or pasted text)
- Target employer name and role title
- Application deadline if any
- Specific posting bullets user wants emphasized

Confirm with user before continuing. Missing posting → ask.

## Workflow

### Stage 1: Voice reference load ⛔ BLOCKING

Step zero. Skipping produces credential-piling and corpo wraps that take many revision cycles to remove.

- [ ] 1.1 Read `references/voice-references.md` or the user-provided writing style guide in full
- [ ] 1.2 Read at least one past cover letter from `./job-applications/materials/`. Closest role-type match. Index: `references/voice-references.md`.
- [ ] 1.3 Note past-letter structure: P1 hook + thesis + three-pillar intro, P2-P4 one pillar each, P5 short personal close
- [ ] 1.4 Note user voice signature: first-person capability claims, evidence threaded as narrative summary, practical client-service paragraph closes, no em dashes, two spaces after sentence-ending periods, Canadian English

### Stage 2: Adjective and pillar brainstorm ⛔ BLOCKING

User drives. Offer candidates; let user pick or substitute.

- [ ] 2.1 Read job posting carefully
- [ ] 2.2 Read `./job-applications/assets/content-bank.md` for closest positioning angle + candidate evidence pool
- [ ] 2.3 Propose 6-8 candidate adjectives/capabilities with one-line evidence anchors. Past hits: interdisciplinary, builder, rigorous, systematic, mechanistic, structural, calibrated, multilingual.
- [ ] 2.4 ⚠️ REQUIRED: Ask user to pick or substitute 3-4 traits scaffolding the narrative for this role. User drives.
- [ ] 2.5 Confirm final pillar list before continuing

### Stage 3: Job-posting mapping ⛔ BLOCKING

Pillars must serve named posting responsibilities, not freestanding self-praise.

- [ ] 3.1 List each posting Major Responsibility bullet
- [ ] 3.2 List each posting Knowledge and Skills item
- [ ] 3.3 Map each pillar to bullets it serves
- [ ] 3.4 Flag posting bullets not covered by any pillar. If essential, add or expand a pillar.
- [ ] 3.5 ⚠️ REQUIRED: Present mapping table to user and confirm before drafting

### Stage 4: Outline

- [ ] 4.1 P1 hook: striking thesis sentence about practice or role (not about user)
- [ ] 4.2 P1 credentials wrap: one sentence on user's combined background tied back to thesis
- [ ] 4.3 P1 closer: name three pillars explicitly as what user brings
- [ ] 4.4 For each pillar paragraph (P2, P3, P4), use three-beat **Capability → Evidence → Relevance** structure. Claim, evidence, significance.
  - [ ] **Capability** opener: first-person, forward-looking ("My [pillar] allows me to [verb] [audience outcome]" or "My [pillar] has given me a strong foundation in…"). Names paragraph theme (e.g. for law tech-transactions: agreements + risk allocation + analysis; for product roles: product + operations + growth strategy; for AI governance: understanding products + working with engineers + using AI responsibly), not chronological setting.
  - [ ] **Evidence** chain: 2-4 anchors from content bank, grouped under theme rather than by employer. Each anchor named (organization, deliverable, named contract or research project). Lists of items (contracts, counterparties, frameworks, projects) sandwiched: lead-in naming what list represents, list itself, interpretive close ("Through that work, I developed practical experience with the issues that often drive [target practice area] decisions…") converting tasks into professional development. Lists support claims; never replace them.
  - [ ] **Relevance** close: practical audience-outcome implication tied to target practice in role-specific language (e.g. for law tech-trans: "central to technology transactions"; for engineering: "central to production reliability at scale"; for consulting: "decision-ready analysis for senior leadership"), not generic self-praise.
- [ ] 4.5 P5: short personal close anchored on concrete connection to employer (past exposure, shared client base, observed past work)
- [ ] 4.6 ⚠️ REQUIRED: Present outline to user and confirm before prose drafting

### Stage 5: Draft

- [ ] 5.1 Write full prose in user's voice per `references/voice-references.md` or the user-provided writing style guide
- [ ] 5.2 Formatting: no em dashes, two spaces after sentence-ending periods, Canadian English (organise, recognise, prioritising, customisation), sentence case for headings
- [ ] 5.2.1 Sequential progression phrases between paragraphs: "Through that work…", "I then built on that foundation at…", "That founder-side perspective gave me…", "It also reinforced…", "My technical fluency complements that commercial perspective…". Distinct from R13: R13 keeps reader inside one chain of reasoning; progression phrases move chain forward across paragraphs.
- [ ] 5.2.2 Audience-facing register over internal-discipline register. Use concrete audience-named language and outcomes. "Client-facing" is the right framing for law, consulting, and in-house roles; "user-facing" for product roles; "stakeholder-facing" for policy or government roles; "researcher-facing" for academic posts. Example for law tech-trans: "product, operations, growth strategy", "operational reality", "practical for business teams", "legally viable", "decision-ready analysis" over abstract internal labels ("matters", "files", "tasks"). Cover letters sell to the target audience, not to peers inside your discipline. Concrete-and-audience-named, not corpo speak (AP15 still binds).
- [ ] 5.3 Write to `./job-applications/active/<role-slug>/candidate-cover-letter.md`
- [ ] 5.4 Add `## {Related}` block: job posting, companion CV, content bank, voice-reference cover letter
- [ ] 5.5 Body paragraph count must land in 4-6 range. Stage 8 DOCX template supports 4-6 and drops middle slots for shorter letters. Outside range → Stage 8 fails.
- [ ] 5.6 Smart quotes throughout (apostrophes `’`, opening `“` and closing `”` doubles, ellipsis `…`). Stage 8 script normalizes straight quotes; smart quotes in source improve readability.

### Stage 6: Self-review against anti-patterns ⚠️ REQUIRED

Scan against this list before delivering. Each hit = rewrite trigger.

- [ ] High-concept metaphors ("different muscle", "data room analogical version", "the deal as one problem not four")
- [ ] False-contrast wraps ("rather than X, but Y" where contrast is weak or invented)
- [ ] Self-superlatives at close ("uncommon enough that it is rarely hired without compromise", "once-in-a-generation talent")
- [ ] Parallel "On X / On Y / On Z" sub-paragraph labels
- [ ] Bold inline pillar headers like `**Legal excellence.**` or `**Technical fluency.**` (reads as memo, not narrative)
- [ ] Heavy R13 connective tissue ("the same instinct", "the same structural reading") used as crutch
- [ ] Counterparty lists and contract enumerations dropped without claim tie
- [ ] Credential-piling in P1; thesis must lead, credentials anchor
- [ ] "On X" mechanical paragraph openers
- [ ] Subject-first abstraction openers ("[Pillar] in my practice starts with…"). Use verb-forward first-person: "My [pillar] allows me to…"
- [ ] Corpo speak: "leverage" (verb), "synergy", "seamless", "best-in-class", "stakeholder alignment". AP15.
- [ ] Chronology-first paragraph openers ("At Dynamsoft, I did X. At Fasken, I did Y."). Lead with capability theme; let chronology fall out of evidence.
- [ ] Résumé-in-paragraph-form: each sentence introduces new employer rather than continuing theme.
- [ ] Naked list of tasks/contracts/counterparties without interpretive sandwich.
- [ ] Paragraph close naming generic outcome ("helped team succeed") rather than target practice in role-specific language.
- [ ] Internal-discipline register where audience-facing fits (e.g. "worked on matters" instead of "advised on product, operations, and growth strategy"; "shipped tickets" instead of "delivered the X feature serving Y users"; "ran experiments" instead of "answered the Z question for the product team").

After scan, read five paragraph-opener sentences in sequence. They should read as one coherent proposition (e.g. for law tech-trans: "I am well suited to this practice because I combine legal drafting and analysis, founder-side commercial judgment, and genuine technical fluency"; for product: "I am well suited to this role because I combine product judgment, engineering depth, and operating experience"). If not, reorder paragraphs or rewrite openers before re-presenting evidence.

### Stage 7: Deliver

- [ ] 7.1 Present draft to user
- [ ] 7.2 Note length (chars and words) vs past-letter baseline from `references/voice-references.md`. Past user-provided letters: compare character and word count against the closest sample. If the draft is much longer, explain why.
- [ ] 7.3 Wait for feedback; iterate on flagged sections only

### Stage 8: Render to DOCX (optional, when employer requires Word and a profession-specific template is bundled)

Currently only the law cover-letter template ships. For law applications, render Markdown into `<skill-dir>/assets/law-cover-letter-injection-template.docx` via `scripts/inject-law-cover-letter.py`. For other professions, build a paired `assets/<profession>-cover-letter-template.docx` + `scripts/inject-<profession>-cover-letter.py` per the law pattern.

- [ ] 8.1 Gather employer-specific header inputs:
  - Date string (e.g. "May 9, 2026")
  - Recipient line (e.g. "Sandra Sbrocchi, Head, Osler Works – Transactional")
  - Organization name (e.g. "Osler, Hoskin & Harcourt LLP")
  - Single-line organization address
  - Salutation (e.g. "Dear Sandra,")
  - Position name for Re-line (e.g. "Technology Transactions Associate")
- [ ] 8.2 Run injection script:

```bash
python <skill-dir>/scripts/inject-law-cover-letter.py \
  --source ./job-applications/active/<role-slug>/candidate-cover-letter.md \
  --output ./job-applications/active/<role-slug>/candidate-cover-letter-<year>.docx \
  --date "<date>" \
  --recipient "<name, title>" \
  --organization "<org>" \
  --address "<address>" \
  --salutation "Dear <name>," \
  --position "<position>"
```

- [ ] 8.3 Verify validation reports `All validations PASSED!`
- [ ] 8.4 Open DOCX in Word (or LibreOffice) for visual check before submitting

**Script notes:**
- Coupled to `law-cover-letter-injection-template.docx`. Template placeholders hardcoded; per-application fields via CLI args.
- Supports 4-6 body paragraphs. Maps paragraphs to slots; drops unused (`…` middle slot for 5-paragraph; `…` + `BODY PARA #2` for 4-paragraph).
- Source Markdown must contain `**Re: ...**` line and `Yours truly,` line; body paragraphs extracted between them.
- Smart quotes applied by default. `--no-smart-quotes` to bypass.

**Stage 8 failure modes:**

- `Header placeholder missing` — template edited and lost a placeholder. Re-pull from `<skill-dir>/assets/`.
- `Body paragraph count N not supported` — draft has <4 or >6 body paragraphs. Edit into range (Stage 5.5) or extend `map_body_paragraphs_to_slots`.
- `Re-line not found in source markdown` — missing `**Re: ...**` line. Re-add under salutation.
- `'Yours truly,' line not found` — sign-off missing. Re-add `Yours truly,` after body.
- Pack failure with `non-zero exit status 1` — output DOCX open in Word (`~$<filename>.docx` lock file). Close Word and re-run.

## Anti-patterns specific to this workflow

- Drafting prose before completing Stages 1-3
- Inventing pillars without user confirmation
- Letting evidence drift from opener-claim
- Padding to hit target length; compress instead
- Treating R12 (chunk factual narrative) as license to over-chunk capability paragraphs; R6 (long sentences for sustained reasoning) governs capability prose

## Distilled principles (from past sessions)

These are the moves that landed for this user, regardless of target firm or profession:

- **Voice reference load first.** Read `references/voice-references.md` or the user-provided writing style guide plus a closest-fit past letter before any drafting. Step zero, not step ten.
- **Pillar brainstorm before drafting.** Distill 3-4 capability pillars with the user; do not impose pillars; user drives.
- **Posting-bullet mapping before evidence.** Pillars must serve named posting responsibilities, not freestanding self-praise.
- **Capability-claim openers in first person.** "My [pillar] allows me to [verb] [audience outcome]" or "My [pillar] has given me a strong foundation in…". Forward-looking, what the trait does FOR the audience.
- **Three-beat Capability → Evidence → Relevance** per pillar paragraph. Claim, evidence, significance.
- **Progression-transition phrasing across paragraphs.** "Through that work…", "I then built on that foundation at…", "That [role] perspective gave me…". Moves the reader's chain of reasoning forward across paragraphs; distinct from R13 literal repetition inside one chain.
- **Audience-facing register over internal-discipline register.** Sell to the target audience (client, user, stakeholder, researcher), not to peers inside the discipline.
- **Concrete over abstract verbs.** Plain-language verb-forward sentences beat consultant-register nominalizations.
- **Self-review against the anti-pattern list** before delivering. Each hit = rewrite trigger.
- **Render to DOCX via Stage 8** when the employer requires Word AND a profession-specific template is bundled. Otherwise deliver Markdown or use Pandoc or another user-provided DOCX converter.


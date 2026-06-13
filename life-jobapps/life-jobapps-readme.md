# life-jobapps

A job-application drafting skill for AI assistants. Give it a job posting and user-provided source material, and it helps tailor cover letters, CVs, resumes, and interview-prep material to the target role while preserving the user's evidence and voice.

## Part A — User Guide

### Who it's for

Job seekers who want application materials grounded in their own source material, not generic role-matching prose. The workflows are profession-agnostic, but the bundled DOCX templates and rendering scripts are currently law-specific.

### What you need

- A job posting, role description, or interview target.
- User-provided source material such as a master CV, resume, content bank, past cover letters, experience notes, or writing samples.
- A user-selected application folder, such as `./job-applications/active/<role-slug>/`.
- Optional: Python 3 and the bundled law templates for DOCX rendering.

This workbench copy is not yet a plug-and-play public release. The public entry points are sanitized, but the full folder is marked `workbench_only_needs_refactor` until external office helpers and non-law rendering assumptions are resolved.

### Quick start

1. Use the skill inside this workbench, or copy the whole folder only for internal testing.
2. Ask your assistant something like:
   - "Draft a cover letter for this role using my source file."
   - "Tailor my CV to this job posting."
   - "Prep me for an interview with this employer."
3. Provide the job posting and the source material you want the skill to use.
4. Confirm the output folder before the assistant writes the draft.

### What you get back

- A tailored Markdown cover letter, CV, resume, or interview-prep packet.
- Evidence mapping from posting requirements to user-provided experience.
- Voice-constrained prose based on `references/voice-references.md` or a user-supplied style guide.
- Optional law-specific DOCX output when the template and helper utilities are available.

### Modes

- **Cover letter**: loads `workflows/cover-letter.md`, maps role requirements to evidence, drafts capability-led paragraphs, and optionally renders a law-style DOCX.
- **CV or resume**: loads `workflows/cv.md`, chooses section structure, tailors role entries, and optionally renders a law-style DOCX.
- **Interview prep**: loads `workflows/interview-prep.md`; currently a scaffold for future expansion.

### Public-status note

The core writing workflow can be adapted for other professions when the user supplies the job posting and source files. DOCX rendering is not yet fully portable because it depends on law-specific templates and external office helper utilities.

## Part B — Technical Reference

### Layout

```text
life-jobapps/
  SKILL.md                          entry point, routing, defaults
  PORTABILITY.md                    workbench-only classification
  life-jobapps-readme.md            this file
  workflows/
    cover-letter.md
    cv.md
    interview-prep.md
  references/
    voice-references.md
  assets/
    law-cover-letter-injection-template.docx
    law-cv-injection-template.docx
  scripts/
    inject-law-cover-letter.py
    inject-law-cv.py
```

### Design notes

- Workflow logic is profession-agnostic; rendering assets are profession-specific.
- Source material is user-provided at runtime. The skill should not assume a private content bank.
- Cover-letter drafting uses a capability -> evidence -> relevance structure.
- CV rendering depends on a strict Markdown authoring contract; malformed role blocks fall back to plain paragraph rendering.
- DOCX generation is separate from drafting so Markdown output remains usable without Python or office helpers.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| User-provided job posting | All workflows | Ask for it before drafting |
| User-provided source material | Evidence-backed output | Ask for source files or pasted material |
| Host file writer | Saving Markdown outputs | Present text in chat and ask for a destination |
| Python 3 | DOCX injection scripts | Deliver Markdown only |
| External office helper utilities | DOCX unpack/pack/validate | Skip DOCX rendering |
| Law DOCX templates | Law cover-letter and CV output | Use Markdown or add new template/script pair |

### Maintenance notes

- Keep `PORTABILITY.md` classified as workbench-only until office helpers are bundled or made clearly external.
- Add new profession support as a template plus injection-script pair; do not fork the core workflows unless the writing process itself changes.
- Keep examples synthetic and neutral.

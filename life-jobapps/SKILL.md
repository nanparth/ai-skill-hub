---
name: life-jobapps
version: '1.0.0'
description: 'Use when tailoring job application materials from user-provided source material: cover letters, CVs, resumes, and interview prep. Trigger on: "draft a cover letter", "write a cover letter", "tailor my CV", "tailor my resume", "prep for interview", "job application", "apply to [employer]". Not for private content-bank lookup unless the user explicitly provides the source files.'
argument-hint: '[cover-letter|cv|resume|interview-prep] [--job-posting path|url] [--source-material path] [--output path]'
---

# life-jobapps

Tailor job application materials from the user's supplied job posting, resume/CV, experience notes, and voice samples.

## Release Status

This workbench copy is partially normalized. The public-facing entry point is standalone, but older bundled workflows, references, and scripts may still contain local-workspace assumptions. Do not release this folder as plug-and-play until those internal files are fully normalized or removed.

## Dependencies

Required: user-provided source material and the host assistant's normal file-writing ability.

Optional: bundled document templates and Python rendering scripts for formatted output. If those are unavailable, return Markdown or plain text.

## Routing

| Intent | Action |
| --- | --- |
| Cover letter | Draft from job posting plus supplied source material. |
| CV or resume | Tailor supplied experience material to the target role. |
| Interview prep | Build a prep brief from the posting, employer information, and supplied career notes. |

## Workflow

1. Ask for missing source material before drafting.
2. Confirm the target role, employer, jurisdiction, format, and output path.
3. Extract role requirements from the posting.
4. Map requirements to user-provided evidence.
5. Draft in the user's requested voice and format.
6. Self-review for unsupported claims, generic phrasing, and missing role alignment.
7. Write to the user-selected output path, or return the draft in chat if no path was provided.

Never assume private content banks, personal file names, or account-specific folder layouts.



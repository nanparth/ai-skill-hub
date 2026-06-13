# biz-interview

A research-operations skill for AI assistants. Give it a customer discovery or stakeholder research goal, interview scripts, transcripts, or persona inputs, and it helps design interviews, clean results, generate synthetic test interviews, and analyze a corpus into codebooks, matrices, hypothesis verdicts, and a narrative report.

## Part A — User Guide

### Who it's for

Founders, product teams, consultants, researchers, and operators who run exploratory interviews and need repeatable qualitative analysis instead of a pile of disconnected transcripts.

### What you need

- An AI assistant that supports folder-based skills and can read/write files in a user-selected project folder.
- Markdown interview scripts or transcript/result files when running cleanup or analysis.
- A hypothesis mapping table when you want the analysis workflow to produce hypothesis verdicts.
- Optional: Python 3.9+ and `openpyxl` for spreadsheet exports. Without it, the skill still produces Markdown analysis outputs, but `.xlsx` matrix and co-occurrence exports are unavailable.

### Quick start

1. Copy the whole `biz-interview` folder into your assistant's skills folder.
2. Ask your assistant something like:
   - "Create a customer discovery interview script for legal operations managers."
   - "Clean up these interview transcripts in `./outputs/customer-discovery/interviews/`."
   - "Generate 8 test interviews from this script and persona grid."
   - "Analyze the interview corpus in `./outputs/customer-discovery/interviews/`."
3. Confirm the output folder, any study segments, and each analysis checkpoint the skill presents.

### What you get back

Depending on the mode, the skill can produce:

- A structured interview script with question architecture, follow-ups, and hypothesis mapping.
- Cleaned interview-result notes that preserve respondent substance while removing conversion noise.
- Synthetic but realistic test interviews for workflow testing or interviewer practice.
- A codebook, binary coding matrix, co-occurrence sheet, hypothesis verdict table, thematic analysis, and final research report.

### Modes

- **Create interview script**: builds a 45-60 minute exploratory interview script with mapped hypotheses and anti-pattern checks.
- **Reformat interview results**: cleans raw transcripts into standard Markdown notes without changing interviewee substance.
- **Generate test interviews**: creates fictional interview results from a script and persona grid after confirming the skeleton.
- **Analyze interviews**: runs a multi-stage qualitative analysis with codebook construction, coding passes, matrices, themes, verdicts, and report assembly.

### Output paths

Outputs go to a user-selected project or research folder. If no location is provided, suggest a neutral path such as `./outputs/biz-interview/customer-discovery/`.

## Part B — Technical Reference

### Layout

```text
biz-interview/
  SKILL.md                         entry point and routing table
  PORTABILITY.md                   standalone-with-optional-tools boundary
  biz-interview-readme.md          this file
  workflows/
    create-exploratory-interview.md
    reformat-interview-results.md
    generate-test-interviews.md
    analyze-interviews.md
  references/
    interview-design-reference.md
    codebook-construction-reference.md
    analysis-protocols-reference.md
    analysis-output-templates.md
  agents/
    interview-writer.md
    interview-coder.md
    coding-aggregator.md
    analysis-report-writer.md
  scripts/
    build_coding_matrix.py
    build_cooccurrence.py
  requirements.txt
```

### Design notes

- `SKILL.md` routes intent to one of four workflows and loads references only when needed.
- Coding agents output JSON first; spreadsheet generation is deterministic and script-owned.
- The analysis workflow runs two coding passes: first for discovery and codebook revision, second for stabilized coding.
- User gates are intentionally frequent: corpus summary, codebook draft, revised codebook, interpretive outputs, and final report.
- Subagent dispatch improves throughput, but small batches can be run inline by the host assistant.

### Dependencies and fallbacks

| Dependency | Needed for | If absent |
| ---------- | ---------- | --------- |
| Host file read/write | All workflows | Required |
| Python 3.9+ | Spreadsheet helper scripts | Markdown-only outputs still work |
| `openpyxl` | `.xlsx` matrix and co-occurrence export | Provide JSON/Markdown summaries instead |
| Subagent support | Parallel test interviews, coding, aggregation, report writing | Run the same checklist sequentially inline |
| User-selected output folder | Saving scripts, notes, and reports | Ask before writing |

### Maintenance notes

- `build_coding_matrix.py` expects coding records with `interview_id`, `interview_name`, `side`, and code assignments.
- `build_cooccurrence.py` expects a workbook with a sheet named `Binary Matrix`.
- Keep interview examples synthetic unless the user explicitly supplies real research material for their private project.

---
name: biz-interview
version: '1.0.0'
description: 'Use when designing, generating, processing, or analyzing market research interviews: customer discovery, stakeholder validation, supply-side interviews, or cross-interview coding. Trigger on: "coding matrix", "codebook", "hypothesis verdicts", "interview coding", "mock interview data", "customer discovery interview". Not for job interviews or survey design.'
argument-hint: '[create|process|analyze|generate-mock|code] [--segment name]'
---

# biz-interview

Design and process market research interview scripts and results for customer discovery and stakeholder research.

## Dependencies

Core workflows need only the host assistant's normal ability to read and write files. The spreadsheet export scripts are optional and require Python plus `openpyxl`; install them with `pip install -r requirements.txt` from this skill folder.

## Routing

| Intent | Route | Load reference? |
| --- | --- | --- |
| Create a new exploratory interview script | `workflows/create-exploratory-interview.md` | Yes: `references/interview-design-reference.md` |
| Reformat raw interview transcripts into clean result notes | `workflows/reformat-interview-results.md` | No |
| Generate fictional interview results for testing or training | `workflows/generate-test-interviews.md` | Yes: `references/interview-design-reference.md` |
| Analyze interview corpus: coding, verdicts, report | `workflows/analyze-interviews.md` | Yes: loaded per step in the workflow |

If intent is ambiguous, ask the user which workflow they need.

## Reference Loading Map

| Need | Reference |
| --- | --- |
| Script architecture, question crafting rules, anti-patterns | `references/interview-design-reference.md` |
| Codebook construction, coding pass protocol, revision rules | `references/codebook-construction-reference.md` |
| Negative case, comparison, segmentation, verdicts | `references/analysis-protocols-reference.md` |
| Output templates for codebook, verdict table, report, matrix | `references/analysis-output-templates.md` |

## Agent Loading Map

| Agent | File | Purpose |
| --- | --- | --- |
| Interview Writer | `agents/interview-writer.md` | Generate one fictional interview result from a skeleton template and persona spec. |
| Interview Coder | `agents/interview-coder.md` | Code a batch of interviews against a codebook, producing JSON coding records. |
| Coding Aggregator | `agents/coding-aggregator.md` | Merge per-batch coding outputs, resolve conflicts, and produce consolidated JSON. |
| Analysis Report Writer | `agents/analysis-report-writer.md` | Assemble the final analysis report from analytical outputs. |

## Shared Conventions

- Write markdown outputs to the user-selected output path using the host assistant's normal file-writing method.
- If the user has no preferred output path, propose `./outputs/biz-interview/customer-discovery/`.
- Keep source transcripts and generated outputs separate.
- Follow the user's project language and spelling conventions.
- Every interview script must include an Interviewer Info table, Key Points Summary template, and hypothesis mapping appendix.
- This skill creates research artifacts. It does not conduct interviews, schedule interviews, or manage recruitment.

## Script Loading Map

| Script | File | Purpose |
| --- | --- | --- |
| Build Coding Matrix | `scripts/build_coding_matrix.py` | Convert JSON coding data to a formatted `.xlsx` binary matrix. |
| Build Co-occurrence | `scripts/build_cooccurrence.py` | Add a co-occurrence sheet to an existing coding matrix `.xlsx`. |

## Future Workflows

| Workflow | Purpose | Status |
| --- | --- | --- |
| `create-structured-interview` | Structured or quantitative interview scripts with closed questions, rating scales, or forced-choice items. | Planned |

# biz-interview

`biz-interview` helps an AI assistant create customer discovery interview scripts, clean interview transcripts, generate fictional test interviews, and analyze interview corpora.

## Use This If

Use this skill when you are doing market research or stakeholder discovery and want a repeatable interview workflow. It is not for job interviews, recruiting, scheduling, or survey design.

## Dependencies

Core workflows do not require Python. They need only file read/write access in the user's chosen project or output folder.

Optional spreadsheet exports require Python and `openpyxl`:

```bash
pip install -r requirements.txt
```

## Main Workflows

- Create an exploratory interview script: `workflows/create-exploratory-interview.md`.
- Reformat raw transcript files: `workflows/reformat-interview-results.md`.
- Generate fictional test interviews: `workflows/generate-test-interviews.md`.
- Analyze interviews into a codebook, matrix, verdicts, and report: `workflows/analyze-interviews.md`.

## Output Paths

Ask the user where outputs should go. If they do not have a preference, use a neutral folder such as:

```text
./outputs/biz-interview/customer-discovery/
```

Markdown outputs are written by the host assistant's normal file-writing method. Spreadsheet helpers write `.xlsx` files to the path the user provides.

## Spreadsheet Helpers

```bash
python <skill-dir>/scripts/build_coding_matrix.py <codings_json> <output_xlsx> --codebook <codebook_md>
python <skill-dir>/scripts/build_cooccurrence.py <matrix_xlsx>
```

The scripts are optional. The interview design and analysis reasoning can still run without them.

## Files To Copy

Copy the whole `biz-interview/` folder. Required local files include `SKILL.md`, `workflows/`, `agents/`, `references/`, `scripts/`, `requirements.txt`, and `PORTABILITY.md`.
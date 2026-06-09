# Analyze Interviews

Cross-interview qualitative analysis workflow.  Produces a codebook, binary coding matrix, hypothesis verdict table, and narrative analysis report from a corpus of exploratory interview result files.

## Prerequisites

Before starting, confirm:
- Interview result `.md` files exist in the project's interview folder (digit-prefix filenames)
- At least one interview script `.md` file with a hypothesis mapping table exists
- The user has confirmed the corpus is complete (no pending transcriptions or reformats)

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `input_dir` | Path to folder containing interview result `.md` files | Ask user |
| `script_paths` | List of interview script `.md` files with hypothesis mapping tables | Ask user |
| `output_dir` | Path for analysis outputs | Ask user; if no preference, suggest `./outputs/biz-interview/customer-discovery/analysis/` |
| `customer_sides` | List of customer groups (e.g., `["consumer", "lawyer"]`) | `["demand"]` |
| `min_interviews_per_side` | Minimum interviews required per side | 3 |
| `top_n_for_negative_case` | Number of top themes for disconfirmation search | 5 |

## Workflow

Copy this checklist and check off items as you complete them:

- [ ] Step 1: Input identification ⛔ BLOCKING
  - [ ] 1.1 Scan `input_dir` for interview result files (digit-prefix `.md` pattern)
  - [ ] 1.2 Read each script in `script_paths`; extract hypothesis mapping tables
  - [ ] 1.3 Classify interviews by customer side (from tags, filename, or user input)
  - [ ] 1.4 Validate minimum counts: at least `min_interviews_per_side` per side
  - [ ] 1.5 Present corpus summary to user:

    | # | Pseudonym | Side | Date | Script Version |
    |---|---|---|---|---|
    | ... | ... | ... | ... | ... |

    **Scripts identified:** [list with hypothesis counts]
    **Corpus:** [N] interviews ([n1] [side-1], [n2] [side-2])

  - [ ] 1.6 User confirms corpus. Do not proceed until confirmed.

- [ ] Step 2: Codebook construction ⛔ BLOCKING
  - [ ] 2.1 Load `references/codebook-construction-reference.md`
  - [ ] 2.2 Extract a priori codes from hypothesis mapping tables in each script
        - For each hypothesis, identify mapped questions and the themes they probe
        - Each theme becomes a candidate code; group into candidate families
  - [ ] 2.3 First-pass reading of all interviews (alternating side order)
        - Note emergent themes not captured by a priori codes
        - Record candidate emergent codes with provisional definitions
  - [ ] 2.4 Draft codebook: formal code entries (name, definition, inclusion, exclusion, exemplar)
        - Target: 8-12 families, 3-8 codes per family
  - [ ] 2.5 Present codebook to user for confirmation
        - User may request merges, splits, additions, or removals
        - Iterate until user confirms
  - [ ] 2.6 Save codebook draft to `output_dir` using the host assistant's normal file-writing method.

- [ ] Step 3: First coding pass
  - [ ] 3.1 Divide interviews into batches of 4-5, each batch containing interviews from both sides
  - [ ] 3.2 Dispatch `interview-coder` agents in parallel (3-4 agents)
        - Load `agents/interview-coder.md` for each agent
        - Input: codebook (full text), batch interview paths, pass_number=1, customer_sides mapping
        - Model: `sonnet` for first pass speed
  - [ ] 3.3 Collect all batch outputs (JSON coding records)

- [ ] Step 4: Codebook revision + second pass ⛔ BLOCKING
  - [ ] 4.1 Aggregate emergent code candidates from all first-pass agents
  - [ ] 4.2 Dispatch `coding-aggregator` agent
        - Load `agents/coding-aggregator.md`
        - Input: all batch outputs, codebook, pass_number=1
  - [ ] 4.3 Review aggregator output: conflict log, emergent candidates, summary stats
  - [ ] 4.4 Apply revision protocol to codebook:
        - Merge codes with >80% co-occurrence overlap
        - Split codes capturing two distinct phenomena
        - Incorporate validated emergent codes
        - Update revision log
  - [ ] 4.5 Present revised codebook to user; user confirms before second pass
  - [ ] 4.6 Dispatch second coding pass with `interview-coder` agents
        - Input: revised codebook, same interview paths, pass_number=2
        - Model: `opus` for quality on second pass
  - [ ] 4.7 Dispatch `coding-aggregator` for second-pass outputs (pass_number=2)

- [ ] Step 5: Matrix assembly
  - [ ] 5.1 Save aggregator's merged_codings JSON to a temp file
  - [ ] 5.2 Run `scripts/build_coding_matrix.py <codings_json> <output_xlsx> --codebook <codebook_path>`
  - [ ] 5.3 Run `scripts/build_cooccurrence.py <output_xlsx>`
  - [ ] 5.4 Present matrix summary to user:
        - Total code assignments, average codes per interview
        - Top 10 codes by frequency
        - Co-occurrence density
        - Side breakdown

- [ ] Step 6: Thematic analysis ⛔ BLOCKING
  - [ ] 6.1 Load `references/analysis-protocols-reference.md`
  - [ ] 6.2 **Negative case analysis**
        - Identify top `top_n_for_negative_case` themes by frequency from the matrix
        - For each, systematically search for disconfirming interviews
        - Document qualifying conditions and boundary statements
        - Minimum: 3 of top 5 must have at least one documented negative case
  - [ ] 6.3 **Two-sided comparison** (skip if `len(customer_sides) == 1`)
        - Within-group comparison first (internal homogeneity per side)
        - Between-group comparison: juxtapose perspectives on shared themes
        - Build comparison table (Theme / Demand-Side / Supply-Side / Structural Insight)
        - Minimum: 5 theme rows, 3 structural insights
        - Look for: mirror inversions, information asymmetries, motivation misalignments, vocabulary gaps
  - [ ] 6.4 **Segmentation**
        - Examine binary matrix for interview clusters sharing 3+ codes
        - Build segment profiles (8-dimension template from protocols reference)
        - Minimum 2 interviews per segment; single-interview outliers reported as such
        - Equal analytical depth regardless of segment size
        - Apply to both customer sides independently if two-sided
  - [ ] 6.5 Present all interpretive outputs to user for confirmation
        - User may challenge interpretations, request deeper analysis, or suggest reframing
        - Iterate until user confirms

- [ ] Step 7: Hypothesis verdicts
  - [ ] 7.1 Map coded evidence to pre-defined hypotheses from scripts
        - Evidence is not restricted to mapped questions; spontaneous mentions count
  - [ ] 7.2 For each hypothesis, document:
        - Supporting evidence (interview numbers + brief quotes)
        - Contradicting evidence (interview numbers + brief quotes)
        - Qualifying conditions (from negative case analysis)
        - Reasoning chain (the inferential step from evidence to verdict)
  - [ ] 7.3 Assign verdict: Confirmed / Partially supported / Refuted / Insufficient data
  - [ ] 7.4 Assign confidence: Very strong / Strong / Moderate / Weak
  - [ ] 7.5 Build verdict summary table
  - [ ] 7.6 Load `references/analysis-output-templates.md` for verdict table format
  - [ ] 7.7 Save hypothesis verdict table to `output_dir` using the host assistant's normal file-writing method.

- [ ] Step 8: Report assembly
  - [ ] 8.1 Compile all inputs for the report writer:
        - Codebook path, matrix summary JSON, verdict table path
        - Segment profiles (markdown), comparison table (markdown), key findings (markdown)
        - Study metadata (corpus size, sides, interviewers, limitations)
  - [ ] 8.2 Dispatch `analysis-report-writer` agent
        - Load `agents/analysis-report-writer.md`
        - Pass all compiled inputs
  - [ ] 8.3 Review report draft for completeness and accuracy
  - [ ] 8.4 Save final report to `output_dir` using the host assistant's normal file-writing method.
  - [ ] 8.5 Update codebook with any final negative case analysis notes and save it to `output_dir`.
  - [ ] 8.6 Present completion summary to user:
        - Files produced: codebook, coding matrix (.xlsx), hypothesis verdict table, analysis report
        - Key statistics: corpus size, codes, segments, hypothesis verdicts
        - Suggested next steps (e.g., adapt for accelerator application, build pitch deck)

## Output Files

All outputs saved to `output_dir`:

| File | Description |
|---|---|
| `codebook.md` | Master codebook with all code families, definitions, and revision log |
| `interview-coding-matrix.xlsx` | Binary coding matrix + co-occurrence sheet |
| `hypothesis-verdict-table.md` | Verdict for each hypothesis with evidence and reasoning |
| `[project]-interview-analysis-report.md` | Narrative analysis report |

## Delegation Rules

- All `.md` files are written to `output_dir` using the host assistant's normal file-writing method.
- The `.xlsx` file is produced by the optional Python scripts. If further formatting is needed, use the spreadsheet tool available in the user's environment.
- Codebook and verdict table use the templates from `references/analysis-output-templates.md`

## Conventions

- Canadian English, no em dashes
- Fuzzy qualifiers only (no percentages from qualitative data)
- Epistemic register for all recommendations and conclusions
- Quote selection by representativeness, not vividness

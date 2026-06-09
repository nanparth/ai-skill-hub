# Analysis Output Templates

Use these templates for markdown outputs. Do not add private workspace metadata, or machine-local paths unless the user explicitly requests them.

## Codebook

```markdown
# Codebook

## Study

- Project: <project name>
- Corpus: <number and segment summary>
- Scripts reviewed: <script paths or names>

## Code Families

### <Family Name>

| Code | Definition | Include When | Exclude When | Example |
| --- | --- | --- | --- | --- |
| <code> | <definition> | <criteria> | <criteria> | <short quote or summary> |

## Revision Log

| Pass | Change | Reason |
| --- | --- | --- |
| 1 | <change> | <reason> |
```

## Hypothesis Verdict Table

```markdown
# Hypothesis Verdicts

| # | Hypothesis | Verdict | Confidence | Supporting Evidence | Contradicting Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | <hypothesis> | Confirmed / Partially supported / Refuted / Insufficient data | Very strong / Strong / Moderate / Weak | <interview refs> | <interview refs> | <qualifiers> |
```

## Analysis Report

```markdown
# <Project Name> Customer Discovery Interview Analysis

## Research Objectives and Method

<Study overview, corpus size, cohort composition, and method.>

## Segment Profiles

<One subsection per segment.>

## Comparison

<Use only when the study has multiple customer sides or stakeholder groups.>

## Key Findings

<Five to eight findings with representative evidence.>

## Recommendations

<Evidence-grounded recommendations using careful qualitative language.>

## Limitations

<State sample and method limits plainly.>
```

## Matrix Summary

```json
{
  "interviews": 0,
  "codes": 0,
  "top_codes": [],
  "notes": []
}
```
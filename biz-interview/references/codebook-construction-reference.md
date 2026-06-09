# Codebook Construction and Coding Pass Protocol

Loaded during Steps 2-4 of the analyze-interviews workflow. Covers codebook construction from hypothesis mapping tables, coding pass execution, and codebook revision.

## 1. Codebook Construction

### 1.1 A Priori Code Extraction

The first step is extracting a priori codes from the hypothesis mapping tables in the interview scripts. Each hypothesis maps to specific questions, and each question probes specific themes. These themes become the initial code families.

Process:

- Work through every hypothesis in every script
- For each hypothesis, identify the questions it maps to
- For each question, identify the themes it probes
- Each theme becomes a candidate code
- Group related codes into candidate families
- Complete this before reading any interviews

### 1.2 First-Pass Reading

Reading order: alternate between one consumer/demand-side interview and one professional/supply-side interview to prevent single-side bias. Within each type, read chronologically by interview number.

During reading:

- Note emergent themes not captured by a priori codes
- Record candidate emergent codes with provisional definitions
- Do not finalise emergent codes during this pass; collect candidates only

### 1.3 Formal Code Entries

Each code entry must contain five elements:

```
### [Family#].[Code#] code-name

- **Definition**: What the code captures (one sentence)
- **Inclusion**: What qualifies a passage for this code
- **Exclusion**: What does NOT qualify despite surface similarity
- **Exemplar**: "Quote text." (Interview ##, Pseudonym)
```

The exclusion criteria are essential. Without them, codes drift during application, and passages that merely mention a topic get coded alongside passages that substantively engage with it.

### 1.4 Family Organisation

Target: 8 to 12 families with 3 to 8 codes per family. Families should be conceptually coherent: all codes in a family address the same broad phenomenon from different angles.

## 2. Revision Protocol

Apply after the first coding pass (Section 3), not before.

- **Merge** codes with greater than 80% overlap in coded passages (codes that almost always co-occur because they capture the same phenomenon with different labels)
- **Split** any code where a single code captures two distinct phenomena that co-occur in some interviews but diverge in others
- **Document** every merge, split, or redefinition in the codebook's revision log:

| Date | Change | Reason | Recoding required |
|---|---|---|---|
| ... | Merged X into Y | >80% co-occurrence; both captured [phenomenon] | Re-checked interviews 03, 07, 12 |

## 3. Coding Pass Protocol

### 3.1 Reading Order

First pass: alternate consumer/professional, chronological within type. This prevents the coder from developing a single-side lens that biases code application.

Second pass: same alternating order, but now against the stabilised codebook (post-revision). This pass catches codes missed in the first pass because the codebook was still evolving. Expect approximately 15% additional code assignments, concentrated in emergent codes.

### 3.2 Coding Unit

The coding unit is the passage: a single sentence or multi-sentence answer to a question. Critical rule: do not split mid-thought. If a participant's answer constitutes one continuous line of reasoning, that entire answer is the passage. If a participant pivots to a different topic within a single answer, the answer may be split at the pivot point.

### 3.3 Multi-Coding

A passage may carry multiple codes. Multi-coding is expected and informative; co-occurrence patterns across multi-coded passages are a primary data source for the co-occurrence matrix.

### 3.4 Ambiguous Passages

Passages where the best-fit code is unclear should be assigned the best-fit code and flagged for review. The flag is a "?" annotation. All flagged items are resolved after completing the full first pass, when the coder has full corpus context.

### 3.5 Recording Format

The coding record uses JSON with interviews as entries and codes as keys:

```json
{
  "interview_id": "09",
  "interview_name": "Sophie",
  "side": "consumer",
  "codings": {
    "google-first": {
      "present": 1,
      "citations": ["Q2: 'Google first, always.'"],
      "flags": []
    },
    "research-paralysis": {
      "present": 1,
      "citations": ["Q3: '...research is a way to feel like I am doing something...'"],
      "flags": []
    }
  },
  "emergent_candidates": []
}
```

Binary (present/absent) is primary. Optional frequency counts are reserved for intensity-sensitive codes only (e.g., "how many distinct information sources did the participant name?").

## 4. Emergent Code Candidates

During the first coding pass, coders note themes not captured by the a priori codebook. Each candidate includes:

- Proposed code name (lowercase-hyphenated)
- Provisional definition (one sentence)
- At least one supporting passage with interview citation
- Proposed family assignment (existing family or new family)

Emergent candidates are collected, deduplicated, and incorporated into the codebook during the revision protocol before the second pass.

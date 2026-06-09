# Analysis Protocols Reference

**Purpose:** Loaded during Step 6 of the analyze-interviews workflow. Covers negative case analysis, quantitising, two-sided comparison, segmentation, and hypothesis verdict protocols.

---

## 1. Negative Case Analysis

### Timing

Conduct after completing the second coding pass, when strong themes are apparent and the coder has a stable sense of what the data say. Conducting it earlier risks premature qualification of themes that have not yet fully emerged.

### Selection

Identify the top N themes by frequency (default: 5), meaning the codes or code families with the highest counts in the binary matrix. For each, deliberately search for interviews that contradict or qualify the theme. This is an active, adversarial search: "Which interviews tell a different story about this theme?"

### Documentation

For each theme under disconfirmation search, record:

- Interview number and disconfirming passage (quoted)
- How the negative case modifies the interpretation

Negative cases establish qualifying conditions ("This holds EXCEPT when [condition]") and boundary statements ("This applies to [segment X] but not [segment Y]").

### Minimum Standard

At least three of the top five themes must have at least one documented negative case. If no negative case exists for a strong theme, note this explicitly as a credibility limitation. A theme with no disconfirming evidence in a small qualitative sample more likely reflects sample homogeneity than universal truth.

---

## 2. Quantitising Protocol

### Binary Coding (Primary)

For each code, record 1 (present) or 0 (absent) per interview. This produces a matrix of [interviews] x [codes]. The binary matrix supports co-occurrence analysis and cross-tabulation.

### Frequency Counting (Secondary)

Use only for intensity-sensitive codes where count carries information beyond mere presence. Example: "multiple-info-sources" (count of distinct sources named). Do not default to frequency counting for all codes.

### Co-occurrence Matrix

For each pair of codes (i, j), count interviews where both are present. Diagonal cell (i, i) contains the total count for code i. Display as upper-triangle with diagonal. Co-occurrence patterns reveal which phenomena travel together in participants' experience.

### Statistical Constraints

At n < 30, the only appropriate test is a simple 2x2 chi-square, treated as exploratory signal only. The feasible comparison for a two-sided study is consumer vs. professional presence of a code. Report results as "the association was [present/absent] at the exploratory level."

### Prohibited Practices

- Do not report percentages ("60% of participants said...")
- Do not run regression, cluster analysis, or correspondence analysis at n < 30
- Do not claim statistical significance
- Use fuzzy qualifiers: "most," "typically," "a few," "nearly all," "several"

---

## 3. Two-Sided Comparison Protocol

### Framing

When the business model is two-sided (marketplace, platform, referral network), both sides are customers. Each has its own Problem Statement Canvas. The comparison table column headers reflect both sides as customers (e.g., "Demand-Side Customer Perspective" and "Supply-Side Customer Perspective").

### Within-Group Comparison (First)

Before comparing across sides, examine whether each side is internally homogeneous on the theme. Are consumers aligned, or do segments diverge? Are professionals aligned, or does experience level create internal differences?

### Between-Group Comparison (Second)

For each shared theme, juxtapose how one side describes it from the inside against how the other side observes it.

### Comparison Table Format

| Theme | Demand-Side Customer Perspective | Supply-Side Customer Perspective | Structural Insight |
|---|---|---|---|
| ... | ... | ... | ... |

### Patterns to Seek

1. **Mirror inversions**: one side wants X, the other complains about X's consequences
2. **Information asymmetries**: one side does not know what the other knows
3. **Motivation misalignments**: different incentive structures producing friction
4. **Vocabulary gaps**: both sides describe the same phenomenon using different words

### Minimum Deliverable

At least 5 theme rows producing at least 3 structural insights not visible from either side alone.

### Single-Sided Studies

Skip this section entirely if `len(customer_sides) == 1`. The workflow marks this as conditional.

---

## 4. Segmentation Protocol

### Derivation

Segments emerge from coding pattern clusters, not demographic categories. A segment is defined by convergent behaviour and attitude patterns across multiple codes.

### Minimum Evidence

Two interviews per segment. A single-interview "segment" is an outlier observation, reported as such.

### Process

After completing the coding matrix and co-occurrence analysis, examine the binary matrix for clusters of interviews sharing high presence (1) on the same set of codes. Two interviews with converging patterns on three or more codes constitute a candidate segment. Read those interviews together to confirm coherent experiential profile.

### Profile Template (8 Dimensions)

1. **Segment name**: descriptive label, not a demographic category
2. **Defining characteristics**: 3 to 5 code patterns that define membership
3. **Representative interviews**: listed by number and pseudonym
4. **Information-seeking behaviour**: how this segment looks for help
5. **Trust model**: what sources or signals this segment trusts
6. **Paralysis/failure pattern**: how this segment gets stuck
7. **Willingness to pay**: price range and payment model preference
8. **Concept reaction**: how this segment responded to the product concept

For supply-side segments, dimensions 4-8 may be replaced with role-appropriate equivalents (e.g., "intake burden pattern" instead of "paralysis pattern," "referral/partnership conditions" instead of "willingness to pay").

### Boundary Cases

Some interviews will not fit cleanly into any segment. Report as boundary cases, noting the segments they most resemble and the specific dimensions on which they diverge.

### Equal Depth

All segments receive equal analytical depth regardless of size. Do not write more about larger segments simply because more data is available.

---

## 5. Hypothesis Verdict Protocol

### Mapping

Map coded evidence back to pre-defined hypotheses from the interview scripts. Evidence is not restricted to the mapped questions; a participant may address a hypothesis spontaneously in response to a different question.

### Verdict Levels

- **Confirmed**: consistent evidence across most interviews with no strong disconfirming cases
- **Partially supported**: evidence exists but with significant qualifying conditions or contradicting cases
- **Refuted**: disconfirming evidence outweighs supporting evidence
- **Insufficient data**: too few interviews addressed this hypothesis

### Confidence Levels

- **Very strong**: unanimous or near-unanimous across all relevant interviews
- **Strong**: clear majority supports the verdict with minor qualifications
- **Moderate**: mixed evidence; verdict depends on weighting of competing considerations
- **Weak**: limited evidence makes the verdict tentative

### Reasoning Chain (Required for Each Hypothesis)

1. Supporting evidence (interview numbers and brief quotes)
2. Contradicting evidence (interview numbers and brief quotes)
3. Qualifying conditions ("EXCEPT when" and "applies to X but not Y" statements)
4. Logical path from evidence to verdict (the inferential step, not a restatement of evidence)

### Epistemic Register

Use: "the qualitative findings give reason for optimism," "the data suggest," "participants consistently indicated," "the evidence supports the proposition that."

Do not use: "this proves," "this guarantees," "the data confirm beyond doubt."

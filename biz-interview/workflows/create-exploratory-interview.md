# Create Exploratory Interview Script

Design and draft an exploratory interview script for customer discovery or stakeholder research.

## Instructions

- [ ] Step 0: Load reference ⚠️ REQUIRED
  - [ ] 0.1 Load `references/interview-design-reference.md` before drafting any questions.

- [ ] Step 1: Gather context ⛔ BLOCKING
  - [ ] 1.1 Identify the interviewee segment.  Who are we interviewing?  Consumers, professionals, institutional buyers, supply-side providers, or a mixed pool?
  - [ ] 1.2 Read the project's business strategy or ideation document to extract hypotheses and assumptions that need validation.
  - [ ] 1.3 Read any existing interview scripts in the project to understand what has already been covered and avoid duplication.
  - [ ] 1.4 If not already clear from context, ask: "What hypotheses or assumptions do you most need to test with this interview segment?" ⛔ BLOCKING

- [ ] Step 2: Hypothesis mapping ⛔ BLOCKING
  - [ ] 2.1 Propose a hypothesis mapping table:

        | # | Hypothesis | What We Need to Learn | Proposed Script Section |
        |---|---|---|---|
        | H1 | ... | ... | ... |

  - [ ] 2.2 Confirm the mapping with the user before proceeding.  The user may add, remove, or reprioritise hypotheses.

- [ ] Step 3: Script architecture ⛔ BLOCKING
  - [ ] 3.1 Propose the script structure following the 9-component architecture from the reference: basic info, opening, free association, background, problem exploration, current solutions, value/willingness to pay, concept reaction, close.
  - [ ] 3.2 Propose section count and question count.  Target: 11-15 core questions + 1-2 time-permitting + close, for a 45-60 minute session.
  - [ ] 3.3 Note which sections are time-permitting and can be skipped if the interview runs long.
  - [ ] 3.4 Confirm architecture with the user.

- [ ] Step 4: Design free association exercise ⛔ BLOCKING
  - [ ] 4.1 Propose a warm-up prompt (trivial, relatable, unrelated to the domain).
  - [ ] 4.2 Propose 2-4 real prompts, each probing a different dimension of the problem space.  Prompts are situations or phrases, not questions.  Move from broad to narrow.
  - [ ] 4.3 For supply-side or professional interviews, ensure prompts do not assume the interviewee endorses the product model or wants to participate.
  - [ ] 4.4 Confirm prompts with the user.

- [ ] Step 5: Draft questions ⚠️ REQUIRED
  - [ ] 5.1 For each section, draft main questions with 3-5 follow-up sub-questions.
  - [ ] 5.2 Apply the question crafting rules from the reference:
    - Main question is open-ended and stands alone.
    - Sub-questions are conditional follow-ups, used only if the main answer does not naturally cover the ground.
    - Mark redundant sub-questions with *(skip if already covered)*.
    - When the interviewee pool spans distinct roles, add profile-specific skip notes so interviewers know which follow-ups to use or skip.
    - Include a "Why important" annotation per question explaining what hypothesis or deliverable field it serves.
  - [ ] 5.3 Run the anti-pattern audit from the reference.  Check every question for:
    - Leading language (assumes the answer or frames the situation favourably).
    - Hidden assumptions about the interviewee's situation or willingness.
    - Business jargon or technical terms the interviewee may not know.  Domain terminology is acceptable for professional-segment interviews.
    - Concept-first ordering (describing the product before exploring the problem).
  - [ ] 5.4 Present the draft to the user for review. ⛔ BLOCKING before proceeding to templates.

- [ ] Step 6: Generate templates ⚠️ REQUIRED
  - [ ] 6.1 Generate the Interviewer Info table with fields appropriate to the interviewee segment (demographic fields for consumers; role, organisation, experience, jurisdiction for professionals).
  - [ ] 6.2 Generate the Key Points Summary template with segment-specific buckets drawn from the hypothesis categories.
  - [ ] 6.3 Generate the hypothesis mapping appendix.  Two tables:
    - **Canvas/deliverable field mapping:** which questions fill which application or canvas fields.
    - **Assumption testing mapping:** which assumptions each question tests and what would confirm or kill each assumption.

- [ ] Step 7: Assemble and save
  - [ ] 7.1 Assemble the full script in this order: title, Interviewer Info table, Key Points Summary template, Interviewer Opening, sections with questions, and hypothesis mapping appendix.
  - [ ] 7.2 Write the file to the user-selected output path using the host assistant's normal file-writing method.
  - [ ] 7.3 If the user has no preferred destination, suggest `./outputs/biz-interview/customer-discovery/`.
  - [ ] 7.4 Confirm the saved path with the user.

## Guardrails

- Do not draft questions before the hypothesis mapping (Step 2) is confirmed.
- Do not introduce the product concept before Section 7+ of the script.
- Do not include more than 15 core questions.  If the hypothesis set is large, consolidate questions that test multiple hypotheses rather than adding more questions.
- The script must work for the stated interviewee pool without requiring per-interviewee rewrites.  Use skip notes for role-specific follow-ups.

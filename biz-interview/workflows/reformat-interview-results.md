# Reformat Interview Results

Clean raw interview transcripts (typically docx-converted) into standardised interview result notes.

## Instructions

- [ ] Step 1: Identify targets ⛔ BLOCKING
  - [ ] 1.1 Identify which files need reformatting.  The user provides specific paths or a folder to scan.
  - [ ] 1.2 Read the interview script these results are based on to understand the expected structure (section headings, question numbering, follow-up format).
  - [ ] 1.3 Read 1-2 result files to assess their current state and identify what needs cleaning.

- [ ] Step 2: Define transformation rules ⛔ BLOCKING
  - [ ] 2.1 **Standard transformations** (apply to all interview results):
    - Replace conversion clutter with a clean title, interviewee summary, and any user-requested metadata fields.
    - Remove broken TOC blocks (Google Docs-style anchors, markdown-style anchors with page numbers).
    - Remove the interviewer opening boilerplate (the "Thank you for taking the time..." paragraph).
    - Remove free association instruction text (the "I am going to say a word or phrase..." paragraph).
    - Remove all interviewer-facing annotations: "Why important for accelerator" paragraphs, hypothesis notes, methodology reminders, or any text addressed to the interviewer rather than recording the interviewee's response.
    - Remove all unused "Possible follow-ups" / "Possible probes" lists, UNLESS actual interviewee answers are written inline under those bullets.  In that case, extract the answers and place them cleanly under the parent question.
    - Remove empty trailing labels that have no content after them: "Follow-up answers:", "The Story: Key facts / timeline / turning point", "Concept reaction answers:", "Anything else to add:", "Notable words / emotional tone / recurring themes:", "Trust signals:", "Distrust signals:", "Top barriers mentioned:", "Interviewee's experience:".
    - Mark questions with no recorded answer: *(No answer recorded.)*
    - Format free association entries as: **"Prompt text"**  -- answer text
  - [ ] 2.2 **Structural transformations:**
    - Heading hierarchy: H1 for interview title, H2 for Interviewer Info / Key Points Summary / Sections, H3 for Questions.
    - Answer text directly under questions without "Main answers:" labels.
    - Keep the Interviewer Info table as-is (it contains factual metadata).
    - Keep the Key Points Summary template with empty bullets preserved for later filling.
  - [ ] 2.3 Present the transformation rules to the user and confirm before executing. ⛔ BLOCKING

- [ ] Step 3: Execute
  - [ ] 3.1 **Bulk reformats (3+ files):** Propose parallel agent execution, one agent per file, each given the confirmed transformation rules and file-specific extraction notes (e.g., which follow-up bullets contain inline answers that need extracting).
  - [ ] 3.2 **Single files or small batches (1-2 files):** Reformat directly and write the cleaned file using the host assistant's normal file-writing method.
  - [ ] 3.3 Verify each reformatted file: title and summary are clear, no empty labels remain, all inline answers have been extracted, heading hierarchy is correct, no interviewer-facing annotations survive.

- [ ] Step 4: Report
  - [ ] 4.1 Present a summary table:

        | File | Lines before | Lines after | Key changes |
        |---|---|---|---|

## Guardrails

- Never alter the substance of interviewee answers.  Reformatting changes structure and removes boilerplate; it does not paraphrase, summarise, or reword what the interviewee said.
- Preserve all actual interviewee content, including mixed-language text, informal phrasing, and verbatim quotes.
- When in doubt about whether text is an interviewer annotation or an interviewee answer, keep it and flag for user review.

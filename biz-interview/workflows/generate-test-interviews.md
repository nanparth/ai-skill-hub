# Generate Test Interviews

Generate fictional interview results from a persona grid and an existing interview script.  Produces realistic cleaned-transcript-style results for prototyping analysis workflows, interviewer training, or skill testing.

## Instructions

- [ ] Step 1: Gather inputs ⛔ BLOCKING
  - [ ] 1.1 Identify the interview script to use (path to the .md script file).
  - [ ] 1.2 Identify or build the persona grid.  Each persona needs:
    - Name (or "Anonymous" + descriptor)
    - Role / occupation
    - Age, ethnicity, gender, languages spoken
    - Interview date and format (virtual / in person / phone)
    - Interviewer name
    - Personality summary (2-3 sentences: how they talk, how much, general attitude)
    - Verbosity level (low / moderate / high)
    - Domain-specific attitudes (e.g., AI attitude for tech-adjacent topics)
  - [ ] 1.3 Confirm persona grid with user. ⛔ BLOCKING

- [ ] Step 2: Build skeleton template ⛔ BLOCKING
  - [ ] 2.1 Read the interview script file.
  - [ ] 2.2 Extract ALL section headings (`## Section N. Title`) and question headings (`### Q N. Full question text`) VERBATIM.  No abbreviation, no paraphrase.
  - [ ] 2.3 Extract the Interviewee Info table structure (all field names and the table format).
  - [ ] 2.4 Extract the Key Points Summary template (all bucket names with empty bullets).
  - [ ] 2.5 For each question, extract the "Possible follow-ups" sub-questions that should be available for the writer agent to use.
  - [ ] 2.6 Assemble the skeleton:
    - Header template with title and summary pattern
    - Interviewee Info table (fields from script, values blank)
    - Key Points Summary (buckets from script, bullets empty)
    - Disclaimer line if applicable (e.g., legal professional interviews)
    - All section headings VERBATIM
    - All question headings VERBATIM
    - Under each question: placeholder for main answer + list of available follow-up sub-questions from the script
    - Follow-up format spec: `Follow-Up Question:` / `Answer:` plain text
    - Free association format spec: `**"Prompt"** -- answer text`
    - Related section template
  - [ ] 2.7 Present skeleton to user for review. ⚠️ REQUIRED.  This is the single most important quality gate.  Every structural issue (shortened headings, wrong formats, missing sections) is caught here, not after 10 agents have already produced output.

- [ ] Step 3: Configure generation parameters
  - [ ] 3.1 Confirm output folder. If the user has no preference, suggest `./outputs/biz-interview/customer-discovery/`.
  - [ ] 3.2 Confirm filename pattern (e.g., `NN-persona-segment-interview.md`).
  - [ ] 3.3 Confirm any file-level variations:
    - Should all personas answer all questions, or should some skip the time-permitting section?
    - Any persona-specific notes (e.g., "this interviewee asks the interviewer a counter-question in Q7")?

- [ ] Step 4: Dispatch parallel agents ⚠️ REQUIRED
  - [ ] 4.1 For each persona, load `agents/interview-writer.md` and dispatch via the Agent tool with these parameters:
    - **model**: `sonnet`
    - **skeleton**: the EXACT skeleton text from Step 2 (not a reference to the script file)
    - **persona**: the persona spec from the grid
    - **output_path**: the resolved file path
    - **follow_up_pool**: the available sub-questions per section
    - **format_rules**: follow-up format, free association format, answer conventions
  - [ ] 4.2 All agents run in parallel (independent, no shared state).
  - [ ] 4.3 Wait for all agents to complete.

- [ ] Step 5: Verify outputs ⚠️ REQUIRED
  - [ ] 5.1 For each generated file, check:
    - All section headings match the skeleton VERBATIM
    - All question headings match the skeleton VERBATIM
    - Follow-up questions are drawn from the script's sub-question pool (max 2-3 natural prompts per file that are not from the pool)
    - Follow-up format is `Follow-Up Question:` / `Answer:` consistently
    - Free association uses `**"Prompt"** -- answer` format (no dialogue format)
    - Title and summary are clear and match the persona
    - Interviewee Info table has all fields filled
    - Key Points Summary has empty bullets (not pre-filled)
    - No interviewer-facing annotations in output
  - [ ] 5.2 Flag any mismatches for manual review or automated fix.
  - [ ] 5.3 Report summary table:

        | # | Persona | Lines | Follow-ups | Verbosity | Issues |
        |---|---|---|---|---|---|

## Guardrails

- The skeleton is the structural contract.  Agents fill in content but NEVER modify headings, table structure, or section order.
- Follow-up questions must come from the script's prepared sub-questions.  Agents may use max 2-3 brief natural interviewer prompts per file ("Can you say more?", "How so?") where no script match fits.
- Answers should read as cleaned transcripts: natural spoken language, no essay prose, no artificial filler (um, uh).  Personality comes through vocabulary and sentence structure, not simulated disfluency.
- Verbosity controls both turn count and answer length, balanced proportionally.  High verbosity produces more follow-up exchanges AND somewhat longer individual answers, but the two scale together so that no single answer block becomes essay-like.  Low verbosity means fewer exchanges with shorter answers.  The goal is that total output grows with verbosity without any single block reading as a written essay.

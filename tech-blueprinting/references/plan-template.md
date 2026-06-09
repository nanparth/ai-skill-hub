# Implementation Plan Template

Load this reference when drafting implementation plans, dev plans, or task breakdowns meant to be executed by `tech-implement`. Supplements the Stage 1-3 workflow with artifact-shape rules. Does not replace the flow.

## Purpose

Implementation plans = execution contracts for an engineer or subagent with zero codebase context. Every task, every step, fully specified. The plan must stand alone: no "see the spec", no "figure it out".

## Rigor Gradient ⛔ READ FIRST

Rigor scales to stakes. Blocker fix earns verbatim before-state + reproduced failure; one-line notice edit earns neither. Tag each task severity, then apply only the blocks that severity earns. This gradient governs every pattern below; it is the antidote to template bloat.

| Severity | Before-state block | Reproduce-first step | Per-task acceptance | Triage line |
|---|---|---|---|---|
| blocker / high | required | required (bug fixes) | required | required |
| medium | required if task modifies existing code | required if reproducible defect | required | required |
| trivial (git-init, notice edit) | omit | omit | one-line check | optional |

Over-building a trivial task = YAGNI violation. Lean stays correct. Match the heavy blocks to severity, never reflexively to every task.

## Header

Every plan starts with:

```markdown
# [Feature Name] Implementation Plan

> **For implementers:** Execute task-by-task via `tech-implement`. Checkbox `- [ ]` steps track progress.

**Goal:** [One sentence. What this builds.]

**Architecture:** [2-3 sentences. Approach and shape.]

**Tech Stack:** [Versioned libraries + key deps. "React 18 + TypeScript + Vite", not "React". Vague stack produces vague code.]

**Commands:** [Full commands with flags: build, test, lint. e.g. `pytest -v`, `npm run build`. The implementer references these constantly.]

**Boundaries:**
- ✅ Always: [run tests before commits, follow naming conventions]
- ⚠️ Ask first: [schema changes, new dependencies, CI config]
- 🚫 Never: [commit secrets, edit `vendor/` or generated dirs, delete failing tests without approval]

**Conventions:**
- Tasks strictly ordered; execute top-to-bottom. Per-task dependencies implicit in ordering.
- Idempotent imports: import an earlier task already added is present → treat sub-step satisfied, add no duplicate.
- Line numbers cite the audited snapshot; re-confirm against the live file before editing (earlier tasks shift them).

**Scope/Provenance:** [N tasks; severity mix (e.g. 2 blocker, 13 high, 18 medium); derived from <audit / spec / issue>. Declares evidentiary basis. Omit for greenfield plans with no prior artifact.]

---
```

Stack must be versioned and Commands must be runnable as written; the header doubles as the six-core-areas surface (Commands, Tech Stack, Boundaries) the implementing agent reads first. Git workflow lives in the per-task commit steps (see Bite-Sized Granularity). Project structure and testing live in the File Structure block and TDD steps below. The **Conventions** block pre-empts cross-task friction (ordering, duplicate imports, stale line numbers); the **Scope/Provenance** line tells the reader what audit or spec the tasks trace to.

## File Structure Block

Before tasks, map which files get created or modified, by which action, by which task. Each file = single responsibility.

```markdown
## File Structure

| File | Action(s) | Task(s) |
|---|---|---|
| `src/auth/token.py` | Create | 2 |
| `src/auth/middleware.py` | Modify | 3, 5 |
| `tests/auth/test_token.py` | Create, Test | 2 |
```

Action vocabulary: Create / Modify / Delete / Test. The `Task(s)` column cross-references the tasks that touch each file. A file appearing under 3+ tasks (e.g. one manager touched by 7 tasks) signals coupling; sequence those tasks deliberately and re-confirm line numbers each time. Greenfield plan with 1:1 file→task mapping → a `Role` column reads fine instead.

Split by responsibility, not technical layer. Files that change together live together. Follow existing patterns; do not unilaterally restructure. Group by concern (entrypoint/core/contracts/utils/adapters) per `shared/code-organization.md`; stay flat below ~8 files / one concern.

## Thematic Sections

Plan over ~8 tasks → group tasks under themed headers (`## A. Test harness`, `## B. Subprocess hardening`), one-line ordering rationale per section. Foundational sections first, so later tasks stay verifiable. Plan under ~8 tasks → keep tasks flat, no sectioning.

## Task Block Template

Canonical block. Blocks marked *(per gradient)* appear only at the severity the Rigor Gradient table requires; trivial tasks drop them.

```markdown
### Task N: [Component Name]

**Findings:** <id / source> · **Severity:** blocker|high|medium|low · **Effort:** trivial|small|medium

**Rationale:** [Why this task exists: failure mode, race, or user impact. Gives the implementer the mental model to adapt when line numbers have drifted.]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

<details><summary><strong>Current state</strong> (before-fix context)</summary>     <!-- per gradient: blocker/high, or medium that modifies code -->

Verbatim current code at `existing.py:123-145`:

​```python
def old_behaviour():
    return wrong
​```

Reproduced failure (clean state):

​```
<exact observed error output, e.g. "ModuleNotFoundError: No module named 'osi'">
​```

</details>

- [ ] **Step 0: Reproduce the defect from a clean state**     <!-- per gradient: bug fixes only -->

  Run: `pytest tests/path/test.py -q`
  Expected: FAIL — `<exact observed message>`. Capture as the baseline the fix must flip.

- [ ] **Step 1: Write failing test**

  ​```python
  def test_specific_behaviour():
      result = function(input)
      assert result == expected
  ​```

- [ ] **Step 2: Run test, verify FAIL**

  Run: `pytest tests/path/test.py::test_name -v`
  Expected: FAIL, `NameError: function not defined`. Cite real observed output where you have run it, not a generic "FAIL".

- [ ] **Step 3: Minimal implementation**

  One change spanning several edit sites → decompose into labelled sub-steps, each individually applicable:

  **3a.** Add the field next to `self._jobs`.
  **3b.** Guard and claim it under `self._lock`.

  ​```python
  def function(input):
      return expected
  ​```

- [ ] **Step 4: Run test, verify PASS**

  Run: `pytest tests/path/test.py::test_name -v`
  Expected: PASS — `1 passed in 0.42s`. Cite the real observed line.

- [ ] **Step 5: Document the behaviour**     <!-- when the task changes user-facing behaviour -->

  Add to `README`, under "Stopping the server":
  > Press Ctrl+C once; the active run is interrupted and workers join before exit.

- [ ] **Step 6: Commit**

  ​```bash
  git add tests/path/test.py src/path/file.py
  git commit -m "feat: add specific feature"
  ​```

**Acceptance criteria:**     <!-- per gradient: required for non-trivial; one-line check for trivial -->
- [Mechanically-checkable statement the reader verifies the build against, distinct from TDD pass/fail.]
- [e.g. `osi doctor` exits 0 with the MinerU worker absent; manifest `events` length stays ≤ the cap.]
```

Each new element earns its place by severity:

- **Triage line** (`Findings · Severity · Effort`) makes the task prioritizable and traceable to the audit or spec that produced it. Required on every non-trivial task; optional on trivial.
- **Rationale** gives the why before the how, so a drifted line number does not strand the implementer.
- **Current state** block carries the verbatim before-code plus the reproduced failure: the half of before/after the implementer cannot otherwise see. Required per gradient.
- **Step 0 reproduce** captures an empirical baseline before any test is written; the fix's job is to flip it.
- **Real expected-output** (`1 passed in 0.42s`, `396 tests collected, 0 errors`) beats generic `PASS`/`FAIL`; cite observed values wherever you ran the command.
- **Sub-steps** (`3a`, `3b`, `3c`) decompose a multi-site change without bundling.
- **Docs step** makes a doc update a real, prose-carrying step, not an afterthought.
- **Acceptance criteria** close the task with checkable statements separate from the TDD loop; the global Success Criteria section aggregates the build-level version.

## Bite-Sized Granularity

Each step = one action, 2-5 minutes. Do not bundle.

- "Reproduce the defect" = step (bug fixes; precedes the failing test)
- "Write failing test" = step
- "Run to verify FAIL" = step
- "Implement minimal code" = step (multi-site change → split into `3a`, `3b`, `3c`, each its own action)
- "Run to verify PASS" = step
- "Document the behaviour" = step (when user-facing behaviour changed)
- "Commit" = step

Bundling breaks the TDD loop and defeats progress tracking. Sub-steps (`3a`/`3b`) are the one sanctioned subdivision: they keep a complex implementation individually applicable without merging the verify/commit loop.

## No-Placeholders Rule ⛔ BLOCKING

These patterns = plan failures. Never write them:

| Forbidden | Reason |
|---|---|
| "TBD", "TODO", "implement later", "fill in details" | Not executable |
| "Add appropriate error handling" | Does not say what or where |
| "Handle edge cases" | Which cases? What handling? |
| "Write tests for the above" without code | Test content must be present |
| "Similar to Task N" | Implementer may read out of order; repeat the code |
| Steps describing what without showing how | Code steps need code blocks |
| References to types, functions, methods not defined in any task | Unresolvable symbol |

If a step would need any of the above, either expand it inline or split into a new task.

**EXACT-content directive.** Content that must be byte-exact (config file, `.gitattributes`, pinned version) → flag it: "Create `pytest.ini` with this EXACT content". Verbatim content carries no judgement; illustrative code does. Mark which is which: implementer copies the first, adapts the second.

## Self-Review Checklist

After writing the complete plan, run this checklist yourself. Not a subagent dispatch.

1. **Spec coverage.** Skim each spec section or requirement. Point to the task that implements it. Gaps → add tasks.
2. **Placeholder scan.** Search for the forbidden patterns above. Fix inline.
3. **Type consistency.** Method signatures, property names, function names in later tasks match earlier task definitions. `clearLayers()` in Task 3 vs `clearFullLayers()` in Task 7 = bug.
4. **File path consistency.** Same file referenced across tasks uses exactly the same path string.
5. **Commit cadence.** Each task ends in at least one commit step. No orphan work.
6. **Triage coverage.** Every non-trivial task carries a `Findings · Severity · Effort` line.
7. **Gradient respected.** Blocker/high tasks carry a before-state block (if modifying code) and acceptance criteria; trivial tasks skip blocks they do not earn.
8. **Acceptance present.** Every non-trivial task closes with checkable `Acceptance criteria`.
9. **Matrix resolves.** Every `Task(s)` number in the File Structure matrix resolves to a real task; sequence multi-touch files deliberately.

Fix issues inline. No re-review needed; just fix and move on.

## Execution Handoff Footer

End every implementation plan with:

```markdown
---

## Execution

Hand this plan to `tech-implement`:

> "Execute this plan: [plan-file-path]"

`tech-implement` sets up a worktree, dispatches an implementer per task with two-stage review (spec + quality), runs the verification gate, and finishes with merge/PR/cleanup + optional README chain.
```

## Source

Adapted from the `writing-plans` pattern for a portable skill folder and optional `tech-implement` execution path.

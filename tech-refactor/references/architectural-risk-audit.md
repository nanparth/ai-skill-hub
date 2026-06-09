# Architectural Risk Audit

Load at Phase 2. Detection checklist for architectural failure modes. Present output in two sections: **Confirmed findings** (observed directly in code) and **Plausible risks** (inferred, need validation). Each finding: category + file/symbol location + severity (blocks migration / degrades quality / informational).

## Contents

1. [Primary failure mode — additive refactor bias](#1-primary-failure-mode--additive-refactor-bias)
2. [Failure mode catalog](#2-failure-mode-catalog) — Competing sources of truth, Partial refactor residue, Runnable-but-wrong behaviour, Context drift, Test coupling, Unsafe operations, Dependency bloat, Orphaned test infrastructure
3. [Audit output format](#3-audit-output-format)

---

## 1. Primary failure mode — additive refactor bias

**Definition:** New abstractions added without retiring old access paths. Architecture appears modular; old coupling preserved. Code volume increases while architecture looks cleaner.

**Symptoms:**
- New canonical modules added; old facade still re-exports private helpers
- Tests patch legacy private symbols (e.g. `module._helper`) instead of canonical owners
- Architecture has two stories: specialized modules for implementation, old facade as legacy dumping ground
- Green test suite proves nothing about centralization
- `__all__` or re-exports expose private names without documented reason

**Detection trigger:** "What old access path was deleted?" If the answer is "none," centralization is incomplete.

**How to detect:**
- Grep for `from legacy_module import _` or `mock.patch('legacy_module._`
- Check `__all__` lists against what each module actually owns vs. re-exports
- Count import sites: if canonical owner has fewer callers than the old facade, migration is incomplete
- Search for the old facade name in test `patch()` strings

**Remediation direction:** Phase 4c legacy path retirement plan. No new abstraction ships without naming the old path it retires.

---

## 2. Failure mode catalog

### Competing sources of truth

**What it looks like:** Same constant, enum, status code, business rule, or schema defined in more than one module. Callers import from different sources; values may have diverged.

**Detection:** `grep -r "STATUS_" src/` or equivalent for domain constants; look for duplicate class hierarchies; diff schema files against each other.

**Remediation direction:** Single canonical module owns definition; all others import from it; copies deleted.

---

### Partial refactor residue

**What it looks like:** Old and new patterns coexist — e.g. two service layers, two config loaders, two error-handling approaches — with no documented migration plan or removal deadline.

**Detection:** Look for parallel naming conventions (`order_service.py` and `orders/service.py`); look for `# TODO: remove after migration` comments with no ticket reference; look for adapter layers with no removal condition.

**Remediation direction:** Complete the migration or document a concrete deadline. Coexistence without a plan is permanent.

---

### Runnable-but-wrong behaviour

**What it looks like:** Tests pass, but the implemented semantics diverge from documented or expected behaviour. Often introduced by previous refactors that changed logic while preserving structure.

**Detection:** Compare docstrings/comments against actual implementation; run characterization tests (write a test with a guessed assertion, let actual output correct it); look for exception-suppression patterns (`except Exception: pass`, broad `except` blocks added during refactors).

**Remediation direction:** Write characterization tests that lock current behaviour before any change. Identify divergence explicitly; fix intentionally, not accidentally.

---

### Context drift

**What it looks like:** Schema files, generated types, API docs, frontend/backend type definitions, config schemas, or CI scripts are out of sync with source code.

**Detection:**
- Diff generated files against their sources (e.g. OpenAPI spec vs. route handlers)
- Compare frontend TypeScript types against backend response shapes
- Check config schema against config loader
- Look for stale doc examples that no longer match current API signatures

**Remediation direction:** Identify owner for each drifted artifact; add to Phase 5 roadmap as sync tasks. Add generation scripts or contract tests to prevent re-drift.

---

### Test coupling

**What it looks like:** Tests assert implementation details rather than behaviour. Patching private symbols, testing internal state, or asserting call counts on private methods. These tests block refactoring without protecting user-visible behaviour.

**Detection:** `grep -r "mock.patch.*\._" tests/`; look for `assert mock_obj._private.called`; look for tests importing from `module._submodule`; look for tests that fail when internal structure changes but user output is unchanged.

**Remediation direction:** Replace with behaviour tests against the public surface. Do not delete until a behaviour-equivalent replacement exists.

---

### Unsafe operations

**What it looks like:** Shell execution, database migrations, file deletion, permission escalation, or secret access in scope of the planned refactor.

**Detection:** `grep -r "subprocess\|os.system\|os.remove\|shutil.rmtree\|DROP TABLE\|os.environ\[" src/`

**Treatment:** Flag each instance explicitly in Phase 2 findings. Each unsafe operation → hard stop in Phase 5 roadmap; requires explicit user confirmation before that task executes. Do not batch unsafe operations into a single task.

---

### Dependency bloat

**What it looks like:** Packages listed in manifests (`package.json`, `pyproject.toml`, `requirements.txt`) with no runtime, type-only, build-time, test, lint, format, CI, or documentation-tooling usage.

**Detection:**
- Cross-reference manifest entries against grep of all import statements
- Check build scripts and test setup files for indirect usage
- Check lint/format config and CI workflows for tool references
- Flag peer dependencies and framework-convention packages separately — they may be needed without explicit imports

**Remediation direction:** Remove confirmed-unused entries; validate build and test suite pass. Do not remove peer dependencies without checking framework docs.

---

### Orphaned test infrastructure

**What it looks like:** Test helpers, mocks, fixtures, and factory functions imported by no active test file. Common after migrations that replaced mocked tests with integration tests.

**Detection:**
- List all files in test support directories (`helpers/`, `mocks/`, `fixtures/`, `factories/`)
- Grep for inbound imports across the test tree: `grep -r "import.*from.*helpers\|require.*fixtures" tests/`
- Identify any support file with no inbound imports within the test tree
- Check Storybook files and test setup files for similar orphans

**Remediation direction:** Delete proven-unused test infrastructure. Preserve helpers documenting important edge cases or supporting external usage even if locally unreferenced.

---

## 3. Audit output format

Structure Phase 2 output as:

```
## Confirmed findings
[category] [file:line or symbol] — [what was observed] — severity: blocks migration / degrades quality / informational

## Plausible risks
[category] [file or module] — [what was inferred and why] — needs: [what would confirm or rule it out]
```

Confirmed = directly observed in code. Plausible = inferred from patterns, naming, or structure. Keep them separate; do not treat inferences as facts.

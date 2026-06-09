# Legacy Path Retirement

Load at Phase 4c. Deletion-oriented centralization protocol.

**Core principle:** Every new abstraction must retire an old access path. Centralization is not complete until old paths are removed. Adding is easy; deletion is the proof.

## Contents

1. [Symbol classification](#1-symbol-classification)
2. [Dependent mapping](#2-dependent-mapping)
3. [Deletion protocol](#3-deletion-protocol)
4. [Test migration protocol](#4-test-migration-protocol)
5. [Guard test templates](#5-guard-test-templates)
6. [Decision rules](#6-decision-rules)
7. [Verification gate](#7-verification-gate)
8. [Deletion confidence levels](#8-deletion-confidence-levels)

---

## 1. Symbol classification

Classify every symbol in affected modules before planning any deletion.

| Category | Definition | Treatment |
| --- | --- | --- |
| Public entrypoint | Documented, user-facing, stable API surface | Preserve; breaking change requires versioning or deprecation notice |
| Internal canonical | New authoritative owner after refactor | Strengthen; all internal callers migrate here |
| Transitional compatibility | Old path kept temporarily with a documented removal deadline | Keep only with removal date; track remaining callers |
| Dead | No callers outside retired tests or stale docs | Delete immediately |

**Transitional rule:** a compatibility alias without a documented removal date is not transitional — it is permanent. Either add a concrete deadline or delete it now.

---

## 2. Dependent mapping

Search production source and test files **separately** — they have different migration rules.

For each symbol being retired, enumerate:
- Direct imports: `from module import symbol`
- Patch targets: strings in `mock.patch('module.symbol')` or `monkeypatch.setattr`
- Generated references: auto-generated clients, protobuf stubs, OpenAPI-derived types
- Config references: config keys, env var names, feature flag names
- Documentation references: docstrings, README examples, inline comments

**Evidence sources — check all before declaring unused:**
- Direct imports and re-exports
- Barrel/index files that re-export symbols
- Dynamic imports (`import()`, `require()`, `importlib.import_module`)
- Lazy-loaded routes and route manifests
- Config files and env-var references
- CLI scripts and `package.json` `scripts` entries
- Test files, mocks, fixtures, and test setup
- Storybook files and documentation examples
- Build tooling and CI workflow references
- String-based references (reflection, plugin registries, monkeypatch strings)
- Generated files and auto-generated clients
- External consumers — if exported from a published package, treat as public unless explicitly marked private

**Treat tests as architecture participants, not passive verification.** A test that imports `from legacy_facade import _helper` is coupling to a private symbol. That coupling must be severed before the symbol can be deleted, not after.

---

## 3. Deletion protocol

Execute in this order — do not delete before test migration is complete (see §4).

1. Private aliases re-exporting private names without a documented public justification → delete
2. Compatibility wrappers with no documented removal deadline → delete or add deadline now
3. Dead constants or statuses duplicated across modules → delete copies, keep canonical
4. Re-exports in `__all__` that expose private names → remove from `__all__`
5. Remove imports made dead by the deletions above (run linter after each deletion)

After each deletion: run the test suite. A failing test reveals a dependency that was missed in §2.

---

## 4. Test migration protocol

Sequence matters. Do not delete old paths until tests are migrated.

1. Identify all test imports and `mock.patch` strings pointing at pre-refactor locations
2. Move test imports to canonical owners — `from canonical.module import Symbol`, not `from legacy.facade import Symbol`
3. Replace implementation-coupled tests (patching `module._private`) with behaviour tests asserting against the canonical public surface
4. Keep tests that prove user-facing behaviour; delete only tests that prove internal coupling
5. After migration: run full test suite with canonical imports only; confirm green
6. Only then delete old paths

**Never delete a test simply to reduce count.** Only delete after a replacement test proves the same behaviour.

---

## 5. Guard test templates

Add after deletion. These tests prevent old coupling from returning.

### Python — block private imports from retired facade

```python
def test_no_private_imports_from_legacy_facade():
    import ast
    import pathlib
    for f in pathlib.Path("src/").rglob("*.py"):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "legacy.facade":
                    private = [a.name for a in node.names if a.name.startswith("_")]
                    assert not private, (
                        f"Private import from retired facade in {f}: {private}"
                    )
```

### Python — block patching deprecated private paths

```python
def test_no_patches_on_retired_private_path():
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", r"mock\.patch.*legacy_module\._", "tests/"],
        capture_output=True, text=True,
    )
    assert not result.stdout, (
        f"Patches on retired private path found:\n{result.stdout}"
    )
```

### Python — block new local definitions of canonical constants

```python
def test_no_local_redefinition_of_canonical_status():
    import ast
    import pathlib
    canonical_names = {"OrderStatus", "PaymentState"}  # update per project
    for f in pathlib.Path("src/").rglob("*.py"):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in canonical_names:
                assert "canonical/module.py" in str(f), (
                    f"Local redefinition of canonical type {node.name} in {f}"
                )
```

**Adapt module paths and canonical names per project.** These templates are starting points; the pattern is the constraint, not the literal strings.

---

## 6. Decision rules

- Do not add a new abstraction unless it retires an existing path
- Do not count behaviour as centralized while old callers still use the old source
- Do not preserve private APIs only because tests imported them
- Keep compatibility only when explicitly public, documented, or operationally necessary
- Accept that the best refactor removes more than it adds
- A "temporary" adapter with no removal condition is a permanent adapter

---

## 7. Verification gate

Before Phase 5, answer all three:

1. **What old path was deleted?** Name the specific module, symbol, or alias removed.
2. **What old import or patch target is now impossible?** State what previously-valid code now fails.
3. **Is there still more than one source of truth?** If yes, the retirement plan is incomplete.

No concrete answer to any of these → plan is incomplete. Do not proceed to Phase 5.

---

## 8. Deletion confidence levels

Classify before acting. Do not delete without High confidence.

### High — delete

No consumers, no framework-driven usage, no public-contract role.

Examples: unused private function with no references; unused local variable; dead branch that cannot execute; file with no imports and no framework entry-point role; test helper with no inbound imports; dependency absent from all imports, scripts, config, and generated tooling.

### Medium — investigate further

Uncertainty remains after first-pass search. Run the §2 evidence-sources checklist fully before deciding.

Examples: exported utilities; barrel/index exports; route-like files; configuration-adjacent files; code referenced only by string names; code used only in tests; feature-flagged code; framework-specific file conventions; types possibly consumed externally.

### Low — preserve and document

Usage cannot be safely disproven. Document the uncertainty and do not force deletion.

Examples: public package exports; migration files; generated files; plugin hook registrations; dynamic registry entries; security guards; payment and billing logic; authentication and authorization checks; compliance-required error-handling fallbacks; backward-compatibility code with unclear external consumers.

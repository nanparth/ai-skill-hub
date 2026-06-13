#!/usr/bin/env python3
"""Verify a merged note's automatable properties.

Runs 10 deterministic assertions against a merge output given its source files
and expected values. Returns 0 on all-pass, 1 on any failure with diagnostics.

Usage:
  python verify_merge.py \\
    --output path/to/merged.md \\
    --sources path/to/a.md path/to/b.md \\
    [--expected-tags "a,b,c,d"] \\
    [--expected-created-at "2025-01-15T08:00:00.000000-05:00"] \\
    [--expected-related "W,X,Y,Z"] \\
    [--source-hashes-before a.md=sha256 b.md=sha256] \\
    [--case-label "case_7_1"]

Assertions (all deterministic; organic coherence is NOT checked here):
  1. Output file exists
  2. Source files untouched (existence + hash match if hashes provided)
  3. Frontmatter present with required fields
  4. Tag union correct (if --expected-tags given)
  5. Date reconciliation (if --expected-created-at given)
  6. Related dedup (if --expected-related given)
  7. No source-tagged markers in output body
  8. No raw H1 concatenation of source titles
  9. Frontmatter quoting correct (double-quoted scalars; quoted tag items)
 10. Shadow tag scan (no bare #WORD outside frontmatter, code, backticks)

Exit codes: 0 = all pass, 1 = one or more failures.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


# ─── Frontmatter extraction ──────────────────────────────────────────────────


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def extract_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter into a dict. Minimal parser for our contract:
    scalar string fields (title, created at, summary) and a list-of-strings
    field (tags). Not a full YAML parser; assumes vault convention."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    fm: dict = {}
    current_list_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                continue
            value = line[4:].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            fm.setdefault(current_list_key, []).append(value)
            continue
        m = re.match(r"^([A-Za-z0-9 _-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        if val == "":
            current_list_key = key
            fm[key] = []
        else:
            current_list_key = None
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            fm[key] = val
    return fm


def frontmatter_raw(text: str) -> str:
    """Return raw frontmatter block (for quoting checks)."""
    match = FRONTMATTER_RE.match(text)
    return match.group(1) if match else ""


def body_without_frontmatter(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    return text[match.end():] if match else text


# ─── Hash helpers ────────────────────────────────────────────────────────────


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ─── Assertions ──────────────────────────────────────────────────────────────


class AssertionResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail

    def __str__(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        out = f"  [{mark}] {self.name}"
        if self.detail:
            out += f" — {self.detail}"
        return out


def assert_output_exists(output: Path) -> AssertionResult:
    if output.exists() and output.is_file():
        return AssertionResult("1. output file exists", True)
    return AssertionResult(
        "1. output file exists", False, f"not found at {output}"
    )


def assert_sources_untouched(
    sources: list[Path], hashes_before: dict[str, str]
) -> AssertionResult:
    missing = [s for s in sources if not s.exists()]
    if missing:
        return AssertionResult(
            "2. source files untouched",
            False,
            f"missing sources: {[str(m) for m in missing]}",
        )
    if not hashes_before:
        return AssertionResult(
            "2. source files untouched",
            True,
            "existence only (no pre-merge hashes provided)",
        )
    mismatches = []
    for src in sources:
        expected = hashes_before.get(str(src)) or hashes_before.get(src.name)
        if expected is None:
            continue
        actual = file_sha256(src)
        if actual != expected:
            mismatches.append(f"{src.name}: expected {expected[:12]}, got {actual[:12]}")
    if mismatches:
        return AssertionResult(
            "2. source files untouched",
            False,
            f"hash mismatch: {mismatches}",
        )
    return AssertionResult("2. source files untouched", True)


def assert_frontmatter_present(fm: dict) -> AssertionResult:
    required = ["title", "created at", "tags", "summary"]
    missing = [k for k in required if k not in fm or (fm[k] == [] if k == "tags" else not fm[k])]
    if missing:
        return AssertionResult(
            "3. frontmatter present",
            False,
            f"missing required fields: {missing}",
        )
    return AssertionResult("3. frontmatter present", True)


def assert_tag_union(fm: dict, expected_tags: list[str] | None) -> AssertionResult:
    if expected_tags is None:
        return AssertionResult("4. tag union", True, "skipped (no --expected-tags)")
    got = fm.get("tags", [])
    expected_sorted = sorted(expected_tags)
    got_sorted = sorted(got)
    if got_sorted != expected_sorted:
        return AssertionResult(
            "4. tag union",
            False,
            f"expected {expected_sorted}, got {got_sorted}",
        )
    if got != expected_sorted:
        return AssertionResult(
            "4. tag union",
            False,
            f"tags not alphabetically ordered: got {got}, expected {expected_sorted}",
        )
    if len(set(got)) != len(got):
        return AssertionResult(
            "4. tag union",
            False,
            f"duplicates in tags: {got}",
        )
    return AssertionResult("4. tag union", True)


def assert_created_at(fm: dict, expected: str | None) -> AssertionResult:
    if expected is None:
        return AssertionResult("5. date reconciliation", True, "skipped (no --expected-created-at)")
    got = fm.get("created at", "")
    if got != expected:
        return AssertionResult(
            "5. date reconciliation",
            False,
            f"expected {expected}, got {got}",
        )
    return AssertionResult("5. date reconciliation", True)


def assert_related_dedup(
    body: str, expected_targets: list[str] | None
) -> AssertionResult:
    related_match = re.search(
        r"^##\s+Related\s*$(.*?)(^##\s|\Z)", body, re.MULTILINE | re.DOTALL
    )
    if not related_match:
        if expected_targets is None:
            return AssertionResult("6. Related dedup", True, "no Related section (not required)")
        return AssertionResult(
            "6. Related dedup",
            False,
            "expected Related section not found",
        )
    related_block = related_match.group(1)
    wikilinks = re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", related_block)
    wikilinks = [w.strip() for w in wikilinks]
    if len(set(wikilinks)) != len(wikilinks):
        dupes = [w for w in wikilinks if wikilinks.count(w) > 1]
        return AssertionResult(
            "6. Related dedup",
            False,
            f"duplicate wikilinks: {sorted(set(dupes))}",
        )
    if expected_targets is not None:
        got_sorted = sorted(wikilinks)
        exp_sorted = sorted(expected_targets)
        if got_sorted != exp_sorted:
            return AssertionResult(
                "6. Related dedup",
                False,
                f"expected targets {exp_sorted}, got {got_sorted}",
            )
    return AssertionResult("6. Related dedup", True)


SOURCE_TAGGED_PATTERNS = [
    re.compile(r"(?i)from source [ab]\b"),
    re.compile(r"(?i)\bsource [ab]:\s"),
    re.compile(r"(?i)borrowed from"),
    re.compile(r"(?i)originally in\s+\w+\.md"),
    re.compile(r"(?i)\(from\s+[\w-]+\.md\)"),
    re.compile(r"(?i)section borrowed"),
]


def assert_no_source_tagged_markers(body: str) -> AssertionResult:
    hits = []
    for pat in SOURCE_TAGGED_PATTERNS:
        for m in pat.finditer(body):
            hits.append(f"'{m.group(0)}'")
    if hits:
        return AssertionResult(
            "7. no source-tagged markers",
            False,
            f"found: {hits[:5]}" + (f" (+{len(hits)-5} more)" if len(hits) > 5 else ""),
        )
    return AssertionResult("7. no source-tagged markers", True)


def extract_h1(text: str) -> str | None:
    body = body_without_frontmatter(text)
    for line in body.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return None


def assert_no_raw_h1_concatenation(
    body: str, sources: list[Path]
) -> AssertionResult:
    source_h1s = []
    for s in sources:
        if not s.exists():
            continue
        h1 = extract_h1(s.read_text(encoding="utf-8"))
        if h1:
            source_h1s.append(h1)
    # If 2+ source H1s appear verbatim in the body, that's concatenation.
    present = [h1 for h1 in source_h1s if h1 in body]
    if len(present) >= 2:
        return AssertionResult(
            "8. no raw H1 concatenation",
            False,
            f"multiple source H1 titles appear verbatim in output: {present}",
        )
    return AssertionResult("8. no raw H1 concatenation", True)


def assert_frontmatter_quoting(fm_raw: str) -> AssertionResult:
    if not fm_raw:
        return AssertionResult("9. frontmatter quoting", False, "no frontmatter block found")
    issues = []
    for line in fm_raw.splitlines():
        if re.match(r"^  - ", line):
            value = line[4:].strip()
            if not (value.startswith('"') and value.endswith('"')):
                issues.append(f"tag item not double-quoted: {line.strip()}")
            continue
        m = re.match(r"^([A-Za-z0-9 _-]+):\s*(.+)$", line)
        if not m:
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        if key == "tags" and val == "":
            continue
        if val == "":
            continue
        if not (val.startswith('"') and val.endswith('"')):
            issues.append(f"scalar '{key}' not double-quoted: {val}")
    if issues:
        return AssertionResult(
            "9. frontmatter quoting",
            False,
            f"{issues[:3]}" + (f" (+{len(issues)-3} more)" if len(issues) > 3 else ""),
        )
    return AssertionResult("9. frontmatter quoting", True)


def assert_no_shadow_tags(text: str) -> AssertionResult:
    # Strip frontmatter, fenced code blocks, and inline backticks.
    body = body_without_frontmatter(text)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"`[^`]*`", "", body)
    # Find bare #WORD tokens (Obsidian tag pattern). Exclude headings (#, ##, etc.).
    shadows = []
    for m in re.finditer(r"(?<![#\w])#([A-Za-z][A-Za-z0-9_/-]*)", body):
        # Exclude valid-looking tag words? We conservatively flag all bare #WORD
        # in body; the workflow's rule is to wrap technical tokens in backticks.
        shadows.append(m.group(0))
    # Remove headings that start a line (they begin with # followed by space).
    shadows = [s for s in shadows if not re.match(r"^#{1,6}$", s.rstrip())]
    if shadows:
        return AssertionResult(
            "10. no shadow tags",
            False,
            f"bare #WORD tokens in body: {sorted(set(shadows))[:5]}",
        )
    return AssertionResult("10. no shadow tags", True)


# ─── Main ────────────────────────────────────────────────────────────────────


def parse_csv(s: str | None) -> list[str] | None:
    if s is None:
        return None
    return [item.strip() for item in s.split(",") if item.strip()]


def parse_hash_pairs(pairs: list[str] | None) -> dict[str, str]:
    if not pairs:
        return {}
    out: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            continue
        path, h = p.split("=", 1)
        out[path.strip()] = h.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True, type=Path, help="Path to merged output file")
    ap.add_argument("--sources", required=True, nargs="+", type=Path, help="Source file paths")
    ap.add_argument("--expected-tags", help="Comma-separated expected tag set")
    ap.add_argument("--expected-created-at", help="Expected created at value")
    ap.add_argument("--expected-related", help="Comma-separated expected Related wikilink targets")
    ap.add_argument("--source-hashes-before", nargs="*", help="Pre-merge hashes: path=sha256")
    ap.add_argument("--case-label", default="", help="Case label for output")
    args = ap.parse_args()

    label = f" [{args.case_label}]" if args.case_label else ""
    print(f"verify_merge{label}: output={args.output}")

    results: list[AssertionResult] = []

    results.append(assert_output_exists(args.output))
    hashes_before = parse_hash_pairs(args.source_hashes_before)
    results.append(assert_sources_untouched(args.sources, hashes_before))

    if args.output.exists():
        text = args.output.read_text(encoding="utf-8")
        fm = extract_frontmatter(text)
        fm_raw = frontmatter_raw(text)
        body = body_without_frontmatter(text)

        results.append(assert_frontmatter_present(fm))
        results.append(assert_tag_union(fm, parse_csv(args.expected_tags)))
        results.append(assert_created_at(fm, args.expected_created_at))
        results.append(assert_related_dedup(body, parse_csv(args.expected_related)))
        results.append(assert_no_source_tagged_markers(body))
        results.append(assert_no_raw_h1_concatenation(body, args.sources))
        results.append(assert_frontmatter_quoting(fm_raw))
        results.append(assert_no_shadow_tags(text))
    else:
        # Output missing: remaining assertions cannot run meaningfully.
        for name in [
            "3. frontmatter present",
            "4. tag union",
            "5. date reconciliation",
            "6. Related dedup",
            "7. no source-tagged markers",
            "8. no raw H1 concatenation",
            "9. frontmatter quoting",
            "10. no shadow tags",
        ]:
            results.append(AssertionResult(name, False, "output missing, cannot evaluate"))

    for r in results:
        print(r)

    failed = [r for r in results if not r.passed]
    print()
    if failed:
        print(f"RESULT: FAIL ({len(failed)}/{len(results)} assertions failed)")
        return 1
    print(f"RESULT: PASS ({len(results)}/{len(results)} assertions passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

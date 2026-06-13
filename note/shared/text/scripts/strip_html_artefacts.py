#!/usr/bin/env python3
"""Strip HTML collapsible-block artefacts from vault markdown files.

Some authoring pipelines (notably LLM-drafted notes) wrap diagrams or auxiliary
content in collapsible `<details>` blocks. For a clean Obsidian markdown
render, these wrappers are removed while preserving the enclosed body.

Artefacts targeted
------------------
    <details>            (line by itself, any indent)
    </details>           (line by itself, any indent)
    <summary>...</summary>  (single-line summary)

Any line whose stripped form is exactly ``<details>`` or ``</details>`` is
removed. Any line matching ``<summary>...</summary>`` on a single line is
removed. Body content between the tags is preserved verbatim; runs of 3 or
more consecutive blank lines created by tag removal are collapsed to 2.

Usage
-----
    strip_html_artefacts.py <path> [--fix | --check | --dry-run]

    --fix       (default) Overwrite the file in place; print a JSON summary.
    --check     Read-only. Exit 0 if clean, exit 2 if artefacts found.
    --dry-run   Print what would change without writing; exit 2 if artefacts found.

Exit codes
----------
    0   File is clean, or --fix / --dry-run completed without error.
    1   Fatal error (file not found, encoding error, etc.).
    2   --check or --dry-run found artefacts (caller should act).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Matchers
# ---------------------------------------------------------------------------
_SUMMARY_LINE_RE = re.compile(r"^\s*<summary>.*</summary>\s*$")
_BLANK_COLLAPSE_RE = re.compile(r"\n{3,}")


# ---------------------------------------------------------------------------
# Core stripper
# ---------------------------------------------------------------------------

class _Stats:
    def __init__(self) -> None:
        self.details_tags_removed: int = 0
        self.summary_lines_removed: int = 0
        self.details_blocks: int = 0

    def total(self) -> int:
        return self.details_tags_removed + self.summary_lines_removed


def strip_html_artefacts(content: str) -> tuple[str, _Stats]:
    """Return (cleaned_content, stats)."""
    stats = _Stats()

    # Pre-strip tally of open/close tags to compute matched-pair count
    open_count = 0
    close_count = 0

    kept: list[str] = []
    for line in content.splitlines(keepends=True):
        stripped = line.strip()
        if stripped == "<details>":
            open_count += 1
            stats.details_tags_removed += 1
            continue
        if stripped == "</details>":
            close_count += 1
            stats.details_tags_removed += 1
            continue
        if _SUMMARY_LINE_RE.match(line.rstrip("\n")):
            stats.summary_lines_removed += 1
            continue
        kept.append(line)

    stats.details_blocks = min(open_count, close_count)

    joined = "".join(kept)
    # Collapse 3+ consecutive newlines to exactly 2 (i.e. max one blank line
    # between content). "\n\n\n" => "\n\n".
    joined = _BLANK_COLLAPSE_RE.sub("\n\n", joined)

    return joined, stats


def has_html_artefacts(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "<details>" or stripped == "</details>":
            return True
        if _SUMMARY_LINE_RE.match(line):
            return True
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Strip <details>/<summary> HTML artefacts from a markdown file."
    )
    parser.add_argument("path", help="Path to the markdown file")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--fix",
        action="store_true",
        default=True,
        help="(default) Overwrite file in place and print JSON summary",
    )
    mode_group.add_argument(
        "--check",
        action="store_true",
        help="Read-only. Exit 0 if clean, exit 2 if artefacts found.",
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing. Exit 2 if artefacts found.",
    )
    args = parser.parse_args()

    if args.check:
        mode = "check"
    elif args.dry_run:
        mode = "dry-run"
    else:
        mode = "fix"

    path = Path(args.path)
    if not path.exists():
        print(json.dumps({"error": f"File not found: {args.path}"}), file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    # --check fast path: scan only
    if mode == "check":
        if has_html_artefacts(content):
            _, stats = strip_html_artefacts(content)
            print(json.dumps({
                "mode": "check",
                "path": str(path),
                "total_artefacts": stats.total(),
                "details_tags_removed": stats.details_tags_removed,
                "summary_lines_removed": stats.summary_lines_removed,
                "details_blocks": stats.details_blocks,
                "status": "dirty",
            }))
            return 2
        print(json.dumps({
            "mode": "check",
            "path": str(path),
            "total_artefacts": 0,
            "details_tags_removed": 0,
            "summary_lines_removed": 0,
            "details_blocks": 0,
            "status": "clean",
        }))
        return 0

    # --fix or --dry-run: run the stripper
    cleaned, stats = strip_html_artefacts(content)

    summary = {
        "mode": mode,
        "path": str(path),
        "total_artefacts": stats.total(),
        "details_tags_removed": stats.details_tags_removed,
        "summary_lines_removed": stats.summary_lines_removed,
        "details_blocks": stats.details_blocks,
        "status": "clean" if stats.total() == 0 else "fixed",
    }

    if mode == "dry-run":
        print(json.dumps(summary, indent=2))
        return 2 if stats.total() > 0 else 0

    # --fix: write only if content changed
    if cleaned != content:
        path.write_text(cleaned, encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Strip ChatGPT PUA-wrapped citation artifacts from vault markdown files.

ChatGPT's web-search tool injects structured markup using Unicode Private Use
Area codepoints as delimiters:

    U+E200  open marker       (precedes token type keyword)
    U+E202  separator         (separates token fields or concatenated cites)
    U+E201  close marker      (follows last field)

Known token families
--------------------
cite    \ue200cite\ue202turnXviewY[\ue202turnXviewY...]\ue201
            -> stripped entirely (inline citation with no external URL)
entity  \ue200entity\ue202["type","name","description"]\ue201
            -> replaced with the name field (second quoted value)
unknown any other \ue200...\ue201 block
            -> stripped entirely, logged to stderr

Usage
-----
    strip_pua_artifacts.py <path> [--fix | --check | --dry-run]

    --fix       (default) Overwrite the file in place; print a JSON summary.
    --check     Read-only. Exit 0 if clean, exit 2 if artifacts found.
    --dry-run   Print what would change without writing; exit 2 if artifacts found.

Exit codes
----------
    0   File is clean, or --fix / --dry-run completed without error.
    1   Fatal error (file not found, encoding error, etc.).
    2   --check or --dry-run found artifacts (caller should act).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# PUA codepoints
# ---------------------------------------------------------------------------
OPEN  = "\ue200"   # precedes token type keyword
SEP   = "\ue202"   # field separator / cite concatenator
CLOSE = "\ue201"   # end of token

# Matches one full PUA-wrapped token (non-greedy between OPEN and CLOSE)
_TOKEN_RE = re.compile(
    rf"{re.escape(OPEN)}(.*?){re.escape(CLOSE)}",
    re.DOTALL,
)

# Matches a cite token body (everything between OPEN and CLOSE for cite tokens)
# Body starts with "cite" followed by SEP-separated turn references
_CITE_BODY_RE = re.compile(
    rf"^cite{re.escape(SEP)}turn\w+(?:{re.escape(SEP)}turn\w+)*$"
)

# Matches an entity token body
# Body: entity\ue202["type","name","description"]
_ENTITY_BODY_RE = re.compile(
    rf'^entity{re.escape(SEP)}\["[^"]*",\s*"([^"]*)",\s*"[^"]*"\]$'
)


# ---------------------------------------------------------------------------
# Core replacer
# ---------------------------------------------------------------------------

class _Stats:
    def __init__(self) -> None:
        self.cite: int = 0
        self.entity: int = 0
        self.unknown: int = 0
        self.unknown_samples: list[str] = []

    def total(self) -> int:
        return self.cite + self.entity + self.unknown


def _replace_token(match: re.Match, stats: _Stats) -> str:  # noqa: D401
    body = match.group(1)

    if _CITE_BODY_RE.match(body):
        stats.cite += 1
        return ""

    m = _ENTITY_BODY_RE.match(body)
    if m:
        stats.entity += 1
        return m.group(1)

    # Unknown PUA token
    stats.unknown += 1
    if len(stats.unknown_samples) < 5:
        stats.unknown_samples.append(repr(match.group(0)))
    return ""


def strip_pua(content: str) -> tuple[str, _Stats]:
    """Return (cleaned_content, stats)."""
    stats = _Stats()
    cleaned = _TOKEN_RE.sub(lambda m: _replace_token(m, stats), content)

    # Mop up any residual bare PUA chars (e.g. unmatched delimiters)
    for cp in (OPEN, SEP, CLOSE):
        count = cleaned.count(cp)
        if count:
            stats.unknown += count
            cleaned = cleaned.replace(cp, "")

    # Normalise spacing artifacts left by removed inline tokens:
    # collapse 2+ spaces between non-whitespace characters (mid-line only).
    # The (?<=\S) / (?=\S) guards prevent collapsing leading indent or
    # intentional trailing two-space hard line-breaks (which are at line end,
    # not followed by another non-space char on the same line).
    cleaned = re.sub(r"(?m)(?<=\S)[ ]{2,}(?=\S)", " ", cleaned)
    # Drop lines that became blank (only whitespace) due to full-line cite removal
    cleaned = re.sub(r"(?m)^[ \t]+$", "", cleaned)

    return cleaned, stats


# ---------------------------------------------------------------------------
# Residual check (post-fix validation)
# ---------------------------------------------------------------------------

def has_pua(content: str) -> bool:
    return any(cp in content for cp in (OPEN, SEP, CLOSE))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Strip ChatGPT PUA-wrapped citation artifacts from a markdown file."
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
        help="Read-only. Exit 0 if clean, exit 2 if artifacts found.",
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing. Exit 2 if artifacts found.",
    )
    args = parser.parse_args()

    # Resolve mode (argparse mutual exclusion means at most one is True)
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
        if has_pua(content):
            _, stats = strip_pua(content)
            print(json.dumps({
                "status": "dirty",
                "cite": stats.cite,
                "entity": stats.entity,
                "unknown": stats.unknown,
                "total": stats.total(),
            }))
            return 2
        print(json.dumps({"status": "clean", "total": 0}))
        return 0

    # --fix or --dry-run: run the replacer
    cleaned, stats = strip_pua(content)

    summary = {
        "mode": mode,
        "path": str(path),
        "cite_removed": stats.cite,
        "entity_replaced": stats.entity,
        "unknown_stripped": stats.unknown,
        "total_artifacts": stats.total(),
        "status": "clean" if stats.total() == 0 else "fixed",
    }

    if stats.unknown_samples:
        summary["unknown_samples"] = stats.unknown_samples
        for sample in stats.unknown_samples:
            print(f"WARNING: unknown PUA token stripped: {sample}", file=sys.stderr)

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

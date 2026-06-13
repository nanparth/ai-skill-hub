#!/usr/bin/env python3
"""Detect and optionally remove dead ![[...image]] wikilink embeds from Obsidian markdown files.

An embed is "dead" when the referenced image/media file does not exist on disk.
Only embeds whose bracketed content ends with a recognised image/media extension
are checked; bare wikilinks such as ![[note-name]] are left untouched.

Usage
-----
    check_dead_embeds.py <path> [--check | --fix] [--root <notes-root>]

    --check   (default) Read-only. Exit 0 if no dead embeds; exit 2 if any found.
    --fix     Remove lines that contain dead embed patterns, collapse excess blank
              lines, and rewrite the file. Exit 0 on success.
    --root    Notes root for embed resolution. Default: walk up from the target
              file looking for a `.obsidian/` marker; if none found, use the
              target file's own directory.

Exit codes
----------
    0   Clean (no dead embeds) or --fix succeeded.
    1   Fatal error (file not found, read/write error).
    2   Dead embeds found (--check mode only).

JSON output (stdout)
--------------------
    {
        "total_dead":    <int>,   # dead embeds found
        "paths":         [<str>], # root-relative embed paths that are dead
        "lines_removed": <int>    # lines removed (0 in --check mode)
    }
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def resolve_notes_root(target: Path, explicit_root: str | None) -> Path:
    """Resolve the notes root for embed resolution.

    Priority: explicit --root arg; nearest ancestor of the target containing
    a `.obsidian/` directory; the target file's own directory.
    """
    if explicit_root:
        return Path(explicit_root).resolve()
    p = target.resolve().parent
    for _ in range(20):
        if (p / ".obsidian").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    return target.resolve().parent


# Matches ![[filename.ext]] or ![[filename.ext|alias]], case-insensitive on ext.
# Also matches when preceded by blockquote markers such as "> " or ">> ".
_EMBED_RE = re.compile(
    r"!\[\[([^\]]+\.(?:jpg|jpeg|png|gif|svg|webp|mp4|mp3|ogg|pdf))(?:\|[^\]]*)?\]\]",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _find_dead_embeds(content: str, notes_root: Path) -> list[tuple[int, str]]:
    """Return list of (line_index, embed_path) for each dead embed in content."""
    dead: list[tuple[int, str]] = []
    for line_idx, line in enumerate(content.splitlines()):
        for match in _EMBED_RE.finditer(line):
            embed_path = match.group(1)
            # Strip leading slash if present
            embed_path_clean = embed_path.lstrip("/")
            full_path = notes_root / embed_path_clean
            if full_path.exists():
                continue
            # Root-wide filename fallback: Obsidian resolves wikilinks by filename
            # across the entire vault, not by literal path. If the file exists anywhere
            # under notes_root with the same basename, the embed is live.
            filename = Path(embed_path_clean).name
            if any(notes_root.rglob(filename)):
                continue
            dead.append((line_idx, embed_path_clean))
    return dead


def _remove_dead_lines(lines: list[str], dead_line_indices: set[int]) -> list[str]:
    """Remove lines at the given indices."""
    return [line for idx, line in enumerate(lines) if idx not in dead_line_indices]


def _collapse_blank_lines(content: str) -> str:
    """Collapse runs of 3+ consecutive newlines down to exactly 2 newlines."""
    return re.sub(r"\n{3,}", "\n\n", content)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect or remove dead ![[image]] wikilink embeds from a markdown file."
    )
    parser.add_argument("path", help="Path to the markdown file (absolute, or relative to cwd)")
    parser.add_argument("--root", help="Notes root for embed resolution (optional)")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--check",
        action="store_true",
        help="(default) Read-only. Exit 0 if clean, exit 2 if dead embeds found.",
    )
    mode_group.add_argument(
        "--fix",
        action="store_true",
        help="Remove dead embed lines, collapse blank lines, rewrite file.",
    )
    args = parser.parse_args()

    # Determine mode
    mode = "fix" if args.fix else "check"

    # Resolve file path
    target = Path(args.path)
    if not target.is_absolute():
        target = Path.cwd() / target

    if not target.exists():
        print(json.dumps({"error": f"File not found: {args.path}"}), file=sys.stderr)
        return 1

    notes_root = resolve_notes_root(target, args.root)

    try:
        content = target.read_text(encoding="utf-8")
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    dead = _find_dead_embeds(content, notes_root)

    dead_paths = [ep for _, ep in dead]
    dead_line_indices = {li for li, _ in dead}

    # --check mode: report only
    if mode == "check":
        payload = {
            "total_dead": len(dead),
            "paths": dead_paths,
            "lines_removed": 0,
        }
        print(json.dumps(payload))
        return 2 if dead else 0

    # --fix mode: remove dead lines, collapse blanks, rewrite
    lines = content.splitlines(keepends=True)
    kept_lines = _remove_dead_lines(lines, dead_line_indices)
    new_content = "".join(kept_lines)
    new_content = _collapse_blank_lines(new_content)

    if new_content != content:
        try:
            target.write_text(new_content, encoding="utf-8")
        except Exception as exc:
            print(json.dumps({"error": f"Write failed: {exc}"}), file=sys.stderr)
            return 1

    payload = {
        "total_dead": len(dead),
        "paths": dead_paths,
        "lines_removed": len(dead_line_indices),
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Markdown adapter: structure-preserving parse of Markdown into NormalizedDoc."""
from __future__ import annotations
import re

from . import NormalizedDoc, DocBlock, DocTable

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_ORDERED_RE = re.compile(r"^\s*(\d+\.)\s+(.*)$")
_UNORDERED_RE = re.compile(r"^\s*([-*])\s+(.*)$")


def _split_row(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{1,}:?", c) for c in cells if c != "")


def parse(src: str, **opts) -> NormalizedDoc:
    with open(src, "r", encoding="utf-8") as fh:
        return parse_text(fh.read(), source_format="md")


def parse_text(text: str, *, source_format: str = "md") -> NormalizedDoc:
    lines = text.splitlines()
    doc = NormalizedDoc(source_format=source_format)
    heading_stack: list[tuple[int, str]] = []
    heading_counter = 0
    sub_counter = 0
    idx = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("|"):
            table_lines = []
            while i < n and lines[i].lstrip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            if table_lines:
                headers = [h for h in _split_row(table_lines[0]) if h != ""]
                data_rows = []
                for tl in table_lines[1:]:
                    if _is_separator_row(tl):
                        continue
                    data_rows.append(_split_row(tl))
                anchor = f"§{heading_counter}#t{len(doc.tables)}"
                doc.tables.append(DocTable(headers=headers, rows=data_rows, anchor=anchor, caption=_current_heading(heading_stack)))
            continue
        m = _HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            heading_counter += 1
            sub_counter = 0
            text_value = m.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, text_value))
            doc.blocks.append(
                DocBlock(
                    text=text_value,
                    block_type="heading",
                    idx=idx,
                    level=level,
                    anchor=f"§{heading_counter}",
                    parent_heading=_parent_heading(heading_stack),
                    heading_path=[h for _, h in heading_stack],
                )
            )
            idx += 1
            i += 1
            continue
        mm = _ORDERED_RE.match(line) or _UNORDERED_RE.match(line)
        if mm:
            sub_counter += 1
            doc.blocks.append(
                DocBlock(
                    text=mm.group(2).strip(),
                    block_type="list_item",
                    idx=idx,
                    anchor=f"§{heading_counter}#{sub_counter}",
                    parent_heading=_current_heading(heading_stack),
                    heading_path=[h for _, h in heading_stack],
                    list_ordinal=mm.group(1),
                )
            )
            idx += 1
            i += 1
            continue
        sub_counter += 1
        doc.blocks.append(
            DocBlock(
                text=line.strip(),
                block_type="paragraph",
                idx=idx,
                anchor=f"§{heading_counter}#{sub_counter}",
                parent_heading=_current_heading(heading_stack),
                heading_path=[h for _, h in heading_stack],
            )
        )
        idx += 1
        i += 1
    return doc


def _current_heading(stack: list[tuple[int, str]]) -> str | None:
    return stack[-1][1] if stack else None


def _parent_heading(stack: list[tuple[int, str]]) -> str | None:
    return stack[-2][1] if len(stack) > 1 else None

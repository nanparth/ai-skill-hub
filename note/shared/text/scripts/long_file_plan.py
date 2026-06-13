#!/usr/bin/env python3
"""Generate deterministic long-file planning metadata for markdown/text files."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import uuid
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*([`~]{3,})(.*)$")
HR_RE = re.compile(r"^\s{0,3}([*\-_])(?:\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^\s{0,3}(?:[-+*]|\d+\.)\s+")
TABLE_RULE_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?(?:\s*\|\s*:?-{2,}:?)*\s*\|?\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate long-file preflight metadata.")
    parser.add_argument("--file", help="Target file path.")
    parser.add_argument("--request-file", help="UTF-8 JSON request file path.")
    parser.add_argument("--output-file", help="Write JSON output to this file instead of stdout.")
    parser.add_argument("--threshold", type=int, default=500, help="Long-mode threshold (strict >).")
    parser.add_argument("--preview-lines", type=int, default=200, help="Preview window line count.")
    parser.add_argument("--chunk-lines", type=int, default=250, help="Target chunk size.")
    parser.add_argument(
        "--chunker",
        choices=["semantic-line", "legacy"],
        default="semantic-line",
        help="Chunking engine.",
    )
    parser.add_argument("--search-back-lines", type=int, default=80, help="Backward scoring window.")
    parser.add_argument("--search-forward-lines", type=int, default=25, help="Forward scoring window.")
    parser.add_argument("--min-chunk-lines", type=int, default=120, help="Minimum preferred chunk size.")
    parser.add_argument(
        "--max-overshoot-lines",
        type=int,
        default=60,
        help="Soft overshoot budget for protected blocks.",
    )
    parser.add_argument("--tail-merge-lines", type=int, default=80, help="Tail merge threshold.")
    parser.add_argument("--decay", type=float, default=0.7, help="Distance decay factor.")
    parser.add_argument("--distance-power", type=float, default=2.0, help="Distance decay exponent.")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format.")
    return parser.parse_args()


def merge_request_args(args: argparse.Namespace) -> argparse.Namespace:
    merged = dict(vars(args))
    request_file = merged.get("request_file")
    if request_file:
        payload = json.loads(Path(request_file).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request-file payload must be a JSON object")
        field_map = {
            "target_path": "file",
            "file": "file",
            "threshold": "threshold",
            "preview_lines": "preview_lines",
            "preview-lines": "preview_lines",
            "chunk_lines": "chunk_lines",
            "chunk-lines": "chunk_lines",
            "chunker": "chunker",
            "search_back_lines": "search_back_lines",
            "search-back-lines": "search_back_lines",
            "search_forward_lines": "search_forward_lines",
            "search-forward-lines": "search_forward_lines",
            "min_chunk_lines": "min_chunk_lines",
            "min-chunk-lines": "min_chunk_lines",
            "max_overshoot_lines": "max_overshoot_lines",
            "max-overshoot-lines": "max_overshoot_lines",
            "tail_merge_lines": "tail_merge_lines",
            "tail-merge-lines": "tail_merge_lines",
            "decay": "decay",
            "distance_power": "distance_power",
            "distance-power": "distance_power",
            "format": "format",
        }
        for key, value in payload.items():
            mapped = field_map.get(key)
            if mapped:
                merged[mapped] = value

    if not merged.get("file"):
        raise ValueError("either --file or --request-file with target_path/file is required")

    return argparse.Namespace(**merged)


def load_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0].lstrip("\ufeff")
    return lines


def normalize_heading_text(text: str) -> str:
    cleaned = re.sub(r"\s+#*$", "", text).strip()
    return cleaned


def extract_headings(lines: list[str]) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for idx, raw in enumerate(lines, start=1):
        match = HEADING_RE.match(raw)
        if not match:
            continue
        headings.append(
            {
                "level": len(match.group(1)),
                "line": idx,
                "text": normalize_heading_text(match.group(2)),
            }
        )
    return headings


def choose_anchor_level(headings: list[dict[str, Any]]) -> int | None:
    levels = {item["level"] for item in headings}
    for candidate in (2, 1, 3, 4, 5, 6):
        if candidate in levels:
            return candidate
    return None


def make_windows(
    start: int,
    end: int,
    chunk_lines: int,
    anchor_heading: str | None,
    strategy: str = "line-window",
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    cursor = start
    while cursor <= end:
        chunk_end = min(end, cursor + chunk_lines - 1)
        windows.append(
            {
                "start_line": cursor,
                "end_line": chunk_end,
                "strategy": strategy,
                "anchor_heading": anchor_heading,
                "boundary_type": strategy,
                "boundary_line": chunk_end,
                "boundary_score": None,
                "boundary_distance": None,
                "boundary_note": "legacy-window",
            }
        )
        cursor = chunk_end + 1
    return windows


def split_segment(
    segment: dict[str, Any],
    all_headings: list[dict[str, Any]],
    chunk_lines: int,
) -> list[dict[str, Any]]:
    start = segment["start_line"]
    end = segment["end_line"]
    anchor_level = segment["anchor_level"]
    anchor_heading = segment["anchor_heading"]
    length = end - start + 1

    if length <= chunk_lines:
        return [
            {
                "start_line": start,
                "end_line": end,
                "strategy": "heading",
                "anchor_heading": anchor_heading,
                "boundary_type": "heading",
                "boundary_line": end,
                "boundary_score": None,
                "boundary_distance": None,
                "boundary_note": "legacy-heading",
            }
        ]

    subheads = [
        h
        for h in all_headings
        if start < h["line"] <= end and (anchor_level is None or h["level"] > anchor_level)
    ]
    if not subheads:
        return make_windows(start, end, chunk_lines, anchor_heading, "line-window")

    boundaries = [start] + [h["line"] for h in subheads]
    ranges: list[tuple[int, int, str | None]] = []
    for idx, range_start in enumerate(boundaries):
        range_end = end if idx == len(boundaries) - 1 else boundaries[idx + 1] - 1
        if range_start > range_end:
            continue
        heading_text = anchor_heading if idx == 0 else subheads[idx - 1]["text"]
        ranges.append((range_start, range_end, heading_text))

    chunks: list[dict[str, Any]] = []
    for range_start, range_end, heading_text in ranges:
        range_len = range_end - range_start + 1
        if range_len <= chunk_lines:
            chunks.append(
                {
                    "start_line": range_start,
                    "end_line": range_end,
                    "strategy": "heading",
                    "anchor_heading": heading_text,
                    "boundary_type": "heading",
                    "boundary_line": range_end,
                    "boundary_score": None,
                    "boundary_distance": None,
                    "boundary_note": "legacy-heading",
                }
            )
            continue
        chunks.extend(make_windows(range_start, range_end, chunk_lines, heading_text, "line-window"))
    return chunks


def build_segments(line_count: int, headings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if line_count == 0:
        return []
    if not headings:
        return [
            {
                "start_line": 1,
                "end_line": line_count,
                "anchor_heading": None,
                "anchor_level": None,
            }
        ]

    anchor_level = choose_anchor_level(headings)
    if anchor_level is None:
        return [
            {
                "start_line": 1,
                "end_line": line_count,
                "anchor_heading": None,
                "anchor_level": None,
            }
        ]

    anchors = [h for h in headings if h["level"] == anchor_level]
    if not anchors:
        anchors = headings

    segments: list[dict[str, Any]] = []
    if anchors[0]["line"] > 1:
        segments.append(
            {
                "start_line": 1,
                "end_line": anchors[0]["line"] - 1,
                "anchor_heading": "Preamble",
                "anchor_level": anchor_level,
            }
        )

    for idx, anchor in enumerate(anchors):
        start = anchor["line"]
        end = line_count if idx == len(anchors) - 1 else anchors[idx + 1]["line"] - 1
        segments.append(
            {
                "start_line": start,
                "end_line": end,
                "anchor_heading": anchor["text"],
                "anchor_level": anchor_level,
            }
        )
    return segments


def build_chunks_legacy(
    line_count: int, headings: list[dict[str, Any]], chunk_lines: int
) -> list[dict[str, Any]]:
    segments = build_segments(line_count, headings)
    all_chunks: list[dict[str, Any]] = []

    for segment in segments:
        all_chunks.extend(split_segment(segment, headings, chunk_lines))

    if not all_chunks and line_count > 0:
        all_chunks = make_windows(1, line_count, chunk_lines, None, "line-window")
    return all_chunks


def detect_frontmatter_end(lines: list[str]) -> int | None:
    if not lines:
        return None
    if lines[0].strip() != "---":
        return None
    for idx in range(2, len(lines) + 1):
        if lines[idx - 1].strip() == "---":
            return idx
    return None


def parse_fences(
    lines: list[str], frontmatter_end: int | None
) -> tuple[list[tuple[int, int]], set[int], set[int]]:
    spans: list[tuple[int, int]] = []
    fence_open_lines: set[int] = set()
    fence_close_lines: set[int] = set()
    in_code = False
    open_line = 0
    open_char = ""
    open_len = 0

    for idx, raw in enumerate(lines, start=1):
        if frontmatter_end and idx <= frontmatter_end:
            continue
        match = FENCE_RE.match(raw)
        if not match:
            continue
        token = match.group(1)
        char = token[0]
        length = len(token)

        if not in_code:
            in_code = True
            open_line = idx
            open_char = char
            open_len = length
            fence_open_lines.add(idx)
            continue

        if char == open_char and length >= open_len:
            spans.append((open_line, idx))
            fence_close_lines.add(idx)
            in_code = False
            open_line = 0
            open_char = ""
            open_len = 0

    if in_code and open_line:
        spans.append((open_line, len(lines)))
        fence_close_lines.add(len(lines))
    return spans, fence_open_lines, fence_close_lines


def build_code_line_map(line_count: int, spans: list[tuple[int, int]]) -> list[bool]:
    in_code = [False] * (line_count + 1)
    for open_line, close_line in spans:
        for ln in range(open_line, close_line + 1):
            in_code[ln] = True
    return in_code


def find_containing_span(line_no: int, spans: list[tuple[int, int]]) -> tuple[int, int] | None:
    for open_line, close_line in spans:
        if open_line <= line_no <= close_line:
            return (open_line, close_line)
    return None


def is_table_line(raw: str) -> bool:
    text = raw.strip()
    if "|" not in text:
        return False
    return bool(TABLE_RULE_RE.match(text) or "|" in text)


def list_continuation_line(raw: str) -> bool:
    return raw.startswith("  ") or raw.startswith("\t")


def build_heading_line_map(headings: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {h["line"]: h for h in headings}


def next_heading_at_or_after(headings: list[dict[str, Any]], line_no: int) -> dict[str, Any] | None:
    for item in headings:
        if item["line"] >= line_no:
            return item
    return None


def count_following_body_lines(lines: list[str], start_line: int, headings: list[dict[str, Any]]) -> int:
    next_heading = next_heading_at_or_after(headings, start_line + 1)
    end = (next_heading["line"] - 1) if next_heading else len(lines)
    body = 0
    for ln in range(start_line + 1, end + 1):
        if lines[ln - 1].strip():
            body += 1
    return body


def base_score_for_heading(level: int) -> int:
    mapping = {1: 100, 2: 90, 3: 80, 4: 70, 5: 60, 6: 50}
    return mapping.get(level, 50)


def build_candidates(
    lines: list[str],
    headings: list[dict[str, Any]],
    fence_open_lines: set[int],
    fence_close_lines: set[int],
    frontmatter_end: int | None,
    in_code: list[bool],
    start: int,
    line_count: int,
) -> dict[int, dict[str, Any]]:
    candidates: dict[int, dict[str, Any]] = {}
    heading_map = build_heading_line_map(headings)

    def add_candidate(end_line: int, kind: str, base: float, note: str = "") -> None:
        if end_line < start or end_line >= line_count:
            return
        if frontmatter_end and end_line < frontmatter_end and start <= frontmatter_end:
            return
        if in_code[end_line] and end_line not in fence_close_lines:
            return
        existing = candidates.get(end_line)
        candidate = {
            "end_line": end_line,
            "boundary_type": kind,
            "base_score": float(base),
            "boundary_note": note,
        }
        if not existing or candidate["base_score"] > existing["base_score"]:
            candidates[end_line] = candidate

    for line_no in range(start + 1, line_count + 1):
        raw = lines[line_no - 1]
        stripped = raw.strip()

        if line_no in heading_map:
            add_candidate(
                line_no - 1,
                f"h{heading_map[line_no]['level']}",
                base_score_for_heading(heading_map[line_no]["level"]),
                "before-heading",
            )

        if line_no in fence_open_lines:
            add_candidate(line_no - 1, "code_fence_open", 80, "before-code-fence")
        if line_no in fence_close_lines:
            add_candidate(line_no, "code_fence_boundary", 80, "after-code-fence")

        if HR_RE.match(raw):
            add_candidate(line_no, "hr", 60, "horizontal-rule")
        if stripped == "":
            add_candidate(line_no, "blank", 20, "blank-line")
        if LIST_RE.match(raw):
            add_candidate(line_no - 1, "list_start", 5, "before-list-item")

        add_candidate(line_no, "line_break", 1, "line-break")

    return candidates


def score_candidate(
    candidate: dict[str, Any],
    target: int,
    lines: list[str],
    headings: list[dict[str, Any]],
    search_back_lines: int,
    search_forward_lines: int,
    decay: float,
    distance_power: float,
) -> dict[str, Any]:
    end_line = candidate["end_line"]
    base = candidate["base_score"]
    distance = abs(target - end_line)
    direction = "backward" if end_line <= target else "forward"
    window = search_back_lines if direction == "backward" else search_forward_lines
    denom = float(max(1, window))
    decay_term = 1.0 - (pow(distance / denom, distance_power) * decay)
    score = base * decay_term

    penalties = 0.0
    bonuses = 0.0

    if direction == "forward":
        penalties += 8.0

    next_line = end_line + 1
    if next_line <= len(lines):
        heading_match = HEADING_RE.match(lines[next_line - 1])
        if heading_match:
            body_lines = count_following_body_lines(lines, next_line, headings)
            if body_lines < 3:
                penalties += 30.0

    if 1 <= end_line < len(lines):
        if is_table_line(lines[end_line - 1]) and is_table_line(lines[end_line]):
            penalties += 40.0

    if 1 <= end_line < len(lines):
        curr = lines[end_line - 1]
        nxt = lines[end_line]
        if (LIST_RE.match(curr) or list_continuation_line(curr)) and (
            LIST_RE.match(nxt) or list_continuation_line(nxt)
        ):
            penalties += 20.0

    final = score + bonuses - penalties
    scored = dict(candidate)
    scored["distance"] = distance
    scored["direction"] = direction
    scored["penalties"] = penalties
    scored["bonuses"] = bonuses
    scored["final_score"] = final
    return scored


def best_candidate(
    candidates: dict[int, dict[str, Any]],
    start: int,
    target: int,
    line_count: int,
    min_chunk_lines: int,
    search_back_lines: int,
    search_forward_lines: int,
    lines: list[str],
    headings: list[dict[str, Any]],
    decay: float,
    distance_power: float,
) -> dict[str, Any] | None:
    min_end = min(line_count - 1, start + min_chunk_lines - 1)
    back_floor = max(min_end, target - search_back_lines)
    fwd_ceil = min(line_count - 1, target + search_forward_lines)

    scoped: list[dict[str, Any]] = []
    for end_line, candidate in candidates.items():
        if end_line < back_floor or end_line > fwd_ceil:
            continue
        scoped.append(
            score_candidate(
                candidate,
                target,
                lines,
                headings,
                search_back_lines,
                search_forward_lines,
                decay,
                distance_power,
            )
        )

    if not scoped:
        return None

    scoped.sort(
        key=lambda c: (
            c["final_score"],
            -c["distance"],
            c["base_score"],
            1 if c["direction"] == "backward" else 0,
        ),
        reverse=True,
    )
    return scoped[0]


def nearest_safe_boundary(
    start: int,
    target: int,
    line_count: int,
    min_chunk_lines: int,
    in_code: list[bool],
    fence_close_lines: set[int],
    frontmatter_end: int | None,
) -> int:
    min_end = min(line_count - 1, start + min_chunk_lines - 1)
    for delta in range(0, line_count + 1):
        for end_line in (target - delta, target + delta):
            if end_line < min_end or end_line >= line_count:
                continue
            if frontmatter_end and end_line < frontmatter_end and start <= frontmatter_end:
                continue
            if in_code[end_line] and end_line not in fence_close_lines:
                continue
            return end_line
    return line_count


def build_chunks_semantic(lines: list[str], headings: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    line_count = len(lines)
    if line_count == 0:
        return []

    chunk_lines = config["chunk_lines"]
    search_back_lines = config["search_back_lines"]
    search_forward_lines = config["search_forward_lines"]
    min_chunk_lines = config["min_chunk_lines"]
    max_overshoot_lines = config["max_overshoot_lines"]
    tail_merge_lines = config["tail_merge_lines"]
    decay = config["decay"]
    distance_power = config["distance_power"]

    frontmatter_end = detect_frontmatter_end(lines)
    spans, fence_open_lines, fence_close_lines = parse_fences(lines, frontmatter_end)
    in_code = build_code_line_map(line_count, spans)
    candidates_all = build_candidates(
        lines,
        headings,
        fence_open_lines,
        fence_close_lines,
        frontmatter_end,
        in_code,
        start=1,
        line_count=line_count,
    )

    chunks: list[dict[str, Any]] = []
    start = 1

    while start <= line_count:
        remaining = line_count - start + 1
        if remaining <= chunk_lines:
            chunks.append(
                {
                    "start_line": start,
                    "end_line": line_count,
                    "strategy": "semantic-line",
                    "anchor_heading": None,
                    "boundary_type": "eof",
                    "boundary_line": line_count,
                    "boundary_score": None,
                    "boundary_distance": None,
                    "boundary_note": "end-of-file",
                }
            )
            break

        target = min(line_count - 1, start + chunk_lines - 1)
        span = find_containing_span(start, spans)
        if span and in_code[start]:
            _, close_line = span
            if (close_line - start + 1) <= (chunk_lines + max_overshoot_lines):
                end_line = close_line
                chunks.append(
                    {
                        "start_line": start,
                        "end_line": end_line,
                        "strategy": "semantic-line",
                        "anchor_heading": None,
                        "boundary_type": "code_fence_boundary",
                        "boundary_line": end_line,
                        "boundary_score": None,
                        "boundary_distance": abs(target - end_line),
                        "boundary_note": "code-block-kept-whole",
                    }
                )
                start = end_line + 1
                continue

            end_line = min(line_count - 1, start + chunk_lines - 1)
            chunks.append(
                {
                    "start_line": start,
                    "end_line": end_line,
                    "strategy": "semantic-line",
                    "anchor_heading": None,
                    "boundary_type": "line_break",
                    "boundary_line": end_line,
                    "boundary_score": None,
                    "boundary_distance": abs(target - end_line),
                    "boundary_note": "forced_in_code",
                }
            )
            start = end_line + 1
            continue

        candidates = {
            end_line: c for end_line, c in candidates_all.items() if end_line >= start and end_line < line_count
        }
        chosen = best_candidate(
            candidates,
            start,
            target,
            line_count,
            min_chunk_lines,
            search_back_lines,
            search_forward_lines,
            lines,
            headings,
            decay,
            distance_power,
        )

        if chosen is None:
            end_line = nearest_safe_boundary(
                start,
                target,
                line_count,
                min_chunk_lines,
                in_code,
                fence_close_lines,
                frontmatter_end,
            )
            chunks.append(
                {
                    "start_line": start,
                    "end_line": end_line,
                    "strategy": "semantic-line",
                    "anchor_heading": None,
                    "boundary_type": "line_break",
                    "boundary_line": end_line,
                    "boundary_score": None,
                    "boundary_distance": abs(target - end_line),
                    "boundary_note": "safe-fallback",
                }
            )
            start = end_line + 1
            continue

        end_line = chosen["end_line"]
        chunks.append(
            {
                "start_line": start,
                "end_line": end_line,
                "strategy": "semantic-line",
                "anchor_heading": None,
                "boundary_type": chosen["boundary_type"],
                "boundary_line": end_line,
                "boundary_score": round(chosen["final_score"], 4),
                "boundary_distance": int(chosen["distance"]),
                "boundary_note": chosen["boundary_note"],
            }
        )
        start = end_line + 1

    if len(chunks) >= 2:
        last = chunks[-1]
        prev = chunks[-2]
        last_len = last["end_line"] - last["start_line"] + 1
        prev_len = prev["end_line"] - prev["start_line"] + 1
        if last_len < tail_merge_lines and (prev_len + last_len) <= (chunk_lines + max_overshoot_lines):
            prev["end_line"] = last["end_line"]
            prev["boundary_line"] = last["boundary_line"]
            prev["boundary_type"] = "tail_merge"
            prev["boundary_note"] = "tail-merge"
            prev["boundary_score"] = None
            prev["boundary_distance"] = None
            chunks.pop()

    return chunks


def compute_chunk_stats(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    if not chunks:
        return {
            "count": 0,
            "avg_lines": 0,
            "min_lines": 0,
            "max_lines": 0,
            "boundary_type_counts": {},
        }
    lengths = [(c["end_line"] - c["start_line"] + 1) for c in chunks]
    boundary_counts: dict[str, int] = {}
    for chunk in chunks:
        kind = str(chunk.get("boundary_type", "unknown"))
        boundary_counts[kind] = boundary_counts.get(kind, 0) + 1
    return {
        "count": len(chunks),
        "avg_lines": round(sum(lengths) / len(lengths), 2),
        "min_lines": min(lengths),
        "max_lines": max(lengths),
        "boundary_type_counts": boundary_counts,
    }


def annotate_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chunks:
        return chunks
    width = max(2, int(math.log10(len(chunks))) + 1)
    for idx, chunk in enumerate(chunks, start=1):
        chunk["id"] = f"C{idx:0{width}d}"
    return chunks


def stable_source_hash(lines: list[str]) -> str:
    data = "\n".join(lines).encode("utf-8", errors="replace")
    return hashlib.sha256(data).hexdigest()


def stable_plan_hash(chunks: list[dict[str, Any]], config: dict[str, Any]) -> str:
    plan_data = {
        "chunks": [
            {
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "boundary_type": c.get("boundary_type"),
                "boundary_note": c.get("boundary_note"),
            }
            for c in chunks
        ],
        "config": config,
    }
    raw = json.dumps(plan_data, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_plan(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    lines = load_lines(path)
    line_count = len(lines)
    mode = "long" if line_count > args.threshold else "normal"
    headings = extract_headings(lines)
    preview_end = min(line_count, max(0, args.preview_lines))

    chunker_config = {
        "chunk_lines": args.chunk_lines,
        "search_back_lines": args.search_back_lines,
        "search_forward_lines": args.search_forward_lines,
        "min_chunk_lines": args.min_chunk_lines,
        "max_overshoot_lines": args.max_overshoot_lines,
        "tail_merge_lines": args.tail_merge_lines,
        "decay": args.decay,
        "distance_power": args.distance_power,
    }

    if args.chunker == "legacy":
        chunks = build_chunks_legacy(line_count, headings, args.chunk_lines)
        algorithm_version = "legacy/v1"
    else:
        chunks = build_chunks_semantic(lines, headings, chunker_config)
        algorithm_version = "semantic-line/v1"

    chunks = annotate_chunks(chunks)
    source_hash = stable_source_hash(lines)
    plan_hash = stable_plan_hash(chunks, {"chunker": args.chunker, **chunker_config})
    session_id = f"lfp-{uuid.uuid4().hex[:12]}"

    return {
        "path": str(path).replace("\\", "/"),
        "line_count": line_count,
        "mode": mode,
        "preview_window": {"start": 1 if line_count else 0, "end": preview_end},
        "headings": headings,
        "chunking_mode": args.chunker,
        "algorithm_version": algorithm_version,
        "chunker_config": chunker_config,
        "chunks": chunks,
        "chunk_stats": compute_chunk_stats(chunks),
        "session_id": session_id,
        "source_hash": source_hash,
        "plan_hash": plan_hash,
    }


def main() -> int:
    try:
        args = merge_request_args(parse_args())
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        return 2

    path = Path(args.file)
    if not path.exists() or not path.is_file():
        print(f'error: file not found: "{path}"')
        return 2

    payload = build_plan(path, args)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        # Use ASCII escapes for console safety on non-UTF-8 terminals.
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

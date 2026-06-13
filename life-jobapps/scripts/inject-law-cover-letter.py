#!/usr/bin/env python3
"""Inject a cover letter Markdown source into law-cover-letter-injection-template.docx.

Template-coupled injection script. Hardcoded placeholder strings and 6-slot body
layout come from `<skill-dir>/assets/law-cover-letter-injection-template.docx`.
Per-application fields (date, recipient, organization, address, salutation,
position, source path, output path) come in via CLI args.

Markdown contract:
- Frontmatter (between `---` lines) is skipped.
- Salutation line and Re-line are skipped (template owns these).
- Body paragraphs are blank-separated paragraphs between the Re-line and "Yours truly,".
- "Yours truly,", the signing name, and any `## {Related}` block are skipped.

Body-slot mapping:
- 6 body paragraphs: INTRO, BODY #1, BODY #2, …, BODY #n-1, CONCLUSION (all filled).
- 5 body paragraphs: drop the `…` slot.
- 4 body paragraphs: drop `…` and `BODY #2` slots.
- Other counts (<4 or >6): error out.

Usage:
  python inject-law-cover-letter.py \\
    --source ./job-applications/active/<role>/candidate-cover-letter.md \\
    --output ./job-applications/active/<role>/candidate-cover-letter-2026.docx \\
    --date "May 9, 2026" \\
    --recipient "Sandra Sbrocchi, Head, Osler Works – Transactional" \\
    --organization "Osler, Hoskin & Harcourt LLP" \\
    --address "1 First Canadian Place, 100 King Street West, Suite 6200, Toronto ON M5X 1B8" \\
    --salutation "Dear Sandra," \\
    --position "Technology Transactions Associate"
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "law-cover-letter-injection-template.docx"

# Find optional office helpers from LIFE_JOBAPPS_OFFICE_DIR, local shared/office, or a sibling _shared/office folder.
def _find_office_dir() -> Path:
    env_path = os.environ.get("LIFE_JOBAPPS_OFFICE_DIR")
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if candidate.exists():
            return candidate

    for candidate in (SKILL_DIR / "shared" / "office", SKILL_DIR.parent / "_shared" / "office"):
        if candidate.exists():
            return candidate

    raise SystemExit("Could not locate office helper utilities. Set LIFE_JOBAPPS_OFFICE_DIR or add shared/office.")

OFFICE = _find_office_dir()
UNPACK = OFFICE / "unpack.py"
PACK = OFFICE / "pack.py"
VALIDATE = OFFICE / "validate.py"


# Template placeholder strings. Order matters: longer / more specific first.
HEADER_PLACEHOLDERS = [
    ("MOTH DAY, YEAR", "date"),
    ("RECRUITERNAME, RECRUITERTITLE", "recipient"),
    ("ORGANIZATION ADDRESS", "address"),
    ("ORGANIZATION", "organization"),
    ("Dear RECRUITER,", "salutation"),
    ("Re: Application for the POSITION NAME", "re_line"),
]

# Body slots in template order. Slot 4 is the `…` ellipsis paragraph; the others
# carry literal placeholder strings.
BODY_SLOTS = [
    "INTRO PARA.",    # slot 1
    "BODY PARA #1",   # slot 2
    "BODY PARA #2",   # slot 3
    "…",              # slot 4 (ellipsis paragraph)
    "BODY PARA #n-1", # slot 5
    "CONCLUSION",     # slot 6
]


def xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))


# Smart-quote conversion: applied before xml_escape so that quote characters
# become Unicode curly quotes rather than ASCII straight quotes. Order matters:
# apostrophes inside words first, then end-of-word, then opening-single, then
# any remaining single (treat as closing), then doubles, then triple-dot to
# ellipsis. Already-curly quotes in source pass through unchanged.
_SMART_QUOTE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(\w)'(\w)"), r"\1’\2"),           # foo's, don't
    (re.compile(r"(\w)'"), r"\1’"),                  # boys'
    (re.compile(r"(^|[\s\(\[])'(\w)"), r"\1‘\2"),    # 'opening
    (re.compile(r"'"), "’"),                          # any remaining
    (re.compile(r'(^|[\s\(\[])"'), r"\1“"),           # "opening
    (re.compile(r'"'), "”"),                          # any remaining
    (re.compile(r"\.\.\."), "…"),                     # ... -> …
]


def smart_quotes(s: str) -> str:
    for pattern, repl in _SMART_QUOTE_RULES:
        s = pattern.sub(repl, s)
    return s


def parse_cover_letter_body(markdown: str) -> list[str]:
    """Extract body paragraphs from cover letter markdown.

    Algorithm:
    - Strip frontmatter (between leading `---` lines).
    - Discard the salutation line (any non-blank line ending in `,` before the Re-line).
    - Discard the Re-line (`**Re: ...**`).
    - Collect paragraphs between Re-line and "Yours truly,".
    - Paragraphs are separated by blank lines.
    """
    text = markdown
    if text.startswith("---"):
        # Strip frontmatter
        end = text.find("\n---", 3)
        if end == -1:
            raise SystemExit("Unterminated frontmatter")
        text = text[end + 4:]

    lines = text.split("\n")
    re_line_idx = None
    yours_truly_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re_line_idx is None and stripped.startswith("**Re:"):
            re_line_idx = i
        if stripped.lower().startswith("yours truly"):
            yours_truly_idx = i
            break

    if re_line_idx is None:
        raise SystemExit("Re-line (starting with '**Re:') not found in source markdown")
    if yours_truly_idx is None:
        raise SystemExit("'Yours truly,' line not found in source markdown")

    body_lines = lines[re_line_idx + 1:yours_truly_idx]
    paragraphs: list[str] = []
    current: list[str] = []
    for line in body_lines:
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(s.strip() for s in current).strip())
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(" ".join(s.strip() for s in current).strip())

    return [p for p in paragraphs if p]


def map_body_paragraphs_to_slots(paragraphs: list[str]) -> dict[int, str]:
    """Return a dict mapping slot index (0-5) to paragraph text. Unmapped slots
    are absent and should be dropped from the template.
    """
    n = len(paragraphs)
    if n == 6:
        return {i: paragraphs[i] for i in range(6)}
    if n == 5:
        # Drop slot 3 (the … slot)
        return {0: paragraphs[0], 1: paragraphs[1], 2: paragraphs[2],
                4: paragraphs[3], 5: paragraphs[4]}
    if n == 4:
        # Drop slots 2 (BODY #2) and 3 (…)
        return {0: paragraphs[0], 1: paragraphs[1],
                4: paragraphs[2], 5: paragraphs[3]}
    raise SystemExit(
        f"Body paragraph count {n} not supported; this template handles 4 to 6. "
        "Edit the cover letter to fit or extend the script."
    )


def drop_paragraph_with_text(xml: str, target_text: str) -> str:
    """Remove the `<w:p>...<w:t>target_text</w:t>...</w:p>` element plus one
    trailing blank `<w:p>...</w:p>` if present.
    """
    escaped = re.escape(target_text)
    p_pattern = re.compile(
        rf'<w:p\b[^>]*>(?:(?!</w:p>).)*?<w:t[^>]*>{escaped}</w:t>(?:(?!</w:p>).)*?</w:p>',
        re.DOTALL,
    )
    m = p_pattern.search(xml)
    if not m:
        raise SystemExit(f"Could not locate paragraph containing {target_text!r}")
    start, end = m.span()

    trailing_blank = re.compile(
        r'\s*<w:p\b[^>]*>\s*<w:pPr>(?:(?!</w:p>).)*?</w:pPr>\s*</w:p>',
        re.DOTALL,
    )
    bm = trailing_blank.match(xml, end)
    drop_end = bm.end() if bm else end
    return xml[:start] + xml[drop_end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--source", required=True, type=Path,
                        help="Source cover letter Markdown path")
    parser.add_argument("--output", required=True, type=Path,
                        help="Output .docx path")
    parser.add_argument("--date", required=True,
                        help='Date string (e.g. "May 9, 2026")')
    parser.add_argument("--recipient", required=True,
                        help='Recipient line (e.g. "Sandra Sbrocchi, Head, Osler Works – Transactional")')
    parser.add_argument("--organization", required=True,
                        help='Organization name (e.g. "Osler, Hoskin & Harcourt LLP")')
    parser.add_argument("--address", required=True,
                        help="Single-line address")
    parser.add_argument("--salutation", required=True,
                        help='Salutation (e.g. "Dear Sandra,")')
    parser.add_argument("--position", required=True,
                        help='Position name (e.g. "Technology Transactions Associate")')
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE,
                        help="Override template path")
    parser.add_argument("--no-smart-quotes", action="store_true",
                        help="Skip smart-quote conversion (use when source is known-clean or quotes need to stay straight)")
    args = parser.parse_args()

    transform = (lambda s: s) if args.no_smart_quotes else smart_quotes

    if not args.source.exists():
        return _fail(f"Source markdown not found: {args.source}")
    if not args.template.exists():
        return _fail(f"Template not found: {args.template}")

    print(f"Reading source: {args.source}")
    markdown = args.source.read_text(encoding="utf-8")
    body_paragraphs = parse_cover_letter_body(markdown)
    print(f"  Parsed {len(body_paragraphs)} body paragraphs")
    slot_map = map_body_paragraphs_to_slots(body_paragraphs)
    print(f"  Slot assignments: {sorted(slot_map.keys())}")

    header_values = {
        "date": args.date,
        "recipient": args.recipient,
        "address": args.address,
        "organization": args.organization,
        "salutation": args.salutation,
        "re_line": f"Re: Application for the {args.position} Position",
    }

    with tempfile.TemporaryDirectory(prefix="law-cover-letter-") as tmpdir:
        work_dir = Path(tmpdir)
        print(f"Unpacking {args.template.name}...")
        subprocess.run(
            ["python", str(UNPACK), str(args.template), str(work_dir)],
            check=True,
        )

        doc_xml_path = work_dir / "word" / "document.xml"
        xml = doc_xml_path.read_text(encoding="utf-8")

        print("Applying header replacements...")
        for placeholder, key in HEADER_PLACEHOLDERS:
            if placeholder not in xml:
                return _fail(f"Header placeholder missing: {placeholder!r}")
            xml = xml.replace(placeholder, xml_escape(transform(header_values[key])))
            print(f"  OK: {placeholder!r}")

        print("Applying body replacements...")
        for slot_idx, slot_placeholder in enumerate(BODY_SLOTS):
            if slot_idx in slot_map:
                replacement = xml_escape(transform(slot_map[slot_idx]))
                if slot_placeholder not in xml:
                    return _fail(f"Body placeholder missing: {slot_placeholder!r}")
                xml = xml.replace(slot_placeholder, replacement)
                print(f"  FILL slot {slot_idx} ({slot_placeholder!r})")
            else:
                xml = drop_paragraph_with_text(xml, slot_placeholder)
                print(f"  DROP slot {slot_idx} ({slot_placeholder!r})")

        doc_xml_path.write_text(xml, encoding="utf-8")

        print(f"Repacking to {args.output}...")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["python", str(PACK), str(work_dir), str(args.output)],
            check=True,
        )

    print("Validating...")
    result = subprocess.run(
        ["python", str(VALIDATE), str(args.output)],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    print(f"OUTPUT: {args.output}")
    return result.returncode


def _fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())



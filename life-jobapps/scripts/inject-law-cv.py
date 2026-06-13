#!/usr/bin/env python3
"""Inject a tailored CV Markdown source into law-cv-injection-template.docx.

Template-coupled CV injection script. Builds document.xml body from scratch
using the template's styles and outer section properties. Per-application
content is parsed from the source Markdown.

Markdown contract (any deviation downgrades to plain paragraph rendering):

- Frontmatter (between leading `---` lines): skipped.
- `# Name` (top H1): skipped. Name + contact live in template's header1.xml.
- Plain contact line immediately after H1 (contains `@` or `|`): skipped.
- `---` standalone lines: HR separators, skipped.
- `## Section Heading`: section title (shaded title bar).
- `### Title  |  Organization`: role heading. Date comes from the next
  italic-meta line.
- `*Date  |  Location  |  Time-commitment*` (immediately after a role H3):
  consumed by the preceding H3; Date goes to top-right of role line.
  Location + Time become the meta line below.
- `**Label:**` (ending in colon, no pipes inside): sub-header within role.
- `**Title | Institution | Date**` or `**Title | Org**  |  Date` or
  `**Title | Org**`: alternative entry-heading patterns used in Community
  and Education sections.
- `- **Prefix** rest`: bullet with bold leading segment.
- `- text`: plain bullet.
- Other non-empty content lines: rendered as plain paragraphs (for Languages,
  Interests, Lawyer's Licence single-line bodies).
- `## {Related}` (or `## Related`): stops parsing.

Usage:
  python inject-law-cv.py \\
    --source ./job-applications/active/<role>/candidate-cv.md \\
    --output ./job-applications/active/<role>/candidate-cv-<year>.docx
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
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "law-cv-injection-template.docx"


def _find_office_dir() -> Path:
    current = SCRIPT_DIR
    for _ in range(8):
        candidate = current / ".claude" / "skills" / "_shared" / "office"
        if candidate.exists():
            return candidate
        current = current.parent
    candidate = SKILL_DIR.parent / "_shared" / "office"
    if candidate.exists():
        return candidate
    raise SystemExit("Could not locate office helper utilities. Set LIFE_JOBAPPS_OFFICE_DIR or add shared/office.")


OFFICE = _find_office_dir()
UNPACK = OFFICE / "unpack.py"
PACK = OFFICE / "pack.py"
VALIDATE = OFFICE / "validate.py"


# ----- Smart-quote conversion (mirrors law cover letter injector) -----

_SMART_QUOTE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(\w)'(\w)"), r"\1’\2"),
    (re.compile(r"(\w)'"), r"\1’"),
    (re.compile(r"(^|[\s\(\[])'(\w)"), r"\1‘\2"),
    (re.compile(r"'"), "’"),
    (re.compile(r'(^|[\s\(\[])"'), r"\1“"),
    (re.compile(r'"'), "”"),
    (re.compile(r"\.\.\."), "…"),
]


def smart_quotes(s: str) -> str:
    for pattern, repl in _SMART_QUOTE_RULES:
        s = pattern.sub(repl, s)
    return s


def xe(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ----- XML Builders -----

def section_title(title: str) -> str:
    return f"""<w:tbl>
<w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>
<w:tblBorders><w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/><w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/><w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/><w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/><w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/><w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/></w:tblBorders>
<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>
<w:tblGrid><w:gridCol w:w="9360"/></w:tblGrid>
<w:tr><w:tc><w:tcPr><w:tcW w:w="9360" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/></w:tcPr>
<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(title)}</w:t></w:r></w:p>
</w:tc></w:tr></w:tbl>"""


def role_header(title_org: str, date: str) -> str:
    """Underlined role title (bold, left) and date (italic, right), tab-aligned. Underline runs continuously across tab."""
    if not date:
        return f"""<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:b/><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(title_org)}</w:t></w:r>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr><w:tab/></w:r></w:p>"""
    return f"""<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:b/><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(title_org)}</w:t></w:r>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr><w:tab/></w:r>
<w:r><w:rPr><w:bCs/><w:i/><w:sz w:val="22"/><w:szCs w:val="22"/><w:u w:val="single"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(date)}</w:t></w:r></w:p>"""


def role_meta(location: str, time_commitment: str) -> str:
    if not location and not time_commitment:
        return ""
    if not time_commitment:
        return f"""<w:p><w:pPr><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(location)}</w:t></w:r></w:p>"""
    return f"""<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="9360"/></w:tabs><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(location)}</w:t></w:r>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:tab/></w:r>
<w:r><w:rPr><w:i/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(time_commitment)}</w:t></w:r></w:p>"""


def subheader(label: str) -> str:
    return f"""<w:p><w:pPr><w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:b/><w:bCs/><w:i/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t>{xe(label)}</w:t></w:r>
<w:r><w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t>:</w:t></w:r></w:p>"""


def bullet(segments: list[tuple[str, str]]) -> str:
    """Bullet with arbitrary number of styled runs. segments = list of (style, text) where style in {plain, bold, italic}."""
    body = ""
    for style, text in segments:
        if style == "bold":
            body += f'<w:r><w:rPr><w:b/><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t xml:space="preserve">{xe(text)}</w:t></w:r>'
        elif style == "italic":
            body += f'<w:r><w:rPr><w:bCs/><w:i/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t xml:space="preserve">{xe(text)}</w:t></w:r>'
        else:
            body += f'<w:r><w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t xml:space="preserve">{xe(text)}</w:t></w:r>'
    return f"""<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="36"/></w:numPr><w:rPr><w:bCs/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>{body}</w:p>"""


def paragraph_plain(text: str) -> str:
    return f"""<w:p><w:pPr><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr></w:pPr>
<w:r><w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-CA"/></w:rPr><w:t xml:space="preserve">{xe(text)}</w:t></w:r></w:p>"""


# ----- Parser -----

PIPE_SPLIT = re.compile(r"\s*\|\s*")
H1 = re.compile(r"^#\s+(.+)$")
H2 = re.compile(r"^##\s+(.+)$")
H3 = re.compile(r"^###\s+(.+)$")
ITALIC_META = re.compile(r"^\*([^*]+)\*$")
BOLD_LINE = re.compile(r"^\*\*([^*]+)\*\*(.*)$")
SUBHEADER_LINE = re.compile(r"^\*\*([^*:]+):\*\*$")
BULLET_LINE = re.compile(r"^-\s+(.*)$")
BULLET_BOLD_PREFIX = re.compile(r"^\*\*([^*]+)\*\*(.*)$")
HR_LINE = re.compile(r"^---+$")


def parse_inline_runs(text: str, transform) -> list[tuple[str, str]]:
    """Convert markdown with **bold** and *italic* and [text](url) into styled run segments. Drops link URLs, keeps link text."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    segments: list[tuple[str, str]] = []
    pos = 0
    pattern = re.compile(r"\*\*([^*]+)\*\*|\*([^*]+)\*")
    for match in pattern.finditer(text):
        if match.start() > pos:
            segments.append(("plain", transform(text[pos:match.start()])))
        if match.group(1) is not None:
            segments.append(("bold", transform(match.group(1))))
        else:
            segments.append(("italic", transform(match.group(2))))
        pos = match.end()
    if pos < len(text):
        segments.append(("plain", transform(text[pos:])))
    return segments


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def parse_and_build(markdown: str, transform) -> str:
    text = strip_frontmatter(markdown)
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    saw_h1 = False
    inside_related = False

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # End-of-content marker
        if stripped.lower() in ("## {related}", "## related"):
            inside_related = True
            break
        if inside_related:
            i += 1
            continue

        # H1 + contact line skipped (header.xml carries name/contact).
        m = H1.match(line)
        if m:
            saw_h1 = True
            i += 1
            continue
        # First non-blank line after H1 = contact line; skip.
        if saw_h1 and ("@" in stripped or "Law Society" in stripped or "LSO" in stripped):
            saw_h1 = False
            i += 1
            continue
        saw_h1 = False

        # HR separator
        if HR_LINE.match(stripped):
            i += 1
            continue

        # ## Section title
        m = H2.match(line)
        if m:
            out.append(section_title(transform(m.group(1).strip())))
            i += 1
            continue

        # ### Role heading: pair with next italic-meta line if present
        m = H3.match(line)
        if m:
            heading = m.group(1).strip()
            parts = PIPE_SPLIT.split(heading)
            title_org = transform(" | ".join(p.strip() for p in parts))
            date = ""
            location = ""
            time_commitment = ""
            # Peek next non-blank line for italic meta
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                meta_match = ITALIC_META.match(lines[j].strip())
                if meta_match:
                    meta_parts = [p.strip() for p in PIPE_SPLIT.split(meta_match.group(1))]
                    if len(meta_parts) == 3:
                        date, location, time_commitment = (transform(p) for p in meta_parts)
                    elif len(meta_parts) == 2:
                        date, location = (transform(p) for p in meta_parts)
                    elif len(meta_parts) == 1:
                        date = transform(meta_parts[0])
                    i = j + 1
                else:
                    i += 1
            else:
                i += 1
            out.append(role_header(title_org, date))
            meta_xml = role_meta(location, time_commitment)
            if meta_xml:
                out.append(meta_xml)
            continue

        # Sub-header **Label:**
        m = SUBHEADER_LINE.match(stripped)
        if m and " | " not in m.group(1):
            out.append(subheader(transform(m.group(1).strip())))
            i += 1
            continue

        # Bullet
        m = BULLET_LINE.match(stripped)
        if m:
            inner = m.group(1)
            segments = parse_inline_runs(inner, transform)
            out.append(bullet(segments))
            i += 1
            continue

        # Bold-led paragraph entry (Community / Education style):
        #   **Title | Institution | Date**
        #   **Title | Org**  |  Date
        #   **Title | Org**
        m = BOLD_LINE.match(stripped)
        if m:
            bold_inner = m.group(1).strip()
            trailing = m.group(2).strip()
            bold_parts = [p.strip() for p in PIPE_SPLIT.split(bold_inner)]
            if trailing.startswith("|"):
                trailing = trailing[1:].strip()
            if len(bold_parts) >= 3 and not trailing:
                # **Title | Institution | Date**
                title_org = transform(" | ".join(bold_parts[:-1]))
                date = transform(bold_parts[-1])
                out.append(role_header(title_org, date))
            elif trailing:
                # **Title | Org**  |  Date
                title_org = transform(" | ".join(bold_parts))
                date = transform(trailing)
                out.append(role_header(title_org, date))
            else:
                # **Title | Org** (no date)
                title_org = transform(" | ".join(bold_parts))
                out.append(role_header(title_org, ""))
            i += 1
            continue

        # Fallback: plain paragraph (Languages, Interests, etc.)
        out.append(paragraph_plain(transform(stripped)))
        i += 1

    return "\n".join(out)


# ----- Document Assembly -----

DOC_HEADER = '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se wp14">\n<w:body>\n'

DOC_FOOTER = """<w:sectPr w:rsidR="0018748B" w:rsidRPr="00C81412" w:rsidSect="004F134E">
<w:headerReference w:type="default" r:id="rId7"/>
<w:pgSz w:w="12240" w:h="15840" w:code="1"/>
<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="454" w:footer="994" w:gutter="0"/>
<w:cols w:space="425"/>
<w:docGrid w:type="lines" w:linePitch="312"/>
</w:sectPr>
</w:body></w:document>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--source", required=True, type=Path, help="Source CV Markdown path")
    parser.add_argument("--output", required=True, type=Path, help="Output .docx path")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Override template path")
    parser.add_argument("--no-smart-quotes", action="store_true", help="Skip smart-quote conversion")
    args = parser.parse_args()

    transform = (lambda s: s) if args.no_smart_quotes else smart_quotes

    if not args.source.exists():
        print(f"ERROR: Source markdown not found: {args.source}", file=sys.stderr)
        return 2
    if not args.template.exists():
        print(f"ERROR: Template not found: {args.template}", file=sys.stderr)
        return 2

    print(f"Reading source: {args.source}")
    markdown = args.source.read_text(encoding="utf-8")
    body = parse_and_build(markdown, transform)
    new_doc_xml = DOC_HEADER + body + "\n" + DOC_FOOTER

    with tempfile.TemporaryDirectory(prefix="law-cv-") as tmpdir:
        work_dir = Path(tmpdir)
        print(f"Unpacking {args.template.name}...")
        subprocess.run(["python", str(UNPACK), str(args.template), str(work_dir)], check=True)
        (work_dir / "word" / "document.xml").write_text(new_doc_xml, encoding="utf-8")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        print(f"Repacking to {args.output}...")
        subprocess.run(["python", str(PACK), str(work_dir), str(args.output)], check=True)

    print("Validating...")
    result = subprocess.run(["python", str(VALIDATE), str(args.output)], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    print(f"OUTPUT: {args.output}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())



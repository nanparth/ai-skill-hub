"""PDF adapter: parse text spans into NormalizedDoc with font-size heading inference.

Heavy import (PyMuPDF / fitz) is LAZY: imported inside parse(), never at module top.
"""
from __future__ import annotations

from . import NormalizedDoc, DocBlock, limit_value, mark_truncated


def parse(src: str, pages=None, **opts) -> NormalizedDoc:
    import fitz  # lazy heavy import

    doc = NormalizedDoc(source_format="pdf")
    pdf = fitz.open(src)
    try:
        total = pdf.page_count
        max_pages = limit_value(opts, "max_pdf_pages")
        page_indices = list(pages) if pages is not None else list(range(total))
        if max_pages and len(page_indices) > max_pages:
            page_indices = page_indices[:max_pages]
            mark_truncated(doc, "PDF_PAGE_LIMIT_REACHED")

        idx = 0
        current_heading_path: list[str] = []
        for page_no in page_indices:
            page = pdf[page_no]
            data = page.get_text("dict")
            anchor = f"page{page_no + 1}"

            # Collect line-level spans with their max font size and bold flag.
            lines = []
            sizes = []
            for block in data.get("blocks", []):
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    line_text = "".join(s.get("text", "") for s in spans).strip()
                    if not line_text:
                        continue
                    max_size = max((s.get("size", 0.0) for s in spans), default=0.0)
                    is_bold = any(
                        bool(s.get("flags", 0) & 16) for s in spans
                    )
                    lines.append((line_text, max_size, is_bold))
                    sizes.append(max_size)

            if not lines:
                continue

            # Heading threshold: largest font on the page.
            max_page_size = max(sizes) if sizes else 0.0
            body_size = _median(sizes) if sizes else 0.0

            for line_text, size, is_bold in lines:
                is_heading = (
                    max_page_size > 0
                    and (size >= max_page_size - 0.1)
                    and (size > body_size or is_bold)
                )
                if is_heading:
                    current_heading_path = [line_text]
                doc.blocks.append(
                    DocBlock(
                        text=line_text,
                        block_type="heading" if is_heading else "paragraph",
                        idx=idx,
                        anchor=anchor,
                        heading_path=list(current_heading_path),
                    )
                )
                idx += 1
    finally:
        pdf.close()

    return doc


def _median(values) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0

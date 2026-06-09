from __future__ import annotations

import re

from ..utils import score_confidence

# Canadian neutral citation court codes.
_NEUTRAL_CITATION = re.compile(
    r"\b(19|20)\d{2}\s+"
    r"(SCC|FCA|FC|FCTD|TCC|ONSC|ONCA|ONCJ|BCSC|BCCA|ABQB|ABCA|QCCA|QCCS|SKQB|SKCA|MBQB|MBCA|NSCA|NSSC|NLCA|NBCA|PESC)"
    r"\s+\d+\b"
)

# "X v. Y, YYYY" style citation.  Only matches when a 4-digit year (optionally
# in brackets/parens and optionally preceded by a comma) follows the case name,
# so that bare prose uses of "v" (e.g. "Option A v Option B") are not promoted.
_CASE_CITATION = re.compile(
    r"\b([A-Z][A-Za-z0-9.&' -]+?)\s+v\.?\s+([A-Z][A-Za-z0-9.&' -]+?)"
    r"(?=[,\d]|$|\s+\d|\s*\.)"
    r"(?=.{0,30}[\[(]?(?:19|20)\d{2})",
    re.MULTILINE | re.DOTALL,
)

# Statutory section references: "section 12(1)(a)" or "s. 12(1)(a)".
# Both branches consume optional subsection groups; no trailing lookahead that
# would prevent subsection capture.
_STATUTORY_REF = re.compile(
    r"\b(?:section|s\.)\s*\d+(?:\(\d+\))?(?:\([a-z]\))?(?:\(\d+\))?"
)

# Rule / Article references.
_RULE_REF = re.compile(r"\b(Rule|Article)\s+\d+\b")

# Paragraph cross-references -- internal, not authorities.
_PARA_REF = re.compile(
    r"\b(?:at\s+)?para(?:s|graph(?:s)?)?\.\s*\d+(?:\s*[-–]\s*\d+)?\b",
    re.I,
)


def harvest_citation(h, sent: str, source_ref, anti: list[str]) -> None:
    """Detect legal authorities in *sent* and emit legal_authorities candidates."""
    # Neutral citation -- high precision, auto-promotes at 0.86.
    for m in _NEUTRAL_CITATION.finditer(sent):
        citation_text = m.group(0)
        signals = ["neutral_citation", "citation_signal"]
        h._add_candidate(
            "legal_authorities",
            "neutral_citation",
            {"citation": citation_text, "authority_type": "case", "jurisdiction": None},
            sent,
            source_ref,
            0.86,
            signals,
            anti,
        )

    # Case-name citation ("X v. Y").  Skip matches that are only paragraph refs.
    for m in _CASE_CITATION.finditer(sent):
        full_match = m.group(0).strip().rstrip(".")
        # Exclude bare paragraph references caught by the para pattern.
        if _PARA_REF.search(full_match):
            continue
        signals = ["case_citation", "citation_signal"]
        confidence = score_confidence(0.70, signals, anti)
        h._add_candidate(
            "legal_authorities",
            "case_citation",
            {"citation": full_match, "authority_type": "case", "jurisdiction": None},
            sent,
            source_ref,
            confidence,
            signals,
            anti,
        )

    # Statutory section reference.
    for m in _STATUTORY_REF.finditer(sent):
        citation_text = m.group(0)
        signals = ["statutory_reference", "citation_signal"]
        confidence = score_confidence(0.78, signals, anti)
        h._add_candidate(
            "legal_authorities",
            "statutory_reference",
            {"citation": citation_text, "authority_type": "statute", "jurisdiction": None},
            sent,
            source_ref,
            confidence,
            signals,
            anti,
        )

    # Rule / Article reference.
    for m in _RULE_REF.finditer(sent):
        citation_text = m.group(0)
        signals = ["rule_reference", "citation_signal"]
        confidence = score_confidence(0.72, signals, anti)
        h._add_candidate(
            "legal_authorities",
            "rule_reference",
            {"citation": citation_text, "authority_type": "rule", "jurisdiction": None},
            sent,
            source_ref,
            confidence,
            signals,
            anti,
        )

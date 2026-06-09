from __future__ import annotations

import re

from ..utils import clean_entity, clean_role, extract_entity_like_names, infer_role_from_text, norm

# Matches litigation captions such as "Smith v. Jones", "R. v. Smith",
# "Acme Corp. v. Beta Holdings Inc.", "Acme Corp. v. Beta Ltd., 2023 FCA 45".
#
# Left side: lazy, capitalised token sequence.
# Separator: "v.", "v", "vs.", or "vs" as a standalone token.
# Right side: lazy, capitalised; ends on a word character followed by an
#   optional abbreviation period (e.g. "Ltd.", "Inc.", "Corp.").  This allows
#   corporate-suffix names that end in a period before a comma or year.
#   Stops before a space followed by a lowercase word (prose continuation),
#   a comma, "et al", or end-of-string.
_CAPTION_SIDE_L = r"([A-Z][A-Za-z0-9.&' ]*?)"
_CAPTION_SIDE_R = r"([A-Z][A-Za-z0-9.&' ]*?[A-Za-z0-9]\.?)"
_CAPTION_SEP = r"\s+(?:vs?\.?|vs)\s+"
_CAPTION_STOP_R = r"(?=\s+[a-z]|\s*,|\s*et\s+al|\s*$)"
_CAPTION_RE = re.compile(
    _CAPTION_SIDE_L + _CAPTION_SEP + _CAPTION_SIDE_R + _CAPTION_STOP_R,
    re.MULTILINE,
)

# Leading words that may appear as sentence-initial capitals but are not party
# names.  Stripped from the front of a captured caption side iteratively so
# that "In re The Estate" reduces to "Estate" rather than keeping "In".
_CAPTION_LEADING_STOPWORDS = frozenset({
    "in", "the", "on", "at", "for", "see", "per", "under",
    "re", "between", "cf", "compare",
})


def _clean_caption_side(raw: str) -> str:
    """Strip trailing punctuation, whitespace, and leading function words."""
    s = raw.strip().rstrip(".,;: ")
    # Strip consecutive leading stop words (one pass, case-insensitive).
    tokens = s.split()
    while tokens and tokens[0].lower() in _CAPTION_LEADING_STOPWORDS:
        tokens = tokens[1:]
    return " ".join(tokens)


def harvest_party_alias(h, sent: str, source_ref, anti: list[str]) -> None:
    patterns = [
        re.compile(r"(?P<name>[A-Z][A-Za-z0-9&.,' -]+?\s+(?:Inc\.?|LLC|Ltd\.?|Corp(?:oration)?\.?|Company|LP|LLP|PLC|GmbH))\s*(?:,\s*(?:a|an)\s+[^()]{2,80})?\s*\(\s*(?:the\s+)?['\"](?P<role>[A-Za-z][A-Za-z ]{1,40})['\"]\s*\)", re.I),
        re.compile(r"(?P<name>[A-Z][A-Za-z0-9&.,' -]+?)\s+(?:is|are)\s+referred\s+to\s+herein\s+as\s+['\"](?P<role>[A-Za-z][A-Za-z ]{1,40})['\"]", re.I),
    ]
    for rx in patterns:
        for m in rx.finditer(sent):
            name = clean_entity(m.group("name"))
            role = clean_role(m.group("role"))
            if not name or not role:
                continue
            h.known_aliases.add(norm(name))
            h.known_aliases.add(norm(role))
            h._add_candidate("parties", "defined_party_alias", {"name": name, "role": role, "type": "party"}, sent, source_ref, 0.88, ["defined_term", "alias_match"], anti)
    if re.search(r"\b(by and among|between|entered into by)\b", sent, re.I):
        for name in extract_entity_like_names(sent)[:4]:
            h.known_aliases.add(norm(name))
            h._add_candidate("parties", "agreement_intro_party", {"name": name, "role": infer_role_from_text(name), "type": "party"}, sent, source_ref, 0.68, ["agreement_intro", "alias_match"], anti)
    if re.search(r"\bBy:\s*|\bName:\s*|\bTitle:\s*", sent, re.I):
        h._add_candidate("parties", "signature_block", {"name": sent, "role": "signatory", "type": "party"}, sent, source_ref, 0.62, ["signature_block"], anti)
    # Litigation caption detection is handled at block level via
    # harvest_litigation_captions because the sentence splitter splits at "v."
    # which prevents the caption from surviving as a single sentence.


def harvest_litigation_captions(h, block_text: str, source_ref, anti: list[str]) -> None:
    """Detect case captions (e.g. 'Smith v. Jones') in raw block text.

    Called once per block before sentence iteration, so the full caption token
    sequence is visible even though the sentence splitter breaks at 'v.'.
    Only existing sentence-level harvesters in SENTENCE_HARVESTERS are called
    per sentence; this function is a block-level supplement for captions only.
    """
    for m in _CAPTION_RE.finditer(block_text):
        left = _clean_caption_side(m.group(1))
        right = _clean_caption_side(m.group(2))
        # Both sides must begin with an uppercase letter and have at least two
        # characters to avoid matching lone initials or noise tokens.
        if not left or not right:
            continue
        if not left[0].isupper() or not right[0].isupper():
            continue
        if len(left) < 2 or len(right) < 2:
            continue
        for side_name in (left, right):
            h.known_aliases.add(norm(side_name))
            h._add_candidate(
                "parties",
                "litigation_caption",
                {"name": side_name, "role": "party", "type": "party"},
                block_text,
                source_ref,
                0.60,
                ["litigation_caption"],
                anti,
            )

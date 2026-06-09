from __future__ import annotations

import re

from ..utils import extract_subject, is_rep_warranty, score_confidence


def harvest_rep_warranty(h, sent: str, source_ref, anti: list[str]) -> None:
    if not is_rep_warranty(sent):
        return
    signals = ["rep_warranty_signal"]
    if h._is_known_subject(extract_subject(sent)):
        signals.append("known_party_subject")
    if re.search(r"\b(true\s+and\s+correct|material\s+respects|knowledge\s+of|except\s+as\s+disclosed|set\s+forth\s+on\s+Schedule)\b", sent, re.I):
        signals.append("qualifier_signal")
    h._add_candidate("concepts", "representation_warranty", {"name": "Representation/Warranty", "concept_type": "representation", "description": sent}, sent, source_ref, score_confidence(0.65, signals, anti), signals, anti)

from __future__ import annotations

import re

from ..utils import extract_subject, score_confidence


def harvest_default_remedy(h, sent: str, source_ref, anti: list[str]) -> None:
    if not re.search(r"\b(breach|default|event\s+of\s+default|failure\s+to\s+perform|non-compliance|cure|remedy|fails?\s+to\s+cure|may\s+terminate|right\s+to\s+terminate|termination\s+event|automatic\s+termination|specific\s+performance|injunctive\s+relief|damages|indemnification|setoff|survive\s+(?:Closing|termination)|remain\s+in\s+effect)\b", sent, re.I):
        return
    signals = ["default_remedy_signal"]
    if re.search(r"\b(obligation|representation|warranty|covenant|remedy|terminate|cure)\b", sent, re.I):
        signals.append("legal_action_object")
    if h._is_known_subject(extract_subject(sent)):
        signals.append("known_party_subject")
    confidence = score_confidence(0.58, signals, anti)
    h._add_candidate("conditions", "default_remedy", {"description": sent, "responsible_party": extract_subject(sent) or None}, sent, source_ref, confidence, signals, anti)

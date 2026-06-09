from __future__ import annotations

import re

from ..lexicon import LEGAL_ACTION_VERBS
from ..utils import control_documents, extract_subject, heading_prior_signals, score_confidence


def harvest_controls(h, sent: str, source_ref, anti: list[str]) -> None:
    if not re.search(r"\b(verified\s+by|evidenced\s+by|control(?:led)?\s+by|audit(?:ed)?\s+(?:by|via)|reviewed\s+by|approved\s+by|sign-?off)\b", sent, re.I):
        return
    signals = ["control_signal", *heading_prior_signals(source_ref, "controls")]
    if re.search(r"\b(verified\s+by|evidenced\s+by|audit(?:ed)?)\b", sent, re.I):
        signals.append("evidence_signal")
    if LEGAL_ACTION_VERBS.search(sent):
        signals.append("legal_action_object")
    confidence = score_confidence(0.56, signals, anti)
    h._add_candidate("controls", "evidence_control", {"description": sent, "owner": extract_subject(sent) or None, "obligation_id": "unlinked", "evidence_documents": control_documents(sent)}, sent, source_ref, confidence, signals, anti)

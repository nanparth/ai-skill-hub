from __future__ import annotations

import re

from ..lexicon import LEGAL_ACTION_VERBS
from ..utils import document_name, extract_subject, heading_prior_signals, score_confidence


def harvest_deliverables(h, sent: str, source_ref, anti: list[str]) -> None:
    if not re.search(r"\b(deliver|provide|furnish|make\s+available|submit|file|send|officer's\s+certificate|secretary's\s+certificate|bring-down\s+certificate|compliance\s+certificate|executed\s+counterpart|books\s+and\s+records|inspection\s+rights)\b", sent, re.I):
        return
    signals = ["deliverable_signal", *heading_prior_signals(source_ref, "documents")]
    if LEGAL_ACTION_VERBS.search(sent):
        signals.append("legal_action_object")
    subject = extract_subject(sent)
    if h._is_known_subject(subject):
        signals.append("known_party_subject")
    confidence = score_confidence(0.58, signals, anti)
    h._add_candidate("documents", "deliverable_document", {"name": document_name(sent), "type": "deliverable", "parties": [subject] if subject else [], "description": sent}, sent, source_ref, confidence, signals, anti)

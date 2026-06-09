from __future__ import annotations

import re

from ..lexicon import LEGAL_ACTION_VERBS
from ..utils import deadline_text, extract_procurement_target, extract_subject, has_deadline_signal, heading_prior_signals, is_rep_warranty, score_confidence


def harvest_obligation(h, sent: str, source_ref, anti: list[str]) -> None:
    if is_rep_warranty(sent) and not re.search(r"\bshall\s+(?:update|notify|cause|deliver|provide|file|submit)\b", sent, re.I):
        return
    patterns = [
        ("negative_obligation", re.compile(r"\b(shall\s+not|will\s+not|agrees?\s+not\s+to|is\s+prohibited\s+from|may\s+not|must\s+not|no\s+party\s+shall)\b", re.I), 0.78),
        ("best_efforts_duty", re.compile(r"\b(use\s+commercially\s+reasonable\s+efforts|reasonable\s+best\s+efforts|best\s+efforts|good\s+faith\s+efforts)\b", re.I), 0.76),
        ("procurement_duty", re.compile(r"\b(shall\s+cause|shall\s+procure\s+that|shall\s+ensure\s+that|cause\s+its\s+affiliates\s+to)\b", re.I), 0.80),
        ("continuing_duty", re.compile(r"\b(continue\s+to|maintain|keep|preserve|retain|not\s+permit)\b", re.I), 0.68),
        ("positive_obligation", re.compile(r"\b(shall|must|agrees?\s+to|undertakes\s+to|covenants\s+to|will|is\s+obligated\s+to|is\s+responsible\s+for|is\s+required\s+to)\b", re.I), 0.70),
    ]
    for frame, rx, base in patterns:
        m = rx.search(sent)
        if not m:
            continue
        subject = extract_subject(sent, m.start())
        signals = [frame, "obligation_strength"]
        if h._is_known_subject(subject):
            signals.append("known_party_subject")
        if LEGAL_ACTION_VERBS.search(sent):
            signals.append("legal_action_object")
        if has_deadline_signal(sent):
            signals.append("deadline_signal")
        signals.extend(heading_prior_signals(source_ref, "obligations"))
        confidence = score_confidence(base, signals, anti)
        h._add_candidate("obligations", frame, {"party": subject or "unspecified", "description": sent, "kind": frame, "deadline": deadline_text(sent)}, sent, source_ref, confidence, signals, anti)
        if frame == "procurement_duty":
            target = extract_procurement_target(sent)
            h._add_candidate("relationships", "procurement_edge", {"from_entity": subject or "unspecified", "to_entity": target or "controlled party", "type": "shall_cause", "description": sent}, sent, source_ref, confidence, [*signals, "shall_cause_edge"], anti)
        break

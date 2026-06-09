from __future__ import annotations

import re

from ..utils import condition_corrob_signals, extract_subject, heading_prior_signals, score_confidence


def harvest_conditions(h, sent: str, source_ref, anti: list[str]) -> None:
    patterns = [
        ("condition_precedent", re.compile(r"\b(condition\s+precedent|subject\s+to\s+the\s+satisfaction\s+of|subject\s+to\s+waiver\s+of|unless\s+and\s+until|provided\s+that)\b", re.I), 0.66),
        ("trigger_condition", re.compile(r"\b(if|in\s+the\s+event\s+that|upon|following|after\s+receipt\s+of|once|where)\b", re.I), 0.42),
        ("exception_carveout", re.compile(r"\b(except\s+that|except\s+as|other\s+than|excluding|provided\s+however|notwithstanding|for\s+the\s+avoidance\s+of\s+doubt|nothing\s+herein\s+shall)\b", re.I), 0.48),
        ("dependency", re.compile(r"\b(conditioned\s+upon|dependent\s+on|contingent\s+upon|subject\s+to)\b", re.I), 0.44),
    ]
    for frame, rx, base in patterns:
        if not rx.search(sent):
            continue
        signals = [frame, *condition_corrob_signals(sent), *heading_prior_signals(source_ref, "conditions")]
        confidence = score_confidence(base, signals, anti)
        h._add_candidate("conditions", frame, {"description": sent, "responsible_party": extract_subject(sent) or None}, sent, source_ref, confidence, signals, anti)

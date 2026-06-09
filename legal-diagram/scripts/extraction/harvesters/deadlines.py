from __future__ import annotations

import re

from ..lexicon import LEGAL_ACTION_VERBS
from ..utils import condition_corrob_signals, deadline_text, extract_subject, heading_prior_signals, score_confidence


def harvest_deadlines(h, sent: str, source_ref, anti: list[str]) -> None:
    patterns = [
        ("hard_deadline", re.compile(r"\b(no\s+later\s+than|on\s+or\s+before|not\s+later\s+than|at\s+least\s+\d+\s+(?:business\s+)?days?\s+before|by\s+(?:\d{4}-\d{2}-\d{2}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|(?:the\s+)?Closing(?:\s+Date)?))\b", re.I), 0.64),
        ("relative_deadline", re.compile(r"\b(within\s+\d+\s+(?:business\s+)?days?\s+(?:after|of)|promptly\s+after|as\s+soon\s+as\s+practicable\s+after)\b", re.I), 0.58),
        ("pre_closing_deadline", re.compile(r"\b(prior\s+to\s+Closing|before\s+the\s+Closing\s+Date|at\s+or\s+before\s+Closing)\b", re.I), 0.62),
        ("post_closing_deadline", re.compile(r"\b(following\s+Closing|after\s+the\s+Closing\s+Date|post-Closing|from\s+and\s+after\s+Closing)\b", re.I), 0.62),
        ("notice_period", re.compile(r"\b(?:upon\s+)?\d+\s+(?:business\s+)?days?[']?\s+(?:prior\s+)?written\s+notice\b", re.I), 0.66),
        ("cure_period", re.compile(r"\b(cure\s+period|fails?\s+to\s+cure\s+within|remedied\s+within)\b", re.I), 0.66),
    ]
    for frame, rx, base in patterns:
        m = rx.search(sent)
        if not m:
            continue
        signals = [frame, "deadline_signal", *heading_prior_signals(source_ref, "deadlines")]
        if condition_corrob_signals(sent):
            signals.append("trigger_signal")
        if LEGAL_ACTION_VERBS.search(sent):
            signals.append("legal_action_object")
        confidence = score_confidence(base, signals, anti)
        if re.search(r"\bpromptly\b", sent, re.I) and not re.search(r"\b(after|following|upon|receipt)\b", sent, re.I):
            confidence = min(confidence, 0.44)
            anti = [*anti, "promptly_without_trigger"]
        h._add_candidate("deadlines", frame, {"date_or_timing": deadline_text(sent) or m.group(0), "description": sent, "party": extract_subject(sent) or None}, sent, source_ref, confidence, signals, anti)

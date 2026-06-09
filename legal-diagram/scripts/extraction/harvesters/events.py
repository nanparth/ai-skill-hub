from __future__ import annotations

import re

from ..lexicon import DATE_RE
from ..utils import anti_penalty, extract_subject, score_confidence


# Future/hypothetical markers: when present in the occurrence-verb branch the
# candidate confidence is capped at 0.44 so it never promotes.
_FUTURE_HYPOTHETICAL = re.compile(
    r"\b(shall|will|may|must|should|if|in the event|subject to|provided that|once|when|to be)\b",
    re.I,
)

# Occurrence verbs: factual/past-tense events only.
# Deliberately excludes shall, deliver, pay, within, no later than (those belong to
# obligations/deadlines, not factual events).
_OCCURRENCE_VERBS = re.compile(
    r"\b("
    r"heard|filed|issued|entered\s+into|rendered|released|decided|dismissed|granted|allowed|denied|"
    r"dated|executed|signed|served|commenced|convened|adjourned|occurred|took\s+place|closed|"
    r"pronounced|sentenced|convicted|acquitted|registered|incorporated|amalgamated|notified|approved"
    r")\b",
    re.I,
)

# Frame families keyed by representative verb patterns.
_HEARING_RE = re.compile(r"\b(heard|convened|adjourned)\b", re.I)
_FILING_RE = re.compile(r"\b(filed|served|registered)\b", re.I)
_ORDER_RE = re.compile(
    r"\b(issued|rendered|released|decided|dismissed|granted|allowed|denied|pronounced|sentenced|convicted|acquitted)\b",
    re.I,
)
_TRANSACTION_RE = re.compile(
    r"\b(executed|signed|entered\s+into|closed|incorporated|amalgamated)\b",
    re.I,
)


def _frame_type(sent: str) -> str:
    """Return the frame type based on the occurrence verb family present in the sentence."""
    if _HEARING_RE.search(sent):
        return "hearing_event"
    if _FILING_RE.search(sent):
        return "filing_event"
    if _ORDER_RE.search(sent):
        return "order_event"
    if _TRANSACTION_RE.search(sent):
        return "transaction_event"
    return "dated_event"


def harvest_event(h, sent: str, source_ref, anti: list[str]) -> None:
    """Harvest factual/procedural dated events from a sentence.

    Fires only when a full date is present. With an occurrence verb the candidate
    is emitted at base confidence 0.66 (promotes at the 0.65 corroborated band).
    Without an occurrence verb the candidate is emitted at 0.42 (hint only).
    """
    date_match = DATE_RE.search(sent)
    if not date_match:
        return

    date_text = date_match.group(0)

    if _OCCURRENCE_VERBS.search(sent):
        frame = _frame_type(sent)
        signals = [frame, "date_signal", "event_verb"]
        confidence = score_confidence(0.66, signals, anti)
        # Guard: future/hypothetical markers indicate the verb describes a
        # potential or required action, not a confirmed factual past event.
        # Cap confidence below the promotion threshold and add an anti-signal.
        if _FUTURE_HYPOTHETICAL.search(sent):
            confidence = min(confidence, 0.44)
            signals = signals + ["future_or_hypothetical"]
        value = {
            "date_or_timing": date_text,
            "description": sent,
            "actor": extract_subject(sent) or None,
        }
        h._add_candidate("events", frame, value, sent, source_ref, confidence, signals, anti)
    else:
        # Date present but no occurrence verb: emit a low-confidence hint only.
        signals = ["date_signal"]
        confidence = 0.42 - anti_penalty(anti)
        value = {
            "date_or_timing": date_text,
            "description": sent,
        }
        h._add_candidate("events", "dated_event", value, sent, source_ref, confidence, signals, anti)

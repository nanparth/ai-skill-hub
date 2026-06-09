from __future__ import annotations

import re

from ..utils import delivery_method, extract_notice_parties, heading_prior_signals, score_confidence


def harvest_notice(h, sent: str, source_ref, anti: list[str]) -> None:
    if not re.search(r"\b(notify|give\s+notice|written\s+notice|notice\s+shall\s+be\s+sent|to\s+the\s+attention\s+of|with\s+a\s+copy\s+to|cc\b|email|overnight\s+courier|certified\s+mail|personal\s+delivery|deemed\s+(?:received|given)|effective\s+upon\s+receipt)\b", sent, re.I):
        return
    sender, recipient = extract_notice_parties(sent)
    method = delivery_method(sent)
    signals = ["notice_signal", *heading_prior_signals(source_ref, "communications")]
    if sender and sender != "unspecified":
        signals.append("sender_signal")
    if recipient and recipient != "unspecified":
        signals.append("recipient_signal")
    if method:
        signals.append("delivery_method_signal")
    confidence = score_confidence(0.62, signals, anti)
    if not method and not recipient and not (sender and sender != "unspecified"):
        confidence = min(confidence, 0.44)
        anti = [*anti, "notice_without_sender_recipient_or_method"]
    h._add_candidate("communications", "notice_communication", {"from_party": sender or "unspecified", "to_party": recipient or "unspecified", "comm_type": "notice", "description": sent, "delivery_method": method}, sent, source_ref, confidence, signals, anti)

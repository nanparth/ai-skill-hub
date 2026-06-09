from __future__ import annotations

import re

from ..lexicon import MONEY_RE
from ..utils import deadline_text, extract_payment_parties, has_deadline_signal, has_payment_verb, heading_prior_signals, money_text, rank_from_text, score_confidence


def harvest_payments(h, sent: str, source_ref, anti: list[str]) -> None:
    if not (has_payment_verb(sent) and (MONEY_RE.search(sent) or re.search(r"\b(purchase\s+price|fee|expense|escrow\s+amount|holdback)\b", sent, re.I))):
        if re.search(r"\b(first|second|then|thereafter|pro\s+rata|pari\s+passu|true-up|setoff|deduct|net\s+of)\b", sent, re.I) and heading_prior_signals(source_ref, "transfers"):
            h._add_candidate("claim_classes", "waterfall_sequence", {"name": sent, "priority_rank": rank_from_text(sent), "claim_type": "waterfall"}, sent, source_ref, 0.58, ["waterfall_signal", "heading_prior"], anti)
        return
    payer, payee = extract_payment_parties(sent)
    signals = ["payment_signal", *heading_prior_signals(source_ref, "transfers")]
    if payer:
        signals.append("known_party_subject" if h._is_known_subject(payer) else "payer_signal")
    if payee:
        signals.append("payee_signal")
    if has_deadline_signal(sent):
        signals.append("deadline_signal")
    confidence = score_confidence(0.66, signals, anti)
    h._add_candidate("transfers", "payment_flow", {"from_party": payer or "unspecified", "to_party": payee or "unspecified", "amount_text": money_text(sent), "description": sent, "timing": deadline_text(sent)}, sent, source_ref, confidence, signals, anti)

from __future__ import annotations

from .lexicon import HINT_MIN, PROMOTE_AUTO, PROMOTE_WITH_CORROBORATION
from .schema import Candidate, PromotionDecision
from .utils import norm, uniq


def resolve_candidates(candidates: list[Candidate], *, sparse: bool = True) -> list[PromotionDecision]:
    decisions: list[PromotionDecision] = []
    for cand in candidates:
        if cand.confidence >= PROMOTE_AUTO:
            decisions.append(PromotionDecision(cand.id, "promote", "confidence >= 0.85", f"candidate:{cand.id}"))
        elif cand.confidence >= PROMOTE_WITH_CORROBORATION and has_corroboration(cand):
            decisions.append(PromotionDecision(cand.id, "promote", "medium confidence with corroborating signals", f"candidate:{cand.id}"))
        elif cand.confidence >= HINT_MIN:
            decisions.append(PromotionDecision(cand.id, "hint", "below promotion threshold; send compact evidence to LLM", None))
        elif sparse and cand.confidence >= 0.35:
            decisions.append(PromotionDecision(cand.id, "hint", "sparse extraction fallback", None))
        else:
            decisions.append(PromotionDecision(cand.id, "suppress", "low confidence or noisy uncorroborated signal", None))
    return decisions


def has_corroboration(cand: Candidate) -> bool:
    corroborators = {
        "table_row_binding", "known_party_subject", "heading_prior", "deadline_signal", "alias_match",
        "legal_action_object", "defined_term", "sender_signal", "recipient_signal", "payment_signal",
        "document_header", "control_header", "party_header", "obligation_header", "qualifier_signal", "rep_warranty_signal",
        "date_signal", "event_verb", "citation_signal",
    }
    return bool(corroborators.intersection(cand.signals)) or cand.source_ref.table_coords is not None


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    by_key: dict[str, Candidate] = {}
    for cand in candidates:
        key = semantic_key(cand)
        existing = by_key.get(key)
        if existing is None or cand.confidence > existing.confidence:
            if existing is not None:
                cand.evidence_ids = uniq([*existing.evidence_ids, *cand.evidence_ids])
                cand.signals = uniq([*existing.signals, *cand.signals])
                cand.anti_signals = uniq([*existing.anti_signals, *cand.anti_signals])
                cand.confidence = max(existing.confidence, cand.confidence)
            by_key[key] = cand
        elif existing is not None:
            existing.evidence_ids = uniq([*existing.evidence_ids, *cand.evidence_ids])
            existing.signals = uniq([*existing.signals, *cand.signals])
            existing.anti_signals = uniq([*existing.anti_signals, *cand.anti_signals])
    return list(by_key.values())


def semantic_key(cand: Candidate) -> str:
    value = cand.normalized_value
    pieces = [cand.target_field, cand.frame_type]
    for key in ("party", "name", "description", "date_or_timing", "from_party", "to_party", "parent", "child", "question"):
        if value.get(key):
            pieces.append(norm(str(value.get(key))))
    if len(pieces) == 2:
        pieces.append(norm(str(value)))
    return "|".join(pieces)

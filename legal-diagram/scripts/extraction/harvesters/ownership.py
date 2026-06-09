from __future__ import annotations

import re

from ..utils import clean_entity, extract_object_entity, extract_subject, heading_prior_signals, score_confidence


def harvest_ownership_control(h, sent: str, source_ref, anti: list[str]) -> None:
    own = re.search(r"(?P<parent>[A-Z][A-Za-z .&]+?)\s+(?:owns?|holds?|beneficially\s+owns|is\s+the\s+record\s+owner\s+of)\s+(?P<pct>\d+(?:\.\d+)?)?%?\s*(?:of\s+)?(?P<child>[A-Z][A-Za-z .&]+)", sent)
    if own:
        signals = ["ownership_signal", *heading_prior_signals(source_ref, "relationships")]
        pct = own.group("pct")
        h._add_candidate("ownership_links", "ownership", {"parent": clean_entity(own.group("parent")), "child": clean_entity(own.group("child")), "percentage": float(pct) if pct else None}, sent, source_ref, score_confidence(0.78, signals, anti), signals, anti)
    if re.search(r"\b(controls|controlled\s+by|under\s+common\s+control|power\s+to\s+direct|authorized\s+to|has\s+authority\s+to|power\s+and\s+authority|duly\s+authorized|may\s+not\s+assign|transfer|pledge|encumber|dispose\s+of|board\s+approval|manager\s+approval|shareholder\s+approval|consent\s+of\s+members)\b", sent, re.I):
        signals = ["control_authority_signal", *heading_prior_signals(source_ref, "relationships")]
        if re.search(r"\b(ownership|voting|affiliate|governance|authority|approval)\b", sent, re.I):
            signals.append("legal_action_object")
        h._add_candidate("relationships", "control_authority", {"from_entity": extract_subject(sent) or "unspecified", "to_entity": extract_object_entity(sent) or "unspecified", "type": "control_or_authority", "description": sent}, sent, source_ref, score_confidence(0.58, signals, anti), signals, anti)

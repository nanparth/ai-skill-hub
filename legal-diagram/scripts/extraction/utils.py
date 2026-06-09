from __future__ import annotations

import re
from typing import Any, Iterable, Optional

from .lexicon import (
    ANTI_SIGNAL_PATTERNS,
    DATE_RE,
    HEADING_PRIORS,
    HEADER_SYNONYMS,
    KNOWN_ROLE_WORDS,
    MONEY_RE,
    SENTENCE_SPLIT,
    SPACE_RE,
)
from .schema import SourceRef


def classify_headers(headers: list[str]) -> dict[int, str]:
    mapped: dict[int, str] = {}
    for idx, header in enumerate(headers):
        h = norm(header)
        for canonical, synonyms in HEADER_SYNONYMS.items():
            if any(h == syn or syn in h for syn in synonyms):
                mapped[idx] = canonical
                break
    return mapped


def row_values(headers: list[str], cells: list[str], header_map: dict[int, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for idx, canonical in header_map.items():
        if idx < len(cells) and cells[idx]:
            values.setdefault(canonical, cells[idx])
    return values


def render_row_text(headers: list[str], cells: list[str]) -> str:
    parts = []
    for idx, cell in enumerate(cells):
        if not cell:
            continue
        header = headers[idx] if idx < len(headers) and headers[idx] else f"Column {idx + 1}"
        parts.append(f"{header}: {cell}")
    return " | ".join(parts)


def sentences_with_offsets(text: str) -> Iterable[tuple[str, int, int]]:
    start = 0
    for part in SENTENCE_SPLIT.split(text):
        stripped = part.strip()
        if not stripped:
            start += len(part)
            continue
        pos = text.find(stripped, start)
        if pos < 0:
            pos = start
        yield stripped, pos, pos + len(stripped)
        start = pos + len(stripped)


def anti_signals(text: str) -> list[str]:
    return [name for name, rx in ANTI_SIGNAL_PATTERNS if rx.search(text)]


def heading_prior_signals(source_ref: SourceRef, field_name: str) -> list[str]:
    text = " > ".join(source_ref.heading_path)
    rx = HEADING_PRIORS.get(field_name)
    return ["heading_prior"] if rx is not None and rx.search(text) else []


def condition_corrob_signals(text: str) -> list[str]:
    signals = []
    if re.search(r"\b(shall|must|agrees?|required|obligated|pay|payment|closing|consent|deliver|certificate|notice|deadline|within|by)\b", text, re.I):
        signals.append("legal_action_object")
    if has_deadline_signal(text):
        signals.append("deadline_signal")
    return signals


def score_boost(signals: list[str]) -> float:
    weights = {
        "table_row_binding": 0.18,
        "known_party_subject": 0.08,
        "legal_action_object": 0.07,
        "deadline_signal": 0.06,
        "heading_prior": 0.05,
        "alias_match": 0.08,
        "defined_term": 0.10,
        "sender_signal": 0.04,
        "recipient_signal": 0.05,
        "payment_signal": 0.06,
        "delivery_method_signal": 0.04,
    }
    return sum(weights.get(signal, 0.0) for signal in set(signals))


def anti_penalty(anti: list[str]) -> float:
    return min(0.28, 0.07 * len(set(anti)))


def score_confidence(base: float, signals: list[str], anti: list[str]) -> float:
    return base + score_boost(signals) - anti_penalty(anti)


def extract_subject(text: str, trigger_start: Optional[int] = None) -> str:
    prefix = text[:trigger_start].strip() if trigger_start is not None else text.strip()
    if not prefix or trigger_start is None:
        m = re.match(r"^(?:The\s+)?(?P<party>[A-Z][A-Za-z0-9 .&'/-]{1,80}?|no\s+party)\s+(?:shall|must|will|agrees?|undertakes|covenants|is\s+required|is\s+obligated|is\s+responsible|may|notify|deliver|provide|pay|reimburse|fund|transfer|remit|wire)\b", text, re.I)
        return clean_party(m.group("party")) if m else ""
    prefix = re.sub(r"^(?:if|provided that|subject to|upon|following|after)\s+", "", prefix, flags=re.I).strip(" ,;:")
    if not prefix:
        return ""
    return clean_party(re.split(r",|;|\band\b", prefix)[-1].strip())


def extract_procurement_target(text: str) -> str:
    m = re.search(r"(?:shall\s+cause|cause)\s+(?P<target>[^.;,]{1,80}?)\s+to\s+", text, re.I)
    return clean_party(m.group("target")) if m else ""


def extract_payment_parties(text: str) -> tuple[str, str]:
    m = re.search(r"(?P<payer>[A-Z][A-Za-z .&']+?)\s+(?:shall\s+|must\s+|will\s+|agrees?\s+to\s+)?(?:pay|reimburse|fund|deposit|remit|wire|transfer)\s+.+?\s+to\s+(?P<payee>[A-Z][A-Za-z .&']+?)(?:\s+(?:on|within|at|by|upon|following|after)\b|[.;,]|$)", text)
    if not m:
        return extract_subject(text), ""
    return clean_party(m.group("payer")), clean_party(m.group("payee"))


def extract_notice_parties(text: str) -> tuple[str, str]:
    m = re.search(r"(?P<sender>[A-Z][A-Za-z .&']+?)\s+(?:shall\s+|must\s+|will\s+)?(?:notify|give\s+notice\s+to|send\s+notice\s+to)\s+(?P<recipient>[A-Z][A-Za-z .&']+)", text)
    if m:
        return clean_party(m.group("sender")), clean_party(m.group("recipient"))
    m = re.search(r"notice\s+shall\s+be\s+sent\s+to\s+(?P<recipient>[A-Z][A-Za-z .&']+)", text, re.I)
    return "", clean_party(m.group("recipient")) if m else ""


def extract_object_entity(text: str) -> str:
    names = extract_entity_like_names(text)
    subject = norm(extract_subject(text))
    for name in names:
        if norm(name) != subject:
            return name
    return ""


def extract_entity_like_names(text: str) -> list[str]:
    names = []
    suffix_rx = re.compile(r"\b([A-Z][A-Za-z0-9&.,' -]+?\s+(?:Inc\.?|LLC|Ltd\.?|Corp(?:oration)?\.?|Company|LP|LLP|PLC|GmbH))\b")
    for m in suffix_rx.finditer(text):
        name = clean_entity(m.group(1))
        if name and name not in names:
            names.append(name)
    return names


def has_deadline_signal(text: str) -> bool:
    return bool(DATE_RE.search(text) or re.search(r"\b(by|within|before|after|following|prior\s+to|no\s+later\s+than|not\s+later\s+than|on\s+or\s+before|promptly\s+after|as\s+soon\s+as\s+practicable|cure\s+period|written\s+notice)\b", text, re.I))


def deadline_text(text: str) -> Optional[str]:
    m = DATE_RE.search(text)
    if m:
        return m.group(0)
    m = re.search(r"\b(?:within\s+\d+\s+(?:business\s+)?days?\s+(?:after|of)|prior\s+to\s+Closing|following\s+Closing|promptly\s+after[^.;,]{0,60}|as\s+soon\s+as\s+practicable\s+after[^.;,]{0,60}|\d+\s+(?:business\s+)?days?[']?\s+(?:prior\s+)?written\s+notice)\b", text, re.I)
    return m.group(0) if m else None


def has_payment_verb(text: str) -> bool:
    return bool(re.search(r"\b(pay|reimburse|fund|deposit|remit|wire|transfer|payable|due\s+and\s+payable)\b", text, re.I))


def money_text(text: str) -> Optional[str]:
    m = MONEY_RE.search(text)
    if m:
        return m.group(0)
    m = re.search(r"\b(purchase\s+price|fee|expense|escrow\s+amount|holdback)\b", text, re.I)
    return m.group(0) if m else None


def amount_number(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[\d,]+(?:\.\d{2})?", text)
    return float(m.group(0).replace(",", "")) if m else None


def is_rep_warranty(text: str) -> bool:
    return bool(re.search(r"\b(represents\s+and\s+warrants|representations?|warranties|true\s+and\s+correct|to\s+the\s+knowledge\s+of|except\s+as\s+disclosed|set\s+forth\s+on\s+Schedule)\b", text, re.I))


def document_name(text: str) -> str:
    m = re.search(r"\b(officer's\s+certificate|secretary's\s+certificate|bring-down\s+certificate|compliance\s+certificate|executed\s+counterpart|instrument|notice|schedule|exhibit|books\s+and\s+records)\b", text, re.I)
    return m.group(0) if m else snippet(text, 90)


def control_documents(text: str) -> list[str]:
    docs = []
    for pattern in [
        r"audit\s+report",
        r"board\s+certificate",
        r"officer's\s+certificate",
        r"secretary's\s+certificate",
        r"compliance\s+certificate",
        r"evidence\s+document",
    ]:
        m = re.search(pattern, text, re.I)
        if m:
            docs.append(m.group(0))
    return uniq(docs)


def delivery_method(text: str) -> Optional[str]:
    m = re.search(r"\b(email|overnight\s+courier|certified\s+mail|personal\s+delivery)\b", text, re.I)
    return m.group(0).lower() if m else None


def rank_from_text(text: str) -> int:
    words = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
    m = re.search(r"\b(first|second|third|fourth|fifth)\b", text, re.I)
    if m:
        return words[m.group(1).lower()]
    m = re.search(r"\b(\d+)[.)]", text)
    return int(m.group(1)) if m else 1


def infer_role_from_text(text: str) -> str:
    lowered = text.lower()
    for role in KNOWN_ROLE_WORDS:
        if role in lowered:
            return role
    return "party"


def clean_value(value: dict[str, Any]) -> dict[str, Any]:
    cleaned = {}
    for key, val in value.items():
        if isinstance(val, str):
            cleaned[key] = clean_text(val)
        elif isinstance(val, list):
            cleaned[key] = [clean_text(v) if isinstance(v, str) else v for v in val if v]
        else:
            cleaned[key] = val
    return cleaned


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", str(value or "")).strip(" .,;:")


def clean_party(value: str) -> str:
    value = clean_text(value)
    value = re.sub(r"^(?:the\s+)", "", value, flags=re.I)
    value = re.sub(r"\b(?:shall|must|will|may|agrees?|undertakes|covenants)$", "", value, flags=re.I).strip()
    return value.strip(" .,;:")[:120]


def clean_entity(value: str) -> str:
    return clean_party(value).strip("()[]{}\"'")[:140]


def clean_role(value: str) -> str:
    return clean_text(value).lower()[:80]


def norm(value: str) -> str:
    return SPACE_RE.sub(" ", str(value or "").strip().lower()).strip(" .,;:")


def clamp(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 2)


def snippet(text: str, limit: int = 650) -> str:
    return clean_text(text)[:limit]


def uniq(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def neighbor_ids(block_id: str) -> list[str]:
    try:
        idx = int(block_id)
    except (TypeError, ValueError):
        return []
    return [str(max(0, idx - 1)), str(idx + 1)]


def page_from_anchor(anchor: str) -> Optional[int]:
    m = re.search(r"page(\d+)", anchor or "", re.I)
    return int(m.group(1)) if m else None


def slide_from_anchor(anchor: str) -> Optional[int]:
    m = re.search(r"slide(\d+)", anchor or "", re.I)
    return int(m.group(1)) if m else None


def sheet_from_anchor(anchor: str) -> Optional[str]:
    return str(anchor).split(":", 1)[1] if str(anchor).startswith("sheet:") else None

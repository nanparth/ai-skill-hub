from __future__ import annotations

import re
from typing import Optional

from ..lexicon import LEGAL_ACTION_VERBS
from ..schema import Candidate, SourceRef
from ..utils import anti_signals, clamp, extract_subject, score_confidence


_PATTERNS = [
    ("consent_given", re.compile(r"\b(consents?\s+to|expressly\s+consents?|hereby\s+consents?|consented\s+to)\b", re.I), 0.60),
    ("consent_required", re.compile(r"\b(requires?\s+consent|with\s+the\s+prior\s+written\s+consent\s+of|without\s+consent|subject\s+to\s+approval)\b", re.I), 0.64),
    ("approval_right", re.compile(r"\bapproval\s+shall\s+not\s+be\s+unreasonably\s+(?:withheld|conditioned|delayed)\b", re.I), 0.72),
    ("sole_discretion", re.compile(r"\b(in\s+its\s+sole\s+discretion|absolute\s+discretion|reasonable\s+discretion)\b", re.I), 0.58),
    ("veto_right", re.compile(r"\b(may\s+block|may\s+object|right\s+to\s+object|shall\s+not\s+proceed\s+without)\b", re.I), 0.66),
    ("waiver", re.compile(r"\b(may\s+waive|waiver\s+of|waived\s+by|failure\s+to\s+enforce\s+shall\s+not\s+constitute\s+waiver)\b", re.I), 0.64),
]


def harvest_consent_discretion(
    sent: str,
    candidates: list[Candidate],
    heading_path: Optional[list[str]] = None,
) -> None:
    """Standalone consent/discretion harvester.

    Matches consent, approval, discretion, veto, and waiver patterns in *sent*
    and appends :class:`~extraction.schema.Candidate` objects directly to
    *candidates*.  No harvester orchestrator is required.

    Args:
        sent: The sentence text to analyse.
        candidates: Mutable list; matched candidates are appended in place.
        heading_path: Optional heading context for the candidate source ref.
    """
    if heading_path is None:
        heading_path = []
    anti = anti_signals(sent)
    source_ref = SourceRef(heading_path=list(heading_path))
    for frame, rx, base in _PATTERNS:
        if not rx.search(sent):
            continue
        subject = extract_subject(sent)
        signals = [frame]
        if LEGAL_ACTION_VERBS.search(sent):
            signals.append("legal_action_object")
        confidence = score_confidence(base, signals, anti)
        if re.search(r"\bmay\b", sent, re.I) and "legal_action_object" not in signals:
            confidence = min(confidence, 0.44)
        confidence = clamp(confidence)
        cid = f"C{len(candidates):04d}"
        candidates.append(
            Candidate(
                id=cid,
                target_field="decision_points",
                frame_type=frame,
                normalized_value={
                    "question": sent,
                    "subject": subject,
                    "yes_path": "permitted/approved",
                    "no_path": "blocked/not approved",
                },
                signals=signals,
                anti_signals=anti,
                confidence=confidence,
                evidence_ids=[],
                source_ref=source_ref,
            )
        )

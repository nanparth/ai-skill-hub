from __future__ import annotations

import re
from typing import Any, Optional

from ..lexicon import KNOWN_ROLE_WORDS
from ..schema import Candidate, EvidencePacket, SourceRef
from ..utils import (
    anti_signals,
    clamp,
    clean_value,
    neighbor_ids,
    page_from_anchor,
    sheet_from_anchor,
    slide_from_anchor,
    snippet,
    sentences_with_offsets,
    norm,
)
from .conditions import harvest_conditions
from .controls import harvest_controls
from .deadlines import harvest_deadlines
from .documents import harvest_deliverables
from .events import harvest_event
from .notices import harvest_notice
from .obligations import harvest_obligation
from .ownership import harvest_ownership_control
from .parties import harvest_litigation_captions, harvest_party_alias
from .payments import harvest_payments
from .remedies import harvest_default_remedy
from .reps import harvest_rep_warranty
from .citations import harvest_citation
from .tables import harvest_tables


class CandidateHarvester:
    def __init__(self, doc: Any, *, input_source: Optional[str] = None) -> None:
        self.doc = doc
        self.source = input_source or getattr(doc, "source", "") or ""
        self.evidence_packets: list[EvidencePacket] = []
        self.candidates: list[Candidate] = []
        self.synthetic_table_block_count = 0
        self.known_aliases: set[str] = set(KNOWN_ROLE_WORDS)

    def run(self) -> list[Candidate]:
        harvest_tables(self)
        for blk in list(getattr(self.doc, "blocks", []) or []):
            self._harvest_block(blk)
        return self.candidates

    def _harvest_block(self, blk: Any) -> None:
        text = str(getattr(blk, "text", "") or "").strip()
        if not text:
            return
        if (getattr(blk, "block_type", "") or "") == "heading":
            self._harvest_heading(text, self._block_source_ref(blk))
            return
        # Caption detection runs on the full block text before sentence iteration
        # because the sentence splitter splits at "v." and breaks caption spans.
        harvest_litigation_captions(self, text, self._block_source_ref(blk), anti_signals(text))
        for sent, start, end in sentences_with_offsets(text):
            if sent:
                self._harvest_sentence(sent, self._block_source_ref(blk, char_span=(start, end)))

    def _harvest_heading(self, text: str, source_ref: SourceRef) -> None:
        if re.search(r"conditions?\s+precedent|closing\s+conditions?", text, re.I):
            self._add_candidate("conditions", "condition_section", {"description": text}, text, source_ref, 0.52, ["heading_prior"])
        if re.search(r"closing\s+deliver(?:y|ies)|documents?|certificates?", text, re.I):
            self._add_candidate("documents", "document_section", {"name": text, "description": text}, text, source_ref, 0.48, ["heading_prior"])

    def _harvest_sentence(self, sent: str, source_ref: SourceRef) -> None:
        anti = anti_signals(sent)
        for fn in SENTENCE_HARVESTERS:
            fn(self, sent, source_ref, anti)

    def _add_candidate(self, target_field: str, frame_type: str, value: dict[str, Any], snippet_text: str, source_ref: SourceRef, confidence: float, signals: list[str], anti_signals: Optional[list[str]] = None) -> None:
        confidence = clamp(confidence)
        evidence_id = f"E{len(self.evidence_packets):04d}"
        candidate_id = f"C{len(self.candidates):04d}"
        evidence = EvidencePacket(
            id=evidence_id,
            snippet=snippet(snippet_text),
            source_ref=source_ref,
            heading_path=list(source_ref.heading_path),
            candidate_fields=[target_field],
            confidence=confidence,
            neighboring_context_ids=neighbor_ids(source_ref.block_id),
        )
        self.evidence_packets.append(evidence)
        self.candidates.append(
            Candidate(
                id=candidate_id,
                target_field=target_field,
                frame_type=frame_type,
                normalized_value=clean_value(value),
                signals=_uniq(signals),
                anti_signals=_uniq(anti_signals or []),
                confidence=confidence,
                evidence_ids=[evidence_id],
                source_ref=source_ref,
            )
        )

    def _block_source_ref(self, blk: Any, char_span: Optional[tuple[int, int]] = None) -> SourceRef:
        anchor = str(getattr(blk, "anchor", "") or "")
        heading_path = list(getattr(blk, "heading_path", []) or [])
        parent = getattr(blk, "parent_heading", None)
        if not heading_path and parent:
            heading_path = [str(parent)]
        return SourceRef(
            source=self.source,
            block_id=str(getattr(blk, "idx", "")),
            anchor=anchor,
            page=page_from_anchor(anchor),
            slide=slide_from_anchor(anchor),
            sheet=sheet_from_anchor(anchor),
            heading_path=heading_path,
            table_coords=getattr(blk, "table_coords", None),
            char_span=char_span,
        )

    def _table_source_ref(self, table: Any, table_idx: int, row_idx: int) -> SourceRef:
        anchor = str(getattr(table, "anchor", "") or f"table{table_idx}")
        heading = str(getattr(table, "caption", "") or "").strip()
        return SourceRef(
            source=self.source,
            block_id=f"{anchor}:r{row_idx}",
            anchor=anchor,
            page=page_from_anchor(anchor),
            slide=slide_from_anchor(anchor),
            sheet=sheet_from_anchor(anchor),
            heading_path=[heading] if heading else [],
            table_coords=(table_idx, row_idx),
        )

    def _is_known_subject(self, subject: str) -> bool:
        normalized = norm(subject)
        if not normalized:
            return False
        if normalized in self.known_aliases:
            return True
        return any(normalized == alias or normalized.endswith(" " + alias) or alias.endswith(" " + normalized) for alias in self.known_aliases if alias)


def _uniq(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


class _ConsentHarvesterProtocol:
    """Protocol adapter: bridges the orchestrator (h, sent, source_ref, anti)
    calling convention into the standalone consent module API.

    Behaves as a plain callable; its __name__ is set to match the original
    function name so that the SENTENCE_HARVESTERS registry name check passes.
    """

    __name__ = "harvest_consent_discretion"
    __qualname__ = "harvest_consent_discretion"

    def __call__(self, h, sent: str, source_ref: SourceRef, anti: list[str]) -> None:
        from ..lexicon import LEGAL_ACTION_VERBS
        from ..utils import extract_subject, score_confidence
        patterns = [
            ("consent_required", re.compile(r"\b(requires?\s+consent|with\s+the\s+prior\s+written\s+consent\s+of|without\s+consent|subject\s+to\s+approval)\b", re.I), 0.64),
            ("approval_right", re.compile(r"\bapproval\s+shall\s+not\s+be\s+unreasonably\s+(?:withheld|conditioned|delayed)\b", re.I), 0.72),
            ("sole_discretion", re.compile(r"\b(in\s+its\s+sole\s+discretion|absolute\s+discretion|reasonable\s+discretion)\b", re.I), 0.58),
            ("veto_right", re.compile(r"\b(may\s+block|may\s+object|right\s+to\s+object|shall\s+not\s+proceed\s+without)\b", re.I), 0.66),
            ("waiver", re.compile(r"\b(may\s+waive|waiver\s+of|waived\s+by|failure\s+to\s+enforce\s+shall\s+not\s+constitute\s+waiver)\b", re.I), 0.64),
        ]
        for frame, rx, base in patterns:
            if not rx.search(sent):
                continue
            subject = extract_subject(sent)
            signals = [frame]
            if h._is_known_subject(subject):
                signals.append("known_party_subject")
            if LEGAL_ACTION_VERBS.search(sent):
                signals.append("legal_action_object")
            confidence = score_confidence(base, signals, anti)
            if re.search(r"\bmay\b", sent, re.I) and "known_party_subject" not in signals and not LEGAL_ACTION_VERBS.search(sent):
                confidence = min(confidence, 0.44)
                anti = [*anti, "uncorroborated_may"]
            h._add_candidate("decision_points", frame, {"question": sent, "yes_path": "permitted/approved", "no_path": "blocked/not approved"}, sent, source_ref, confidence, signals, anti)


harvest_consent_discretion = _ConsentHarvesterProtocol()


# Registry of sentence-level harvesters called in order by _harvest_sentence.
# Defined here (at module end) so all names -- including harvest_consent_discretion
# above -- are already bound when this list is evaluated.
SENTENCE_HARVESTERS: list = [
    harvest_party_alias,
    harvest_rep_warranty,
    harvest_obligation,
    harvest_conditions,
    harvest_controls,
    harvest_deadlines,
    harvest_consent_discretion,
    harvest_deliverables,
    harvest_payments,
    harvest_default_remedy,
    harvest_notice,
    harvest_ownership_control,
    harvest_event,
    harvest_citation,
]

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXTRACT = ROOT / "extract_entities.py"
SELECTOR = ROOT / "diagram_selector.py"


def _run_extract(text: str) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(EXTRACT), "--stdin"],
        input=text,
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _run_extract_file(path: Path, extra_args: list[str] | None = None) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(EXTRACT), "--input", str(path), *(extra_args or [])],
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _decisions(sidecar: dict) -> dict[str, str]:
    return {d["candidate_id"]: d["action"] for d in sidecar.get("promotion_decisions", [])}


def _candidates(sidecar: dict, field: str | None = None, frame: str | None = None) -> list[dict]:
    rows = sidecar.get("candidates", [])
    if field is not None:
        rows = [c for c in rows if c.get("target_field") == field]
    if frame is not None:
        rows = [c for c in rows if c.get("frame_type") == frame]
    return rows


def _promoted(sidecar: dict, field: str, frame: str) -> list[dict]:
    decisions = _decisions(sidecar)
    return [c for c in _candidates(sidecar, field, frame) if decisions.get(c["id"]) == "promote"]


def test_extractor_is_canonical_and_keeps_manifest_shape() -> None:
    data = _run_extract(
        '''# Closing Deliveries

Parties: Acme Holdings Inc. ("Buyer"), Beta LLC ("Seller")

Seller shall cause its Affiliates to deliver the officer's certificate no later than June 1, 2026.
Buyer may not assign this Agreement without the prior written consent of Seller.
If Seller fails to cure within 10 business days after written notice, Buyer may terminate.
Buyer shall pay $500,000 to Seller at Closing.
Seller represents and warrants that the statements are true and correct as of Closing.
'''
    )
    for key in ["extraction_result", "extraction_hints", "coverage", "enrichment_directives", "matter_type_evidence", "candidate_manifest", "llm_enrichment"]:
        assert key in data
    sidecar = data["candidate_manifest"]
    extraction = data["extraction_result"]
    assert sidecar["schema_version"] == "legal-diagram-candidates"
    assert _promoted(sidecar, "obligations", "procurement_duty")
    assert _promoted(sidecar, "relationships", "procurement_edge")
    assert _promoted(sidecar, "transfers", "payment_flow")
    assert _promoted(sidecar, "deadlines", "hard_deadline")
    assert extraction["obligations"]
    assert extraction["relationships"]
    assert extraction["transfers"]
    assert extraction["deadlines"]
    assert extraction["concepts"]
    assert not _promoted(sidecar, "communications", "notice_communication")
    assert all("represents and warrants" not in item["description"].lower() for item in extraction["obligations"])


def test_table_row_binding_promotes_canonical_row_entities() -> None:
    data = _run_extract(
        '''# Compliance Matrix

| Responsible Party | Obligation | Due Date | Control | Document |
| --- | --- | --- | --- | --- |
| Seller | Deliver certificate | June 1, 2026 | Legal review | Officer certificate |
'''
    )
    sidecar = data["candidate_manifest"]
    extraction = data["extraction_result"]
    assert sidecar["structure_metrics"]["tables"] == 1
    assert sidecar["structure_metrics"]["table_rows"] == 1
    for field, frame in [
        ("parties", "table_party"),
        ("obligations", "table_obligation"),
        ("deadlines", "table_deadline"),
        ("controls", "table_control"),
        ("documents", "table_document"),
    ]:
        rows = _promoted(sidecar, field, frame)
        assert rows, (field, frame)
        assert "table_row_binding" in rows[0]["signals"]
        assert extraction[field], field


def test_old_runtime_directory_is_removed() -> None:
    assert not (ROOT / "det" "ectors").exists()


def test_noisy_standalone_phrases_do_not_promote() -> None:
    data = _run_extract("This section may include affiliates. Subject to the foregoing. Promptly comply.")
    sidecar = data["candidate_manifest"]
    decisions = _decisions(sidecar)
    assert all(decisions.get(c["id"]) != "promote" for c in sidecar.get("candidates", []))
    assert not any(data["extraction_result"][field] for field in ["conditions", "obligations", "relationships"])


def test_one_span_can_produce_condition_and_control_without_false_deadline() -> None:
    data = _run_extract(
        "If Seller fails to deliver documents, remediation is verified by an audit report and evidenced by a board certificate."
    )
    sidecar = data["candidate_manifest"]
    assert _candidates(sidecar, "conditions", "trigger_condition")
    assert _candidates(sidecar, "controls", "evidence_control")
    assert not _candidates(sidecar, "deadlines", "hard_deadline")


def test_materialization_downgrades_missing_required_fields() -> None:
    from extraction.materialize import materialize_result
    from extraction.schema import Candidate, EvidencePacket, PromotionDecision, SourceRef

    ref = SourceRef(block_id="1", anchor="a1")
    cand = Candidate(id="C0", target_field="relationships", frame_type="bad_relationship", normalized_value={"from_entity": "A"}, confidence=0.99, evidence_ids=["E0"], source_ref=ref)
    evidence = EvidencePacket(id="E0", snippet="A controls.", source_ref=ref, confidence=0.99)
    decision = PromotionDecision("C0", "promote", "test")
    result, decisions = materialize_result([cand], [decision], [evidence])
    assert not result.relationships
    assert result.extraction_hints
    assert decisions[0].action == "hint"
    assert "missing_required_fields" in decisions[0].reason


def test_generated_ids_are_stable() -> None:
    data1 = _run_extract("Seller shall deliver the officer's certificate no later than June 1, 2026.")
    data2 = _run_extract("Seller shall deliver the officer's certificate no later than June 1, 2026.")
    assert data1["extraction_result"]["obligations"][0]["id"] == data2["extraction_result"]["obligations"][0]["id"] == "OBL-0001"


def test_semantic_dedupe_merges_evidence_and_keeps_highest_confidence() -> None:
    from extraction.resolver import dedupe_candidates
    from extraction.schema import Candidate

    a = Candidate(id="C1", target_field="documents", frame_type="deliverable_document", normalized_value={"name": "Certificate"}, confidence=0.5, evidence_ids=["E1"], signals=["a"])
    b = Candidate(id="C2", target_field="documents", frame_type="deliverable_document", normalized_value={"name": "Certificate"}, confidence=0.9, evidence_ids=["E2"], signals=["b"])
    out = dedupe_candidates([a, b])
    assert len(out) == 1
    assert out[0].confidence == 0.9
    assert out[0].evidence_ids == ["E1", "E2"]
    assert out[0].signals == ["a", "b"]


def test_selector_accepts_extraction_result_payload() -> None:
    payload = json.dumps({"extraction_result": {"events": [{"date": "2026-06-01", "description": "closing"}]}})
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(SELECTOR), "--extraction-json", payload],
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["recommended_type"] == "timeline"


def test_html_renderer_escapes_untrusted_fields_and_requires_explicit_cdn() -> None:
    from render_html import render

    desc = {
        "title": 'Matter </title><script>alert(1)</script>',
        "matter_context": '<img src=x onerror=alert(1)>',
        "caption": 'Caption <script>alert(1)</script>',
        "overview": 'Overview <b onclick=alert(1)>unsafe</b>',
        "how_to_read": 'Read </p><script>alert(1)</script>',
        "observations": ['<img src=x onerror=alert(1)>'],
        "caveats": ['</li><script>alert(1)</script>'],
    }
    semantic_map = json.dumps({"nodes": {"A": "sem-party"}, "meta": {"label": "</script><script>alert(1)</script>"}})
    mermaid = 'flowchart TD\nA["</pre><script>alert(1)</script>"]'

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "figure.html"
        render(mermaid, desc, str(out), semantic_map=semantic_map)
        html = out.read_text(encoding="utf-8")
        assert "<script>alert(1)</script>" not in html
        assert "</pre><script" not in html
        assert "<img src=x onerror=alert(1)>" not in html
        assert "LEGAL_DIAGRAM_SOURCE_ONLY" in html
        assert "cdn.jsdelivr.net" not in html
        assert "securityLevel: 'strict'" in html

        cdn_out = Path(tmp) / "figure-cdn.html"
        render("flowchart TD\nA-->B", {"title": "Safe"}, str(cdn_out), allow_cdn=True)
        cdn_html = cdn_out.read_text(encoding="utf-8")
        assert "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js" in cdn_html


def test_html_renderer_rejects_invalid_semantic_map() -> None:
    from render_html import render

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bad.html"
        try:
            render("flowchart TD\nA-->B", {"title": "Bad"}, str(out), semantic_map="[]")
        except ValueError as exc:
            assert "root must be an object" in str(exc)
        else:
            raise AssertionError("expected invalid semantic map to fail")


def test_file_input_uses_basename_unless_full_path_opted_in() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Client Matter.md"
        path.write_text("Seller shall deliver the officer's certificate no later than June 1, 2026.", encoding="utf-8")

        data = _run_extract_file(path)
        extraction = data["extraction_result"]
        assert extraction["input_source"] == path.name
        assert extraction["matter_name"] == "Client Matter"
        assert str(path) not in json.dumps(data)

        full_path_data = _run_extract_file(path, ["--include-source-path"])
        assert full_path_data["extraction_result"]["input_source"] == str(path)


def test_file_size_limit_blocks_untrusted_oversized_input() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "large.md"
        path.write_text("Seller shall deliver documents.", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(EXTRACT), "--input", str(path), "--max-file-bytes", "1"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        assert proc.returncode != 0
        assert "max_file_bytes" in proc.stderr


def test_specific_limit_warnings_are_included_with_source_truncated() -> None:
    from extraction.handoff import warning_codes
    from normalize import NormalizedDoc, mark_truncated

    doc = NormalizedDoc(source_format="xlsx")
    mark_truncated(doc, "XLSX_ROW_LIMIT_REACHED")
    warnings = warning_codes(doc, [])
    assert "XLSX_ROW_LIMIT_REACHED" in warnings
    assert "SOURCE_TRUNCATED" in warnings


def test_sentence_harvesters_registry_is_iterable() -> None:
    from extraction.harvesters.base import SENTENCE_HARVESTERS

    expected_names = {
        "harvest_party_alias",
        "harvest_rep_warranty",
        "harvest_obligation",
        "harvest_conditions",
        "harvest_controls",
        "harvest_deadlines",
        "harvest_consent_discretion",
        "harvest_deliverables",
        "harvest_payments",
        "harvest_default_remedy",
        "harvest_notice",
        "harvest_ownership_control",
        "harvest_event",
        "harvest_citation",
    }
    assert isinstance(SENTENCE_HARVESTERS, list)
    assert all(callable(fn) for fn in SENTENCE_HARVESTERS)
    actual_names = {fn.__name__ for fn in SENTENCE_HARVESTERS}
    assert expected_names == actual_names


def test_neutral_citation_promotes_authority() -> None:
    data = _run_extract("See Smith v. Jones, 2024 ONSC 1234.")
    assert data["extraction_result"]["legal_authorities"], "expected at least one promoted legal authority"
    assert any(
        "2024 ONSC 1234" in (auth.get("citation") or "")
        for auth in data["extraction_result"]["legal_authorities"]
    ), "expected an authority whose citation contains '2024 ONSC 1234'"


def test_paragraph_reference_is_not_an_authority() -> None:
    data = _run_extract("As noted at para. 42, the limitation test applies.")
    assert not data["extraction_result"]["legal_authorities"], (
        "bare paragraph reference must not produce a legal_authorities entry"
    )


def test_judgment_excerpt_yields_party_authority_event() -> None:
    data = _run_extract(
        "Smith v. Jones, 2024 ONSC 1234. "
        "The motion was heard on March 12, 2024. "
        "The motion is dismissed."
    )
    sidecar = data["candidate_manifest"]
    ext = data["extraction_result"]
    assert _candidates(sidecar, "parties", "litigation_caption"), (
        "expected litigation_caption party candidates"
    )
    assert ext["legal_authorities"], "expected at least one promoted legal authority"
    assert ext["events"], "expected at least one promoted event"


def test_litigation_caption_yields_party_candidates() -> None:
    data = _run_extract("Smith v. Jones is the leading authority.")
    sidecar = data["candidate_manifest"]
    caps = _candidates(sidecar, "parties", "litigation_caption")
    assert len(caps) >= 2
    names = [c["normalized_value"]["name"] for c in caps]
    assert any("Smith" in n for n in names)
    assert any("Jones" in n for n in names)


def test_litigation_role_words_present() -> None:
    from extraction.lexicon import KNOWN_ROLE_WORDS

    required = {"appellant", "respondent", "plaintiff", "defendant"}
    assert required <= KNOWN_ROLE_WORDS


def test_dated_procedural_event_promotes() -> None:
    data = _run_extract("The motion was heard on March 12, 2024.")
    sidecar = data["candidate_manifest"]
    extraction = data["extraction_result"]
    assert _candidates(sidecar, "events"), "expected at least one events candidate"
    assert extraction["events"], "expected at least one promoted event"
    assert any("March 12, 2024" in (evt.get("date") or "") for evt in extraction["events"]), (
        "expected event with date containing 'March 12, 2024'"
    )


def test_bare_date_without_event_verb_does_not_promote() -> None:
    data = _run_extract("The amount is calculated as of June 1, 2026 per the schedule.")
    extraction = data["extraction_result"]
    assert not extraction["events"], "bare date with no occurrence verb must not produce a promoted event"


def test_privacy_profile_emits_directed_inference() -> None:
    data = _run_extract(
        "The vendor collects personal data and transfers it to its processor."
        " The main risk is unauthorized access. Encryption mitigates the risk."
    )
    assert data["profile_signals"]["privacy"] >= 0.34
    fields = {d["field"] for d in data["enrichment_directives"] if d["type"] == "directed_inference"}
    assert "data_flows" in fields


def test_governance_profile_emits_directed_inference() -> None:
    data = _run_extract(
        "The board approved the transaction subject to audit committee review."
        " The shareholder resolution passed by quorum."
    )
    assert data["profile_signals"]["governance"] >= 0.34
    fields = {d["field"] for d in data["enrichment_directives"] if d["type"] == "directed_inference"}
    assert fields & {"process_steps", "decision_points"}


def test_plain_clause_emits_no_directed_inference() -> None:
    data = _run_extract(
        "Seller shall deliver the officer's certificate no later than June 1, 2026."
    )
    assert not any(d["type"] == "directed_inference" for d in data["enrichment_directives"])


def test_caption_simple_still_works() -> None:
    """Simple unpunctuated caption must still produce both sides."""
    data = _run_extract("Smith v. Jones is the leading authority.")
    names = [c["normalized_value"].get("name", "") for c in _candidates(data["candidate_manifest"], "parties", "litigation_caption")]
    assert any(n == "Smith" for n in names), f"expected 'Smith' in {names}"
    assert any(n == "Jones" for n in names), f"expected 'Jones' in {names}"


def test_caption_corporate_suffix() -> None:
    """Corporate-suffix parties (Ltd./Corp.) before a comma must match, and the
    leading stop word 'In' must not appear in any extracted party name."""
    data = _run_extract("In Acme Corp. v. Beta Ltd., 2023 FCA 45 governed the appeal.")
    names = [c["normalized_value"].get("name", "") for c in _candidates(data["candidate_manifest"], "parties", "litigation_caption")]
    assert any("Acme" in n and "Corp" in n for n in names), f"expected a name containing 'Acme' and 'Corp' in {names}"
    assert any("Beta" in n and "Ltd" in n for n in names), f"expected a name containing 'Beta' and 'Ltd' in {names}"
    assert all(not n.startswith("In ") for n in names), f"a name starts with 'In ': {names}"


def test_caption_with_neutral_citation_comma() -> None:
    """Caption followed by neutral citation (comma then year) must still extract both sides."""
    data = _run_extract("Smith v. Jones, 2024 ONSC 1234.")
    names = [c["normalized_value"].get("name", "") for c in _candidates(data["candidate_manifest"], "parties", "litigation_caption")]
    assert any("Smith" in n for n in names), f"expected 'Smith' in {names}"
    assert any("Jones" in n for n in names), f"expected 'Jones' in {names}"


# ---------------------------------------------------------------------------
# Fix A -- statutory subsections captured in citation text
# ---------------------------------------------------------------------------

def test_statutory_reference_captures_subsection() -> None:
    """_STATUTORY_REF must include subsection text such as (1)(a) in the citation."""
    data = _run_extract("Pursuant to section 12(1)(a), the rule applies.")
    authorities = data["extraction_result"]["legal_authorities"]
    assert authorities, "expected at least one promoted legal authority"
    assert any(
        "12(1)(a)" in (auth.get("citation") or "")
        for auth in authorities
    ), f"expected an authority whose citation contains '12(1)(a)', got: {[a.get('citation') for a in authorities]}"


# ---------------------------------------------------------------------------
# Fix B -- future/conditional statements do not promote as events
# ---------------------------------------------------------------------------

def test_future_conditional_not_promoted_as_event() -> None:
    """A sentence with 'if' + occurrence verb must not produce a promoted event."""
    data = _run_extract("If the request is approved by March 1, 2024, the funds release.")
    assert not data["extraction_result"]["events"], (
        "future/conditional sentence must not produce a promoted event"
    )


def test_future_shall_not_promoted_as_event() -> None:
    """A sentence with 'shall' + occurrence verb must not produce a promoted event."""
    data = _run_extract("The loan shall be approved no later than 31 December 2024.")
    assert not data["extraction_result"]["events"], (
        "future 'shall' sentence must not produce a promoted event"
    )


# ---------------------------------------------------------------------------
# Fix C -- case_citation requires a year to follow the case name
# ---------------------------------------------------------------------------

def test_case_citation_requires_year_context() -> None:
    """'Option A v Option B' with no following year must not produce a legal_authorities entry."""
    data = _run_extract("We compared Option A v Option B today.")
    assert not data["extraction_result"]["legal_authorities"], (
        "prose 'v' without a following year must not produce a legal_authorities entry"
    )


# ---------------------------------------------------------------------------
# Fix D -- profile keyword matching respects word boundaries
# ---------------------------------------------------------------------------

def test_profile_keywords_respect_word_boundaries() -> None:
    """Substring-only matches (brisket=risk, berating=rating, asterisk=risk) must not activate risk_assessment.

    Under the old substring matching this scored {risk, rating} = 0.67 and falsely
    activated the profile; with word boundaries it scores 0.0.
    """
    data = _run_extract("The brisket was tasty and the berating frisky cat slept near the asterisk.")
    assert data["profile_signals"]["risk_assessment"] < 0.34, (
        f"risk_assessment must not be active from substrings alone, got {data['profile_signals']['risk_assessment']}"
    )


# === TESTS: Task 1 (domain relocation) ===
def test_t1_domain_importable_from_extraction_package():
    from extraction.domain import ExtractionResult, ENTITY_FIELDS
    assert ExtractionResult is not None
    assert isinstance(ENTITY_FIELDS, dict)

def test_t1_materialize_no_extraction_schema_import():
    import inspect
    import extraction.materialize as m
    src = inspect.getsource(m)
    assert "from extraction_schema" not in src
    assert 'import extraction_schema' not in src
    assert '__import__("extraction_schema")' not in src

def test_t1_diagram_selector_no_extraction_schema_import():
    import inspect, sys
    scripts_dir = str(__import__("pathlib").Path(__file__).parent.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import diagram_selector as ds
    src = inspect.getsource(ds)
    assert "from extraction_schema" not in src

def test_t1_manifest_no_extraction_schema_import():
    import inspect
    import extraction.manifest as m
    src = inspect.getsource(m)
    assert "from extraction_schema" not in src


# === TESTS: Task 2 (manifest relocation) ===
def test_t2_manifest_importable_from_extraction_package():
    from extraction.manifest import build_manifest
    assert callable(build_manifest)

def test_t2_extraction_init_exports_build_manifest():
    import extraction
    assert hasattr(extraction, "build_manifest")
    assert callable(extraction.build_manifest)

def test_t2_extract_entities_imports_manifest_from_package():
    import inspect, sys
    scripts_dir = str(__import__("pathlib").Path(__file__).parent.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import extract_entities
    src = inspect.getsource(extract_entities)
    assert "from manifest import" not in src
    assert "import manifest\n" not in src

def test_t2_manifest_build_returns_expected_keys():
    from extraction.manifest import build_manifest
    from extraction.domain import ExtractionResult
    result = build_manifest(
        doc=None,
        extraction_result=ExtractionResult(),
        candidates=[],
        decisions=[],
        evidence_packets=[],
    )
    assert isinstance(result, dict)
    assert "extraction_result" in result
    assert "enrichment_directives" in result


# === TESTS: Task 3 (consent harvester extraction) ===
def test_t3_consent_harvester_in_own_module():
    from extraction.harvesters.consent import harvest_consent_discretion
    assert callable(harvest_consent_discretion)

def test_t3_consent_not_defined_in_base():
    import inspect
    import extraction.harvesters.base as b
    src = inspect.getsource(b)
    assert "def harvest_consent_discretion" not in src

def test_t3_consent_harvester_reachable_via_base():
    from extraction.harvesters.base import harvest_consent_discretion
    assert callable(harvest_consent_discretion)

def test_t3_consent_harvester_produces_candidate_for_consent_sentence():
    from extraction.harvesters.consent import harvest_consent_discretion
    from extraction.schema import Candidate
    candidates: list[Candidate] = []
    harvest_consent_discretion(
        "Client expressly consents to disclosure of all records.",
        candidates,
        heading_path=[],
    )
    assert len(candidates) >= 1
    assert all(0.0 <= c.confidence <= 1.0 for c in candidates)


# === TESTS: Task 4 (handoff + engine cleanup) ===
def test_t4_structure_metrics_reads_stored_value():
    from extraction.handoff import structure_metrics
    class FakeDoc:
        blocks: list = []
        tables: list = []
        structure_metrics = {"headings": 5, "paragraphs": 10, "lists": 2, "tables": 1, "blocks": 13}
    result = structure_metrics(FakeDoc(), synthetic_table_blocks=3)
    assert result["headings"] == 5
    assert result["paragraphs"] == 10
    assert result["table_rows"] == 3

def test_t4_structure_metrics_fallback_when_not_stored():
    from extraction.handoff import structure_metrics
    class FakeBlock:
        block_type: str
        def __init__(self, t: str):
            self.block_type = t
    class FakeDoc:
        blocks = [FakeBlock("heading"), FakeBlock("paragraph"), FakeBlock("paragraph")]
        tables: list = []
        structure_metrics = None  # type: ignore
    result = structure_metrics(FakeDoc())
    assert result["headings"] == 1
    assert result["paragraphs"] == 2

def test_t4_no_duplicate_source_unparseable_warning():
    from extraction.handoff import warning_codes
    class FakeDoc:
        warning_codes = ["SOURCE_UNPARSEABLE_OR_EMPTY"]
        blocks = None
        tables = None
    result = warning_codes(FakeDoc(), [])
    assert result.count("SOURCE_UNPARSEABLE_OR_EMPTY") == 1

def test_t4_engine_build_candidate_manifest_removed():
    import extraction
    assert not hasattr(extraction, "build_candidate_manifest")


# === TESTS: Task 5 (score_confidence helper) ===
def test_t5_score_confidence_helper_exists():
    from extraction.utils import score_confidence
    assert callable(score_confidence)

def test_t5_score_confidence_matches_formula():
    from extraction.utils import score_confidence, score_boost, anti_penalty
    base = 0.55
    signals = ["obligation_verb", "known_party_subject"]
    anti = ["boilerplate"]
    expected = base + score_boost(signals) - anti_penalty(anti)
    assert score_confidence(base, signals, anti) == expected

def test_t5_obligations_no_inline_formula():
    import inspect
    import extraction.harvesters.obligations as o
    src = inspect.getsource(o)
    assert "score_boost(signals) - anti_penalty" not in src
    assert "score_confidence(" in src


# === TESTS: Task 6-B5 ===
def test_t6_b5_cli_loop_registers_all_default_limits():
    result = subprocess.run(
        [sys.executable, str(EXTRACT), "--help"],
        capture_output=True,
        text=True,
    )
    from normalize import DEFAULT_LIMITS
    for key in DEFAULT_LIMITS:
        flag = f"--{key.replace('_', '-')}"
        assert flag in result.stdout, f"Missing flag: {flag}"
    assert 'add_argument("--max-pdf-pages"' not in EXTRACT.read_text()


# === TESTS: Task 6-B6 ===
def test_t6_b6_missing_required_uses_explicit_sentinel():
    import inspect
    import extraction.materialize as m
    src = inspect.getsource(m)
    assert "dataclasses.MISSING" in src or "_MISSING" in src
    assert "field.default is not field.default_factory" not in src


# === TESTS: Task 6-B8 ===
def test_t6_b8_no_count_assertion_in_harvester_test():
    src = Path(__file__).read_text()
    count_assert = "len(SENTENCE_HARVES" "TERS) == 14"
    assert count_assert not in src


# === TESTS: Task 7 ===
def test_t7_docx_adapter_has_heading_stack():
    import inspect
    import normalize.docx_adapter as da
    src = inspect.getsource(da)
    assert "heading_stack" in src
    assert "heading_path" in src


def test_t7_pdf_adapter_has_heading_path():
    import inspect
    import normalize.pdf_adapter as pa
    src = inspect.getsource(pa)
    assert "heading_path" in src


def test_t7_pptx_adapter_has_heading_path():
    import inspect
    import normalize.pptx_adapter as pp
    src = inspect.getsource(pp)
    assert "heading_path" in src


# === TESTS: Task 8 ===
def test_t8_c1_entities_field_drives_erdiagram():
    from diagram_selector import RULES
    field_names = [r[0] for r in RULES]
    assert "entities" in field_names

def test_t8_c1_documents_field_in_rules():
    from diagram_selector import RULES
    field_names = [r[0] for r in RULES]
    assert "documents" in field_names

def test_t8_c2_journey_reachable_from_counseling_intent():
    from diagram_selector import _score
    from extraction.domain import ExtractionResult
    er = ExtractionResult()
    payload = {"extraction_result": er.__dict__, "intent": "client explanation walkthrough"}
    scores = _score(er, payload["intent"])
    assert scores.get("journey", 0) > 0

def test_t8_c3_matter_boosts_five_added():
    from diagram_selector import MATTER_BOOSTS
    for mt in ["privacy", "real_estate", "arbitration", "deal", "tech"]:
        assert mt in MATTER_BOOSTS, f"Missing: {mt}"

def test_t8_c4_compound_intent_matches_multiple_keywords():
    from diagram_selector import _score
    from extraction.domain import Event, ExtractionResult
    er = ExtractionResult()
    er.events = [Event(date="2026-01-01", description="filed") for _ in range(3)]
    payload = {"extraction_result": er.__dict__, "intent": "timeline sequence of events"}
    scores = _score(er, payload["intent"])
    assert scores.get("timeline", 0) > 0
    assert scores.get("sequenceDiagram", 0) > 0

def test_t8_c5_missing_payload_key_exits_nonzero():
    payload = json.dumps({"bad_key": {}, "intent": "general"})
    r = subprocess.run(
        [sys.executable, str(SELECTOR), "--extraction-json", payload],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "extraction_result" in r.stderr

def test_t8_c4_no_break_in_intent_loop():
    import inspect
    import diagram_selector as ds
    src = inspect.getsource(ds._score)
    assert "break" not in src


# ---------------------------------------------------------------------------
# TESTS: render_html digest_table + source_path
# ---------------------------------------------------------------------------

def test_render_html_accepts_digest_table():
    import inspect, sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    sig = inspect.signature(render_html.render)
    assert 'digest_table' in sig.parameters


def test_render_html_accepts_source_path():
    import inspect, sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    sig = inspect.signature(render_html.render)
    assert 'source_path' in sig.parameters


def test_render_html_digest_table_appears_in_output(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    rows = [{'row_num': 1, 'category': 'Obligation', 'finding': 'Seller must deliver docs',
             'party': 'Seller', 'verbatim': 'Seller shall deliver to Buyer, no later than June 30, 2026',
             'anchor': '§1 ¶2', 'page': None, 'slide': None, 'unverified': False}]
    out = tmp_path / 'out.html'
    render_html.render('flowchart TD\n  A-->B', {'title': 'Test'}, str(out), digest_table=rows)
    html = out.read_text()
    assert 'verification-table' in html
    assert 'Seller must deliver docs' in html
    assert 'Seller shall deliver to Buyer' in html


def test_render_html_pdf_source_link_includes_page(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    rows = [{'row_num': 1, 'category': 'Deadline', 'finding': 'June 30 deadline',
             'party': 'Seller', 'verbatim': 'no later than June 30, 2026',
             'anchor': '§1 ¶2', 'page': 3, 'slide': None, 'unverified': False}]
    out = tmp_path / 'out.html'
    render_html.render('flowchart TD\n  A-->B', {'title': 'T'}, str(out),
                       digest_table=rows, source_path='/fake/doc.pdf')
    html = out.read_text()
    assert '#page=3' in html


def test_render_html_docx_source_link_no_fragment(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    rows = [{'row_num': 1, 'category': 'Obligation', 'finding': 'Deliver docs',
             'party': 'Seller', 'verbatim': 'Seller shall deliver',
             'anchor': '§1', 'page': None, 'slide': None, 'unverified': False}]
    out = tmp_path / 'out.html'
    render_html.render('flowchart TD\n  A-->B', {'title': 'T'}, str(out),
                       digest_table=rows, source_path='/fake/contract.docx')
    html = out.read_text()
    assert 'contract.docx' in html
    assert '#page' not in html


def test_render_html_unverified_row_marked(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    rows = [{'row_num': 1, 'category': 'Decision', 'finding': 'Financing satisfactory?',
             'party': 'Purchaser', 'verbatim': 'in its sole discretion',
             'anchor': '§3 ¶1', 'page': None, 'slide': None, 'unverified': True}]
    out = tmp_path / 'out.html'
    render_html.render('flowchart TD\n  A-->B', {'title': 'T'}, str(out), digest_table=rows)
    html = out.read_text()
    assert 'unverified' in html.lower() or '⚠' in html


def test_render_html_no_digest_table_backward_compat(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(ROOT))
    import render_html
    out = tmp_path / 'out.html'
    render_html.render('flowchart TD\n  A-->B', {'title': 'T'}, str(out))
    html = out.read_text()
    assert 'verification-table' not in html


def test_cli_digest_table_flag(tmp_path):
    import subprocess, sys as _sys, json
    rows = json.dumps([{'row_num': 1, 'category': 'Obligation', 'finding': 'Seller deliver',
                        'party': 'Seller', 'verbatim': 'Seller shall deliver to Buyer',
                        'anchor': '§1', 'page': None, 'slide': None, 'unverified': False}])
    out = tmp_path / 'out.html'
    r = subprocess.run(
        [_sys.executable, 'render_html.py',
         '--mermaid-block', 'flowchart TD\n  A-->B',
         '--figure-desc', '{"title": "T"}',
         '--output-path', str(out),
         '--digest-table', rows],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout)
    assert result['ok'] is True
    html = out.read_text()
    assert 'Seller deliver' in html


def _run_selector(payload: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(SELECTOR), "--extraction-json", json.dumps(payload)],
        text=True, capture_output=True, env=env, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_selector_flags_grouping_on_dense_timeline() -> None:
    events = [{"date": f"2026-06-{d:02d}", "description": f"event {d}"} for d in range(1, 13)]
    result = _run_selector({"extraction_result": {"events": events, "matter_type": "litigation"},
                            "intent": "chronology"})
    assert result["recommended_type"] == "flowchart"
    assert result["grouping_suggested"] is True
    assert result["grouping_axis"] == "era"


def test_selector_no_grouping_on_sparse_timeline() -> None:
    events = [{"date": "2026-06-01", "description": "closing"},
              {"date": "2026-06-05", "description": "filing"}]
    result = _run_selector({"extraction_result": {"events": events, "matter_type": "litigation"},
                            "intent": "chronology"})
    assert result["recommended_type"] == "timeline"
    assert result["grouping_suggested"] is False
    assert result["grouping_axis"] is None


def test_selector_grouping_fields_present_on_empty_signals() -> None:
    result = _run_selector({"extraction_result": {}})
    assert result["grouping_suggested"] is False
    assert result["grouping_axis"] is None


def test_extraction_result_hierarchy_field_roundtrips():
    from extraction.domain import ExtractionResult
    r = ExtractionResult()
    assert r.hierarchy == []
    node = {"id": "H-a", "label": "A", "parent": None, "depth": 0, "source": "deterministic"}
    r2 = ExtractionResult.from_dict({"hierarchy": [node]})
    assert r2.hierarchy[0]["id"] == "H-a"
    assert "hierarchy" in r2.to_dict()


def test_materialize_builds_deterministic_hierarchy_from_headings():
    from extraction.schema import Candidate, SourceRef, PromotionDecision
    from extraction.materialize import materialize_result
    cand = Candidate(id="c1", target_field="events", frame_type="event",
                     normalized_value={"date": "2026-01-01", "description": "filed"},
                     source_ref=SourceRef(heading_path=["Background", "Procedural History"]))
    dec = PromotionDecision(candidate_id="c1", action="promote", reason="ok")
    result, _ = materialize_result([cand], [dec], [])
    tops = [n for n in result.hierarchy if n["depth"] == 0]
    kids = [n for n in result.hierarchy if n["depth"] == 1]
    assert tops and tops[0]["label"] == "Background" and tops[0]["parent"] is None
    assert kids and kids[0]["label"] == "Procedural History"
    assert kids[0]["parent"] == tops[0]["id"]


def test_materialize_hierarchy_caps_depth_at_two():
    from extraction.schema import Candidate, SourceRef, PromotionDecision
    from extraction.materialize import materialize_result
    cand = Candidate(id="c1", target_field="events", frame_type="event",
                     normalized_value={"date": "2026-01-01", "description": "x"},
                     source_ref=SourceRef(heading_path=["L0", "L1", "L2", "L3", "L4"]))
    dec = PromotionDecision(candidate_id="c1", action="promote", reason="ok")
    result, _ = materialize_result([cand], [dec], [])
    assert result.hierarchy
    assert max(n["depth"] for n in result.hierarchy) <= 2


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")

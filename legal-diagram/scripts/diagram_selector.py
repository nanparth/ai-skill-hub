import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extraction.domain import ExtractionResult

STATE_DIAGRAM = "stateDiagram-" + "v" + "2"

RULES = [
    ("events",             ["timeline", "gantt"],                2.0),
    ("deadlines",          ["gantt", "timeline"],                2.0),
    ("phases",             ["gantt", "timeline"],                2.5),
    ("tasks",              ["gantt"],                            2.5),
    ("ownership_links",    ["erDiagram", "flowchart"],           3.0),
    ("relationships",      ["erDiagram", "flowchart"],           1.5),
    ("entities",           ["erDiagram", "flowchart"],           1.5),
    ("documents",          ["flowchart", "requirementDiagram"],  1.0),
    ("obligations",        ["requirementDiagram", "flowchart"],  2.5),
    ("controls",           ["requirementDiagram"],               1.5),
    ("conditions",         ["flowchart", "requirementDiagram"],  2.0),
    ("states",             [STATE_DIAGRAM, "flowchart"],     2.5),
    ("transitions",        [STATE_DIAGRAM],                  2.0),
    ("decision_points",    ["flowchart"],                        2.5),
    ("process_steps",      ["flowchart", STATE_DIAGRAM],     2.5),
    ("investigation_steps",["timeline", "flowchart"],            2.0),
    ("risk_items",         ["quadrantChart"],                    3.0),
    ("negotiation_issues", ["quadrantChart"],                    3.0),
    ("transfers",          ["sequenceDiagram", "flowchart"],     2.0),
    ("claim_classes",      ["flowchart", "timeline"],            2.5),
    ("communications",     ["sequenceDiagram"],                  3.0),
    ("concepts",           ["mindmap", "flowchart"],             2.5),
    ("data_flows",         ["flowchart", "sequenceDiagram"],     2.5),
    ("witnesses",          ["mindmap"],                          2.0),
    ("legal_authorities",  ["mindmap", "flowchart"],             1.5),
    ("ip_assets",          [STATE_DIAGRAM, "timeline"],      2.0),
    ("parties",            ["sequenceDiagram", "flowchart"],     0.5),
]

INTENT_MAP = {
    "chronology": ["timeline", "gantt"], "timeline": ["timeline", "gantt"],
    "entity structure": ["erDiagram", "flowchart"], "ownership": ["erDiagram", "flowchart"],
    "compliance": ["requirementDiagram", "flowchart"], "obligations": ["requirementDiagram"],
    "workflow": ["flowchart", STATE_DIAGRAM], "process": ["flowchart"], "state": [STATE_DIAGRAM],
    "funds flow": ["sequenceDiagram", "flowchart"], "deal timeline": ["gantt"], "risk": ["quadrantChart"],
    "research": ["mindmap"], "issue tree": ["mindmap", "flowchart"], "strategy": ["quadrantChart", "mindmap"],
    "witness": ["mindmap"], "sequence": ["sequenceDiagram"],
    "client explanation": ["journey"], "client guide": ["journey"],
    "counseling": ["journey"], "explain to client": ["journey"],
    "communications": ["sequenceDiagram"], "tax structure": ["erDiagram"], "ip": [STATE_DIAGRAM],
    "bankruptcy": ["flowchart", "timeline"], "waterfall": ["flowchart", "timeline"],
}

MATTER_BOOSTS = {
    "litigation": {"timeline": 1.0, "flowchart": 0.5}, "corporate": {"erDiagram": 1.0, "gantt": 0.5},
    "compliance": {"requirementDiagram": 1.5}, "employment": {"timeline": 1.0, "flowchart": 0.5},
    "ip": {STATE_DIAGRAM: 1.5}, "bankruptcy": {"timeline": 1.0, "flowchart": 0.5}, "tax": {"erDiagram": 1.0},
    "privacy":     {"flowchart": 1.0, "sequenceDiagram": 0.5},
    "real_estate": {"gantt": 1.0, "flowchart": 0.5},
    "arbitration": {"timeline": 1.0, "sequenceDiagram": 0.5},
    "deal":        {"gantt": 1.0, "flowchart": 0.5},
    "tech":        {"requirementDiagram": 1.5},
}

def _event_text(e):
    if isinstance(e, dict):
        return e.get("description") or ""
    return getattr(e, "description", "") or ""


def _grouping_decision(r, top):
    """Phase 1 single-layer grouping: only the dense-timeline path fires.

    Returns (new_top, grouping_axis, rationale_override|None). grouping_suggested
    is derived from grouping_axis being non-null at the call site.
    """
    if top == "timeline":
        events = r.events or []
        n = len(events)
        if n > 10 or (n and sum(len(_event_text(e)) for e in events) / n > 50):
            return ("flowchart", "era",
                    f"Timeline overridden to a grouped flowchart: {n} events exceed the density "
                    f"threshold. Rendering as a vertical flowchart with era subgraphs.")
    return (top, None, None)


def _score(r, intent):
    scores = {}
    for fld, types, weight in RULES:
        items = getattr(r, fld, [])
        if items:
            boost = min(len(items) / 3.0, 2.0)
            for t in types:
                scores[t] = scores.get(t, 0) + weight * boost
    il = intent.lower()
    matched_types: set[str] = set()
    for kw, types in INTENT_MAP.items():
        if kw in il:
            for t in types:
                if t not in matched_types:
                    scores[t] = scores.get(t, 0) + 3.0
                    matched_types.add(t)
    for t, b in MATTER_BOOSTS.get((r.matter_type or "").lower(), {}).items():
        scores[t] = scores.get(t, 0) + b
    return scores

def recommend(r, intent):
    scores = _score(r, intent)
    if not scores:
        return {"recommended_type": "flowchart", "rationale": "No signals; flowchart is the versatile default.",
                "alternatives": ["mindmap", "timeline"], "confidence": 0.3,
                "grouping_suggested": False, "grouping_axis": None}
    ranked = sorted(scores, key=lambda t: scores[t], reverse=True)
    top, total = ranked[0], sum(scores.values())
    conf = round(min(scores[top] / total, 1.0), 2) if total else 0.3
    drivers = [f.replace("_", " ") for f, types, _ in RULES if top in types and getattr(r, f)]
    base_rationale = f"{top} selected based on: {', '.join(drivers) or 'intent match'}."
    new_top, grouping_axis, rationale_override = _grouping_decision(r, top)
    return {"recommended_type": new_top,
            "rationale": rationale_override or base_rationale,
            "alternatives": ranked[1:3], "confidence": conf,
            "grouping_suggested": grouping_axis is not None, "grouping_axis": grouping_axis}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--extraction-json", required=True)
    args = p.parse_args()
    try:
        payload = json.loads(args.extraction_json)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr); sys.exit(1)
    if "extraction_result" not in payload and "extraction" not in payload:
        print("Error: payload must contain 'extraction_result' key", file=sys.stderr)
        sys.exit(1)
    extraction_payload = payload.get("extraction_result") or payload.get("extraction") or {}
    r = ExtractionResult.from_dict(extraction_payload)
    print(json.dumps(recommend(r, payload.get("intent", "general"))))

if __name__ == "__main__":
    main()

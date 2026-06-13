import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extraction.domain import ExtractionResult
from extraction.utils import strip_diacritics

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

# INTENT_MAP: keyword -> (target types, specificity).
#
# specificity ranks how diagram-defining a keyword is.  Shape-naming nouns
# ("chronology", "flows", "phases", "ownership structure") score 2; generic
# legal modifiers that appear across many document kinds ("compliance",
# "obligations", "deadlines", "notice periods") score 1.  Matching collects ALL
# substring hits, then the single highest-specificity hit (longest keyword breaks
# ties) becomes the dominant signal; the rest are secondary (see _score).  This is
# the longest-/most-specific-match precedence that replaces first-substring-wins.
# Structure stays data-driven so W3 can append FR keywords with their own
# specificity.  Every keyword here is a plausible generic user phrase.
INTENT_MAP: dict[str, tuple[list[str], int]] = {
    "chronology": (["timeline", "gantt"], 2), "timeline": (["timeline", "gantt"], 2),
    "entity structure": (["erDiagram", "flowchart"], 2),
    "ownership structure": (["erDiagram"], 2), "ownership": (["erDiagram", "flowchart"], 2),
    "compliance": (["requirementDiagram", "flowchart"], 1), "obligations": (["requirementDiagram"], 1),
    "workflow": (["flowchart", STATE_DIAGRAM], 2), "process": (["flowchart"], 2),
    "state": ([STATE_DIAGRAM], 2),
    "funds flow": (["sequenceDiagram", "flowchart"], 2), "deal timeline": (["gantt"], 2),
    "risk": (["quadrantChart"], 2),
    "research": (["mindmap"], 2), "issue tree": (["mindmap", "flowchart"], 2),
    "strategy": (["quadrantChart", "mindmap"], 2),
    "witness": (["mindmap"], 2), "sequence": (["sequenceDiagram"], 2),
    "client explanation": (["journey"], 2), "client guide": (["journey"], 2),
    "counseling": (["journey"], 2), "explain to client": (["journey"], 2),
    "communications": (["sequenceDiagram"], 2), "tax structure": (["erDiagram"], 2),
    "ip": ([STATE_DIAGRAM], 2),
    "bankruptcy": (["flowchart", "timeline"], 2), "waterfall": (["flowchart", "timeline"], 2),
    # Added so each diagram type is reachable by a natural generic phrase.
    "data flow": (["flowchart", "sequenceDiagram"], 2),
    "data flows": (["flowchart", "sequenceDiagram"], 2),
    "privacy flows": (["flowchart"], 2), "flows": (["flowchart"], 2),
    "phases": (["gantt", "timeline"], 2), "schedule": (["gantt", "timeline"], 2),
    "deadlines": (["gantt", "timeline"], 1),
    "compliance checklist": (["requirementDiagram"], 2),
    "checklist": (["requirementDiagram"], 2),
    "notice periods": (["requirementDiagram"], 1),
    # W3.5 FR keywords: each mirrors the (types, specificity) of its EN twin
    # concept.  Keys keep their accents; matching folds both sides (NFD-strip +
    # casefold, see _fold), so unaccented spellings such as "echeancier" match too.
    "chronologie": (["timeline", "gantt"], 2),
    "échéancier": (["gantt", "timeline"], 2),
    "organigramme": (["erDiagram", "flowchart"], 2),
    "arbre de décision": (["flowchart"], 2),
    "schéma": (["flowchart"], 2),
    "liste d'obligations": (["requirementDiagram"], 2),
    "qui-fait-quoi-quand": (["sequenceDiagram"], 2),
    "carte mentale": (["mindmap"], 2),
    "grille de priorités": (["quadrantChart"], 2),
    "carte d'expérience": (["journey"], 2),
}

# Intent boost magnitudes.  The dominant (most-specific) keyword hit decisively
# nudges its types so a clearly stated user intent can win against a diffuse
# fallback pileup; remaining hits add a smaller secondary nudge.
DOMINANT_INTENT_BOOST = 8.0
SECONDARY_INTENT_BOOST = 2.0

# Non-primary types inside one RULES entry are fallbacks; they earn this fraction
# of the rule weight.  Without it, a catch-all fallback (flowchart appears as a
# secondary type in many rules) sponges full weight from every signal and drowns
# the document's true primary shape (defect-1 structural cause).
SECONDARY_TYPE_FACTOR = 0.6

MATTER_BOOSTS = {
    "litigation": {"timeline": 1.0, "flowchart": 0.5}, "corporate": {"erDiagram": 1.0, "gantt": 0.5},
    "compliance": {"requirementDiagram": 1.5}, "employment": {"timeline": 1.0, "flowchart": 0.5},
    "ip": {STATE_DIAGRAM: 1.5}, "bankruptcy": {"timeline": 1.0, "flowchart": 0.5}, "tax": {"erDiagram": 1.0},
    "privacy":     {"flowchart": 1.0, "sequenceDiagram": 0.5},
    "real_estate": {"gantt": 1.0, "flowchart": 0.5},
    "arbitration": {"timeline": 1.0, "sequenceDiagram": 0.5},
    # "deal" favours gantt strongly: a deal matter wants a closing schedule, and the
    # former flowchart secondary boost fought any schedule-naming intent (W1 calibration).
    "deal":        {"gantt": 3.0},
    "tech":        {"requirementDiagram": 1.5},
}


def _intent_types(keyword: str) -> list[str]:
    """Return the target diagram types for an INTENT_MAP keyword."""
    return INTENT_MAP[keyword][0]


def _fold(text: str) -> str:
    """Accent-insensitive comparison key: NFD-strip diacritics, then casefold.

    EN keywords contain no accents, so folding them is the identity transform and
    EN matching behaviour is unchanged (for ASCII, casefold == lower).
    Curly apostrophe (U+2019) folds to ASCII so intents typed with smart quotes
    still match keys like "liste d'obligations".
    """
    return strip_diacritics(text).replace("’", "'").casefold()


def _intent_hits(intent: str) -> list[tuple[str, list[str], int]]:
    """Collect every INTENT_MAP keyword that occurs in the intent string.

    Case- and accent-insensitive substring match: both the intent text and each
    keyword are folded via _fold, so "echeancier" matches "échéancier".  Returned
    ordered by specificity (desc), then keyword length (desc), then keyword
    alphabetically (asc) so same-specificity same-length collisions break
    deterministically by spelling, never by INTENT_MAP insertion order.  The sort
    key operates on the original keyword strings, so adding FR keys cannot perturb
    EN tie-breaks.  The first hit becomes the dominant signal.
    """
    il = _fold(intent)
    hits = [(kw, types, spec) for kw, (types, spec) in INTENT_MAP.items() if _fold(kw) in il]
    hits.sort(key=lambda h: (-h[2], -len(h[0]), h[0]))
    return hits


def _event_text(e):
    if isinstance(e, dict):
        return e.get("description") or ""
    return getattr(e, "description", "") or ""


def _grouping_decision(r, top, intent_exempt=False):
    """Phase 1 single-layer grouping: only the dense-timeline path fires.

    Returns (new_top, grouping_axis, rationale_override|None). grouping_suggested
    is derived from grouping_axis being non-null at the call site.

    intent_exempt: when the user's intent explicitly names timeline (an INTENT_MAP
    keyword resolved to timeline), the dense-timeline override is suppressed so the
    stated intent is honoured.  The no-intent path passes intent_exempt=False, so its
    10-event / 50-char boundaries are unchanged (defect-2 fix).
    """
    if top == "timeline" and not intent_exempt:
        events = r.events or []
        n = len(events)
        if n > 10 or (n and sum(len(_event_text(e)) for e in events) / n > 50):
            return ("flowchart", "era",
                    f"Timeline overridden to a grouped flowchart: {n} events exceed the density "
                    f"threshold. Rendering as a vertical flowchart with era subgraphs.")
    return (top, None, None)


def _score(r, intent):
    """Score every diagram type from structural signals, intent, and matter boosts.

    Returns the score dict.  The intent contribution uses most-specific-match
    precedence: the single dominant hit boosts its types by DOMINANT_INTENT_BOOST,
    every other hit by SECONDARY_INTENT_BOOST; a type is boosted only once.
    """
    return _score_with_intent_types(r, intent)[0]


def _score_with_intent_types(r, intent):
    """Like _score, but also return the set of intent-boosted types.

    The returned set lets recommend() decide grouping-override exemption without
    re-running keyword matching.
    """
    scores: dict[str, float] = {}
    for fld, types, weight in RULES:
        items = getattr(r, fld, [])
        if items:
            boost = min(len(items) / 3.0, 2.0)
            for idx, t in enumerate(types):
                factor = 1.0 if idx == 0 else SECONDARY_TYPE_FACTOR
                scores[t] = scores.get(t, 0) + weight * boost * factor
    matched_types: set[str] = set()
    for rank, (_kw, types, _spec) in enumerate(_intent_hits(intent)):
        amount = DOMINANT_INTENT_BOOST if rank == 0 else SECONDARY_INTENT_BOOST
        for t in types:
            if t not in matched_types:
                scores[t] = scores.get(t, 0) + amount
                matched_types.add(t)
    for t, b in MATTER_BOOSTS.get((r.matter_type or "").lower(), {}).items():
        scores[t] = scores.get(t, 0) + b
    return scores, matched_types


def _confidence(scores, top):
    """Margin-based confidence in [0, 1].

    conf = 0.9 * (top / (top + second)) + 0.1 * (top / total).

    The dominant term is the head-to-head margin between the winner and the runner-up,
    so a clear winner reports high confidence even when many other types carry small
    residual scores (the old top/total formula diluted clear winners to ~0.32-0.42 and
    would have tripped the 0.50 interrupt almost always).  The small share-of-total term
    breaks genuine ambiguity downward: when several types are near-tied the residual mass
    pulls confidence below 0.50 so the interrupt fires.  A perfect uncontested winner
    approaches 1.0; an exact two-way tie sits at 0.50; multi-way ambiguity lands below it.
    """
    ranked = sorted(scores, key=lambda t: scores[t], reverse=True)
    second = scores[ranked[1]] if len(ranked) > 1 else 0.0
    total = sum(scores.values())
    margin = scores[top] / (scores[top] + second) if (scores[top] + second) else 0.0
    share = scores[top] / total if total else 0.0
    return round(min(0.9 * margin + 0.1 * share, 1.0), 2)


def recommend(r, intent):
    scores, intent_types = _score_with_intent_types(r, intent)
    if not scores:
        return {"recommended_type": "flowchart", "rationale": "No signals; flowchart is the versatile default.",
                "alternatives": ["mindmap", "timeline"], "confidence": 0.3,
                "grouping_suggested": False, "grouping_axis": None}
    ranked = sorted(scores, key=lambda t: scores[t], reverse=True)
    top = ranked[0]
    conf = _confidence(scores, top)
    drivers = [f.replace("_", " ") for f, types, _ in RULES if top in types and getattr(r, f)]
    base_rationale = f"{top} selected based on: {', '.join(drivers) or 'intent match'}."
    new_top, grouping_axis, rationale_override = _grouping_decision(
        r, top, intent_exempt=top in intent_types)
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

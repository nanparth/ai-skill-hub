# Generation workflow (shared core)

Diagram-generation core shared by `direct.md` and `guided.md`. Lanes differ only in elicitation and confirmation; generation = identical, lives here once.

**Caller contract.** Inputs: enriched `ExtractionResult`, `intent` string (or fixed Mermaid type), `mode` (`direct` | `guided`), output preferences (HTML flag, path override).

## Step 1 — Select type

Fixed Mermaid type from caller → if type is `mindmap`, apply precision guard per `shared/diagram-type-map.md` § Mindmap scope rule before honouring it. Otherwise proceed directly. Run `python <skill-dir>/scripts/diagram_selector.py --extraction-json <enriched JSON>` with intent. Keep `recommended_type`, `rationale`, `alternatives`, `confidence`.

Confidence gate, **direct mode only** (hard cap 1): < 0.50 → present top 2 and ask once; ≥ 0.50 → proceed. Guided mode never blocks here; already showed digest and offers alternatives at delivery.

## Step 2 — Guards

Load `shared/parser-guards.md`; apply guards for type. For `erDiagram`/`flowchart`, normalise entity names per § Entity name normalization (log each substitution).

## Step 3 — Generate

Emit fenced Mermaid block natively. Truncate labels over ~40 chars. Self-check: every referenced node declared, no unclosed brackets or quotes.

**Grouping and nesting (when `grouping_suggested: true`, or `extraction_result.hierarchy` is populated).** Build containment, `flowchart TB`:
- `hierarchy` populated → nest by node depth: depth 0 = outermost subgraph, depth 1 nested inside its `parent`, depth 2 inside that. Hard cap depth 2; deeper tiers collapse to one summary node (detail → figure description).
- No `hierarchy` → one containment layer keyed by `grouping_axis`. `axis: "era"` → group events by period; chain chronologically within each.
- Each subgraph: unique alphanumeric ID (reuse the `hierarchy` node `id`), human-readable label, `direction TB`. Too many siblings in one subgraph → split by a sub-axis or summarise; never shrink.

**Readability over fit.** Never shrink, compress, or over-truncate to fit a canvas. Size to content; HTML export pans and zooms, so large-but-legible beats small-but-cramped. ~40-char node-label cap still applies; full verbatim text lives in figure description, never in a shrunken node.

## Step 3.5 — Build semantic map

After fenced Mermaid block assembled, classify all node IDs for HTML export colour layer. Load `shared/node-styles.md`.

1. **Active palette** = base 5 categories + domain extension rows matching `extraction_result.matter_type`.
2. **Deterministic pass**: for each promoted entity in `extraction_result`, look up field in § ExtractionResult field → category mapping table. Map node ID (label used in Mermaid source) to corresponding `sem-*` class. Add `sem-risk-high` to any obligation/deadline node where `risk_level == "high"`.
3. **Residual pass**: for any node ID not yet classified (subgraph labels, connector text, synthesised nodes), classify from active palette only using residual classification prompt in `shared/node-styles.md` § Residual classification. Return JSON only.
4. **Containers (grouped diagrams only)**: when the diagram uses subgraphs, map each subgraph ID to its nesting depth, `0` for the outermost layer, `1` one level in, and so on. Ungrouped diagram → omit or leave empty.
5. **Emit semantic map**:
   ```json
   {
     "meta": { "matter_type": "...", "diagram_type": "...", "active_palette": [...] },
     "nodes": { "NODE_ID": "sem-class", ... },
     "containers": { "SUBGRAPH_ID": 0, ... }
   }
   ```
   Store as `semantic_map_json` and pass to `workflows/html-export.md`. Discard if HTML export declined.

**⛔ Class name constraint.** Only use classes defined in `shared/node-styles.md` § Universal base palette and § Domain extension palettes. The valid classes are: `sem-party`, `sem-authority`, `sem-risk`, `sem-outcome`, `sem-process`, `sem-evidence`, `sem-claim`, `sem-ownership`, `sem-financial`, `sem-control`, `sem-gap`, `sem-dataflow`, `sem-finding`, `sem-ip-asset`, and modifier `sem-risk-high`. Never invent new `sem-*` class names — unlisted classes produce no colour.

**classDef injection (automatic).** `render_html.py` derives Mermaid `classDef` + `class` statements from `semantic_map.nodes` and appends them to the diagram block at render time. This is the primary node-colouring mechanism for `flowchart` and `stateDiagram` types. Do **not** emit `classDef` or `class` statements manually in the Mermaid block — `render_html.py` owns this step.

**Container shading (automatic).** `render_html.py` derives Mermaid `style <subgraph-id> fill:...` statements from `semantic_map.containers`, shading each subgraph by depth tier (light to dark, greyscale, flowchart/graph only; depth beyond tier 2 clamps). Do **not** emit container `style` statements manually. Tier shades: `shared/node-styles.md` § Container tier palette.

## Step 3.6 — Build digest table (always, unless declined)

Build `digest_rows` from `ExtractionResult` for the Source Docs tab in HTML export. **Default = always emit.** Skip only if user has explicitly said "no source table", "no verification table", or equivalent in this session.

For each populated field in `ExtractionResult` (obligations, conditions, deadlines, events, parties, decision_points, risk_items), emit one row per entity:

| Field | `row.category` |
|---|---|
| `obligations` | `Obligation` |
| `conditions` | `Condition` |
| `deadlines` | `Deadline` |
| `events` | `Key Event` |
| `parties` | `Party` |
| `decision_points` | `Decision` |
| `risk_items` | `Risk` |
| `documents` | `Document` |
| hint-only / unverified | same category + `unverified: true` |

Row fields: `row_num` (sequential), `category`, `finding` (short label), `party` (or null), `verbatim` (exact text from document — use `extraction_hints[].snippet` or `llm_enrichment.evidence_packets[].text`; never paraphrase), `anchor` (paragraph/section ref from `source_ref` or `anchor` field), `source_doc` (basename of input file).

Mark `unverified: true` for any hint-only entity or any entity where source text could not be confirmed from extraction evidence. These render with ⚠ in the table.

## Step 4 — Deliver (rationale + alternatives)

Use plain-language diagram names from `shared/diagram-type-map.md` § Plain-language names in everything user reads. Never print a Mermaid-internal type name to user.

**If `mode == "guided" and output_mode == "html"`:** skip Step 4 entirely. Diagram goes into HTML (Step 5); no raw block in chat. User already chose type at Step 2.5.

**If `mode == "guided" and output_mode == "inline"`:** show fenced Mermaid block and sanitizations only. No rationale. No alternatives. User already saw both at Step 2.5.

**If `mode == "direct"`:** full output, no preamble:
1. Fenced Mermaid block inline (block uses technical syntax; expected and fine).
2. Rationale, one plain-language line: "I drew a <plain name> because <selector rationale, rephrased plainly>."
3. Alternatives, one line: "This matter would also work as a <plain alt1> (<what it shows>) or a <plain alt2> (<what it shows>) — want either?" Pull "what it shows" from `shared/figure-description-schema.md` caption patterns. Offer only types a populated driving field supports; never list a type with no backing data.
4. Bullet list of any sanitizations (normalized names, escaped colons, truncated labels).

## Step 5 — Output

No vault note written. Output = CLI display only: fenced Mermaid block (Step 3–4) renders as artifact in Claude web app and syntax-highlighted code in CLI.

**If caller `output_mode = "html"` (chosen in guided.md Step 0.5):** re-invoke `render_html.py` with same `digest_rows` + `source_path` from Step 2, now passing `--mermaid-block` and `--figure-desc`. Produces final HTML with verification table above diagram. Confirm in plain English: "I've added the diagram to your report — [filepath]." Do **not** offer HTML again.

**If `output_mode = "inline"` or mode is `direct`:** after fenced block, offer prominently — not buried in prose:

---
**→ Get the full report as a file you can open, print, and share?** Y / n *(default Y)*

Opening it in your browser gives you the diagram plus a table showing the exact wording from your document for each item found.

---

Y or no response → load `workflows/html-export.md`. Explicit N → continue to Step 6.

## Step 6 — Refine / branch

Before refine prompt, re-surface a compact reference of diagram contents so users without Mermaid knowledge have concrete handles. Format depends on diagram type:

- **flowchart / stateDiagram / sequenceDiagram**: list subgraph/group names and the main node labels within each, e.g. "**No Written Rule** — Commissioner's Message, Rationale shifted, Not broadcast on WITV · **Minor Court Void** — Ordered charge himself, Presided as judge, Conflict admitted …"
- **erDiagram / classDiagram**: list entity names and their relationships.
- **timeline / gantt**: list section headers and key events/tasks.
- **mindmap**: list top-level branches.
- **other types**: list the primary labelled elements.

Then: "Want to change anything? Describe it in plain English, name an alternative diagram type, or type Y to export as HTML."

Accept plain-English change descriptions ("remove the Arbour point", "rename CM Pitts to Correctional Manager Pitts", "add a node for the settlement offer") → translate to structural edits before re-generating. Re-run guards on any new block. Named alternative type → fresh generation pass. If HTML was exported, re-invoke `workflows/html-export.md` in full (rebuild FigureDescription; never reuse a stale one).

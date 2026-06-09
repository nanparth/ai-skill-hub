# Parser guards (shared)

Apply guards for active diagram type before emitting block. After generation (all types): every referenced node declared, no unclosed brackets or quotes, labels within budget, one diagram per block.

|Type|Guards|
|---|---|
|`requirementDiagram`|`id:` values alphanumeric only (replace hyphens with `_`, log). Zero indentation inside `{}`. All `requirement` blocks before `element` blocks.|
|`gantt`|`dateFormat` line before `title`. Consistent date format; placeholder dates if missing. Milestone: `:milestone, YYYY-MM-DD, 0d`.|
|`state diagram`|Use the current state diagram syntax, never the older shorthand. States + transitions non-empty; warn if skeletal.|
|`mindmap`|Indentation hierarchy only, no brackets. Exactly 2 spaces per level. No circular parents.|
|`sequenceDiagram`|`autonumber` when >5 messages. Declare `participant` aliases at top.|
|`erDiagram`|Normalise entity names (below). Relationship labels double-quoted. Both cardinality ends required.|
|`flowchart`|Truncate labels >~40 chars with an ellipsis (full text → figure description, not node). Node IDs alphanumeric. Normalise names (below). When `grouping_suggested`: containment from `hierarchy` (depth ≤ 2) or one layer keyed by `grouping_axis`; subgraph IDs alphanumeric + unique; `direction TB` per tier; cross-boundary edges allowed, labelled, few.|
|`timeline`|Section headers = bare dates or month names. No colons in event labels (escape `&#58;`).|
|`quadrantChart`|x/y scores floats in `[0.0, 1.0]`. No colons in labels.|

## Grouping and readability

Applies when selector sets `grouping_suggested`.

- **Depth cap 2.** Nesting follows `extraction_result.hierarchy`; hard cap depth 2 (three levels). Deeper tiers collapse to a summary node. Each tier sets `direction`; subgraph IDs unique across all tiers.
- **Size to content, never shrink.** Never compress or shrink to fit. HTML viewer pans and zooms; large-but-legible correct, cramped not.
- **Collapse, do not shrink.** Group past readable size → collapse members into one summary node; push detail to figure description.
- **Cross-boundary edges.** Allowed, but label every wall-crossing edge; keep few. Mermaid routing degrades there.

## Entity name normalization

Before `erDiagram`/`flowchart`: node IDs reject spaces and hyphens. Apply in order; log each substitution to user ("Entity name normalised: 'Operating Sub A' → 'OperatingSubA'"):

1. Spaces removed: `Operating Sub A` → `OperatingSubA`.
2. Hyphens removed: `Sub-A` → `SubA`.
3. Leading digit → prefix `E`: `1stFinance` → `E1stFinance`.
4. Collision → numeric suffix: two `OperatingSubA` → `OperatingSubA1`, `OperatingSubA2`.

Keep original name in display label: erDiagram relationship label (double-quoted), or flowchart node text `Node[Operating Sub A]` with ID normalized.

## Confirmed bugs (project-verified)

- `requirementDiagram`: a hyphen in an `id:` value throws `Expecting 'NEWLINE', got 'LINE'` (the `-` is lexed as the `LINE` token). Use `PRIV001`, not `PRIV-001`.
- `requirementDiagram`: properties inside `{}` must be flush-left; indentation mis-tokenises and fails.
- `gantt`: missing `dateFormat`, or `dateFormat` after `title`, renders blank silently.
- `timeline`: a colon in label text breaks the parser (colon = section separator); escape as `&#58;`.
- `mindmap`: inconsistent indentation collapses the hierarchy; 2 spaces per level throughout.
- `erDiagram`: spaces and hyphens in entity names break node resolution; normalise first.
- `stateDiagram` has Mermaid 10+ rendering regressions; always use the current state diagram syntax.
- All types: labels >~60 chars overflow; truncate, keeping the full text in the figure description, not the node.

## Platform note

Fenced ` ```mermaid ` renders in any Mermaid-capable Markdown viewer (GitHub, VS Code, Obsidian, the Claude web app). HTML export prefers vendored Mermaid; uses pinned CDN fallback only when explicitly enabled. `Sankey`/`architecture`/`kanban` render unevenly; selector substitutes a portable primary (`shared/diagram-type-map.md`).

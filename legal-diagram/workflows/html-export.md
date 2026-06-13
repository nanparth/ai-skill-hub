# HTML export workflow

Optional. Builds a standalone scientific-paper-figure HTML from Mermaid block and FigureDescription via `render_html.py`. Called by `direct.md` and `tutorial.md`.

## Step 1 — Opt-in

Caller passed `html_export=true` → skip prompt. Otherwise present one line: "Export as standalone HTML? Y/N (default Y) — pan/zoom, semantic legend, save/export menu." Affirmative or no response → proceed. Explicit N → exit. "Yes, save to <path>" captures path.

## Step 2 — Collect inputs

Collect `semantic_map_json` from caller (passed from `workflows/generation.md` § Step 3.5). If absent or empty, default to `'{}'` — coloring JS no-ops gracefully and legend hidden.

Determine Mermaid asset mode. Prefer vendored file at assets/vendor/mermaid.min.js (skill-root relative, not shipped by default). If absent, do not load network JavaScript unless user or caller explicitly accepts CDN fallback; CLI flag `--allow-cdn`, pinned to Mermaid 10.9.1.

## Step 2a — Build the FigureDescription

Fields and per-type content from `shared/figure-description-schema.md`.
- `title`: `<matter_name> — <category_label>`; fallback `<category_label> — <YYYY-MM-DD>`.
- `matter_context`: matter_type + jurisdiction (if any) + one-line parties summary.
- `caption`: per-type one-line pattern.
- `overview`: 3 sentences (what it shows, why it matters to matter type, what decision it supports).
- `how_to_read`: per-type legend.
- `observations`: scan Mermaid block's structure, produce 3-5 plain-language bullets.
- `caveats`: matter-type base set + diagram-type addendum + date-validity note.

## Step 3 — Output path

User-specified path validated, else `./diagrams/` (created if absent; otherwise current directory). Filename `<matter_slug>_<diagram_type>_<YYYYMMDD>.html`. Collision appends `_2`, `_3`.

## Step 4 — Detect runtime and render

**Detect context first.** Check `render_html.py` reachable: run `python scripts/check_setup.py` or test `python --version`. Two paths:

### 4a — CLI / local Python available

`python scripts/render_html.py --mermaid-block <block> --figure-desc <JSON> --output-path <path> --semantic-map '<semantic_map_json>'`

Append `--allow-cdn` only after explicit approval for network-loaded Mermaid.

Script returns `{ok, output_path, file_size_kb}`. `PermissionError` → suggest alternative path, offer retry. Script-not-found or jinja2 missing → surface message, fall through to 4b.

### 4b — Web app / no local Python

Assemble HTML inline using same escaping rules as `render_html.py`: all matter text = text content, observations/caveats = list items, `semantic_map_json` = valid JSON inside `<script id="semantic-map" type="application/json">...</script>`. Include vendored Mermaid if available. Include pinned CDN script only after explicit approval. Emit as HTML artifact in response. Artifact panel lets user copy, open, or download directly.

## Step 5 — Confirm

**CLI path:** Print "HTML exported to: `<path>`."
**Web app path:** Print "HTML figure ready in the artifact panel — open, copy, or download from there."

HTML embeds escaped diagram source, figure description, ARIA tab panels, labelled pill controls (Zoom in, Zoom out, Reset, High contrast, Flip, Full screen), a Save / Export menu (PNG, SVG, HTML), and an Advanced editor disclosure for tweaking the Mermaid source. Fully self-contained when a vendored mermaid.min.js (assets/vendor/ under skill root) is embedded into export; otherwise shows the source-only explainer panel unless `--allow-cdn` used. Description static once generated.

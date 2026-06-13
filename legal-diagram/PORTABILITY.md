# Portability

Classification: standalone

The skill runs from a copied folder. It has no host-environment paths, no generated artifacts, no hooks, and no shared dependencies outside its own tree. Document parsing degrades gracefully: Markdown, plain text, pasted text, and conversation input need only the Python standard library, so the engine produces output before any optional parser is installed.

## Portable Surface

Everything in the folder:

- `SKILL.md`, `PORTABILITY.md`, `legal-diagram-readme.md`, `LICENSE`, `requirements.txt`, `constraints.txt`
- `workflows/` (tutorial, guided, direct, generation, extract, html-export)
- `references/` (extraction schema), `shared/` (setup check, parser guards, figure-description schema, diagram-type map, node styles, elicitation)
- `scripts/` Python engine: `check_setup.py`, `first_run.py`, `extract_entities.py`, `diagram_selector.py`, `render_html.py`, plus the `normalize/`, `extraction/`, and `tests/` packages
- `assets/html_template.html`

## Required When Copying

1. Copy the entire `legal-diagram/` folder into the host assistant's skills folder (for example `~/.claude/skills/legal-diagram/` on one common assistant; use the equivalent location for yours).
2. Python 3.9 or newer on PATH.
3. For binary formats and HTML export: `pip install -r requirements.txt -c constraints.txt`.

## Required Runtime Dependencies

- Python 3.9+. The core path (Markdown, plain text, pasted text, conversation context) uses only the standard library.

## Optional Dependencies

- `python-docx`, `PyMuPDF`, `openpyxl`, `python-pptx` — binary-format parsing (`.docx`, `.pdf`, `.xlsx`, `.pptx`). Absent → those formats are skipped; `check_setup.py` names what is missing and which formats stay available.
- `jinja2` — HTML report rendering. Absent → the diagram still generates; only the HTML export step is unavailable.
- `pdfplumber` — ruled-table extraction from PDFs. Absent → PDF degrades to text-only with warning code `PDF_TABLES_UNAVAILABLE`.
- Vendored Mermaid bundle (`assets/vendor/mermaid.min.js`, not shipped) — offline HTML rendering. Absent → the HTML report shows a source-only explainer panel unless the caller passes `--allow-cdn` to load pinned Mermaid 10.9.1 from a CDN.

## No Vault Or Personal Path Dependencies

No private vault, note system, or machine-local path is required. Chat output stays in the assistant; HTML reports write only to a user-selected path or the neutral default `./diagrams/`.

## Adapter Notes

- **Structured choice UI.** Three human gates (tutorial offer, build mode, HTML report) present as a structured choice when the host assistant supports one, otherwise a numbered list in plain text; the skill stops and waits for the reply either way.
- **Subagents.** None required. The skill runs as a single linear flow.
- **Shell + file write.** The Python scripts run via a shell and write the HTML report to a user-selected output path (default `./diagrams/`, created if absent). A read-only filesystem disables only the HTML export and the first-run state file.
- **First-run state.** `first_run.py` records whether the tutorial was offered. Path resolves `$LEGAL_DIAGRAM_STATE`, then `~/.legal-diagram/state.json`. No writable location → the detector returns `unknown` and the skill skips the first-run prompt rather than asking every session. State lives outside the folder, so the package stays standalone.
- **OS assumptions.** Pure Python on any filesystem (Linux, macOS, Windows). No platform-specific calls.

## Public Defaults

- `input_source` is basename-only by default; `--include-source-path` is an explicit opt-in for trusted provenance.
- File parsing has default caps (file size, PDF pages, DOCX paragraphs/tables/rows, PPTX slides/shapes, XLSX sheets/rows/cells). A cap hit sets `truncated=true` and emits a warning code in the manifest where a partial parse is possible.

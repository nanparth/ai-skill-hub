# Portability

Classification: standalone

The skill runs from a copied folder with no host-environment paths, generated artifacts, hooks, or shared dependencies.

## Portable Surface

Everything under `legal-diagram/`:

- `SKILL.md`, `PORTABILITY.md`, `requirements.txt`, `constraints.txt`
- `scripts/` including `check_setup.py`, `normalize/`, `extraction/`, `extract_entities.py`, `diagram_selector.py`, and `render_html.py`
- `assets/html_template.html` and an optional vendored Mermaid file under `assets/vendor/`
- `workflows/`, `shared/`, `references/`

## Required When Copying

1. Copy the entire `legal-diagram/` directory.
2. Install optional parser dependencies with `pip install -r requirements.txt -c constraints.txt` when using binary document parsing or HTML export.
3. Python 3.9+.

The Python layer degrades gracefully. Markdown, plain text, pasted text, and conversation context need only the standard library. `check_setup.py` reports exactly which libraries are missing and which input formats remain available.

## Required Runtime Dependencies

- Python 3.9+.

## Optional Dependencies

- `python-docx`, `PyMuPDF`, `openpyxl`, `python-pptx`, and `jinja2` from `requirements.txt` for binary input parsing and HTML export.
- A Mermaid-capable Markdown viewer is convenient for fenced Mermaid blocks. The standalone HTML export gives the same diagram in a browser.

## No Vault Or Personal Path Dependencies

No vault or personal path dependencies. Output is CLI display plus optional HTML export to a user-selected path.

## Adapter Notes

No external skill is invoked. Extraction is direct binary parsing, not a handoff to a separate document tool. HTML export escapes matter text, runs Mermaid in strict mode, and uses a vendored Mermaid file under `assets/vendor/` when present. If the vendored asset is absent, output is source-only unless the caller explicitly enables the pinned CDN fallback with `--allow-cdn`.

## Public Defaults

- `input_source` is basename-only by default; `--include-source-path` is an explicit opt-in.
- File parsing has default caps for file size, PDF pages, DOCX paragraphs/tables/table rows, PPTX slides/text shapes, and XLSX sheets/rows/cells. Limit hits set `truncated=true` and emit warning codes in the manifest where a partial parse is possible.
# legal-diagram

Turn legal material into a diagram. Drop a contract, paste a matter description, or describe a dispute, and the skill produces a timeline, an org chart, an obligation checklist, a decision tree, or another fitting shape. The diagram renders inline in any Mermaid-capable viewer and can be exported as a standalone HTML figure with a plain-language walkthrough.

It serves anyone who works with legal documents and wants a picture: lawyers, paralegals, students, founders reading their own contracts. No diagramming knowledge is needed. You ask in plain words ("make me an org chart"), and the skill maps it to the right diagram internally.

## Part A: User guide

### What it does

A Python engine reads the structure of your document, harvests legal candidates with evidence, promotes the high-confidence ones, and hands the uncertain gaps to the assistant. The assistant fills those gaps and picks the diagram type that fits. You get a fenced Mermaid block, an explanation of why that type was chosen, and an optional HTML report.

### Prerequisites

- Python 3.9 or newer on your PATH.
- For binary formats (`.docx`, `.pdf`, `.xlsx`, `.pptx`) and HTML export: the packages in `requirements.txt`. Markdown, plain text, pasted text, and conversation context need only the Python standard library, so you can use the skill before installing anything.

### Install

1. Copy the whole `legal-diagram/` folder into your assistant's skills folder. On one common assistant that path is `~/.claude/skills/legal-diagram/`; use the equivalent location for yours.
2. Confirm Python: `python --version` (expect 3.9+).
3. Install the optional parsers and HTML renderer:
   ```bash
   pip install -r requirements.txt -c constraints.txt
   ```
4. Verify:
   ```bash
   python scripts/check_setup.py
   ```
   Expect JSON like `{"ok": true, "installed": [...], "missing": [], "optional": {...}}`. If `ok` is `false`, the `missing` list names the packages to install. `pdfplumber` is reported under `optional`; its absence does not block anything else. Markdown and pasted text work even with packages missing.

Inside the assistant, you can also just say "check setup" to run this step.

### Quick start

Drop a contract and ask for a picture. Each choice below is a structured pick (a button-style choice where the host supports one, otherwise a numbered list), not something you type:

> You: Diagram this dispute. [attach `vendor-dispute.md`]
>
> Skill (first run only): First time here. Want a quick tutorial, or go straight to your diagram?  `[Start tutorial]`  `[Skip, straight to my diagram]`
>
> You: `[Skip, straight to my diagram]`
>
> Skill: I've read **vendor-dispute.md**. Found 2 parties, 6 events, 3 obligations. How should I build it?  `[Guided, step by step]`  `[Direct, just make it]`
>
> You: `[Direct, just make it]`
>
> Skill: I drew a **timeline** because six dated events drive a chronology. This matter would also work as an **obligation checklist** or a **party map**. Want either?
> [Mermaid timeline displayed inline, nodes coloured by semantic category]
>
> Skill: Want the full report as a file you can open, print, and share?  `[HTML report]`  `[No, just the diagram]`

That is the whole loop: a one-time tutorial offer, ingest and show what was found, choose how to build, draw the best diagram, explain why, then offer the HTML report. Returning users skip the tutorial offer automatically.

### Build modes and flags

After it ingests your material, the skill asks how to build: guided or direct. An explicit `--direct` or `--guided` flag counts as your answer and skips the prompt.

- **Guided (default).** The interactive path. It shows a plain-language digest of every field it found (parties, events, obligations, claims, and so on) for you to confirm or correct, then recommends a diagram type with a rationale and alternatives before drawing anything. With no document, it asks a short set of questions tailored to the matter type (litigation, corporate, compliance, employment, IP, privacy, bankruptcy, tax, real estate).
- **Direct (power user).** The fast path. Reads every signal in one pass and generates with at most one interruption: it stops only if extraction is empty or diagram-type confidence falls below 0.50.
- **Tutorial (first run).** A guided walkthrough that runs one worked example end to end. Offered automatically the first time, through a prompt you can decline. Start it anytime with "tutorial", "show me how", "first time", or "demo".

Other flags: `--html` pre-signals you want the HTML report (skips the prompt); `--tutorial` starts the walkthrough; `--include-source-path` records full file paths instead of basenames (for trusted local use); `--max-*` flags raise the parsing caps for trusted local inputs.

### Input formats

Markdown, plain text, `.docx`, `.pdf`, `.xlsx`, `.pptx`, pasted text, or the current conversation. Large PDFs are probed first and you are asked for a page range; scanned PDFs (no extractable text) prompt you to paste instead.

By default the skill records only the file's basename, not its full path. Default caps protect shared use: 25 MB file size, 50 PDF pages, 5000 DOCX paragraphs, 200 DOCX tables, 5000 DOCX table rows, 200 PPTX slides, 5000 PPTX text shapes, 20 XLSX sheets, 1000 XLSX rows per sheet, 50000 XLSX cells per sheet.

### Diagram names

You only ever see plain-language names: timeline, schedule, flowchart, decision tree, org chart, obligation checklist, who-does-what-when, mind map, priority grid, experience map. Ask for any by name and the skill maps it internally.

### What you get back: the HTML report

Choosing the report generates an HTML figure: the diagram plus a scientific-paper-style caption, an overview, a "how to read this" legend, key observations, and limitations. It includes:

- A semantic colour layer (parties in slate blue, authority in sage, risk in dusty rose, outcomes in stone grey), with colourblind-safe hatch patterns and a high-contrast toggle (`◐`).
- Labelled pill controls: zoom, reset, flip, full screen.
- A plain-language export menu: picture (PNG), sharp vector (SVG), or the whole page (HTML).
- An "Advanced: edit the diagram's drawing instructions" panel to tweak the source and redraw.

The export escapes all matter text and runs Mermaid in strict mode. It embeds a vendored Mermaid bundle (`assets/vendor/mermaid.min.js`) when present; otherwise it shows a source-only explainer panel unless you render with `--allow-cdn`, which loads pinned Mermaid 10.9.1 from a CDN. Output defaults to a `./diagrams/` folder (created if absent) or any path you specify.

### Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `check_setup.py` reports `ok: false` | `python-docx`, `PyMuPDF`, or `jinja2` not installed | `pip install -r requirements.txt -c constraints.txt`. Markdown and pasted text still work without them. |
| HTML export shows Mermaid source, not a rendered diagram | No vendored Mermaid asset and CDN fallback not enabled | Add a pinned `mermaid.min.js` under `assets/vendor/`, or re-export with `--allow-cdn`. |
| Diagram comes back empty from a PDF | Scanned (image-only) PDF, no extractable text | Paste the relevant text instead, or run OCR first. |
| Skill stops to ask which diagram | Selector confidence below 0.50 on thin input | Give a clearer intent ("make a timeline") or add detail. |
| `Parse error ... Expecting 'NEWLINE'` in a requirement diagram | A hyphen in an `id:` value is lexed as a token | Use alphanumeric IDs (`PRIV001`, not `PRIV-001`). Handled automatically; see `shared/parser-guards.md`. |

## Part B: Technical reference

### Layout

```text
legal-diagram/
  SKILL.md                  Routing gate: first-run check, ingest, build-mode gate, plain-language rule
  PORTABILITY.md            Standalone classification and copy requirements
  legal-diagram-readme.md   This guide
  LICENSE                   MIT
  requirements.txt          Optional package compatibility set
  constraints.txt           Pinned release-verification versions
  workflows/                tutorial, guided, direct, generation, extract, html-export
  references/               extraction-schema.md (field catalogue, detection tiers)
  shared/                   setup-check, parser-guards, figure-description-schema,
                            diagram-type-map, node-styles, elicitation
  assets/                   html_template.html (Jinja2 HTML shell)
  scripts/                  Python engine (below)
```

The engine is a four-layer Python pipeline plus assistant-guided enrichment. `normalize/` converts any format into a structure-preserving `NormalizedDoc` (headings, lists, tables). `extraction/` harvests typed candidates with evidence provenance. The resolver promotes high-confidence candidates into a canonical `ExtractionResult` and keeps the rest as compact hints. `manifest.py` plus `workflows/extract.md` emit a stable manifest and bounded enrichment directives for unresolved evidence. The assistant applies those directives with evidence and source requirements, then `diagram_selector.py` scores the enriched result and recommends a type.

### Key scripts

| Script | Purpose | Output contract |
|---|---|---|
| `scripts/check_setup.py` | Dependency check | `{ok, missing[], installed[], optional{}}` |
| `scripts/first_run.py` | First-run state; `--mark` consumes the flag | `{state}` (`returning`/`first_run`/`unknown`) |
| `scripts/extract_entities.py` | Orchestrator: normalize → harvest → manifest | manifest JSON with `candidate_manifest`, `llm_enrichment` |
| `scripts/diagram_selector.py` | Enriched extraction + intent → type | `{recommended_type, rationale, alternatives, confidence}` |
| `scripts/render_html.py` | Mermaid + figure description → standalone HTML | `{ok, output_path, file_size_kb}` |

These CLI shapes are contracts; the workflows parse them. `scripts/normalize/` and `scripts/extraction/` are libraries used by the orchestrator.

### Dependency table

| Dependency | Needed for | If absent |
|---|---|---|
| Python 3.9+ | Everything | Hard requirement |
| (stdlib only) | Markdown, text, pasted, conversation input | Always works |
| `python-docx`, `PyMuPDF`, `openpyxl`, `python-pptx` | `.docx`/`.pdf`/`.xlsx`/`.pptx` parsing | Those formats skipped; `check_setup.py` reports |
| `jinja2` | HTML report | Diagram still generates; HTML step unavailable |
| `pdfplumber` | PDF ruled-table extraction | PDF degrades to text-only (`PDF_TABLES_UNAVAILABLE`) |
| Vendored `mermaid.min.js` | Offline HTML rendering | Source-only explainer panel unless `--allow-cdn` |

### Design notes

- **Standalone Python, no external-skill dependencies.** Extraction is direct binary parsing, not a handoff to a separate document tool. One language is simpler to copy and run.
- **Candidate-first precision.** The deterministic layer harvests broadly, but only resolver-approved candidates become canonical entities. Medium and low confidence candidates stay as hints, so the assistant fills gaps without inventing unsupported entities.
- **Evidence-bounded enrichment.** Pass 2 uses manifest directives and requires evidence plus source references for each assistant-added entity; unsupported items stay out of the result and become warnings.
- **Measured deterministic layer.** `scripts/tests/run_golden.py` and `scripts/tests/calibrate.py` check pinned manifests, selector outputs, and precision/recall for the shipped extractor.
- **Plain-language surface.** Mermaid type names never reach the user; a glossary in `shared/diagram-type-map.md` maps them to words like "org chart".
- **One generation core.** Direct and guided differ only in elicitation; the select-guard-generate-deliver core lives once in `workflows/generation.md`.
- **Deterministic Pass 1.** No wall-clock, no randomness in the scripts; results are sorted by anchor so tests reproduce.

### Tests

Every `test_*.py` under `scripts/tests/` is standalone-runnable without pytest:

```bash
for t in scripts/tests/test_*.py; do python "$t" || exit 1; done
```

`scripts/tests/run_golden.py` checks the engine against pinned golden manifests and selector outputs. `scripts/tests/calibrate.py` reports deterministic precision/recall metrics. Test fixtures under `scripts/tests/fixtures/` are synthetic legal documents with fabricated party names; no real client or personal data ships.

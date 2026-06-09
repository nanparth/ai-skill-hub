# Direct workflow

Power-user front-end. Read every signal in one pass, resolve input, hand enriched extraction to shared generation core. Hard cap of one interruption.

## Step 0 — Read all signals at once

Extract from user message: (a) input source (file path / pasted text / "use conversation"); (b) diagram type (exact Mermaid type / legal category / "recommend" / nothing); (c) output preferences (HTML flag / path override / matter_type override).

## Step 1 — Input resolution

- **File path** → load `shared/setup-check.md`, then enter `workflows/extract.md` with `skip_confirmation=true`.
- **Pasted text** → `workflows/extract.md` with `skip_confirmation=true` (pipes to `extract_entities.py --stdin`).
- **"Use conversation"** → synthesise `ExtractionResult` from context window; build coverage map by hand.
- **No input** → ask exactly one question: "What are you mapping? Paste text, drop a file path, or describe the matter."

**Interruption policy (hard cap 1).** Proceed at confidence ≥ 0.50. Halt only if (a) extraction fully empty (`is_empty()`) and no input text available, or (b) requested file does not exist.

## Step 2 — Type intent

- **Diagram type named** (plain word like "org chart" or "timeline", or technical type) → map plain word via `shared/diagram-type-map.md` § Plain-language names, then pass through fixed (core flags a clear mismatch once, then honours it).
- **Legal category given** → map via `shared/diagram-type-map.md`; ambiguous row defers to selector.
- **"Recommend" or nothing** → intent = matter type + dominant populated field.

## Step 3 — Generate

Load `workflows/generation.md` with enriched extraction, intent (or fixed type), `mode=direct`, and output preferences. Selects, guards, generates, delivers (rationale + alternatives), writes note, and runs refine loop.

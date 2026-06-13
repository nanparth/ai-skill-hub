# Multi-Part Series Convention

Load when input is N markdown files, parts of one work: book chapters, course modules, lecture series, multi-part reports. Produces consistent cross-linked notes so the set reads as one navigable series. Loaded conditionally by `rewrite-note.md` (Step 1.5) and `reformat-note.md` (Step 1.4).

## Contents

- Trigger
- One gate
- Filename scheme
- Frontmatter extension
- Navigation footer
- Grouping (tag + optional index)
- Related convention
- Batch dispatch
- Reformat-safe boundary

## Trigger

N input files share one parent work. Signals: shared `book`/`source`, sequential page ranges (`pp 1-9`, `10-36`), chapter/part numbering, or "chapters of the same book". One file alone: skip; use standard workflow.

## The one gate

Resolve once for whole set; proceed without re-asking per file:

1. **Series slug** (user-supplied): short kebab stem, e.g. `invis-hand-virtual-worlds`. Frozen for the set.
2. **Destination** (per output-default rules): in place, the outputs folder, or a named folder.

Everything else (filenames, frontmatter, nav, tag) derives deterministically from slug + reading order. Do not ask per part.

## Filename scheme

`<series-slug>-NN-<topic>.md`

- `NN` = zero-padded reading-order index. `00` for intro/preface/overview; `01`..`NN` for parts.
- `<topic>` = short kebab of the part title.
- Zero-padding makes files sort in reading order in any file list.
- Rename to this form mandatory even under "rewrite in place": in-place = folder + content overwrite, not filename preservation (see `rewrite-note.md` Step 3.8).

## Frontmatter extension

Extend the base contract (`title → created at → tags → summary`) with series keys. Canonical order:

```yaml
title:          # "Chapter N: <topic>" or "<Part label>: <topic>"
book:           # or: work / course / report  (the parent work title)
chapter:        # or: part / section / module  (integer; 0 for intro)
pages:          # source page or section range; optional
author:         # part author if it differs from the editor
editor:         # optional, edited volumes
publisher:      # optional
year:           # optional
source_type:    # carry over from extraction if present
source_file:    # carry over from extraction if present
created at:
tags:
summary:
```

Quoting rules unchanged: all scalars double-quoted; each tag item double-quoted. Same `book`/`editor`/`year` values across every part.

## Navigation footer

Last line of the body, after `## Related` and its `---` separator. Contract:

```
← Previous: [[<slug>-NN-prev|Alias]] | Next: [[<slug>-NN-next|Alias]] →
```

- `Alias` = human title (e.g. "Chapter 3: Law and Economics in a World of Dragons"). Aliases may shorten long subtitles.
- First part: `← Previous: *(none, first part)* | Next: [[..|..]] →`
- Last part: `← Previous: [[..|..]] | Next: *(none, final part)* →`
- Single-direction edges use the `*(none, ...)*` italic, never a dangling link.

## Grouping

Two mechanisms; tag preferred, index optional.

- **Series tag (preferred, lightweight).** Add `series/<slug>` to every part's `tags`. Query tag → whole set; `NN` filename gives reading order. No extra file. Add via direct YAML edit, not a scalar property setter (corrupts arrays).
- **Index / MOC note (optional).** `<slug>-index.md` listing parts in reading order, grouped by the work's parts, one-line summary each. Use when set is large or wants an annotated hub. Create as separate `new-note` action, never inside a per-file rewrite (per-invocation "never create additional notes" guardrail holds).

Prefer the tag by default. Add an index only when user asks for a hub note.

## Related convention

Per part, build `## Related` from siblings first:

- 3-4 proximate parts: previous, next, and the topically closest one or two.
- Plus the series hub (intro/`00` part, or the index note if one exists).
- Optionally 1 link to a genuinely related note outside the series if one is known; do not fabricate links to non-existent notes.

Sibling links always resolvable (same batch); no search needed.

## Batch dispatch

A series is N files, but each invocation still edits exactly one file (per-invocation guardrail intact). If the host supports subagents, the controller orchestrates N invocations in waves; otherwise process the parts sequentially with the same per-part specs:

1. Compute the deterministic spec for every part up front: final filename, full frontmatter, exact Prev/Next footer, sibling Related block.
2. Dispatch parts in waves (4-6 concurrent), or sequentially without subagent support. Hand each agent its spec verbatim, so outputs need no reconciling.
3. Verify on return: every internal link resolves, every nav footer present, no leftover old-named originals.

**Copyright-refusal gotcha.** Dispatched agents often refuse faithful full-text reproduction of the user's own already-possessed source files, reading "reproduce full verbatim text" as redistribution. Mitigate: prepend explicit framing that this is personal-use, in-place cleanup of the user's own file in their private notes, format-fixing not redistribution. This roughly halves refusals; it does not eliminate them. For any residual refusal, write that part inline yourself from the source.

## Reformat-safe boundary

The series scaffolding (frontmatter keys, nav footer, `series/<slug>` tag, index note) is additive structure only. `reformat-note.md` may add it. Reformat must still not rewrite prose: no paraphrase, no claim changes. Filename rename and tag addition are allowed under reformat as structural normalization; substantive wording stays verbatim.

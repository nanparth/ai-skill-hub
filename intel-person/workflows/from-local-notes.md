# Workflow: from-local-notes

Notes-first: read the user's existing notes, map to checklist fields.

## Inputs

- Person name (required)
- Note path(s): one or more notes containing intel about this person

## Steps

### 1. Read source notes

Read all provided note paths. If none are provided, search the user's notes folder for the person's name with whatever search the environment provides (the note app's built-in search or recursive text search).

Common note sources for intel:
- Panel/event bios, speaker bios
- Meeting prep notes
- Project notes mentioning the person
- Previously created stub or partial intel notes

### 2. Map content to checklist fields

Map each finding to checklist field:

**Extract in this order:**
1. Name and aliases (legal name vs. professional name; note any discrepancy)
2. Current role and organisation
3. Career timeline: all roles mentioned, with firms and rough dates if stated
4. Education and credentials (degrees, professional qualifications, year of call or licensure if stated)
5. Affiliations and community roles
6. Awards and recognition (with award body names)
7. Personal details (location, interests, activities)
8. Contact details if present
9. Any quotes or characterisations that inform positioning analysis

### 3. Flag gaps

Against the full checklist, mark each field as:
- `FOUND` — extracted from a note source (internal tracking only; not surfaced in compiled brief)
- `MISSING` — not mentioned in any note
- `PARTIAL` — mentioned but incomplete

`FOUND` = internal. Brief surfaces only `MISSING` and `PARTIAL`.

### 4. Decide on supplemental web research

URL provided or critical fields MISSING → pass gap list to `workflows/from-web.md`; web fills gaps; notes stay primary for FOUND.

No URL + gaps remain → flag in report; proceed with available intel. User supplements later.

### 5. Return compiled brief

```
SOURCE: <note-path>
TYPE: local-note
FIELDS EXTRACTED: [list]
CONTENT:
<extracted text, keyed by field>

GAPS: [list of MISSING / PARTIAL fields]
```

Pass to SKILL.md Step 5 (gap analysis).

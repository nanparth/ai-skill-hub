# Skill Normalization Playbook

An operational guide for turning a **personal** AI skill into a **public, plug-and-play**
one. Written for an AI agent (or a human maintainer) running the prep pass before a skill
folder is shared.

Personal skills accrete things that are fine on your own machine but break or leak in
public: absolute paths, knowledge-base (vault) links, secrets, a real name in a header, a
committed cache folder, or a quiet dependency on a *sibling* skill that won't travel with
the copy. Normalization removes those so each skill folder is **safe** and **independent**.

This file is the *how-to-execute* companion to the repo's policy docs. It does not restate
the rules in [`CONTRIBUTING.md`](./CONTRIBUTING.md) or [`SECURITY.md`](./SECURITY.md) — it
shows the method that enforces them.

---

## 1. When to run this

Run the full pass when you are about to publish, hand off, or open-source a skill that grew
out of your own workflow. Run Phase 1 (the scan) any time before a commit that adds scripts,
examples, or references.

The repo's stance (see [`README.md`](./README.md)): skills are shared *"cleaned up enough to
share,"* with no *"private documents, real client data, secrets, or local machine paths."*
This playbook is how you reach "cleaned up enough."

---

## 2. Definition of done

A normalized skill passes this acceptance test:

> The skill folder, **copied alone** into `~/.claude/skills/<name>/` (or `.agents/skills/`,
> `.github/skills/`) on a **fresh machine with no sibling folders present**, runs correctly —
> with no secrets, no personal data, no machine-local paths, and no broken or escaping
> references.

Two goals, checked separately:

- **Privacy-safe** — nothing personal or secret ships (Phase 1 + Phase 4).
- **Independent / portable** — it works standalone (Phase 2), with portability documented (Phase 5).

---

## 3. Operator-identity placeholders (fill before scanning)

The scan needs to know *your* identifiers so it can hunt for them. Fill this table in your
**working notes only** — do **not** commit it, and never paste your real values into any
shipped file (that would just move the leak). Substitute these into the Phase 1 / Phase 4
recipes.

| Token          | Meaning                                   | Example (synthetic)                 |
| -------------- | ----------------------------------------- | ----------------------------------- |
| `REAL_NAME`    | Your legal/full name                      | `Jane Doe`                          |
| `EMAIL`        | Personal email(s)                         | `jane@example.com`                  |
| `USERNAME`     | OS / GitHub username, machine login       | `jdoe`                              |
| `HOME_PATH`    | Home dir on your machine                  | `C:\Users\jdoe`, `/home/jdoe`       |
| `PROJECT_PATH` | Absolute path where the skill lives now   | `~/projects/my-skills`              |
| `VAULT_NAME`   | Knowledge-base / Obsidian vault name      | `my-vault`                          |

> The shipped skill must contain **none** of these. A real name in a `LICENSE` is the one
> conventional exception — and it is a **human decision** (see Phase 3).

---

## 4. Phase 1 — Automated secret / PII / path scan

Run each recipe from the skill (or repo) root. Patterns are [ripgrep](https://github.com/BurntSushi/ripgrep)
(`rg`); the Claude Code `Grep` tool takes the same regexes. **Most hits are benign** — the
goal is to *read each hit*, not to panic. Benign-vs-real notes are inline.

**4.1 Absolute / machine-local paths**
```
rg -n -i '[A-Za-z]:\\|/Users/|/home/|~/'
```
Real: `C:\Users\jdoe\...`, `/home/jdoe/...`, a hardcoded `PROJECT_PATH`.
Benign: documented install paths like `~/.claude/skills/<name>/`; a generic, env-overridable
`/tmp/...` default in a script.

**4.2 Operator identifiers** (substitute your Phase 3 tokens)
```
rg -n -i 'REAL_NAME|EMAIL|USERNAME|PROJECT_PATH'
```
Any hit is suspect. Expect zero. The only acceptable `REAL_NAME` hit is `LICENSE` — and only
if you chose to keep it.

**4.3 Secrets / keys / tokens**
```
rg -n -i 'api[_-]?key|secret|passw(or)?d|token|bearer|AKIA|sk-ant|sk-[A-Za-z0-9]{20}|ghp_|BEGIN (RSA|PRIVATE|OPENSSH)'
```
Real: a value assigned to one of these. Benign: prose *telling users not to commit secrets*;
domain words like *"secretary's certificate"* / *"trade secret"* in subject-matter text;
an example field like `password: string` in a code sample.

**4.4 Emails**
```
rg -n -i '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'
```
Flag anything that is **not** a reserved placeholder (`example.com`, `example.org`).

**4.5 Network bindings** (assess — do not auto-flag)
```
rg -n -i 'localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.|10\.0\.|:[0-9]{4,5}\b'
```
Fine when a server binds loopback by default and any `0.0.0.0`/remote exposure is warned
about. Flag a hardcoded private host/IP or an unwarned public bind.

**4.6 Vault / knowledge-base residue**
```
rg -n '\[\[|!\[\['
rg -n -i 'obsidian|vault|field.manual|VAULT_NAME'
```
Real: an Obsidian-style `[[wiki-link]]` to a note you don't ship; a reference to your vault.
Benign: Python list-comprehensions (`[[0] * n ...]`) and bash test syntax (`[[ -f x ]]`) —
**not** wiki-links; a `PORTABILITY.md` line that *asserts* "No vault … dependencies."

**4.7 Path-escaping references**
```
rg -n '\.\./\.\.'
```
A `../../` inside a skill almost always climbs **out** of the skill folder once it is
installed standalone. Treat every hit as a portability bug to fix in Phase 3.

**4.8 Dangling references to unshipped files**
```
rg -n '\.claude/agents/|\.agents/|\.github/'
```
Plus a grep for each **sibling skill name** in the hub. Real: a doc pointing to a companion
file/agent that isn't in this folder, or a hard load of `../<other-skill>/...`. Benign: the
README's documented *install* paths.

**4.9 Build artifacts & local files** (delete, don't ship)
```
rg --files | rg -i 'pytest_cache|__pycache__|\.pyc$|\.DS_Store|Thumbs\.db|\.log$|\.bak$'
```
These should already be in [`.gitignore`](./.gitignore) — but a folder copied before the
ignore rule took effect (or one that isn't a git repo yet) can still carry them. Remove them.

---

## 5. Phase 2 — Per-skill independence audit (fan-out)

The scan finds leaks; independence needs *reading*. For a hub with several skills, launch
**one read-only `Explore` agent per skill, in parallel** (one message, multiple tool calls).
Give each agent this checklist and an output contract.

**Each agent verifies:**

1. **Frontmatter** — `SKILL.md` has `name` (== folder name), a trigger-phrase `description`,
   and an `argument-hint`. (Convention details in §8.)
2. **References resolve** — every `workflows/…`, `references/…`, `shared/…`, `scripts/…`,
   `agents/…` path named anywhere in the skill points to a file that **exists** here.
3. **No hard cross-skill coupling** — the skill must not *require* a sibling. Optional
   interop is fine **only** when gated on *"if that skill is installed."*
4. **Dependencies declared** — third-party imports appear in `requirements.txt`
   (+ `constraints.txt` if pinned); heavy imports are lazy; the skill **degrades gracefully**
   when an optional lib is missing.
5. **OS portability** — `.sh`/bash-only scripts are documented for Windows users; paths use
   `pathlib`/equivalents, not hardcoded separators; `/tmp`-style defaults are env-overridable.
6. **Fresh-copy test** — would it run with no sibling folders and no pre-existing local state?

**Agent output contract** (one line per finding):
```
severity (BLOCKER | HIGH | MEDIUM | LOW) | file:line | what | why it breaks portability/privacy | suggested fix
```
Require a `file:line` for every claim and "verify before asserting" — especially for
"broken reference" and "missing dependency" calls.

---

## 6. Phase 3 — Fix patterns

Apply the smallest change that removes the defect. Common shapes (before → after):

- **Path-escape** — a reference that climbs out of the folder:
  `load `../../shared/x.md`` → `load `../shared/x.md``.
- **Vault wiki-link** — remove the `[[…]]` clause, or inline the content it pointed to:
  `… see [[my-field-manual]].` → (drop the clause) or paste the relevant text.
- **Dangling pointer to an unshipped file** — reword to keep the substance, drop the path:
  ``see `.claude/agents/my-operator.md``` → ``a non-interactive variant can drive the same
  contract …`` (no path).
- **Local artifact** — delete it (`.pytest_cache/`, `__pycache__/`, stray `*.log`); confirm
  `.gitignore` covers the pattern so it won't return.
- **Cosmetic doc errors** — fix typos/garbled phrases in place.

**Human-decision items — surface and ASK, do not auto-decide:**

- **Real name in `LICENSE`.** Standard for MIT, but it is the operator's legal name, public
  forever. Offer: keep, or pseudonymize to a handle/org. Apply only what they choose.
- **A referenced-but-unshipped companion file.** They may intend to ship it. Offer:
  remove the reference, stub the file, or include it. Don't silently delete the mention.

> Rule of thumb: mechanical defects (paths, links, artifacts, typos) → fix. Anything that
> changes *identity, attribution, or intended scope* → ask first.

---

## 7. Phase 4 — Verification (prove it clean)

A normalization is not done until the re-scan is empty. Re-run the targeted recipes and
confirm **zero** matches:

```
rg -n -i 'REAL_NAME|EMAIL|USERNAME'      # expect: no matches
rg -n '\.\./\.\.'                        # expect: no matches
rg -n '\[\[[^]]*manual|VAULT_NAME'       # expect: no matches (your specific vault leaks)
rg --files | rg -i 'pytest_cache|__pycache__'   # expect: no matches
```

Then, if the skill ships scripts/tests, **run them** from a clean checkout (`pytest`,
`npm test`, etc.) to confirm the fixes didn't break behavior. Re-confirm every reference the
Phase 2 agents flagged now resolves.

---

## 8. Phase 5 — Portability artifacts every skill should ship

Normalization produces documentation, not just deletions. Each skill folder should carry:

**`PORTABILITY.md`** — the repo's canonical shape (headings, in order):

```
# Portability

Classification: standalone            # or standalone_with_optional_tools

<one sentence: runs from a copied folder with no host paths / shared deps>

## Portable Surface            # (optional) the exact files/folders that make up the skill
## Required When Copying       # what to copy + runtime prerequisite (e.g. Python 3.9+)
## Required Runtime Dependencies
## Optional Dependencies
## No Vault Or Personal Path Dependencies   # required section — state outputs go to a user path
## Adapter Notes               # (optional) special integration behavior, graceful degradation
## Public Defaults             # (optional) flags, size caps, opt-ins
```

**`SKILL.md` frontmatter** — minimal, convention-matching:

```yaml
---
name: <folder-name>                 # must equal the folder name
description: '<trigger-phrase style: "Use when…" / "Generate…" + quoted signal phrases the agent listens for>'
argument-hint: '[positional] [--flags]'
# effort: high        # optional
# context: full       # optional
---
```

**Also:**

- An optional **`<skill>-readme.md`** — the human companion to `SKILL.md` (plain-language
  intro, dependency summary, workflow bullets, files-to-copy). Keep it short and conversational.
- **`requirements.txt`** (+ `constraints.txt` for pins) whenever scripts have third-party deps.
- The repo-level **[`.gitignore`](./.gitignore)** is the enforcement backstop — it already
  covers secrets, caches, OS files, local scratch, and vault/local dirs. Point to it; don't
  re-list patterns inside skills.

---

## 9. Release gate — one-page checklist

The skim-and-sign-off block. It **maps onto** the existing
[`CONTRIBUTING.md`](./CONTRIBUTING.md) "Before you contribute" list and the
[`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md) safety checklist, and
**adds** the independence checks.

Privacy-safe:
- [ ] No secrets/keys/tokens/passwords (Phase 4.3 clean).
- [ ] No `REAL_NAME` / `EMAIL` / `USERNAME` anywhere (Phase 4.2 clean); `LICENSE` name is the chosen value.
- [ ] No machine-local paths (`HOME_PATH` / `PROJECT_PATH`, drive letters) — `CONTRIBUTING.md` §"Before you contribute".
- [ ] No vault links / knowledge-base residue (Phase 4.6 clean).
- [ ] No real client/customer/legal data; all examples synthetic.
- [ ] No build artifacts or caches committed (Phase 4.9 clean).

Independent / portable:
- [ ] `SKILL.md` frontmatter valid; `name` == folder.
- [ ] Every internal reference resolves; no `../../` escapes.
- [ ] No hard sibling-skill dependency; optional interop gated on "if installed."
- [ ] Dependencies declared; optional libs degrade gracefully.
- [ ] OS assumptions documented; runs from a fresh standalone copy.
- [ ] `PORTABILITY.md` present and accurate.

---

## 10. Worked example — this hub

This repo (`legal-diagram`, `biz-interview`, `tech-blueprinting`, `tech-implement`,
`tech-refactor`) was normalized with this method. The pass:

- Ran Phase 1 across the tree, then fanned out one `Explore` agent per skill (Phase 2).
- **Findings & fixes (Phase 3):**
  - *Path-escape* — `tech-implement/references/tdd-protocol.md` loaded `../../shared/…`
    (climbs out of the skill); corrected to `../shared/…`. This was the **only** `../../`
    in the repo.
  - *Vault residue* — `biz-interview/references/interview-design-reference.md` had an
    Obsidian `[[…-field-manual]]` link to an unshipped note; the dangling clause was removed.
  - *Dangling pointer* — `tech-implement/agents/implementer.md` pointed to an unshipped
    `.claude/agents/…` operator file; reworded to keep the substance, drop the path.
  - *Local artifact* — a committed `legal-diagram/.pytest_cache/` (already in `.gitignore`)
    was deleted.
  - *Human decision* — the `LICENSE` carried the author's real legal name; per the author's
    choice it was pseudonymized to **`Nanparth`**.
  - *Cosmetic* — two garbled phrases in `legal-diagram/PORTABILITY.md` were fixed.
- **Verification (Phase 4):** re-scanned for the author's identifiers, `../../`, the vault
  link, and cache dirs — all returned zero. The personal email was scanned for and **never
  appeared**. Machine paths: none in skill content.

Every skill already shipped a `PORTABILITY.md` and a valid `SKILL.md` frontmatter, and the
inter-skill references were already optional and gated on *"if that skill is installed"* —
so the skills were independent by construction; normalization was the privacy + reference
clean-up above.

---

## Out of scope (possible follow-ups)

- Packaging this playbook as its own runnable skill.
- A CI job that runs the Phase 1 recipes on every PR.

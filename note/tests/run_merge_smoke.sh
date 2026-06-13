#!/usr/bin/env bash
# run_merge_smoke.sh — Orchestrator for /note merge smoke tests.
#
# Flow per case:
#   1. Clean and stage fixtures into the run dir (<skill-dir>/tests/.merge-run/<case>/ by default)
#   2. Record pre-merge SHA-256 hashes for each source
#   3. Print the note-merge invocation the user (or auto-mode) should run
#   4. Wait for the merged output to appear, then run verify_merge.py
#   5. Report pass/fail per case; exit non-zero if any case fails
#
# Usage:
#   bash <skill-dir>/tests/run_merge_smoke.sh [case_id...]
#   Cases: 7_1, 7_2, 7_6, 7_7, 7_8, all (default)
#   Override the staging dir with MERGE_RUN_DIR=<path>
#
# Non-interactive mode (for CI): set NONINTERACTIVE=1 and pre-run the merges,
# placing outputs at the paths printed by this script. The script will then
# only stage fixtures and run verifications.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$SKILL_DIR/fixtures/merge"
VERIFY="$SKILL_DIR/verify_merge.py"
RUN_DIR="${MERGE_RUN_DIR:-$SKILL_DIR/.merge-run}"

mkdir -p "$RUN_DIR"

NONINTERACTIVE="${NONINTERACTIVE:-0}"

# ─── Case table ──────────────────────────────────────────────────────────────
# Each case defines: sources (relative to RUN_DIR/<case>), expected output path,
# expected tags, expected created-at, expected related targets.

declare -A CASE_LABELS=(
  [7_1]="new-file merge: two short notes"
  [7_2]="absorb merge: small note into host"
  [7_6]="duplicate tags across sources"
  [7_7]="Related section deduplication"
  [7_8]="frontmatter date reconciliation"
)

stage_case() {
  local case_id="$1"
  local dest="$RUN_DIR/$case_id"
  rm -rf "$dest"
  mkdir -p "$dest"
  case "$case_id" in
    7_1)
      cp "$FIXTURE_DIR/case_7_1_new_file_a.md" "$dest/prep-tips.md"
      cp "$FIXTURE_DIR/case_7_1_new_file_b.md" "$dest/prep-brainstorming.md"
      ;;
    7_2)
      cp "$FIXTURE_DIR/case_7_2_absorb_host.md" "$dest/pitch-deck-outline.md"
      cp "$FIXTURE_DIR/case_7_2_absorb_foreign.md" "$dest/design-philosophy.md"
      ;;
    7_6)
      cp "$FIXTURE_DIR/case_7_6_tags_a.md" "$dest/tags-a.md"
      cp "$FIXTURE_DIR/case_7_6_tags_b.md" "$dest/tags-b.md"
      ;;
    7_7)
      cp "$FIXTURE_DIR/case_7_7_related_a.md" "$dest/related-a.md"
      cp "$FIXTURE_DIR/case_7_7_related_b.md" "$dest/related-b.md"
      ;;
    7_8)
      cp "$FIXTURE_DIR/case_7_8_date_a.md" "$dest/date-a.md"
      cp "$FIXTURE_DIR/case_7_8_date_b.md" "$dest/date-b.md"
      ;;
  esac
}

hash_pair() {
  local path="$1"
  local h
  h=$(sha256sum "$path" | awk '{print $1}')
  echo "$path=$h"
}

print_invocation() {
  local case_id="$1"
  local dest="$RUN_DIR/$case_id"
  echo
  echo "======================================================================"
  echo "CASE $case_id: ${CASE_LABELS[$case_id]}"
  echo "======================================================================"
  echo "Fixtures staged at: $dest"
  case "$case_id" in
    7_1)
      echo "Invoke: /note merge $dest/prep-tips.md $dest/prep-brainstorming.md"
      echo "Expected output: $dest/<derived-name>.md (in same folder as primary source)"
      ;;
    7_2)
      echo "Invoke: /note merge $dest/pitch-deck-outline.md $dest/design-philosophy.md"
      echo "Expected: host ($dest/pitch-deck-outline.md) modified in place; foreign untouched"
      ;;
    7_6)
      echo "Invoke: /note merge $dest/tags-a.md $dest/tags-b.md into $dest/tags-merged.md"
      echo "Expected output: $dest/tags-merged.md"
      ;;
    7_7)
      echo "Invoke: /note merge $dest/related-a.md $dest/related-b.md into $dest/related-merged.md"
      echo "Expected output: $dest/related-merged.md"
      ;;
    7_8)
      echo "Invoke: /note merge $dest/date-a.md $dest/date-b.md into $dest/date-merged.md"
      echo "Expected output: $dest/date-merged.md"
      ;;
  esac
}

verify_case() {
  local case_id="$1"
  local dest="$RUN_DIR/$case_id"
  local rc=0
  case "$case_id" in
    7_1)
      # Output filename is derived by the workflow; find the new .md file.
      local output
      output=$(find "$dest" -maxdepth 1 -name "*.md" ! -name "prep-tips.md" ! -name "prep-brainstorming.md" | head -n 1)
      if [[ -z "$output" ]]; then
        echo "  FAIL: no new output file found in $dest"
        return 1
      fi
      python3 "$VERIFY" \
        --output "$output" \
        --sources "$dest/prep-tips.md" "$dest/prep-brainstorming.md" \
        --expected-tags "customer-discovery,ideation,interviewing" \
        --expected-created-at "2026-02-28T14:30:00.000000-04:00" \
        --expected-related "codebook,interview-script-template,market-sizing" \
        --source-hashes-before "$(cat "$dest/.hashes")" \
        --case-label "7_1" || rc=$?
      ;;
    7_2)
      # Host is modified in place; foreign is untouched. Verify against host.
      python3 "$VERIFY" \
        --output "$dest/pitch-deck-outline.md" \
        --sources "$dest/design-philosophy.md" \
        --expected-tags "fundraising,product,startup" \
        --expected-created-at "2026-03-01T11:00:00.000000-04:00" \
        --expected-related "competitive-landscape,market-sizing,user-research-summary" \
        --source-hashes-before "$dest/design-philosophy.md=$(sha256sum "$dest/design-philosophy.md.orig" | awk '{print $1}')" \
        --case-label "7_2" || rc=$?
      ;;
    7_6)
      python3 "$VERIFY" \
        --output "$dest/tags-merged.md" \
        --sources "$dest/tags-a.md" "$dest/tags-b.md" \
        --expected-tags "a,b,c,d" \
        --source-hashes-before "$(cat "$dest/.hashes")" \
        --case-label "7_6" || rc=$?
      ;;
    7_7)
      python3 "$VERIFY" \
        --output "$dest/related-merged.md" \
        --sources "$dest/related-a.md" "$dest/related-b.md" \
        --expected-related "W,X,Y,Z" \
        --source-hashes-before "$(cat "$dest/.hashes")" \
        --case-label "7_7" || rc=$?
      ;;
    7_8)
      python3 "$VERIFY" \
        --output "$dest/date-merged.md" \
        --sources "$dest/date-a.md" "$dest/date-b.md" \
        --expected-created-at "2025-01-15T08:00:00.000000-05:00" \
        --source-hashes-before "$(cat "$dest/.hashes")" \
        --case-label "7_8" || rc=$?
      ;;
  esac
  return $rc
}

# ─── Main ────────────────────────────────────────────────────────────────────

CASES=("$@")
if [[ ${#CASES[@]} -eq 0 || "${CASES[0]}" == "all" ]]; then
  CASES=(7_1 7_2 7_6 7_7 7_8)
fi

FAILED=()

for case_id in "${CASES[@]}"; do
  if [[ -z "${CASE_LABELS[$case_id]:-}" ]]; then
    echo "Unknown case: $case_id" >&2
    continue
  fi
  stage_case "$case_id"
  dest="$RUN_DIR/$case_id"
  # Record pre-merge hashes for all staged .md files
  : > "$dest/.hashes"
  for f in "$dest"/*.md; do
    hash_pair "$f" >> "$dest/.hashes"
  done
  # For absorb case, also preserve the original host content for hash comparison
  if [[ "$case_id" == "7_2" ]]; then
    cp "$dest/design-philosophy.md" "$dest/design-philosophy.md.orig"
    cp "$dest/pitch-deck-outline.md" "$dest/pitch-deck-outline.md.orig"
  fi
  # Convert newlines to spaces for single-arg hash flag
  HASHES=$(tr '\n' ' ' < "$dest/.hashes")
  echo "$HASHES" > "$dest/.hashes"

  print_invocation "$case_id"

  if [[ "$NONINTERACTIVE" == "1" ]]; then
    echo "(NONINTERACTIVE=1: expecting output already present, skipping wait)"
  else
    echo
    read -r -p "Press ENTER once the merge has run, or 'skip' to skip this case: " resp
    if [[ "$resp" == "skip" ]]; then
      echo "  [SKIP] case $case_id"
      continue
    fi
  fi

  if verify_case "$case_id"; then
    echo "  CASE $case_id: PASS"
  else
    echo "  CASE $case_id: FAIL"
    FAILED+=("$case_id")
  fi
done

echo
echo "======================================================================"
if [[ ${#FAILED[@]} -eq 0 ]]; then
  echo "SMOKE TEST RESULT: ALL PASS"
  exit 0
else
  echo "SMOKE TEST RESULT: FAIL — cases: ${FAILED[*]}"
  exit 1
fi

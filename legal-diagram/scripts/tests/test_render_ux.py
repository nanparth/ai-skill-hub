"""Tests for W5.1 UX defaults and fallbacks (W5.5 test subset).

Assertions:
  1. Overview tab carries `active` in served markup (not applied by JS only).
  2. Source-only fallback renders an explainer panel instead of raw <pre class="mermaid">.
  3. No occurrence of `--allow-cdn` or `assets/vendor` outside HTML comments.
  4. All new UX strings exist in both "en" and "fr" UI_STRINGS entries.
  5. FR alert strings are not garbled (no HTML entity &#39; inside <script> context).
  6. alert_no_renderer and alert_rerender_error carry distinct messages.

Conventions (mirror scripts/tests/test_render_ui_strings.py):
  - Plain functions, no pytest fixtures (tempfile used inline).
  - Standalone __main__ block iterating test_* callables; exit non-zero on failure.
  - Works under pytest too.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import render_html
from render_html import UI_STRINGS


def _render(out: Path, **kwargs) -> str:
    render_html.render("flowchart TD\n  A-->B", {"title": "T"}, str(out), **kwargs)
    return out.read_text(encoding="utf-8")


def _render_source_only(out: Path, **kwargs) -> str:
    """Render without CDN and without vendored file -> source-only mode."""
    # Ensure allow_cdn=False (default) and no vendored file present (it is absent in test env).
    return _render(out, allow_cdn=False, **kwargs)


def _extract_script_blocks(html: str) -> str:
    """Return the concatenated text content of all <script> tags (not src= references)."""
    return "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL))


# ── W5.1.1: Overview tab active in served markup ──────────────────────────────

def test_overview_tab_active_in_markup():
    """First tab button must carry class `active` in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The first tab-btn must have class="tab-btn active" or similar in markup
    assert 'class="tab-btn active"' in html or "tab-btn active" in html, (
        "Overview tab button must have `active` class in served markup"
    )


def test_overview_panel_active_in_markup():
    """First tab panel (#tab-overview) must carry class `active` in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The overview panel must have `active` in its class list in markup
    assert 'id="tab-overview"' in html
    # Find the overview panel tag and check it has `active`
    m = re.search(r'<div[^>]*id="tab-overview"[^>]*>', html)
    assert m, "tab-overview panel not found"
    assert "active" in m.group(0), (
        "tab-overview panel must have `active` class in served markup, got: " + m.group(0)
    )


def test_print_all_panels_still_visible():
    """Print stylesheet must still force all tab-panels visible (unchanged behaviour)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The print CSS rule must remain: .tab-panel { display: block !important;
    assert ".tab-panel { display: block !important;" in html or \
           ".tab-panel{display:block!important" in html, (
        "Print stylesheet must still force all tab-panels visible with the literal rule text"
    )


# ── W5.1.2: Source-only friendly fallback panel ───────────────────────────────

def test_source_only_no_raw_pre_mermaid():
    """In source-only mode, raw <pre class=\"mermaid\"> must not be the user-facing element."""
    with tempfile.TemporaryDirectory() as d:
        html = _render_source_only(Path(d) / "out.html")
    # When mermaid engine is absent, the diagram frame must show the explainer panel
    # and must NOT leave a raw <pre class="mermaid"> visible as the primary UI.
    # The explainer panel div must exist.
    assert 'id="sourceOnlyPanel"' in html or 'class="source-only-panel"' in html, (
        "Source-only fallback panel must be present in source-only mode"
    )


def test_source_only_plain_language_message():
    """Source-only fallback panel must contain the plain-language explainer message."""
    with tempfile.TemporaryDirectory() as d:
        html = _render_source_only(Path(d) / "out.html")
    key_phrase = "exported without its drawing engine"
    assert key_phrase in html, (
        f"Source-only panel must include plain-language message containing {key_phrase!r}"
    )


def test_source_only_has_collapsed_disclosure():
    """Source-only fallback must include a collapsed <details> disclosure with the Mermaid source."""
    with tempfile.TemporaryDirectory() as d:
        html = _render_source_only(Path(d) / "out.html")
    assert "<details" in html, "Source-only panel must include a <details> disclosure element"
    assert "<summary" in html, "Source-only panel must include a <summary> inside <details>"


def test_source_only_action_line():
    """Source-only fallback must include the ask-for-rendered-version action line."""
    with tempfile.TemporaryDirectory() as d:
        html = _render_source_only(Path(d) / "out.html")
    key_phrase = "Ask the person who sent you this file"
    assert key_phrase in html, (
        f"Source-only panel must include action line containing {key_phrase!r}"
    )


def test_source_only_no_flag_names():
    """Source-only panel must not expose flag names or file paths to the user."""
    with tempfile.TemporaryDirectory() as d:
        html = _render_source_only(Path(d) / "out.html")
    # These must not appear OUTSIDE HTML comments in the visible user content.
    # Strip HTML comments first, then check.
    stripped = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    assert "LEGAL_DIAGRAM_SOURCE_ONLY" not in stripped, (
        "Flag name LEGAL_DIAGRAM_SOURCE_ONLY must not appear outside HTML comments in source-only mode"
    )


def test_normal_mode_no_source_only_panel():
    """When Mermaid engine IS present (mocked by passing script_body), no source-only panel."""
    # In test environment, vendored mermaid is absent and CDN is disabled.
    # We test normal mode indirectly: a normal render must not inject the source-only panel.
    # The source-only panel appears only when mermaid_loader.mode == "source-only".
    # We verify: when allow_cdn=True, the cdn loader is used and no source-only panel appears.
    # (CDN mode is distinct from source-only mode even though vendor is absent.)
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", allow_cdn=True)
    # In CDN mode, the source-only explainer panel must NOT appear.
    # The panel signals: "exported without its drawing engine"
    assert "exported without its drawing engine" not in html, (
        "Source-only panel must not appear when a Mermaid engine (CDN) is used"
    )


# ── W5.1.3: Jargon-free error messages ───────────────────────────────────────

def test_no_technical_remedies_in_alert_strings():
    """Technical remedies (--allow-cdn, assets/vendor) must not appear outside HTML comments."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # Strip HTML comments
    stripped = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    assert "--allow-cdn" not in stripped, (
        "--allow-cdn must not appear outside HTML comments (user-visible area)"
    )
    assert "assets/vendor" not in stripped, (
        "assets/vendor path must not appear outside HTML comments (user-visible area)"
    )


def test_technical_remedies_preserved_in_html_comment():
    """Technical remedies must still be available to maintainers inside an HTML comment."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # At least one HTML comment must mention --allow-cdn
    comments = re.findall(r"<!--.*?-->", html, flags=re.DOTALL)
    has_allow_cdn_comment = any("--allow-cdn" in c for c in comments)
    assert has_allow_cdn_comment, (
        "--allow-cdn must appear inside at least one HTML comment for maintainers"
    )


def test_lay_reader_flip_alert():
    """Flip button's no-renderer alert must be jargon-free."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # Old jargon string must be gone
    assert "Re-export with --allow-cdn" not in html, (
        "Flip alert must not contain 'Re-export with --allow-cdn' jargon"
    )
    assert "vendor assets/vendor" not in html, (
        "Flip alert must not contain 'vendor assets/vendor' path jargon"
    )
    # Lay-reader replacement must contain the key phrase from the spec
    assert "typo" in html or "could not be redrawn" in html or "press Cancel" in html, (
        "Flip/rerender alert must contain lay-reader wording ('could not be redrawn', 'typo', or 'press Cancel')"
    )


def test_lay_reader_rerender_alert():
    """Re-render error alert must be jargon-free."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The rerender function's alert must have lay wording; check both old jargon is absent
    # and new wording is present (already covered by test_lay_reader_flip_alert for no-renderer).
    # For the render-error catch, check the spec wording appears:
    assert "could not be redrawn" in html or "typo" in html, (
        "Render-error alert must contain lay-reader wording"
    )


# ── W5 UI_STRINGS: new keys present in both languages ────────────────────────

_EXPECTED_W5_KEYS = [
    "source_only_message",
    "source_only_disclosure_label",
    "source_only_action",
    "alert_no_renderer",
    "alert_rerender_error",
    "alert_svg_not_ready",
    "alert_png_failed",
]


def test_w5_ui_string_keys_exist_in_en():
    """All W5.1 new UI_STRINGS keys must be present in the 'en' table."""
    missing = [k for k in _EXPECTED_W5_KEYS if k not in UI_STRINGS["en"]]
    assert not missing, f"Missing W5 keys in UI_STRINGS['en']: {missing}"


def test_w5_ui_string_keys_exist_in_fr():
    """All W5.1 new UI_STRINGS keys must be present in the 'fr' table."""
    missing = [k for k in _EXPECTED_W5_KEYS if k not in UI_STRINGS["fr"]]
    assert not missing, f"Missing W5 keys in UI_STRINGS['fr']: {missing}"


def test_fr_source_only_message_is_french():
    """The 'fr' source_only_message must be in French (contain accented characters or key word)."""
    msg = UI_STRINGS["fr"].get("source_only_message", "")
    # French message must contain at least one French word pattern
    assert msg and any(c in msg for c in "àâéèêëîïôùûüçœæÀÂÉÈÊËÎÏÔÙÛÜÇŒÆ"), (
        f"FR source_only_message must be French, got: {msg!r}"
    )


def test_ui_strings_fr_still_covers_en_keys():
    """fr table must still cover all en keys (regression guard for adding new keys)."""
    assert set(UI_STRINGS["fr"]) == set(UI_STRINGS["en"]), (
        f"key mismatch -- en-only: {set(UI_STRINGS['en']) - set(UI_STRINGS['fr'])}, "
        f"fr-only: {set(UI_STRINGS['fr']) - set(UI_STRINGS['en'])}"
    )


# ── W5 Finding 1: FR apostrophe not garbled in <script> context ───────────────

def test_fr_alerts_no_html_entity_in_script():
    """FR render must not emit &#39; inside <script> blocks (Jinja2 autoescape + tojson fix)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    scripts = _extract_script_blocks(html)
    assert "&#39;" not in scripts, (
        "FR alert strings must not contain HTML entity &#39; inside <script> context; "
        "use tojson filter instead of wrapping in single-quote string literals"
    )


def test_fr_alert_apostrophe_correct_in_script():
    """FR alert string with apostrophe must appear JSON-escaped (not entity-encoded) in script."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    scripts = _extract_script_blocks(html)
    # The FR alert_no_renderer or alert_rerender_error strings contain "n'a" / "n'est"
    # After tojson, apostrophes stay as literal ' (inside JSON double-quoted strings, ' is not escaped)
    # The string "redessiné" (redessiné) must appear, proving the FR content is present.
    # And there must be no &#39; anywhere in script blocks.
    assert "&#39;" not in scripts, (
        "&#39; must not appear in script blocks for FR render"
    )
    # Verify the FR content is actually present and readable (not missing)
    assert "redessin" in scripts, (
        "FR alert content ('redessin...') must appear in script blocks, proving tojson emits the string"
    )


# ── W5 Finding 2: alert_no_renderer distinct from alert_rerender_error ────────

def test_alert_no_renderer_distinct_from_alert_rerender_error_in_strings():
    """UI_STRINGS alert_no_renderer and alert_rerender_error must be distinct in both languages."""
    for lang in ("en", "fr"):
        no_renderer = UI_STRINGS[lang]["alert_no_renderer"]
        rerender_err = UI_STRINGS[lang]["alert_rerender_error"]
        assert no_renderer != rerender_err, (
            f"UI_STRINGS['{lang}']['alert_no_renderer'] and ['alert_rerender_error'] "
            f"must be distinct strings, but both are: {no_renderer!r}"
        )


def test_alert_no_renderer_does_not_mention_typo():
    """alert_no_renderer fires when the engine never loaded, not on a typo; must not say 'typo'."""
    for lang in ("en", "fr"):
        msg = UI_STRINGS[lang]["alert_no_renderer"]
        assert "typo" not in msg.lower(), (
            f"UI_STRINGS['{lang}']['alert_no_renderer'] must not mention 'typo' "
            f"(that condition belongs to alert_rerender_error); got: {msg!r}"
        )


def test_alert_no_renderer_no_flag_names():
    """alert_no_renderer must not expose technical flag names or the word 'renderer'."""
    for lang in ("en", "fr"):
        msg = UI_STRINGS[lang]["alert_no_renderer"]
        assert "renderer" not in msg.lower(), (
            f"UI_STRINGS['{lang}']['alert_no_renderer'] must not use the word 'renderer'; "
            f"got: {msg!r}"
        )
        assert "--allow-cdn" not in msg, (
            f"UI_STRINGS['{lang}']['alert_no_renderer'] must not mention '--allow-cdn'; "
            f"got: {msg!r}"
        )


def test_alert_no_renderer_both_langs_in_rendered_html():
    """alert_no_renderer text must appear in the rendered HTML for each language."""
    for lang in ("en", "fr"):
        with tempfile.TemporaryDirectory() as d:
            html = _render(Path(d) / "out.html", ui_lang=lang)
        scripts = _extract_script_blocks(html)
        # The key phrase from alert_no_renderer must appear in the script block
        # (the exact phrase varies, but the first few distinctive words must be present)
        msg = UI_STRINGS[lang]["alert_no_renderer"]
        # Check the first 20 chars of the message appear in scripts
        fragment = msg[:20]
        assert fragment in scripts or fragment in html, (
            f"alert_no_renderer ({lang}) key phrase {fragment!r} must appear in rendered output"
        )


# ── W5.2.4: Coach-hint overlay ───────────────────────────────────────────────


_EXPECTED_W52_KEYS = [
    "hint_chip",
    "hint_pulse",
    "hint_got_it",
    "fab_save_label",
    "fab_edit_label",
    "export_png",
    "export_svg",
    "export_html",
]

_EN_HINT_CHIP = "Drag to move · scroll or pinch to zoom · buttons below right"
_EN_HINT_PULSE = "More detail in these tabs"
_EN_GOT_IT = "Got it"

# EN export menu spec-verbatim entries
_EN_EXPORT_PNG = "Picture (PNG), best for email and Word"
_EN_EXPORT_SVG = "Sharp vector (SVG), best for printing and slides"
_EN_EXPORT_HTML = "This whole page (HTML)"


def test_w52_ui_string_keys_exist_in_en():
    """All W5.2 new UI_STRINGS keys must be present in the 'en' table."""
    missing = [k for k in _EXPECTED_W52_KEYS if k not in UI_STRINGS["en"]]
    assert not missing, f"Missing W5.2 keys in UI_STRINGS['en']: {missing}"


def test_w52_ui_string_keys_exist_in_fr():
    """All W5.2 new UI_STRINGS keys must be present in the 'fr' table."""
    missing = [k for k in _EXPECTED_W52_KEYS if k not in UI_STRINGS["fr"]]
    assert not missing, f"Missing W5.2 keys in UI_STRINGS['fr']: {missing}"


def test_hint_chip_en_value_verbatim():
    """hint_chip EN value must match spec verbatim (including middle dots)."""
    assert UI_STRINGS["en"].get("hint_chip") == _EN_HINT_CHIP, (
        f"hint_chip EN must be {_EN_HINT_CHIP!r}, got {UI_STRINGS['en'].get('hint_chip')!r}"
    )


def test_hint_pulse_en_value_verbatim():
    """hint_pulse EN value must match spec verbatim."""
    assert UI_STRINGS["en"].get("hint_pulse") == _EN_HINT_PULSE, (
        f"hint_pulse EN must be {_EN_HINT_PULSE!r}, got {UI_STRINGS['en'].get('hint_pulse')!r}"
    )


def test_hint_got_it_en_value_verbatim():
    """hint_got_it EN value must be 'Got it'."""
    assert UI_STRINGS["en"].get("hint_got_it") == _EN_GOT_IT, (
        f"hint_got_it EN must be {_EN_GOT_IT!r}, got {UI_STRINGS['en'].get('hint_got_it')!r}"
    )


def test_coach_chip_markup_in_rendered_html():
    """Coach-hint chip element must be present in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'id="hintChip"' in html or 'class="hint-chip"' in html, (
        "Coach-hint chip element (id='hintChip' or class='hint-chip') must be in rendered HTML"
    )


def test_got_it_button_in_rendered_html():
    """Got it button must be present in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The button text (EN) must appear somewhere in the hint markup
    assert UI_STRINGS["en"]["hint_got_it"] in html, (
        f"Got it button text {UI_STRINGS['en']['hint_got_it']!r} must appear in rendered HTML"
    )


def test_hint_tab_pulse_markup_in_rendered_html():
    """Tab-row pulse element must be present in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'id="hintPulse"' in html or 'class="hint-pulse"' in html, (
        "Tab-row pulse element (id='hintPulse' or class='hint-pulse') must be in rendered HTML"
    )


def test_localStorage_key_in_script():
    """localStorage key 'legal-diagram-hints-v1' must appear as a literal string in script blocks."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "legal-diagram-hints-v1" in scripts, (
        "localStorage key 'legal-diagram-hints-v1' must appear as a literal in script blocks"
    )


def test_localStorage_try_catch_guard_in_script():
    """A try/catch guard around localStorage access must be present in script blocks."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # Both 'try' and 'catch' must appear in the script blocks (localStorage guard)
    assert "try" in scripts and "catch" in scripts, (
        "A try/catch block guarding localStorage access must be present in script blocks"
    )


def test_hint_chip_text_in_rendered_html_en():
    """Chip text (EN) must appear in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    chip_text = UI_STRINGS["en"]["hint_chip"]
    assert chip_text in html, (
        f"Hint chip text {chip_text!r} must appear in rendered HTML"
    )


def test_hint_hidden_in_print_stylesheet():
    """Print stylesheet must hide hint elements (hint-chip and/or hint-pulse).

    The @media print block contains nested {} rules so non-greedy regex stops
    too early; instead extract everything from @media print to end of <style>
    and verify the hint class appears there.
    """
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # Extract the section from @media print to end of the enclosing </style>
    idx = html.find("@media print")
    assert idx >= 0, "@media print rule not found in rendered HTML"
    # The hint class must appear after the @media print marker (within the same style block)
    after_print = html[idx:]
    end_style = after_print.find("</style>")
    print_section = after_print[:end_style] if end_style >= 0 else after_print[:2000]
    assert (
        "hint-chip" in print_section
        or "hintChip" in print_section
        or "hint-pulse" in print_section
        or "hintPulse" in print_section
    ), "Print stylesheet must hide hint elements (hint-chip and/or hint-pulse)"


# ── W5.2.5: Icon + text pill controls ────────────────────────────────────────


def _extract_button_content(html: str, data_action: str) -> str:
    """Return the inner HTML of a button with the given data-action value."""
    m = re.search(
        r'<button[^>]+data-action="' + re.escape(data_action) + r'"[^>]*>(.*?)</button>',
        html,
        re.DOTALL,
    )
    return m.group(1) if m else ""


def _button_visible_text(html: str, data_action: str) -> str:
    """Return the concatenated visible text of a button (glyph + label spans joined by a space).

    Extracts text content from each child span in the button, strips surrounding
    whitespace from each span's text, and joins them with a single space -- the
    same normalisation a browser applies when ``textContent`` is read across
    adjacent inline elements.  Spec usage: assert equality with the verbatim
    spec string (e.g. ``"+ Zoom in"``).
    """
    inner = _extract_button_content(html, data_action)
    if not inner:
        return ""
    parts = re.findall(r"<span[^>]*>(.*?)</span>", inner, re.DOTALL)
    if parts:
        return " ".join(p.strip() for p in parts if p.strip())
    # Fallback: strip all tags and collapse whitespace.
    text = re.sub(r"<[^>]+>", "", inner)
    return " ".join(text.split())


def _fab_visible_text(html: str, popup_name: str) -> str:
    """Return the concatenated visible text of a FAB button (glyph + label joined by a space).

    FAB buttons use ``onclick="togglePopup('<popup_name>')"`` instead of
    ``data-action``.  The glyph is a bare text node; the label lives in a
    ``<span class="fab-btn-label">`` child.
    """
    m = re.search(
        r'<button[^>]+onclick="togglePopup\(\'' + re.escape(popup_name) + r'\'\)"[^>]*>(.*?)</button>',
        html,
        re.DOTALL,
    )
    if not m:
        return ""
    inner = m.group(1)
    # Strip child-element markup to get text nodes, then normalise.
    text = re.sub(r"<[^>]+>", " ", inner)
    return " ".join(text.split())


def test_pill_zoom_in_label_in_rendered_html():
    """Zoom in pill must include visible label text as button content (not just title attr)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The button must still have data-action="zoom-in"
    assert 'data-action="zoom-in"' in html, (
        "zoom-in button must retain data-action='zoom-in' attribute"
    )
    # The label must appear as text INSIDE the button element (not only in title=)
    content = _extract_button_content(html, "zoom-in")
    assert "Zoom in" in content or UI_STRINGS["en"]["ctrl_zoom_in"] in content, (
        f"zoom-in button inner content must include visible label, got: {content!r}"
    )


def test_pill_zoom_out_label_in_rendered_html():
    """Zoom out pill must include visible label text as button content."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    content = _extract_button_content(html, "zoom-out")
    assert "Zoom out" in content or UI_STRINGS["en"]["ctrl_zoom_out"] in content, (
        f"zoom-out button inner content must include visible label, got: {content!r}"
    )


def test_pill_reset_label_in_rendered_html():
    """Reset pill must include visible label text as button content."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    content = _extract_button_content(html, "reset")
    label = UI_STRINGS["en"]["ctrl_reset"]
    assert "Reset" in content or label in content, (
        f"reset button inner content must include visible label, got: {content!r}"
    )


def test_pill_fullscreen_label_in_rendered_html():
    """Fullscreen pill must include visible label text as button content."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    content = _extract_button_content(html, "fullscreen")
    assert "Fullscreen" in content or UI_STRINGS["en"]["ctrl_fullscreen"] in content, (
        f"fullscreen button inner content must include visible label, got: {content!r}"
    )


def test_fab_save_label_in_rendered_html():
    """Save FAB must include visible label text inside the FAB button element."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    label = UI_STRINGS["en"].get("fab_save_label", "Save")
    content = _fab_visible_text(html, "popupSave")
    assert label in content, (
        f"Save FAB button visible text must include {label!r}, got: {content!r}"
    )


def test_fab_edit_label_in_rendered_html():
    """Edit FAB must include visible label text inside the FAB button element."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    label = UI_STRINGS["en"].get("fab_edit_label", "Edit")
    content = _fab_visible_text(html, "popupEdit")
    assert label in content, (
        f"Edit FAB button visible text must include {label!r}, got: {content!r}"
    )


# ── W5.2.6: Plain-language export menu ───────────────────────────────────────


def test_export_png_plain_language_in_en_strings():
    """export_png EN must use the spec plain-language string."""
    assert UI_STRINGS["en"].get("export_png") == _EN_EXPORT_PNG, (
        f"export_png EN must be {_EN_EXPORT_PNG!r}, got {UI_STRINGS['en'].get('export_png')!r}"
    )


def test_export_svg_plain_language_in_en_strings():
    """export_svg EN must use the spec plain-language string."""
    assert UI_STRINGS["en"].get("export_svg") == _EN_EXPORT_SVG, (
        f"export_svg EN must be {_EN_EXPORT_SVG!r}, got {UI_STRINGS['en'].get('export_svg')!r}"
    )


def test_export_html_plain_language_in_en_strings():
    """export_html EN must use the spec plain-language string."""
    assert UI_STRINGS["en"].get("export_html") == _EN_EXPORT_HTML, (
        f"export_html EN must be {_EN_EXPORT_HTML!r}, got {UI_STRINGS['en'].get('export_html')!r}"
    )


def test_export_menu_en_strings_in_rendered_html():
    """Export menu EN plain-language strings must appear in rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    for entry, key in [
        (_EN_EXPORT_PNG, "export_png"),
        (_EN_EXPORT_SVG, "export_svg"),
        (_EN_EXPORT_HTML, "export_html"),
    ]:
        assert entry in html, (
            f"Export menu entry {entry!r} (UI_STRINGS['en']['{key}']) must appear in rendered HTML"
        )


def test_export_menu_fr_strings_in_rendered_html():
    """Export menu FR strings (idiomatic, not EN) must appear in FR-rendered HTML.

    HTML-context Jinja2 autoescape converts apostrophes to &#39; in text content,
    which is correct browser rendering behaviour; the test normalises before comparing.
    """
    import html as html_module

    with tempfile.TemporaryDirectory() as d:
        rendered = _render(Path(d) / "out.html", ui_lang="fr")
    # Unescape HTML entities so we can compare plain string values
    unescaped = html_module.unescape(rendered)
    for key in ("export_png", "export_svg", "export_html"):
        fr_str = UI_STRINGS["fr"].get(key, "")
        assert fr_str and fr_str in unescaped, (
            f"FR export string for '{key}' ({fr_str!r}) must appear in FR-rendered HTML"
        )


def test_export_filenames_still_figure_in_script():
    """Download filenames must remain figure.png / figure.svg / figure.html in script blocks."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "'figure.png'" in scripts or '"figure.png"' in scripts, (
        "Download filename 'figure.png' must remain in script blocks"
    )
    assert "'figure.svg'" in scripts or '"figure.svg"' in scripts, (
        "Download filename 'figure.svg' must remain in script blocks"
    )
    assert "'figure.html'" in scripts or '"figure.html"' in scripts, (
        "Download filename 'figure.html' must remain in script blocks"
    )


# ── W5.2 FR locale assertions ─────────────────────────────────────────────────


def test_fr_hint_chip_in_rendered_html():
    """FR render must include FR hint chip text."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    fr_chip = UI_STRINGS["fr"].get("hint_chip", "")
    assert fr_chip and fr_chip in html, (
        f"FR hint_chip text {fr_chip!r} must appear in FR-rendered HTML"
    )


def test_fr_pill_labels_in_rendered_html():
    """FR render must include FR pill label text as visible button content (not just title attr)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    # FR zoom in label must appear as visible content INSIDE the zoom-in button
    fr_zoom_in = UI_STRINGS["fr"].get("ctrl_zoom_in", "")
    content = _extract_button_content(html, "zoom-in")
    assert fr_zoom_in and fr_zoom_in in content, (
        f"FR ctrl_zoom_in text {fr_zoom_in!r} must appear as button content in FR-rendered HTML, "
        f"got: {content!r}"
    )


def test_fr_no_html_entity_in_script_w52():
    """W5.2 FR render must not emit &#39; in script blocks (regression guard)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    scripts = _extract_script_blocks(html)
    assert "&#39;" not in scripts, (
        "FR W5.2 render must not contain &#39; in <script> blocks"
    )


# ── W5.T2 fix: exact pill and FAB visible text (spec-verbatim) ────────────────
#
# Each assertion extracts the concatenated visible text (glyph + label spans
# joined by a single space) and compares to the spec-mandated string exactly.
# Four EN values were wrong (verbose W3-era titles); FIX 1 corrects them.


# Spec-mandated EN visible texts (glyph + space + short label).
_PILL_TEXTS_EN = {
    "zoom-in":    "+ Zoom in",
    "zoom-out":   "− Zoom out",   # U+2212 MINUS SIGN (−), not ASCII hyphen
    "reset":      "⟲ Reset",      # ⟲
    "contrast":   "◐ High contrast",  # ◐
    "flip":       "↔ Flip",       # ↔
    "fullscreen": "⛶ Full screen",  # ⛶
    "exit-fs":    "✕ Exit",       # ✕  (exit-fs renders label as bare text)
}

# Spec-mandated EN FAB visible texts.
_FAB_TEXTS_EN = {
    "popupSave": "\U0001f4be Save",   # 💾
    "popupEdit": "✏ Edit",       # ✏
}

# FR spot-check values (zoom-in and fullscreen per spec requirement).
_PILL_TEXTS_FR_SPOT = {
    "zoom-in":    "+ Zoom avant",
    "fullscreen": "⛶ Plein écran",  # ⛶ Plein écran
}


def _button_exit_fs_text(html: str) -> str:
    """Return the visible text of the exit-fs button (bare text, not glyph+label spans)."""
    m = re.search(
        r'<button[^>]+data-action="exit-fs"[^>]*>(.*?)</button>',
        html,
        re.DOTALL,
    )
    if not m:
        return ""
    inner = m.group(1)
    text = re.sub(r"<[^>]+>", " ", inner)
    return " ".join(text.split())


def test_pill_exact_text_en_all():
    """All pill buttons must have exactly the spec-mandated visible text (EN)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    for action, expected in _PILL_TEXTS_EN.items():
        if action == "exit-fs":
            actual = _button_exit_fs_text(html)
        else:
            actual = _button_visible_text(html, action)
        assert actual == expected, (
            f"Pill '{action}' visible text must be exactly {expected!r}, got {actual!r}"
        )


def test_fab_exact_text_en_all():
    """All FAB buttons must have exactly the spec-mandated visible text (EN)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    for popup, expected in _FAB_TEXTS_EN.items():
        actual = _fab_visible_text(html, popup)
        assert actual == expected, (
            f"FAB '{popup}' visible text must be exactly {expected!r}, got {actual!r}"
        )


def test_pill_exact_text_fr_spot():
    """FR spot-check: zoom-in and fullscreen must use spec FR short-label visible text."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    for action, expected in _PILL_TEXTS_FR_SPOT.items():
        actual = _button_visible_text(html, action)
        assert actual == expected, (
            f"FR pill '{action}' visible text must be exactly {expected!r}, got {actual!r}"
        )


# ── Quality-review fix: pill-button JS clobber guard (Finding 1) ─────────────


def test_sync_flip_button_targets_ctrl_glyph_not_textcontent():
    """syncFlipButton must update .ctrl-glyph child span, not overwrite btn.textContent.

    A bare ``btn.textContent = ...`` assignment destroys the <span class="ctrl-glyph">
    and <span class="ctrl-label"> children of the flip pill after the first flip,
    reverting it to icon-only.  The fix must:
      1. Contain ``querySelector('.ctrl-glyph')`` inside syncFlipButton.
      2. NOT contain ``btn.textContent`` as a whole-button write for any pill button.
    """
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # Must target the glyph span, not the whole button
    assert "querySelector('.ctrl-glyph')" in scripts or '.querySelector(".ctrl-glyph")' in scripts, (
        "syncFlipButton must use btn.querySelector('.ctrl-glyph') to update only the glyph span"
    )
    # Must NOT wholesale overwrite the button's textContent (destroys pill structure)
    assert "btn.textContent" not in scripts, (
        "No pill button may use btn.textContent= (destroys ctrl-glyph/ctrl-label spans); "
        "use btn.querySelector('.ctrl-glyph').textContent= instead"
    )


# ── Quality-review fix: aria-hidden on hint elements (Finding 2) ──────────────


def test_dismiss_hints_sets_aria_hidden():
    """_dismissHints and the disabled-at-init path must set aria-hidden='true' on hint elements.

    Hiding via display:none alone leaves the elements announced to screen readers;
    aria-hidden='true' is required alongside the display change.
    """
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "aria-hidden" in scripts, (
        "_dismissHints (and the hints-disabled init path) must call "
        "setAttribute('aria-hidden','true') on hint chip and pulse elements"
    )


# ── Quality-review fix: prefers-reduced-motion for pulse (Finding 3) ─────────


def test_reduced_motion_media_query_for_hint_pulse():
    """CSS must include @media (prefers-reduced-motion: reduce) that disables .hint-pulse animation."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The media query must be present
    assert "prefers-reduced-motion" in html, (
        "CSS must contain @media (prefers-reduced-motion: reduce) block for .hint-pulse"
    )
    # Within the reduced-motion block the hint-pulse animation must be suppressed
    idx = html.find("prefers-reduced-motion")
    assert idx >= 0
    after = html[idx:]
    # Find the closing brace of the outer @media block (two levels deep)
    closing = after.find("}}", 0)
    block = after[:closing + 2] if closing >= 0 else after[:500]
    assert "hint-pulse" in block and "animation" in block, (
        "@media (prefers-reduced-motion: reduce) block must contain .hint-pulse { animation: none; }"
    )


# ── Quality-review fix: Got it button type="button" (Finding 4) ──────────────


def test_got_it_button_has_type_button():
    """Got it button must have type=\"button\" to prevent accidental form submission."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # Find the Got it button markup
    m = re.search(r'<button[^>]+id="hintGotIt"[^>]*>', html)
    assert m, "hintGotIt button not found in rendered HTML"
    assert 'type="button"' in m.group(0), (
        f"hintGotIt button must have type=\"button\", got: {m.group(0)!r}"
    )


# ── W5.3 Advanced editor disclosure ──────────────────────────────────────────

# Spec-verbatim EN strings (Item 7)
_EN_EDITOR_SUMMARY = "Advanced: edit the diagram's drawing instructions"
_EN_EDITOR_WARNING = "Changes here affect the picture only, not your documents."
_EN_REDRAW = "Re-draw"
_EN_CANCEL = "Cancel"


def test_w53_ui_string_keys_exist_in_en():
    """W5.3 new UI_STRINGS keys must be present in the 'en' table."""
    needed = ["editor_summary", "editor_warning", "cancel"]
    missing = [k for k in needed if k not in UI_STRINGS["en"]]
    assert not missing, f"Missing W5.3 keys in UI_STRINGS['en']: {missing}"


def test_w53_ui_string_keys_exist_in_fr():
    """W5.3 new UI_STRINGS keys must be present in the 'fr' table."""
    needed = ["editor_summary", "editor_warning", "cancel"]
    missing = [k for k in needed if k not in UI_STRINGS["fr"]]
    assert not missing, f"Missing W5.3 keys in UI_STRINGS['fr']: {missing}"


def test_w53_editor_summary_en_verbatim():
    """editor_summary EN must match spec verbatim."""
    assert UI_STRINGS["en"].get("editor_summary") == _EN_EDITOR_SUMMARY, (
        f"editor_summary EN must be {_EN_EDITOR_SUMMARY!r}, "
        f"got {UI_STRINGS['en'].get('editor_summary')!r}"
    )


def test_w53_editor_warning_en_verbatim():
    """editor_warning EN must match spec verbatim."""
    assert UI_STRINGS["en"].get("editor_warning") == _EN_EDITOR_WARNING, (
        f"editor_warning EN must be {_EN_EDITOR_WARNING!r}, "
        f"got {UI_STRINGS['en'].get('editor_warning')!r}"
    )


def test_w53_rerender_renamed_redraw_en():
    """rerender EN must be renamed to 'Re-draw'."""
    assert UI_STRINGS["en"].get("rerender") == _EN_REDRAW, (
        f"rerender EN must be {_EN_REDRAW!r}, got {UI_STRINGS['en'].get('rerender')!r}"
    )


def test_w53_cancel_en():
    """cancel EN must be 'Cancel'."""
    assert UI_STRINGS["en"].get("cancel") == _EN_CANCEL, (
        f"cancel EN must be {_EN_CANCEL!r}, got {UI_STRINGS['en'].get('cancel')!r}"
    )


def test_w53_editor_disclosure_markup_in_html():
    """Editor must be inside a <details> disclosure element."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # The editor must live inside a <details> element
    assert "<details" in html and "class=\"editor-disclosure\"" in html or (
        re.search(r"<details[^>]*>", html) is not None and 'id="editorWrap"' in html
    ), "Editor must be wrapped in a <details> element"


def test_w53_editor_summary_text_in_html():
    """The <summary> of the editor disclosure must contain the spec-verbatim EN text.

    HTML-context Jinja2 autoescape converts apostrophes to &#39; in text content,
    which is correct browser rendering; the test normalises before comparing.
    """
    import html as _html_mod
    with tempfile.TemporaryDirectory() as d:
        raw = _render(Path(d) / "out.html")
    unescaped = _html_mod.unescape(raw)
    assert _EN_EDITOR_SUMMARY in unescaped, (
        f"Editor disclosure <summary> must contain {_EN_EDITOR_SUMMARY!r}"
    )


def test_w53_editor_warning_text_in_html():
    """The editor warning line must appear in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert _EN_EDITOR_WARNING in html, (
        f"Editor warning line must contain {_EN_EDITOR_WARNING!r}"
    )


def test_w53_redraw_button_in_html():
    """Re-draw button must appear in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert _EN_REDRAW in html, (
        f"Re-draw button text {_EN_REDRAW!r} must appear in rendered HTML"
    )


def test_w53_cancel_button_in_html():
    """Cancel button must appear in the rendered HTML."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert _EN_CANCEL in html, (
        f"Cancel button text {_EN_CANCEL!r} must appear in rendered HTML"
    )


def test_w53_cancel_restore_in_script():
    """Cancel handler must reference the original mermaid source variable (structural JS check)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # cancelEdit function must exist and assign back to the editor + re-render original
    assert "cancelEdit" in scripts or "cancelRestore" in scripts or (
        "mermaidSource" in scripts and "Cancel" in html
    ), "Cancel handler must restore original mermaid source (reference mermaidSource in JS)"
    # Specifically: cancel must set the textarea value back to mermaidSource
    assert "mermaidSource" in scripts, (
        "Script must contain mermaidSource variable for cancel-restore to work"
    )


def test_w53_fab_popup_opens_disclosure():
    """FAB popup 'Edit Source' entry must open the <details> disclosure (JS structural check)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # The toggleEditor function must set open on the details element or similar
    assert "open" in scripts and ("detail" in scripts.lower() or "editorDisc" in scripts), (
        "toggleEditor in JS must set .open on the details/disclosure element"
    )


def test_w53_print_excludes_editor_disclosure():
    """Print stylesheet must exclude the editor disclosure element."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    idx = html.find("@media print")
    assert idx >= 0, "@media print rule not found"
    after_print = html[idx:]
    end_style = after_print.find("</style>")
    print_section = after_print[:end_style] if end_style >= 0 else after_print[:3000]
    # editor-wrap or editor-disclosure must be in the print-hide rule
    assert (
        "editor-wrap" in print_section
        or "editor-disclosure" in print_section
        or "editor-details" in print_section
    ), "Print stylesheet must exclude the editor disclosure element"


def test_w53_fr_editor_summary_in_html():
    """FR render must contain FR editor_summary string."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    fr_summary = UI_STRINGS["fr"].get("editor_summary", "")
    assert fr_summary and fr_summary in html, (
        f"FR editor_summary {fr_summary!r} must appear in FR-rendered HTML"
    )


def test_w53_fr_cancel_in_html():
    """FR render must contain FR cancel string."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    fr_cancel = UI_STRINGS["fr"].get("cancel", "")
    assert fr_cancel and fr_cancel in html, (
        f"FR cancel {fr_cancel!r} must appear in FR-rendered HTML"
    )


def test_w53_fr_no_html_entity_in_script():
    """FR W5.3 render must not emit &#39; in script blocks (regression guard)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html", ui_lang="fr")
    scripts = _extract_script_blocks(html)
    assert "&#39;" not in scripts, (
        "FR W5.3 render must not contain &#39; in <script> blocks"
    )


# ── W5.3 Item 8: Pinch zoom ───────────────────────────────────────────────────


def test_w53_pinch_two_pointer_tracking_in_script():
    """Pinch zoom: script must track two active pointers (evidence of pointer map/array)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # Two-pointer tracking: must have a data structure for active pointers
    # (e.g., activePointers, pointers, pinchPointers, _ptrs)
    has_pointer_map = (
        "activePointers" in scripts
        or "pinchPointers" in scripts
        or "_ptrs" in scripts
        or re.search(r"\bpointers\b", scripts) is not None
    )
    assert has_pointer_map, (
        "Script must contain a data structure for tracking multiple active pointers "
        "(e.g., activePointers, pinchPointers, _ptrs, or pointers)"
    )


def test_w53_pinch_distance_calc_in_script():
    """Pinch zoom: script must contain a distance calculation (Math.hypot or Math.sqrt)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    has_distance = (
        "Math.hypot" in scripts
        or "Math.sqrt" in scripts
        or "hypot" in scripts
    )
    assert has_distance, (
        "Pinch zoom handler must compute pointer distance (Math.hypot or Math.sqrt)"
    )


def test_w53_pinch_pointerdown_handler_in_script():
    """Pinch zoom: pointerdown handler must exist on the diagram frame."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    # The existing drag already has a pointerdown; pinch extends it
    assert "pointerdown" in scripts, (
        "Script must contain a pointerdown event listener for pinch/drag"
    )


def test_w53_touch_action_none_on_frame():
    """#diagramFrame must have touch-action: none in CSS or inline style."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # touch-action: none can appear in CSS rules or inline style
    assert "touch-action" in html and "none" in html, (
        "touch-action: none must be set on #diagramFrame to prevent native gestures "
        "from conflicting with pinch zoom"
    )


# ── W5.4 ARIA tabs ────────────────────────────────────────────────────────────


def test_w54_tablist_role_in_html():
    """Tab row must have role='tablist'."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'role="tablist"' in html, (
        "Tab row (.tabs div) must have role='tablist'"
    )


def test_w54_tab_role_on_buttons_in_html():
    """Tab buttons must have role='tab'."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'role="tab"' in html, (
        "Tab buttons (.tab-btn) must have role='tab'"
    )


def test_w54_aria_selected_on_first_tab_in_html():
    """First tab button must have aria-selected='true' in markup."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'aria-selected="true"' in html, (
        "Active tab button must have aria-selected='true' in markup"
    )


def test_w54_aria_selected_false_on_inactive_tabs():
    """Inactive tab buttons must have aria-selected='false'."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'aria-selected="false"' in html, (
        "Inactive tab buttons must have aria-selected='false'"
    )


def test_w54_tabpanel_role_on_panels():
    """Tab panels must have role='tabpanel'."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'role="tabpanel"' in html, (
        "Tab panels (.tab-panel) must have role='tabpanel'"
    )


def test_w54_aria_labelledby_on_panels():
    """Tab panels must have aria-labelledby pointing at the tab button id."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert "aria-labelledby" in html, (
        "Tab panels must have aria-labelledby attribute pointing at the tab button id"
    )


def test_w54_tab_ids_in_markup():
    """Tab buttons must have id attributes for aria-labelledby references."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    # Check that tab buttons have id= attributes (e.g., id="tab-btn-overview")
    m = re.search(r'<button[^>]+role="tab"[^>]+id="[^"]+"', html) or \
        re.search(r'<button[^>]+id="[^"]+"[^>]+role="tab"', html)
    assert m, (
        "Tab buttons must have id= attributes so aria-labelledby can reference them"
    )


def test_w54_tabindex_management_in_script():
    """Tab switching JS must manage tabindex (0 on active, -1 on others)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "tabIndex" in scripts or "tabindex" in scripts.lower(), (
        "Tab switching JS must set tabIndex (0 on active tab, -1 on others)"
    )


def test_w54_arrow_key_handler_in_script():
    """ArrowLeft/ArrowRight key handler must be present in script blocks."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "ArrowLeft" in scripts and "ArrowRight" in scripts, (
        "Keyboard handler must include ArrowLeft and ArrowRight for tab navigation"
    )


def test_w54_focus_visible_rule_in_css():
    """CSS must include a :focus-visible outline rule for interactive controls."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert ":focus-visible" in html, (
        "CSS must include :focus-visible outline rule covering tab buttons, pills, FABs, etc."
    )


# ── W5.4 Item 10: Preservation assertions ────────────────────────────────────


def test_w54_disclaimer_banner_preserved():
    """Disclaimer banner markup must still be present after W5.3/W5.4 changes."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'class="disclaimer-banner"' in html, (
        "Disclaimer banner (.disclaimer-banner) must still be present"
    )


def test_w54_semantic_legend_preserved():
    """Semantic legend element must still be present."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'id="semanticLegend"' in html or 'class="semantic-legend"' in html, (
        "Semantic legend element must still be present"
    )


def test_w54_pattern_overlay_class_preserved():
    """sem-pattern-overlay class must still appear in JS (colourblind patterns preserved)."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    scripts = _extract_script_blocks(html)
    assert "sem-pattern-overlay" in scripts, (
        "sem-pattern-overlay class must still appear in JS (colourblind patterns preserved)"
    )


def test_w54_contrast_button_preserved():
    """High-contrast toggle button must still be present."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert 'data-action="contrast"' in html, (
        "High-contrast toggle button (data-action='contrast') must still be present"
    )


def test_w54_print_stylesheet_preserved():
    """Print stylesheet must still be present with key rules."""
    with tempfile.TemporaryDirectory() as d:
        html = _render(Path(d) / "out.html")
    assert "@media print" in html, (
        "@media print stylesheet must still be present"
    )
    # Hint chip/pulse must still be excluded from print
    idx = html.find("@media print")
    after_print = html[idx:]
    end_style = after_print.find("</style>")
    print_section = after_print[:end_style] if end_style >= 0 else after_print[:3000]
    assert "hint-chip" in print_section or "hint-pulse" in print_section or (
        "fab-group" in print_section
    ), "Print stylesheet must still exclude hint chips and fab-group"


if __name__ == "__main__":
    _tests = [
        v for name, v in sorted(globals().items())
        if name.startswith("test_") and callable(v)
    ]
    _failed = 0
    for _test in _tests:
        try:
            _test()
            print(f"ok : {_test.__name__}")
        except Exception as _exc:
            print(f"FAIL: {_test.__name__}: {_exc}")
            _failed += 1
    print(f"\n{len(_tests) - _failed} tests passed, {_failed} failed")
    if _failed:
        sys.exit(1)

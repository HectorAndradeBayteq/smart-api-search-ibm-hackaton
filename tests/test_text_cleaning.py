"""Pruebas unitarias para limpieza de texto y documento marcador (TK-002 US-002).

Cubre: clean_text (macros, admoniciones, espacios, idempotencia, vacío)
y make_marker_document (spec sin paths, spec con paths vacío).
"""

from __future__ import annotations

import json

from smart_api_search.cli.ingest import clean_text, make_marker_document

# ---------------------------------------------------------------------------
# clean_text
# ---------------------------------------------------------------------------


class TestCleanText:
    def test_hugo_macro_shortcode_percent_removed(self) -> None:
        result = clean_text("{{% note %}} Important text {{% /note %}}")
        assert "{%" not in result
        assert "Important text" in result

    def test_hugo_macro_shortcode_angle_removed(self) -> None:
        result = clean_text("{{< warning >}} Watch out {{< /warning >}}")
        assert "{{<" not in result
        assert "Watch out" in result

    def test_jinja_template_expression_removed(self) -> None:
        result = clean_text("Hello {{ user.name }}, welcome!")
        assert "{{" not in result
        assert "Hello" in result
        assert "welcome" in result

    def test_rst_note_admonition_removed(self) -> None:
        result = clean_text("Some text\n.. note::\n   This is a note.\nMore text")
        assert ".. note::" not in result
        assert "Some text" in result

    def test_rst_warning_admonition_removed(self) -> None:
        result = clean_text("Before\n.. warning::\n   Be careful.\nAfter")
        assert ".. warning::" not in result

    def test_rst_tip_admonition_removed(self) -> None:
        result = clean_text(".. tip::\n   Helpful hint.\n")
        assert ".. tip::" not in result

    def test_markdown_admonition_bang_note_removed(self) -> None:
        result = clean_text("Some text\n!!! note\n    Important info\nMore text")
        assert "!!! note" not in result

    def test_markdown_admonition_bang_warning_removed(self) -> None:
        result = clean_text("!!! warning\n    Be careful!\n")
        assert "!!! warning" not in result

    def test_multiple_spaces_collapsed(self) -> None:
        result = clean_text("Too   many   spaces")
        assert result == "Too many spaces"

    def test_tabs_collapsed_to_single_space(self) -> None:
        result = clean_text("word\tanother\tword")
        assert "\t" not in result
        assert result == "word another word"

    def test_three_or_more_newlines_collapsed_to_two(self) -> None:
        result = clean_text("line1\n\n\n\nline2")
        assert "\n\n\n" not in result
        assert "line1" in result
        assert "line2" in result

    def test_two_newlines_preserved(self) -> None:
        result = clean_text("line1\n\nline2")
        assert result == "line1\n\nline2"

    def test_strip_leading_trailing_whitespace(self) -> None:
        result = clean_text("  hello world  ")
        assert result == "hello world"

    def test_empty_string_returns_empty(self) -> None:
        assert clean_text("") == ""

    def test_idempotent_with_macros(self) -> None:
        text = "{{% note %}} Some note {{% /note %}} Normal text"
        once = clean_text(text)
        twice = clean_text(once)
        assert once == twice

    def test_idempotent_with_admonitions(self) -> None:
        text = "Before\n.. warning::\n   Careful.\nAfter"
        once = clean_text(text)
        twice = clean_text(once)
        assert once == twice

    def test_idempotent_already_clean_text(self) -> None:
        text = "This is already clean text with no issues."
        assert clean_text(clean_text(text)) == clean_text(text)

    def test_plain_text_unchanged(self) -> None:
        text = "Normal API description without any markup."
        assert clean_text(text) == text

    def test_mixed_cleanup(self) -> None:
        text = "{{% note %}} A note {{% /note %}}\n\n\n\n.. warning::\n   Watch out.\nNormal   text"
        result = clean_text(text)
        assert "{%" not in result
        assert ".. warning::" not in result
        assert "Normal text" in result
        assert "\n\n\n" not in result


# ---------------------------------------------------------------------------
# make_marker_document
# ---------------------------------------------------------------------------


SPEC_WITHOUT_PATHS = {
    "openapi": "3.0.0",
    "info": {
        "title": "Empty API",
        "version": "1.0.0",
        "description": "An API without paths",
    },
    "servers": [{"url": "https://api.example.com"}],
}

SPEC_WITH_EMPTY_PATHS = {
    "openapi": "3.0.0",
    "info": {"title": "Empty Paths API", "version": "2.0.0"},
    "paths": {},
}


class TestMakeMarkerDocument:
    def test_marker_method_is_marker(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["method"] == "MARKER"

    def test_marker_path_is_root(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["path"] == "/"

    def test_spec_ref_format(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["spec_ref"] == "portal:empty-api|MARKER|/"

    def test_summary_is_no_paths_declared(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["summary"] == "(no paths declared)"

    def test_source_file_stored(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["source_file"] == "portal:empty-api"

    def test_spec_format_stored(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "yaml")
        assert doc["spec_format"] == "yaml"

    def test_api_title_from_info(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["api_title"] == "Empty API"

    def test_api_version_from_info(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["api_version"] == "1.0.0"

    def test_api_description_from_info(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        assert doc["api_description"] == "An API without paths"

    def test_raw_spec_contains_info_and_format(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        raw = json.loads(str(doc["raw_spec"]))
        assert "info" in raw
        assert "format" in raw

    def test_with_empty_paths_dict(self) -> None:
        doc = make_marker_document(SPEC_WITH_EMPTY_PATHS, "portal:empty-paths", "json")
        assert doc["method"] == "MARKER"
        assert doc["api_title"] == "Empty Paths API"

    def test_required_fields_all_present(self) -> None:
        doc = make_marker_document(SPEC_WITHOUT_PATHS, "portal:empty-api", "json")
        required = {
            "source_file",
            "spec_format",
            "api_title",
            "api_version",
            "api_description",
            "method",
            "path",
            "spec_ref",
            "summary",
            "raw_spec",
        }
        for field in required:
            assert field in doc, f"Campo requerido faltante: {field}"

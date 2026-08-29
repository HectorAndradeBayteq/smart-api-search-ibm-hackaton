"""Pruebas unitarias para apply_category_metadata y resolve_category_key (TK-004 US-002)."""

from __future__ import annotations

from smart_api_search.cli.ingest import apply_category_metadata, resolve_category_key

CONFIG = {
    "payments": {"title": "Payments API", "description": "Pay endpoints"},
    "users": {"title": "User Mgmt"},
}

BASE_OP = {
    "method": "GET",
    "path": "/things",
    "api_title": "My API",
    "api_description": "A generic API",
    "tags": [],
}


class TestResolveCategoryKey:
    def test_first_tag_used(self) -> None:
        op = {**BASE_OP, "tags": ["payments", "other"]}
        assert resolve_category_key(op) == "payments"

    def test_empty_tags_returns_empty(self) -> None:
        assert resolve_category_key({**BASE_OP, "tags": []}) == ""

    def test_missing_tags_returns_empty(self) -> None:
        op = {k: v for k, v in BASE_OP.items() if k != "tags"}
        assert resolve_category_key(op) == ""

    def test_blank_first_tag_returns_empty(self) -> None:
        assert resolve_category_key({**BASE_OP, "tags": [""]}) == ""


class TestApplyCategoryMetadata:
    def test_tag_in_config_uses_config_title_and_description(self) -> None:
        op = {**BASE_OP, "tags": ["payments"]}
        result = apply_category_metadata(op, CONFIG)
        assert result["category"] == "payments"

    def test_tag_in_config_only_title_uses_api_description_as_fallback(self) -> None:
        op = {**BASE_OP, "tags": ["users"]}
        result = apply_category_metadata(op, CONFIG)
        assert result["category"] == "users"

    def test_tag_not_in_config_uses_api_title_as_category(self) -> None:
        op = {**BASE_OP, "tags": ["unknown"]}
        result = apply_category_metadata(op, CONFIG)
        assert result["category"] == "My API"

    def test_no_tags_uses_api_title_as_category(self) -> None:
        result = apply_category_metadata(BASE_OP, CONFIG)
        assert result["category"] == "My API"

    def test_empty_config_falls_back_to_api_title(self) -> None:
        op = {**BASE_OP, "tags": ["payments"]}
        result = apply_category_metadata(op, {})
        assert result["category"] == "My API"

    def test_does_not_mutate_original_dict(self) -> None:
        op = {**BASE_OP, "tags": ["payments"]}
        original_keys = set(op.keys())
        apply_category_metadata(op, CONFIG)
        assert set(op.keys()) == original_keys
        assert "category" not in op

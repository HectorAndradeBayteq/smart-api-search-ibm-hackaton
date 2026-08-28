"""Pruebas unitarias para el parser de operaciones OpenAPI (TK-001 US-002).

Cubre: parse_spec, detect_spec_version, get_base_url, apply_text_fallback,
build_raw_spec y extract_operations.
"""

from __future__ import annotations

import json

import pytest

from smart_api_search.cli.ingest import (
    apply_text_fallback,
    build_raw_spec,
    detect_spec_version,
    extract_operations,
    get_base_url,
    parse_spec,
)

# ---------------------------------------------------------------------------
# parse_spec
# ---------------------------------------------------------------------------


class TestParseSpec:
    def test_json_bytes(self) -> None:
        content = json.dumps({"openapi": "3.0.0"}).encode()
        result = parse_spec(content, "json")
        assert result == {"openapi": "3.0.0"}

    def test_yaml_bytes(self) -> None:
        content = b"openapi: '3.0.0'\n"
        result = parse_spec(content, "yaml")
        assert result["openapi"] == "3.0.0"

    def test_bom_stripped_json(self) -> None:
        bom = b"\xef\xbb\xbf"
        content = bom + json.dumps({"swagger": "2.0"}).encode()
        result = parse_spec(content, "json")
        assert result == {"swagger": "2.0"}

    def test_bom_stripped_yaml(self) -> None:
        bom = b"\xef\xbb\xbf"
        content = bom + b"swagger: '2.0'\n"
        result = parse_spec(content, "yaml")
        assert result["swagger"] == "2.0"

    def test_invalid_json_raises(self) -> None:
        with pytest.raises(ValueError, match="json"):
            parse_spec(b"not valid json!!!", "json")

    def test_invalid_yaml_raises(self) -> None:
        with pytest.raises(ValueError, match="yaml"):
            parse_spec(b":\n  - invalid: [\n", "yaml")

    def test_unknown_format_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_spec(b"anything", "xml")


# ---------------------------------------------------------------------------
# detect_spec_version
# ---------------------------------------------------------------------------


class TestDetectSpecVersion:
    def test_oas3(self) -> None:
        assert detect_spec_version({"openapi": "3.0.0"}) == "oas3"

    def test_swagger2(self) -> None:
        assert detect_spec_version({"swagger": "2.0"}) == "swagger2"

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="versión"):
            detect_spec_version({"info": {"title": "No version"}})


# ---------------------------------------------------------------------------
# get_base_url
# ---------------------------------------------------------------------------


class TestGetBaseUrl:
    def test_oas3_with_servers(self) -> None:
        spec = {"servers": [{"url": "https://api.example.com/v1"}]}
        assert get_base_url(spec, "oas3") == "https://api.example.com/v1"

    def test_oas3_without_servers(self) -> None:
        assert get_base_url({}, "oas3") == ""

    def test_swagger2_full(self) -> None:
        spec = {"schemes": ["https"], "host": "api.example.com", "basePath": "/v2"}
        assert get_base_url(spec, "swagger2") == "https://api.example.com/v2"

    def test_swagger2_missing_base_path(self) -> None:
        spec = {"schemes": ["https"], "host": "api.example.com"}
        result = get_base_url(spec, "swagger2")
        assert result == "https://api.example.com"

    def test_swagger2_missing_all_fields(self) -> None:
        assert get_base_url({}, "swagger2") == ""

    def test_swagger2_missing_scheme(self) -> None:
        spec = {"host": "api.example.com", "basePath": "/v1"}
        result = get_base_url(spec, "swagger2")
        assert result == "api.example.com/v1"


# ---------------------------------------------------------------------------
# apply_text_fallback
# ---------------------------------------------------------------------------


class TestApplyTextFallback:
    def test_summary_used_first(self) -> None:
        op = {"summary": "Create user", "description": "Long desc", "operationId": "createUser"}
        assert apply_text_fallback(op) == "Create user"

    def test_description_first_line_when_no_summary(self) -> None:
        op = {"description": "First line\nSecond line", "operationId": "op"}
        assert apply_text_fallback(op) == "First line"

    def test_operation_id_when_no_summary_description(self) -> None:
        op = {"operationId": "getUser"}
        assert apply_text_fallback(op) == "getUser"

    def test_parameters_descriptions_when_all_missing(self) -> None:
        op = {
            "parameters": [
                {"name": "id", "description": "User ID"},
                {"name": "format", "description": "Response format"},
            ]
        }
        result = apply_text_fallback(op)
        assert result == "User ID, Response format"

    def test_empty_string_when_nothing(self) -> None:
        assert apply_text_fallback({}) == ""

    def test_empty_summary_skipped(self) -> None:
        op = {"summary": "", "description": "Fallback desc"}
        assert apply_text_fallback(op) == "Fallback desc"

    def test_parameters_without_description_skipped(self) -> None:
        op = {"parameters": [{"name": "id"}, {"name": "q", "description": "Query"}]}
        assert apply_text_fallback(op) == "Query"


# ---------------------------------------------------------------------------
# build_raw_spec
# ---------------------------------------------------------------------------


class TestBuildRawSpec:
    def _oas3_spec(self) -> dict:  # type: ignore[return]
        return {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/users": {
                    "get": {"summary": "List users", "responses": {"200": {"description": "OK"}}}
                }
            },
        }

    def test_raw_spec_fields_oas3(self) -> None:
        spec = self._oas3_spec()
        raw = build_raw_spec(spec, "/users", "GET", "json", "oas3")
        assert raw["info"] == spec["info"]
        assert raw["servers"] == spec["servers"]
        assert raw["format"] == "json"
        assert raw["path"] == "/users"
        assert raw["method"] == "GET"
        assert raw["operation"] == spec["paths"]["/users"]["get"]

    def test_raw_spec_swagger2(self) -> None:
        spec = {
            "swagger": "2.0",
            "info": {"title": "SW API", "version": "2.0"},
            "schemes": ["https"],
            "host": "sw.example.com",
            "basePath": "/api",
            "paths": {
                "/items": {
                    "post": {
                        "summary": "Create item",
                        "responses": {"201": {"description": "Created"}},
                    }
                }
            },
        }
        raw = build_raw_spec(spec, "/items", "POST", "yaml", "swagger2")
        assert raw["format"] == "yaml"
        assert raw["method"] == "POST"
        assert isinstance(raw["servers"], list)
        assert len(raw["servers"]) == 1

    def test_all_md02_fields_present(self) -> None:
        spec = self._oas3_spec()
        raw = build_raw_spec(spec, "/users", "GET", "json", "oas3")
        for field in ("info", "servers", "format", "path", "method", "operation"):
            assert field in raw, f"Campo MD-02 faltante: {field}"


# ---------------------------------------------------------------------------
# extract_operations
# ---------------------------------------------------------------------------


SAMPLE_OAS3 = {
    "openapi": "3.0.0",
    "info": {"title": "Sample API", "version": "1.0.0", "description": "A sample API"},
    "servers": [{"url": "https://api.example.com/v1"}],
    "paths": {
        "/users": {
            "get": {
                "summary": "List users",
                "operationId": "listUsers",
                "tags": ["users"],
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "operationId": "createUser",
                "description": "Create a new user\nMore details",
                "tags": ["users"],
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/items": {
            "delete": {
                "summary": "Delete item",
                "responses": {"204": {"description": "No content"}},
            },
            "parameters": [{"name": "id", "in": "path"}],  # no es método HTTP — debe ignorarse
        },
    },
}

SAMPLE_SWAGGER2 = {
    "swagger": "2.0",
    "info": {"title": "SW API", "version": "2.0"},
    "schemes": ["https"],
    "host": "sw.example.com",
    "basePath": "/api",
    "paths": {
        "/pets": {
            "get": {
                "summary": "List pets",
                "tags": ["pets"],
                "responses": {"200": {"description": "OK"}},
            }
        }
    },
}


class TestExtractOperations:
    def test_methods_normalized_uppercase(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        methods = {op["method"] for op in ops}
        assert methods == {"GET", "POST", "DELETE"}

    def test_non_http_keys_ignored(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        # 'parameters' a nivel de path no debe generar una operación
        assert all(
            op["method"] in ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE")
            for op in ops
        )

    def test_spec_ref_format(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        for op in ops:
            parts = op["spec_ref"].split("|")
            assert len(parts) == 3
            assert parts[0] == "portal:sample-api"
            assert parts[2].startswith("/")

    def test_summary_fallback_used(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        post_op = next(o for o in ops if o["method"] == "POST" and o["path"] == "/users")
        # description: "Create a new user\nMore details" → primera línea
        assert post_op["summary"] == "Create a new user"

    def test_server_url_oas3(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        for op in ops:
            assert op["server_url"] == "https://api.example.com/v1"

    def test_server_url_swagger2_composed(self) -> None:
        ops = extract_operations(SAMPLE_SWAGGER2, "portal:sw-api", "yaml")
        assert len(ops) == 1
        assert ops[0]["server_url"] == "https://sw.example.com/api"

    def test_raw_spec_is_json_string(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        for op in ops:
            raw = json.loads(op["raw_spec"])
            assert "info" in raw and "operation" in raw

    def test_api_title_version_description_present(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        for op in ops:
            assert op["api_title"] == "Sample API"
            assert op["api_version"] == "1.0.0"
            assert op["api_description"] == "A sample API"

    def test_tags_and_operation_id_present(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "json")
        get_op = next(o for o in ops if o["method"] == "GET" and o["path"] == "/users")
        assert get_op["tags"] == ["users"]
        assert get_op["operationId"] == "listUsers"

    def test_spec_format_stored(self) -> None:
        ops = extract_operations(SAMPLE_OAS3, "portal:sample-api", "yaml")
        for op in ops:
            assert op["spec_format"] == "yaml"

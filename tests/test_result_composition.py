"""Pruebas unitarias de composición y normalización del resultado (TK-003, US-004).

Cubre: compose_result(), normalize_params(), get_by_spec_ref() (AC-004..AC-008).
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest


def _make_scored_point(
    spec_ref: str = "portal:api|GET|/users",
    server_url: str = "https://api.example.com",
    path: str = "/users",
    method: str = "GET",
    extra_payload: dict | None = None,
) -> object:
    """Crea un ScoredPoint sintético con payload mínimo válido."""
    from qdrant_client.http import models

    raw_spec = json.dumps({
        "operation": {
            "parameters": [
                {"name": "limit", "in": "query", "required": False},
            ]
        }
    })
    payload: dict = {
        "spec_ref": spec_ref,
        "server_url": server_url,
        "path": path,
        "method": method,
        "category": "Test Category",
        "summary": "Get users",
        "description": "Returns a list of users",
        "enriched_text": "Enriched description",
        "deeplink": "https://portal.example.com/users",
        "tags": ["users"],
        "source_file": "portal:api",
        "raw_spec": raw_spec,
    }
    if extra_payload:
        payload.update(extra_payload)
    return models.ScoredPoint(
        id="test-id-1234",
        version=1,
        score=0.9,
        payload=payload,
        vector=None,
    )


# ---------------------------------------------------------------------------
# compose_result
# ---------------------------------------------------------------------------


def test_compose_result_all_fields_present() -> None:
    """compose_result() produce SearchResult con todos los campos de MD-03."""
    from smart_api_search.domain.result import compose_result

    point = _make_scored_point()
    result = compose_result(point, ranking=1)

    assert result is not None
    assert result.ranking == 1
    assert result.method == "GET"
    assert result.path == "/users"
    assert result.spec_ref == "portal:api|GET|/users"
    assert result.source == "portal:api"
    assert result.category == "Test Category"
    assert result.summary == "Get users"
    assert result.tags == ["users"]


def test_compose_result_call_url_is_server_url_plus_path() -> None:
    """call_url debe ser server_url + path, no el deeplink (AC-005)."""
    from smart_api_search.domain.result import compose_result

    point = _make_scored_point(
        server_url="https://api.example.com",
        path="/users",
    )
    result = compose_result(point, ranking=1)

    assert result is not None
    assert result.call_url == "https://api.example.com/users"
    assert result.call_url != result.deeplink


def test_compose_result_invalid_spec_ref_two_segments() -> None:
    """spec_ref con 2 segmentos es inválido — devuelve None."""
    from smart_api_search.domain.result import compose_result

    point = _make_scored_point(spec_ref="portal:api|GET")  # solo 2 segmentos
    result = compose_result(point, ranking=1)
    assert result is None


def test_compose_result_invalid_spec_ref_empty_segment() -> None:
    """spec_ref con segmento vacío es inválido."""
    from smart_api_search.domain.result import compose_result

    point = _make_scored_point(spec_ref="portal:api||/users")  # segmento vacío
    result = compose_result(point, ranking=1)
    assert result is None


def test_compose_result_valid_spec_ref_four_segments_invalid() -> None:
    """spec_ref con 4 segmentos (demasiados) es inválido."""
    from smart_api_search.domain.result import compose_result

    point = _make_scored_point(spec_ref="a|b|c|d")
    result = compose_result(point, ranking=1)
    assert result is None


# ---------------------------------------------------------------------------
# normalize_params
# ---------------------------------------------------------------------------


def test_normalize_params_includes_declared_params() -> None:
    """Parámetros declarados en la operación se incluyen."""
    from smart_api_search.domain.params import normalize_params

    operation = {
        "parameters": [
            {"name": "limit", "in": "query", "required": False},
            {"name": "offset", "in": "query", "required": False},
        ]
    }
    result = normalize_params(operation, "/users")
    names = [p["name"] for p in result]
    assert "limit" in names
    assert "offset" in names


def test_normalize_params_infers_path_params() -> None:
    """Parámetros del template del path se infieren si no están declarados."""
    from smart_api_search.domain.params import normalize_params

    operation: dict = {"parameters": []}
    result = normalize_params(operation, "/users/{userId}/posts/{postId}")
    names = [p["name"] for p in result]
    assert "userId" in names
    assert "postId" in names


def test_normalize_params_omits_unnamed() -> None:
    """Parámetros sin nombre se omiten (AC-006)."""
    from smart_api_search.domain.params import normalize_params

    operation = {
        "parameters": [
            {"name": "", "in": "query", "required": False},  # sin nombre
            {"name": "page", "in": "query", "required": False},
        ]
    }
    result = normalize_params(operation, "/items")
    names = [p["name"] for p in result]
    assert "" not in names
    assert "page" in names


def test_normalize_params_no_duplicate_path_params() -> None:
    """Parámetros ya declarados no se duplican por inferencia del path."""
    from smart_api_search.domain.params import normalize_params

    operation = {
        "parameters": [
            {"name": "userId", "in": "path", "required": True},
        ]
    }
    result = normalize_params(operation, "/users/{userId}")
    names = [p["name"] for p in result]
    assert names.count("userId") == 1


# ---------------------------------------------------------------------------
# get_by_spec_ref
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_spec_ref_returns_empty_for_invalid_format() -> None:
    """spec_ref inválido devuelve [] sin excepción (AC-008)."""
    from smart_api_search.domain.result import get_by_spec_ref

    client = AsyncMock()
    result = await get_by_spec_ref("invalid-no-pipes", client, "test-col")
    assert result == []
    client.scroll.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_spec_ref_returns_empty_for_nonexistent_point() -> None:
    """Punto inexistente devuelve [] sin excepción (AC-008)."""
    from smart_api_search.domain.result import get_by_spec_ref

    client = AsyncMock()
    client.scroll = AsyncMock(return_value=([], None))

    result = await get_by_spec_ref("portal:api|GET|/nonexistent", client, "test-col")
    assert result == []

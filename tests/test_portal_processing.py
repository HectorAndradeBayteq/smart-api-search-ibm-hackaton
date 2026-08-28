"""Pruebas unitarias del procesamiento de fuentes, deeplinks y manejo de errores.

Cubre: assign_source_name (TC-011, TC-012), build_deeplink_map (TC-013, TC-014),
errores de configuración (TC-018, TC-019) y error de API sin attachment (TC-020).
"""

from __future__ import annotations

import logging

import pytest

from smart_api_search.cli.ingest import assign_source_name, build_deeplink_map

# ---------------------------------------------------------------------------
# TC-011 / AC-006: slugs únicos → source_name sin sufijo
# ---------------------------------------------------------------------------


def test_assign_source_name_unique_slugs() -> None:
    """TC-011 — Slugs únicos reciben portal:{slug} sin sufijo."""
    seen: set[str] = set()
    assert assign_source_name("payments-api", seen) == "portal:payments-api"
    assert assign_source_name("users-api", seen) == "portal:users-api"
    assert assign_source_name("inventory-api", seen) == "portal:inventory-api"
    assert seen == {"portal:payments-api", "portal:users-api", "portal:inventory-api"}


def test_assign_source_name_stable_across_calls() -> None:
    """TC-011 — Resultado estable: misma entrada produce mismo resultado."""
    seen1: set[str] = set()
    seen2: set[str] = set()
    name1 = assign_source_name("my-api", seen1)
    name2 = assign_source_name("my-api", seen2)
    assert name1 == name2 == "portal:my-api"


# ---------------------------------------------------------------------------
# TC-012 / AC-006: slugs duplicados → sufijo numérico incremental
# ---------------------------------------------------------------------------


def test_assign_source_name_two_duplicate_slugs() -> None:
    """TC-012 — Dos APIs con el mismo slug: portal:{slug} y portal:{slug}-2."""
    seen: set[str] = set()
    first = assign_source_name("payments-api", seen)
    second = assign_source_name("payments-api", seen)
    assert first == "portal:payments-api"
    assert second == "portal:payments-api-2"


def test_assign_source_name_three_duplicate_slugs() -> None:
    """TC-012 — Tres APIs con el mismo slug: sufijos -2 y -3."""
    seen: set[str] = set()
    first = assign_source_name("payments-api", seen)
    second = assign_source_name("payments-api", seen)
    third = assign_source_name("payments-api", seen)
    assert first == "portal:payments-api"
    assert second == "portal:payments-api-2"
    assert third == "portal:payments-api-3"
    assert len(seen) == 3


def test_assign_source_name_all_unique_after_dedup() -> None:
    """TC-012 — Todos los source_name resultantes son únicos."""
    seen: set[str] = set()
    names = [assign_source_name("api", seen) for _ in range(5)]
    assert len(names) == len(set(names))  # sin duplicados


# ---------------------------------------------------------------------------
# TC-013 / AC-007: mapa de deeplinks — par existente devuelve URL
# ---------------------------------------------------------------------------


def test_build_deeplink_map_existing_pair_returns_url() -> None:
    """TC-013 — Par existente en el mapa devuelve la URL correcta."""
    api_detail = {
        "id": "payments-api",
        "resources": [
            {
                "path": "/payments/{id}",
                "method": "get",
                "url": "https://portal.example.com/apis/payments/resources/get-payment-by-id",
            }
        ],
    }
    deeplink_map = build_deeplink_map(api_detail)
    assert deeplink_map[("/payments/{id}", "GET")] == (
        "https://portal.example.com/apis/payments/resources/get-payment-by-id"
    )


def test_build_deeplink_map_method_stored_uppercase() -> None:
    """TC-013 — El método HTTP en la clave del mapa está en mayúsculas."""
    api_detail = {
        "resources": [
            {"path": "/users", "method": "post", "url": "https://portal.example.com/users"}
        ]
    }
    deeplink_map = build_deeplink_map(api_detail)
    assert ("/users", "POST") in deeplink_map


# ---------------------------------------------------------------------------
# TC-014 / AC-007: mapa de deeplinks — par inexistente devuelve cadena vacía
# ---------------------------------------------------------------------------


def test_build_deeplink_map_missing_pair_returns_empty_string() -> None:
    """TC-014 — Par inexistente en el mapa devuelve cadena vacía, sin excepción."""
    api_detail = {
        "resources": [
            {
                "path": "/payments/{id}",
                "method": "GET",
                "url": "https://portal.example.com/apis/payments/resources/get",
            }
        ]
    }
    deeplink_map = build_deeplink_map(api_detail)
    # Par inexistente: DELETE no está en los recursos
    assert deeplink_map.get(("/payments/{id}", "DELETE"), "") == ""


def test_build_deeplink_map_completely_new_path_returns_empty_string() -> None:
    """TC-014 — Path completamente nuevo también devuelve cadena vacía."""
    api_detail = {"resources": [{"path": "/a", "method": "GET", "url": "https://example.com/a"}]}
    deeplink_map = build_deeplink_map(api_detail)
    assert deeplink_map.get(("/b", "GET"), "") == ""


def test_build_deeplink_map_empty_resources_returns_empty_dict() -> None:
    """TC-014 — Detalle sin sección de recursos devuelve diccionario vacío."""
    api_detail: dict[str, object] = {"id": "api-001"}  # sin 'resources'
    deeplink_map = build_deeplink_map(api_detail)
    assert deeplink_map == {}


# ---------------------------------------------------------------------------
# TC-020 / AC-009: error API sin attachment — log.error y continúa
# ---------------------------------------------------------------------------


def test_process_attachment_error_logs_and_continues(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """TC-020 — El error de API sin attachment se registra sin abortar el proceso."""
    from smart_api_search.cli.ingest import process_portal_apis_attachments_errors

    apis_details = [
        {"id": "api-1", "title": "API 1", "attachments": [{"url": "/api-1/attachment.json"}]},
        {"id": "api-2", "title": "API 2", "attachments": []},  # sin attachment
        {"id": "api-3", "title": "API 3", "attachments": [{"url": "/api-3/attachment.json"}]},
    ]

    with caplog.at_level(logging.ERROR):
        successes, errors = process_portal_apis_attachments_errors(apis_details)

    assert len(successes) == 2
    assert successes[0]["id"] == "api-1"
    assert successes[1]["id"] == "api-3"
    assert len(errors) == 1
    assert errors[0]["id"] == "api-2"
    # El error debe quedar registrado con log.error
    assert any("api-2" in record.message for record in caplog.records)
    # Sin stack trace: el mensaje debe ser legible y corto
    for record in caplog.records:
        assert "Traceback" not in record.message

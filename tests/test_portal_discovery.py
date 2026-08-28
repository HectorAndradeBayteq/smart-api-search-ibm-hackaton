"""Pruebas unitarias del descubrimiento paginado y descarga de specs OpenAPI.

Cubre: paginación de listado (TC-006, TC-007), descarga paralela de detalles
(TC-008, TC-009, TC-010), descarga de attachment con/sin BOM (TC-015, TC-016, TC-017).
"""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from smart_api_search.cli.ingest import download_attachment, fetch_api_details, list_all_apis

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(json_data: object | None = None, content: bytes = b"") -> MagicMock:
    """Crea un mock de respuesta httpx con raise_for_status sin efecto."""
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    if json_data is not None:
        resp.json.return_value = json_data
    resp.content = content
    resp.headers = {}
    return resp


def _make_failing_response() -> MagicMock:
    """Crea un mock de respuesta httpx que lanza HTTPStatusError al raise_for_status."""
    import httpx

    resp = MagicMock()
    resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=MagicMock()
    )
    return resp


# ---------------------------------------------------------------------------
# TC-006 / AC-004: paginación — múltiples páginas hasta cubrir count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_apis_multiple_pages() -> None:
    """TC-006 — Itera páginas hasta cubrir el total indicado por count."""
    page1_apis = [{"id": str(i)} for i in range(1, 11)]  # 10 APIs
    page2_apis = [{"id": str(i)} for i in range(11, 21)]  # 10 APIs
    page3_apis = [{"id": str(i)} for i in range(21, 26)]  # 5 APIs  (total = 25)

    mock_client = AsyncMock()
    mock_client.get.side_effect = [
        _make_response({"count": 25, "results": page1_apis}),
        _make_response({"count": 25, "results": page2_apis}),
        _make_response({"count": 25, "results": page3_apis}),
    ]

    result = await list_all_apis(mock_client)

    assert len(result) == 25
    assert mock_client.get.call_count == 3
    mock_client.get.assert_any_call("/apis", params={"page": 1})
    mock_client.get.assert_any_call("/apis", params={"page": 2})
    mock_client.get.assert_any_call("/apis", params={"page": 3})


@pytest.mark.asyncio
async def test_list_all_apis_single_page() -> None:
    """TC-006 — Una sola página cuando todas las APIs caben en ella."""
    apis = [{"id": str(i)} for i in range(1, 6)]

    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response({"count": 5, "results": apis})

    result = await list_all_apis(mock_client)

    assert len(result) == 5
    assert mock_client.get.call_count == 1


# ---------------------------------------------------------------------------
# TC-007 / AC-004: paginación — count = 0 devuelve lista vacía
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_apis_count_zero() -> None:
    """TC-007 — Si count=0 devuelve lista vacía sin más peticiones."""
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response({"count": 0, "results": []})

    result = await list_all_apis(mock_client)

    assert result == []
    assert mock_client.get.call_count == 1


@pytest.mark.asyncio
async def test_list_all_apis_raises_on_missing_count() -> None:
    """TC-006 — Falla con error claro si la respuesta no contiene 'count'."""
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response({"results": []})  # sin count

    with pytest.raises(SystemExit, match="1"):
        await list_all_apis(mock_client)


# ---------------------------------------------------------------------------
# TC-008 / AC-005: descarga paralela — orden conservado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_api_details_preserves_order() -> None:
    """TC-008 — Los detalles se devuelven en el mismo orden que la lista de IDs."""
    api_ids = [str(i) for i in range(1, 26)]  # 25 IDs

    async def fake_get(path: str, **_kwargs: object) -> MagicMock:
        api_id = path.split("/")[-1]
        return _make_response({"id": api_id, "title": f"API {api_id}"})

    mock_client = AsyncMock()
    mock_client.get.side_effect = fake_get

    result = await fetch_api_details(mock_client, api_ids)

    assert len(result) == 25
    for i, detail in enumerate(result, start=1):
        assert detail is not None
        assert detail["id"] == str(i)


@pytest.mark.asyncio
async def test_fetch_api_details_respects_concurrency_limit() -> None:
    """TC-010 — El semáforo limita la concurrencia a max_concurrent peticiones."""
    max_concurrent = 12
    concurrent_count = 0
    peak_concurrent = 0

    async def fake_get(path: str, **_kwargs: object) -> MagicMock:
        nonlocal concurrent_count, peak_concurrent
        concurrent_count += 1
        peak_concurrent = max(peak_concurrent, concurrent_count)
        await asyncio.sleep(0.01)  # simula latencia
        concurrent_count -= 1
        api_id = path.split("/")[-1]
        return _make_response({"id": api_id})

    mock_client = AsyncMock()
    mock_client.get.side_effect = fake_get

    api_ids = [str(i) for i in range(1, 26)]  # 25 IDs, más que max_concurrent
    await fetch_api_details(mock_client, api_ids, max_concurrent=max_concurrent)

    assert peak_concurrent <= max_concurrent


# ---------------------------------------------------------------------------
# TC-009 / AC-005: fallo parcial no aborta el resto
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_api_details_partial_failure_returns_none(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """TC-009 — El fallo de una petición individual produce None y registra warning."""
    import httpx

    async def fake_get(path: str, **_kwargs: object) -> MagicMock:
        api_id = path.split("/")[-1]
        if api_id == "3":
            resp = MagicMock()
            resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500", request=MagicMock(), response=MagicMock()
            )
            return resp
        return _make_response({"id": api_id})

    mock_client = AsyncMock()
    mock_client.get.side_effect = fake_get

    api_ids = ["1", "2", "3", "4", "5"]

    with caplog.at_level(logging.WARNING):
        result = await fetch_api_details(mock_client, api_ids)

    assert len(result) == 5
    assert result[0] is not None and result[0]["id"] == "1"
    assert result[1] is not None and result[1]["id"] == "2"
    assert result[2] is None  # fallo parcial
    assert result[3] is not None and result[3]["id"] == "4"
    assert result[4] is not None and result[4]["id"] == "5"
    # Debe registrar algún warning con info del fallo
    assert any("3" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# TC-015 / AC-008: attachment JSON con BOM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_attachment_json_with_bom() -> None:
    """TC-015 — Descarga attachment JSON con BOM y lo parsea correctamente."""
    json_content = b'{"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0"}}'
    bom_json = b"\xef\xbb\xbf" + json_content

    api_detail = {
        "id": "api-001",
        "title": "Test API",
        "attachments": [{"url": "/apis/api-001/attachment", "type": "openapi"}],
    }

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = bom_json
    mock_response.headers = {"content-type": "application/json"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    content_bytes, fmt = await download_attachment(mock_client, api_detail)

    assert fmt == "json"
    # El BOM debe estar eliminado
    assert not content_bytes.startswith(b"\xef\xbb\xbf")
    assert content_bytes == json_content


# ---------------------------------------------------------------------------
# TC-016 / AC-008: attachment YAML con BOM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_attachment_yaml_with_bom() -> None:
    """TC-016 — Descarga attachment YAML con BOM y lo retorna sin BOM."""
    yaml_content = b"openapi: '3.0.0'\ninfo:\n  title: Test\n  version: '1.0'\n"
    bom_yaml = b"\xef\xbb\xbf" + yaml_content

    api_detail = {
        "id": "api-002",
        "title": "YAML API",
        "attachments": [{"url": "/apis/api-002/attachment.yaml", "type": "openapi"}],
    }

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = bom_yaml
    mock_response.headers = {"content-type": "application/yaml"}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    content_bytes, fmt = await download_attachment(mock_client, api_detail)

    assert fmt == "yaml"
    assert not content_bytes.startswith(b"\xef\xbb\xbf")
    assert content_bytes == yaml_content


# ---------------------------------------------------------------------------
# TC-017 / AC-008: attachment ausente — error claro
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_attachment_raises_on_missing_attachment() -> None:
    """TC-017 — Lanza ValueError con mensaje claro si no hay attachment OpenAPI."""
    api_detail = {
        "id": "api-sin-attachment",
        "title": "API sin attachment",
        "attachments": [],
    }

    mock_client = AsyncMock()

    with pytest.raises(ValueError, match="api-sin-attachment"):
        await download_attachment(mock_client, api_detail)

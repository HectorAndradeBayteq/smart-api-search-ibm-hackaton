"""Pruebas unitarias del pipeline de enriquecimiento e indexación.

Cubre AC-002/AC-003 (enriquecimiento con/sin LLM), AC-004/AC-005
(vectores duales y tipo del vector disperso) y AC-007 (payload completo).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch


def _make_op() -> dict[str, object]:
    return {
        "method": "GET",
        "path": "/pets",
        "summary": "List pets",
        "description": "Returns all pets",
        "server_url": "https://api.example.com",
        "spec_format": "json",
        "source_file": "file:petstore.json",
        "spec_ref": "file:petstore.json|GET|/pets",
        "raw_spec": "{}",
        "tags": ["pets"],
        "operationId": "listPets",
        "api_title": "Petstore",
        "api_version": "1.0",
        "api_description": "A simple Petstore API",
        "category": "Animals",
        "environment": "prod",
        "deeplink": "https://portal.example.com/pets",
    }


# ---------------------------------------------------------------------------
# enrich_operation
# ---------------------------------------------------------------------------


def test_enrich_no_enrich_flag_skips_llm() -> None:
    """Con no_enrich=True, no debe llamarse al LLM."""
    from smart_api_search.domain.enricher import enrich_operation

    with patch("smart_api_search.domain.enricher._openai") as mock_llm:
        result = enrich_operation(_make_op(), no_enrich=True)

    mock_llm.responses.create.assert_not_called()
    assert "Petstore" in result or "List pets" in result


def test_enrich_calls_llm_when_flag_false() -> None:
    """Con no_enrich=False, debe llamarse a la API de OpenAI."""
    from smart_api_search.domain.enricher import enrich_operation

    mock_response = MagicMock()
    mock_response.output_text = "Enriched description for Petstore API."

    with patch("smart_api_search.domain.enricher._openai") as mock_llm:
        mock_llm.responses.create.return_value = mock_response
        result = enrich_operation(_make_op(), no_enrich=False)

    mock_llm.responses.create.assert_called_once()
    assert result == "Enriched description for Petstore API."


# ---------------------------------------------------------------------------
# index_operation
# ---------------------------------------------------------------------------


def test_index_operation_writes_both_vectors() -> None:
    """index_operation debe escribir el punto con los dos vectores nombrados (AC-004)."""

    from smart_api_search.domain.indexer import _DENSE, _SPARSE, index_operation

    mock_client = MagicMock()

    with (
        patch("smart_api_search.domain.indexer.get_embedding", return_value=[0.1] * 5),
        patch("smart_api_search.domain.indexer.settings") as mock_settings,
    ):
        mock_settings.COLLECTION_NAME = "test-col"
        index_operation(mock_client, _make_op(), "Test enriched text")

    mock_client.upsert.assert_called_once()
    point = mock_client.upsert.call_args[1]["points"][0]
    assert _DENSE in point.vector
    assert _SPARSE in point.vector
    assert point.vector[_DENSE] is not None
    assert point.vector[_SPARSE] is not None


def test_index_operation_sparse_is_document() -> None:
    """El vector disperso debe ser instancia de models.Document (AC-005, BR-02)."""
    from qdrant_client.http import models

    from smart_api_search.domain.indexer import _SPARSE, index_operation

    mock_client = MagicMock()

    with (
        patch("smart_api_search.domain.indexer.get_embedding", return_value=[0.1] * 5),
        patch("smart_api_search.domain.indexer.settings") as mock_settings,
    ):
        mock_settings.COLLECTION_NAME = "test-col"
        index_operation(mock_client, _make_op(), "Test enriched text")

    point = mock_client.upsert.call_args[1]["points"][0]
    assert isinstance(point.vector[_SPARSE], models.Document)


def test_index_operation_payload_has_required_fields() -> None:
    """El payload debe contener todos los campos obligatorios de AC-007."""
    from smart_api_search.domain.indexer import index_operation

    required_fields = {
        "api_title", "api_version", "api_description", "category",
        "method", "path", "summary", "description", "tags", "operationId",
        "environment", "server_url", "spec_format", "source_file",
        "enriched_text", "raw_spec", "deeplink", "spec_ref",
    }

    mock_client = MagicMock()

    with (
        patch("smart_api_search.domain.indexer.get_embedding", return_value=[0.1] * 5),
        patch("smart_api_search.domain.indexer.settings") as mock_settings,
    ):
        mock_settings.COLLECTION_NAME = "test-col"
        index_operation(mock_client, _make_op(), "Enriched text")

    point = mock_client.upsert.call_args[1]["points"][0]
    missing = required_fields - set(point.payload.keys())
    assert not missing, f"Campos faltantes en el payload: {missing}"

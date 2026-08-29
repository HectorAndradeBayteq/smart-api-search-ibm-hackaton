"""Pruebas unitarias del pipeline de búsqueda híbrida (TK-002, US-004).

Cubre: HyDE activo/inactivo, separación BM25/densa, validación top_k.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from smart_api_search.config import EmbedProvider, Settings


def _make_settings(**kwargs: object) -> Settings:
    """Crea Settings de prueba con valores ficticios."""
    defaults: dict[str, object] = {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "test-key",
        "COLLECTION_NAME": "test-col",
        "EMBED_DIM": 1024,
        "EMBED_PROVIDER": EmbedProvider.OPENAI,
        "OPENAI_API_KEY": "sk-test",
        "HYDE_ENABLED": True,
    }
    defaults.update(kwargs)
    return Settings(**defaults)  # type: ignore[arg-type]


def _make_mock_client(points: list[object] | None = None) -> AsyncMock:
    """Crea un AsyncQdrantClient simulado."""
    client = AsyncMock()
    result = MagicMock()
    result.points = points or []
    client.query_points = AsyncMock(return_value=result)
    return client


@pytest.mark.asyncio
async def test_search_top_k_validation_too_low() -> None:
    """top_k=0 debe lanzar ValueError."""
    from smart_api_search.domain.retrieval import search

    client = _make_mock_client()
    s = _make_settings()
    with pytest.raises(ValueError, match="top_k"):
        await search("query", 0, client, s)


@pytest.mark.asyncio
async def test_search_top_k_validation_too_high() -> None:
    """top_k=11 debe lanzar ValueError."""
    from smart_api_search.domain.retrieval import search

    client = _make_mock_client()
    s = _make_settings()
    with pytest.raises(ValueError, match="top_k"):
        await search("query", 11, client, s)


@pytest.mark.asyncio
async def test_search_hyde_disabled_no_llm_call() -> None:
    """Con HYDE_ENABLED=False no se llama al LLM; el embed recibe query directamente."""
    from smart_api_search.domain import retrieval

    s = _make_settings(HYDE_ENABLED=False)
    client = _make_mock_client()

    with (
        patch.object(retrieval, "hyde_expand") as mock_hyde,
        patch.object(retrieval, "embed", return_value=[0.1] * 1024) as mock_embed,
    ):
        await retrieval.search("my query", 3, client, s)

    mock_hyde.assert_not_called()
    mock_embed.assert_called_once_with("my query")


@pytest.mark.asyncio
async def test_search_hyde_enabled_uses_expanded_text() -> None:
    """Con HYDE_ENABLED=True el embed recibe el texto expandido por HyDE."""
    from smart_api_search.domain import retrieval

    s = _make_settings(HYDE_ENABLED=True)
    client = _make_mock_client()

    with (
        patch.object(retrieval, "hyde_expand", return_value="expanded text") as mock_hyde,
        patch.object(retrieval, "embed", return_value=[0.2] * 1024) as mock_embed,
    ):
        await retrieval.search("my query", 3, client, s)

    mock_hyde.assert_called_once_with("my query", s)
    mock_embed.assert_called_once_with("expanded text")


@pytest.mark.asyncio
async def test_search_bm25_always_receives_original_query() -> None:
    """La rama BM25 recibe siempre la consulta original, incluso con HyDE activo (AC-003)."""
    from qdrant_client.http import models

    from smart_api_search.domain import retrieval

    s = _make_settings(HYDE_ENABLED=True)
    client = _make_mock_client()

    with (
        patch.object(retrieval, "hyde_expand", return_value="expanded text"),
        patch.object(retrieval, "embed", return_value=[0.1] * 1024),
    ):
        await retrieval.search("original query", 2, client, s)

    call_kwargs = client.query_points.call_args[1]
    prefetches = call_kwargs["prefetch"]
    # El segundo prefetch es la rama BM25
    bm25_prefetch = prefetches[1]
    assert isinstance(bm25_prefetch.query, models.Document)
    assert bm25_prefetch.query.text == "original query"
    assert bm25_prefetch.query.model == "Qdrant/bm25"


@pytest.mark.asyncio
async def test_search_valid_top_k_bounds() -> None:
    """top_k=1 y top_k=10 son válidos y no lanzan excepción."""
    from smart_api_search.domain import retrieval

    s = _make_settings(HYDE_ENABLED=False)
    client = _make_mock_client()

    with patch.object(retrieval, "embed", return_value=[0.0] * 1024):
        await retrieval.search("q", 1, client, s)
        await retrieval.search("q", 10, client, s)

    assert client.query_points.call_count == 2

"""Pruebas unitarias de shared.embed() y warn_if_mismatch() (TK-004, US-004).

Cubre: proveedor OpenAI, proveedor Watsonx, advertencia por desajuste (AC-009..AC-011).
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from smart_api_search.config import EmbedProvider


def test_embed_openai_calls_sdk_with_correct_model_and_dim() -> None:
    """embed() con EMBED_PROVIDER=openai llama al SDK con modelo y dimensión correctos."""
    from smart_api_search.shared import embeddings

    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=[0.1] * 1024)]

    mock_settings = MagicMock()
    mock_settings.EMBED_PROVIDER = EmbedProvider.OPENAI
    mock_settings.EMBED_DIM = 1024

    with (
        patch.object(embeddings, "settings", mock_settings),
        patch.object(embeddings, "openai") as mock_openai,
    ):
        mock_openai.embeddings.create.return_value = fake_response
        result = embeddings.embed("test query")

    mock_openai.embeddings.create.assert_called_once_with(
        model="text-embedding-3-large",
        input="test query",
        dimensions=1024,
    )
    assert len(result) == 1024


def test_embed_watsonx_calls_sdk_with_correct_model() -> None:
    """embed() con EMBED_PROVIDER=watsonx llama al cliente Watsonx."""
    from smart_api_search.shared import embeddings

    mock_instance = MagicMock()
    mock_instance.embed_query.return_value = [0.5] * 768

    mock_settings = MagicMock()
    mock_settings.EMBED_PROVIDER = EmbedProvider.WATSONX
    mock_settings.EMBED_DIM = 768
    mock_settings.WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
    mock_settings.WATSONX_API_KEY = "wx-key"
    mock_settings.WATSONX_PROJECT_ID = "proj-id"

    # _embed_watsonx usa ibm_watsonx_ai.foundation_models.Embeddings (fallback);
    # parchamos ese símbolo para que no contacte la red.
    with (
        patch.object(embeddings, "settings", mock_settings),
        patch("ibm_watsonx_ai.foundation_models.Embeddings", return_value=mock_instance),
    ):
        result = embeddings.embed("test query")

    assert result == [0.5] * 768


def test_embed_is_same_as_get_embedding() -> None:
    """embed y get_embedding son el mismo objeto (alias de compatibilidad)."""
    from smart_api_search.shared import embeddings

    assert embeddings.embed is embeddings.get_embedding


def test_warn_if_mismatch_emits_warning_on_provider_mismatch(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """warn_if_mismatch() emite logging.warning cuando el proveedor no coincide."""
    from smart_api_search.shared import embeddings

    mock_settings = MagicMock()
    mock_settings.EMBED_PROVIDER = EmbedProvider.OPENAI
    mock_settings.EMBED_DIM = 1024

    with (
        patch.object(embeddings, "settings", mock_settings),
        caplog.at_level(logging.WARNING),
    ):
        embeddings.warn_if_mismatch("watsonx", 1024)

    assert any("proveedor" in record.message for record in caplog.records)


def test_warn_if_mismatch_emits_warning_on_dim_mismatch(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """warn_if_mismatch() emite logging.warning cuando la dimensión no coincide."""
    from smart_api_search.shared import embeddings

    mock_settings = MagicMock()
    mock_settings.EMBED_PROVIDER = EmbedProvider.OPENAI
    mock_settings.EMBED_DIM = 1024

    with (
        patch.object(embeddings, "settings", mock_settings),
        caplog.at_level(logging.WARNING),
    ):
        embeddings.warn_if_mismatch("openai", 768)

    assert any("dimensión" in record.message for record in caplog.records)


def test_warn_if_mismatch_no_warning_when_matching(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """warn_if_mismatch() NO emite warning cuando proveedor y dimensión coinciden."""
    from smart_api_search.shared import embeddings

    mock_settings = MagicMock()
    mock_settings.EMBED_PROVIDER = EmbedProvider.OPENAI
    mock_settings.EMBED_DIM = 1024

    with (
        patch.object(embeddings, "settings", mock_settings),
        caplog.at_level(logging.WARNING),
    ):
        embeddings.warn_if_mismatch("openai", 1024)

    # No warnings should have been emitted
    assert not any(record.levelno == logging.WARNING for record in caplog.records)

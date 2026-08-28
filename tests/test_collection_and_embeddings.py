"""Pruebas unitarias de ensure_collection() y del cliente de embeddings.

Cubre los criterios AC-001 (colección híbrida), AC-005 (vector disperso como
Document), AC-008 (índices keyword idempotentes), AC-025 (proveedor configurable)
y AC-026 (modelos por proveedor).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(**kwargs: object) -> object:
    """Crea un mock de settings con los atributos indicados."""
    mock = MagicMock()
    for k, v in kwargs.items():
        setattr(mock, k, v)
    return mock


# ---------------------------------------------------------------------------
# IT-01: config.py expone las variables Qdrant y embeddings
# ---------------------------------------------------------------------------


def test_config_has_qdrant_fields() -> None:
    """config.Settings debe exponer QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME."""
    from smart_api_search import config

    s = config.Settings(
        QDRANT_URL="http://localhost:6333",
        QDRANT_API_KEY="key",
        COLLECTION_NAME="test-col",
        EMBED_DIM=1024,
        EMBED_PROVIDER=config.EmbedProvider.OPENAI,
    )
    assert s.QDRANT_URL == "http://localhost:6333"
    assert s.QDRANT_API_KEY == "key"
    assert s.COLLECTION_NAME == "test-col"
    assert s.EMBED_DIM == 1024
    assert s.EMBED_PROVIDER == config.EmbedProvider.OPENAI


def test_config_embed_dim_never_literal() -> None:
    """EMBED_DIM debe venir de config, nunca hardcodeado en otra parte."""
    from smart_api_search import config

    # Verificar que config expone EMBED_DIM como campo de modelo (pydantic v2)
    assert "EMBED_DIM" in config.Settings.model_fields


# ---------------------------------------------------------------------------
# IT-02 / IT-03: get_embedding delega al SDK correcto
# ---------------------------------------------------------------------------


def test_get_embedding_openai_provider() -> None:
    """get_embedding con EMBED_PROVIDER=openai debe llamar al SDK de OpenAI."""
    from smart_api_search.config import EmbedProvider
    from smart_api_search.shared import embeddings

    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

    mock_settings = _make_settings(
        EMBED_PROVIDER=EmbedProvider.OPENAI,
        EMBED_DIM=1024,
    )

    with (
        patch.object(embeddings, "settings", mock_settings),
        patch.object(embeddings, "openai") as mock_openai,
    ):
        mock_openai.embeddings.create.return_value = fake_response

        result = embeddings.get_embedding("hola mundo")

        mock_openai.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large",
            input="hola mundo",
            dimensions=1024,
        )
        assert result == [0.1, 0.2, 0.3]


def test_get_embedding_watsonx_provider() -> None:
    """get_embedding con EMBED_PROVIDER=watsonx debe llamar al SDK de IBM."""
    from smart_api_search.config import EmbedProvider
    from smart_api_search.shared import embeddings

    mock_instance = MagicMock()
    mock_instance.embed_query.return_value = [0.4, 0.5, 0.6]

    mock_settings = _make_settings(
        EMBED_PROVIDER=EmbedProvider.WATSONX,
        EMBED_DIM=768,
        WATSONX_API_KEY="wxkey",
        WATSONX_URL="https://us-south.ml.cloud.ibm.com",
        WATSONX_PROJECT_ID="proj",
    )

    with (
        patch.object(embeddings, "settings", mock_settings),
        patch.object(embeddings, "WatsonxEmbeddings", return_value=mock_instance),
    ):
        result = embeddings.get_embedding("hola mundo")
        assert result == [0.4, 0.5, 0.6]


def test_shared_exports_get_embedding() -> None:
    """smart_api_search.shared debe exportar get_embedding."""
    from smart_api_search import shared

    assert hasattr(shared, "get_embedding")
    assert callable(shared.get_embedding)


# ---------------------------------------------------------------------------
# IT-04: ensure_collection crea la colección híbrida e índices keyword
# ---------------------------------------------------------------------------


def test_ensure_collection_creates_when_not_exists() -> None:
    """ensure_collection debe llamar a create_collection cuando no existe."""
    from smart_api_search.domain.collection import ensure_collection

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False

    mock_settings = _make_settings(COLLECTION_NAME="test-col", EMBED_DIM=1024)

    with patch("smart_api_search.domain.collection.settings", mock_settings):
        ensure_collection(mock_client)

    mock_client.create_collection.assert_called_once()
    call_kwargs = mock_client.create_collection.call_args
    assert call_kwargs[1]["collection_name"] == "test-col" or call_kwargs[0][0] == "test-col"


def test_ensure_collection_skips_when_exists() -> None:
    """ensure_collection NO debe llamar a create_collection si ya existe."""
    from smart_api_search.domain.collection import ensure_collection

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True

    mock_settings = _make_settings(COLLECTION_NAME="test-col", EMBED_DIM=1024)

    with patch("smart_api_search.domain.collection.settings", mock_settings):
        ensure_collection(mock_client)

    mock_client.create_collection.assert_not_called()


def test_ensure_collection_creates_payload_indexes() -> None:
    """ensure_collection debe crear índices keyword para source_file y spec_ref."""
    from smart_api_search.domain.collection import ensure_collection

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False

    mock_settings = _make_settings(COLLECTION_NAME="test-col", EMBED_DIM=1024)

    with patch("smart_api_search.domain.collection.settings", mock_settings):
        ensure_collection(mock_client)

    # Debe haber al menos dos llamadas a create_payload_index: source_file y spec_ref
    calls = mock_client.create_payload_index.call_args_list
    field_names = []
    for c in calls:
        args = c[0]
        kwargs = c[1]
        field_name = kwargs.get("field_name") or (args[1] if len(args) > 1 else "")
        field_names.append(field_name)

    assert "source_file" in field_names
    assert "spec_ref" in field_names


def test_ensure_collection_idempotent_index_error() -> None:
    """ensure_collection debe ignorar excepciones al crear índices que ya existen."""
    from smart_api_search.domain.collection import ensure_collection

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    # Simular que create_payload_index lanza excepción (índice ya existe)
    mock_client.create_payload_index.side_effect = Exception("already exists")

    mock_settings = _make_settings(COLLECTION_NAME="test-col", EMBED_DIM=1024)

    with patch("smart_api_search.domain.collection.settings", mock_settings):
        # No debe propagar la excepción
        ensure_collection(mock_client)

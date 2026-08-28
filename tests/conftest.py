"""Fixtures compartidas para las pruebas de US-004 (TK-004).

Provee: settings de prueba (openai/watsonx), ScoredPoint sintético
y un cliente Qdrant asíncrono simulado.
"""

from __future__ import annotations

import json

import pytest

from smart_api_search.config import EmbedProvider, Settings


@pytest.fixture()
def settings_openai() -> Settings:
    """Settings con EMBED_PROVIDER=openai, claves ficticias."""
    return Settings(
        QDRANT_URL="http://localhost:6333",
        QDRANT_API_KEY="test-key",
        COLLECTION_NAME="test-col",
        EMBED_DIM=1024,
        EMBED_PROVIDER=EmbedProvider.OPENAI,
        OPENAI_API_KEY="sk-test",
        HYDE_ENABLED=True,
    )  # type: ignore[call-arg]


@pytest.fixture()
def settings_watsonx() -> Settings:
    """Settings con EMBED_PROVIDER=watsonx, claves ficticias."""
    return Settings(
        QDRANT_URL="http://localhost:6333",
        QDRANT_API_KEY="test-key",
        COLLECTION_NAME="test-col",
        EMBED_DIM=768,
        EMBED_PROVIDER=EmbedProvider.WATSONX,
        WATSONX_API_KEY="wx-key",
        WATSONX_URL="https://us-south.ml.cloud.ibm.com",
        WATSONX_PROJECT_ID="proj-id",
        HYDE_ENABLED=False,
    )  # type: ignore[call-arg]


@pytest.fixture()
def scored_point_factory():  # type: ignore[no-untyped-def]
    """Fábrica de ScoredPoint sintéticos con payload mínimo válido."""
    from qdrant_client.http import models

    def _factory(
        spec_ref: str = "portal:api|GET|/users",
        server_url: str = "https://api.example.com",
        path: str = "/users",
        method: str = "GET",
        **extra: object,
    ) -> models.ScoredPoint:
        raw_spec = json.dumps({"operation": {}})
        payload = {
            "spec_ref": spec_ref,
            "server_url": server_url,
            "path": path,
            "method": method,
            "category": "Test",
            "summary": "Test endpoint",
            "description": "",
            "enriched_text": "",
            "deeplink": "",
            "tags": [],
            "source_file": "portal:api",
            "raw_spec": raw_spec,
            **extra,
        }
        return models.ScoredPoint(
            id="fixture-id",
            version=1,
            score=0.9,
            payload=payload,
            vector=None,
        )

    return _factory

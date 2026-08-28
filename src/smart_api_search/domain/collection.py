"""Gestión de la colección Qdrant híbrida: creación idempotente y configuración.

Implementa ``ensure_collection()`` que crea o verifica la colección con:
- Vector denso con métrica coseno y dimensión ``EMBED_DIM`` (AC-001, ADR-002, ADR-009).
- Vector disperso BM25 con modificador IDF (AC-001, ADR-010).
- Índices de payload ``keyword`` para ``source_file`` y ``spec_ref`` (AC-008, ADR-011, BR-03).
"""

from __future__ import annotations

import contextlib

from qdrant_client import QdrantClient
from qdrant_client.http import models

from smart_api_search.config import settings

#: Nombre del vector denso en la colección híbrida.
DENSE_VECTOR_NAME = "dense"

#: Nombre del vector disperso BM25 en la colección híbrida.
SPARSE_VECTOR_NAME = "sparse"


def ensure_collection(client: QdrantClient) -> None:
    """Crea o verifica la colección Qdrant con configuración híbrida.

    Si la colección ya existe, no la recrea. En cualquier caso, crea los
    índices de payload ``keyword`` para ``source_file`` y ``spec_ref`` de
    forma idempotente (las excepciones por índices ya existentes se ignoran).

    La dimensión del vector denso se lee de ``settings.EMBED_DIM`` para cumplir
    AC-027: nunca aparece como literal numérico en este módulo.

    Args:
        client: Cliente Qdrant ya inicializado.
    """
    collection_name = settings.COLLECTION_NAME
    embed_dim = settings.EMBED_DIM

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                DENSE_VECTOR_NAME: models.VectorParams(
                    size=embed_dim,
                    distance=models.Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                ),
            },
        )

    # Crear índices keyword de forma idempotente (BR-03, ADR-011).
    for field_name in ("source_file", "spec_ref"):
        with contextlib.suppress(Exception):
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

"""Indexación híbrida de operaciones OpenAPI en Qdrant.

Implementa ``index_operation()`` que escribe un punto con vector denso y
vector disperso BM25 simultáneamente (AC-004, BR-01, BR-02, ADR-010).
El payload contiene todos los campos obligatorios (AC-007).
``spec_ref`` se deriva como ``{source_file}|{METHOD}|{path}`` (ADR-005).
"""

from __future__ import annotations

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from smart_api_search.config import settings
from smart_api_search.shared import get_embedding

#: Nombre del vector denso (debe coincidir con collection.DENSE_VECTOR_NAME).
_DENSE = "dense"

#: Nombre del vector disperso BM25 (debe coincidir con collection.SPARSE_VECTOR_NAME).
_SPARSE = "sparse"

#: Modelo BM25 usado por Qdrant para la inferencia del vector disperso.
_BM25_MODEL = "Qdrant/bm25"


def index_operation(
    client: QdrantClient,
    op: dict[str, object],
    enriched_text: str,
) -> None:
    """Escribe una operación OpenAPI como punto híbrido en Qdrant.

    Compone el texto indexable con la cabecera compacta más ``enriched_text``
    y genera ambos vectores (denso y disperso) antes de escribir el punto.
    El ``deeplink`` no forma parte del texto embebido (AC-006).
    Nunca escribe un punto con un solo vector (BR-01, AC-004).

    Args:
        client: Cliente Qdrant ya inicializado.
        op: Diccionario de operación con todos los campos del spec.
        enriched_text: Texto generado por el LLM o de metadatos.
    """
    # --- Cabecera compacta (AC-006) ---
    raw_tags = op.get("tags")
    tags_str = ", ".join(str(t) for t in raw_tags) if isinstance(raw_tags, list) else ""
    header = (
        f"[{op.get('category', '')} | {op.get('api_title', '')} | "
        f"{op.get('spec_format', '')} | {op.get('method', '')} {op.get('path', '')} | "
        f"{tags_str} | {op.get('server_url', '')}]"
    )
    indexable_text = f"{header}\n\n{enriched_text}"

    # --- Vectores (BR-01, BR-02, AC-004, AC-005) ---
    dense_vector = get_embedding(indexable_text)
    sparse_vector = models.Document(text=indexable_text, model=_BM25_MODEL)

    # --- spec_ref (ADR-005) ---
    spec_ref = f"{op.get('source_file', '')}|{str(op.get('method', '')).upper()}|{op.get('path', '')}"

    # --- Payload completo (AC-007) ---
    payload: dict[str, object] = {
        "api_title": op.get("api_title", ""),
        "api_version": op.get("api_version", ""),
        "api_description": op.get("api_description", ""),
        "category": op.get("category", ""),
        "method": op.get("method", ""),
        "path": op.get("path", ""),
        "summary": op.get("summary", ""),
        "description": op.get("description", ""),
        "tags": op.get("tags", []),
        "operationId": op.get("operationId", ""),
        "environment": op.get("environment", ""),
        "server_url": op.get("server_url", ""),
        "spec_format": op.get("spec_format", ""),
        "source_file": op.get("source_file", ""),
        "spec_ref": spec_ref,
        "enriched_text": enriched_text,
        "raw_spec": op.get("raw_spec", ""),
        "deeplink": op.get("deeplink", ""),
    }

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector={
            _DENSE: dense_vector,
            _SPARSE: sparse_vector,
        },
        payload=payload,
    )

    client.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=[point],
    )

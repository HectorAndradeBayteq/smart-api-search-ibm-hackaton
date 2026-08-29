"""Composición y normalización del resultado de búsqueda.

Transforma ``ScoredPoint`` de Qdrant en objetos ``SearchResult`` (MD-03).
Incluye parseo estricto de ``spec_ref`` (3 segmentos no vacíos) y recuperación
segura por referencia que devuelve lista vacía sin lanzar excepción (AC-008).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from smart_api_search.domain.params import normalize_params


@dataclass
class SearchResult:
    """Resultado de búsqueda (MD-03).

    Representa un endpoint recuperado y ordenado por RRF.
    """

    ranking: int
    method: str
    path: str
    call_url: str
    spec_ref: str
    source: str
    category: str | None = field(default=None)
    summary: str | None = field(default=None)
    description: str | None = field(default=None)
    consolidated_definition: str | None = field(default=None)
    deeplink: str | None = field(default=None)
    tags: list[str] = field(default_factory=list)
    params: list[dict[str, Any]] = field(default_factory=list)
    body: dict[str, Any] | None = field(default=None)


def _parse_spec_ref(spec_ref: str) -> tuple[str, str, str] | None:
    """Parsea ``spec_ref`` en exactamente tres segmentos no vacíos (AC-007).

    Returns:
        Tupla ``(source_file, method, path)`` o ``None`` si el formato es inválido.
    """
    parts = spec_ref.split("|")
    if len(parts) != 3 or not all(parts):
        return None
    return (parts[0], parts[1], parts[2])


def compose_result(
    scored_point: qdrant_models.ScoredPoint,
    ranking: int,
) -> SearchResult | None:
    """Construye un ``SearchResult`` a partir de un ``ScoredPoint`` de Qdrant.

    Args:
        scored_point: Punto recuperado por Qdrant con payload completo.
        ranking: Posición en la lista de resultados (1-based).

    Returns:
        ``SearchResult`` con todos los campos de MD-03, o ``None`` si el
        ``spec_ref`` del payload tiene formato inválido (omitir del ranking).
    """
    payload: dict[str, Any] = dict(scored_point.payload or {})

    spec_ref: str = str(payload.get("spec_ref") or "")
    parsed = _parse_spec_ref(spec_ref)
    if parsed is None:
        logging.warning(
            "spec_ref inválido en punto %s — omitido del ranking: %r",
            scored_point.id,
            spec_ref,
        )
        return None

    source_file, method, path = parsed
    server_url: str = str(payload.get("server_url") or "")
    call_url = server_url + path

    # Parámetros normalizados (AC-006)
    raw_spec_str: str = str(payload.get("raw_spec") or "{}")
    try:
        raw_spec: dict[str, Any] = json.loads(raw_spec_str)
    except (json.JSONDecodeError, ValueError):
        raw_spec = {}
    operation: dict[str, Any] = raw_spec.get("operation") or {}
    params = normalize_params(operation, path)

    # Body del request si existe
    body: dict[str, Any] | None = None
    request_body = operation.get("requestBody")
    if isinstance(request_body, dict):
        body = request_body

    # Tags (asegurar list[str])
    raw_tags = payload.get("tags") or []
    tags: list[str] = [str(t) for t in raw_tags] if isinstance(raw_tags, list) else []

    return SearchResult(
        ranking=ranking,
        category=str(payload.get("category") or "") or None,
        method=method,
        path=path,
        summary=str(payload.get("summary") or "") or None,
        description=str(payload.get("description") or "") or None,
        consolidated_definition=str(payload.get("enriched_text") or "") or None,
        call_url=call_url,
        deeplink=str(payload.get("deeplink") or "") or None,
        spec_ref=spec_ref,
        tags=tags,
        source=source_file,
        params=params,
        body=body,
    )


async def get_by_spec_ref(
    spec_ref: str,
    client: AsyncQdrantClient,
    collection: str,
) -> list[SearchResult]:
    """Recupera resultados por ``spec_ref`` de forma segura (AC-008).

    Devuelve lista vacía sin lanzar excepción si el punto no existe o si el
    ``spec_ref`` tiene formato inválido.

    Args:
        spec_ref: Referencia en formato ``source_file|METHOD|/path``.
        client: ``AsyncQdrantClient`` ya inicializado.
        collection: Nombre de la colección Qdrant.

    Returns:
        Lista de ``SearchResult`` (puede ser vacía).
    """
    if _parse_spec_ref(spec_ref) is None:
        logging.warning("get_by_spec_ref: spec_ref con formato inválido: %r", spec_ref)
        return []

    try:
        scroll_result, _ = await client.scroll(
            collection_name=collection,
            scroll_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="spec_ref",
                        match=qdrant_models.MatchValue(value=spec_ref),
                    )
                ]
            ),
            with_payload=True,
            limit=10,
        )
    except Exception:
        return []

    results: list[SearchResult] = []
    for i, record in enumerate(scroll_result, start=1):
        # Convert Record to a ScoredPoint-like object for compose_result
        fake_point = qdrant_models.ScoredPoint(
            id=record.id,
            version=0,
            score=0.0,
            payload=record.payload,
            vector=None,
        )
        composed = compose_result(fake_point, ranking=i)
        if composed is not None:
            results.append(composed)

    return results

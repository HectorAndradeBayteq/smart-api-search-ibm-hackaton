"""Composición y recuperación de resultados de búsqueda.

Este módulo será implementado completamente en US-004. Por ahora expone
los stubs de interfaz que el servidor MCP (US-005) necesita para registrar
sus herramientas.
"""
from __future__ import annotations

from typing import Any


def compose_result(point: dict[str, Any], ranking: int) -> dict[str, Any]:
    """Compone un SearchResult (MD-03) a partir de un punto Qdrant scored.

    Args:
        point: Punto scored devuelto por Qdrant (payload + score).
        ranking: Posición del resultado en la lista (1-based).

    Returns:
        Diccionario con los campos de SearchResult (MD-03).

    Note:
        Stub — implementación completa en US-004/TK-003.
    """
    payload: dict[str, Any] = point.get("payload", {})
    server_url: str = str(payload.get("server_url", ""))
    path: str = str(payload.get("path", ""))
    return {
        "ranking": ranking,
        "category": payload.get("category"),
        "method": payload.get("method", ""),
        "path": path,
        "summary": payload.get("summary"),
        "description": payload.get("description"),
        "call_url": server_url + path,
        "deeplink": payload.get("deeplink", ""),
        "spec_ref": payload.get("spec_ref", ""),
        "tags": payload.get("tags", []),
        "source": payload.get("source_file", ""),
        "params": [],
        "body": None,
    }


def get_by_spec_ref(
    spec_ref: str,
    client: Any,  # noqa: ANN401
    collection: str,
) -> list[dict[str, Any]]:
    """Recupera un punto Qdrant por su spec_ref.

    Args:
        spec_ref: Referencia única de la operación (``source|METHOD|/path``).
        client: Cliente Qdrant asíncrono o síncrono.
        collection: Nombre de la colección vectorial.

    Returns:
        Lista de puntos que coinciden con el spec_ref (vacía si no se encuentra).

    Note:
        Stub — implementación completa en US-004/TK-003.
    """
    return []

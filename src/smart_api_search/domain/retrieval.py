"""Capa de recuperación (retrieval) — búsqueda híbrida HyDE + RRF.

Este módulo será implementado completamente en US-004. Por ahora expone
los stubs de interfaz que el servidor MCP (US-005) necesita para registrar
sus herramientas.
"""
from __future__ import annotations

from typing import Any


async def search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Ejecuta la búsqueda híbrida HyDE + RRF sobre la colección Qdrant.

    Args:
        query: Consulta en lenguaje natural.
        top_k: Número de resultados a devolver (1–10).

    Returns:
        Lista de puntos scored ordenados por relevancia RRF.

    Note:
        Stub — implementación completa en US-004/TK-002.
    """
    return []

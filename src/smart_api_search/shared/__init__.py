"""Capa compartida de embeddings: único punto de acceso al modelo de vectorización.

Arquitectura: ninguna otra capa puede importar directamente los clientes de
OpenAI o Watsonx para obtener embeddings — toda llamada debe pasar por aquí
(ver ADR-009 y RNF-07).
"""

from __future__ import annotations

from smart_api_search.shared.embeddings import get_embedding

__all__ = ["get_embedding"]

"""Pipeline de búsqueda híbrida HyDE + RRF.

Implementa ``search(query, top_k)`` que:
1. Expande la consulta opcionalmente con HyDE (LLM) si ``HYDE_ENABLED=True``.
2. Genera el vector denso via la capa ``shared``.
3. Envuelve la consulta original (sin modificar) en ``Document`` para BM25.
4. Lanza ambos prefetch en paralelo contra Qdrant con fusión RRF nativa.

La rama BM25 recibe siempre el texto original (AC-003, ADR-010).
La capa ``shared`` es el único punto de acceso a embeddings (ADR-009).
"""

from __future__ import annotations

from typing import Any

import openai as _openai
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from smart_api_search.config import Settings
from smart_api_search.config import settings as _default_settings
from smart_api_search.domain.collection import DENSE_VECTOR_NAME, SPARSE_VECTOR_NAME
from smart_api_search.shared import embed

#: Modelo BM25 que Qdrant infiere del objeto ``Document`` (ADR-010).
_BM25_MODEL = "Qdrant/bm25"

#: Prompt de sistema para la expansión HyDE.
_HYDE_SYSTEM_PROMPT = (
    "You are an API documentation expert. "
    "Given a natural-language query about an API, generate a concise hypothetical "
    "API endpoint description (1-3 sentences) that would match that query. "
    "Only output the description, nothing else."
)


def hyde_expand(query: str, s: Settings | None = None) -> str:
    """Genera una descripción hipotética de endpoint a partir de ``query`` (HyDE).

    Llama a la OpenAI Responses API. Solo debe invocarse cuando
    ``settings.HYDE_ENABLED=True`` (ADR-008).

    Args:
        query: Consulta original del usuario.
        s: Instancia de ``Settings`` a usar (por defecto la global).

    Returns:
        Texto expandido hipotético generado por el LLM.
    """
    _s = s or _default_settings
    response = _openai.responses.create(
        model="gpt-4o-mini",
        input=query,
        instructions=_HYDE_SYSTEM_PROMPT,
    )
    return str(response.output_text)


async def search(
    query: str,
    top_k: int,
    client: AsyncQdrantClient,
    s: Settings | None = None,
) -> list[models.ScoredPoint]:
    """Ejecuta la búsqueda híbrida y devuelve hasta ``top_k`` resultados.

    Flujo (AC-001, FL-02):
    1. Validar ``1 ≤ top_k ≤ 10``.
    2. Expandir con HyDE si ``HYDE_ENABLED=True``; si no, usar ``query`` directamente.
    3. Embeber el texto expandido (o ``query``) para la rama densa.
    4. Envolver ``query`` original en ``Document(text=query, model="Qdrant/bm25")``.
    5. Lanzar ambos prefetch con fusión RRF nativa de Qdrant.
    6. Devolver los ``top_k`` puntos fusionados.

    Args:
        query: Consulta en lenguaje natural.
        top_k: Número de resultados a devolver (1 ≤ top_k ≤ 10).
        client: ``AsyncQdrantClient`` ya inicializado.
        s: Instancia de ``Settings`` a usar (por defecto la global).

    Returns:
        Lista de ``ScoredPoint`` ordenada por score RRF descendente.

    Raises:
        ValueError: Si ``top_k`` está fuera del rango [1, 10].
    """
    _s = s or _default_settings

    # IT-05: Validar rango de top_k (AC-001)
    if not (1 <= top_k <= 10):
        raise ValueError(f"top_k debe estar en [1, 10], recibido: {top_k}")

    # IT-01 / IT-02: Expansión HyDE + rama densa
    text_to_embed = hyde_expand(query, _s) if _s.HYDE_ENABLED else query
    dense_vector: list[float] = embed(text_to_embed)

    # IT-03: Rama BM25 siempre con la consulta original (AC-003)
    bm25_document: Any = models.Document(text=query, model=_BM25_MODEL)

    # IT-04: Prefetch paralelo + fusión RRF
    prefetch_limit = top_k * 2
    result = await client.query_points(
        collection_name=_s.COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=dense_vector,
                using=DENSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
            models.Prefetch(
                query=bm25_document,
                using=SPARSE_VECTOR_NAME,
                limit=prefetch_limit,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )
    return list(result.points)

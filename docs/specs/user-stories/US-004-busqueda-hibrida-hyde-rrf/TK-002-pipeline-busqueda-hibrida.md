# TK-002: Pipeline de búsqueda híbrida

**Estado:** Ready
**Historia:** [US-004](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el pipeline de búsqueda híbrida en `smart_api_search.domain`: recibe `query: str` y `top_k: int` (1 ≤ top_k ≤ 10), expande opcionalmente la consulta con HyDE (llamada al LLM si `HYDE_ENABLED=true`), genera el vector denso a través de la capa `shared`, envuelve la consulta original en `Document(text=query, model="Qdrant/bm25")` para la rama dispersa, lanza ambos prefetch en paralelo contra Qdrant y devuelve los `top_k` puntos fusionados por RRF. Cuando `HYDE_ENABLED=false` no se llama al LLM y se embebe la consulta original directamente.

## Dependencias

- TK-001 (`smart_api_search.shared.embed`) — generación del vector denso a partir del texto expandido o de la consulta original
- `qdrant-client` — `AsyncQdrantClient`, `models.Prefetch`, `models.SparseVector`, `models.Document`, fusión RRF nativa
- OpenAI Responses API (Python SDK) — generación del texto HyDE cuando `HYDE_ENABLED=true`
- `smart_api_search.config.Settings` (MD-05) — `HYDE_ENABLED`, claves de OpenAI y parámetros de Qdrant

## Referencias

- **Arquitectura:** [ADR-007 — Consulta híbrida con ramas densa y BM25 fusionadas con RRF](../../adr/ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- **Arquitectura:** [ADR-008 — Expansión de consulta con HyDE, desactivable](../../adr/ADR-008-expansion-consulta-hyde.md)
- **Arquitectura:** [ADR-010 — Inferencia de vectores dispersos delegada al motor](../../adr/ADR-010-inferencia-vectores-dispersos-motor.md)
- **Documentación técnica:** [FL-02: Retrieval híbrido (HyDE + RRF)](../../specs/technical-docs/smart-api-search.md#fl-02)
- **Documentación técnica:** [MD-05: Settings](../../specs/technical-docs/smart-api-search.md#md-05)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── domain/
        ├── + retrieval.py     # Función search(query, top_k) con el pipeline completo HyDE→embed→prefetch→RRF
        └── ~ __init__.py      # Reexportar search desde domain
```

## Plan de implementación

- [x] **IT-01** — Implementar la función `hyde_expand(query: str, settings: Settings) -> str` en `domain/retrieval.py`
  Llama a la OpenAI Responses API con un prompt que pide generar una descripción hipotética de un endpoint de API a partir de `query`. Devuelve el texto expandido. Solo se invoca si `settings.HYDE_ENABLED=True`.
- [x] **IT-02** — Implementar la rama densa: `embed` del texto expandido (HyDE) o de `query` directamente
  Llamar a `shared.embed(hyde_text if settings.HYDE_ENABLED else query)`. El vector resultante es el vector denso para el prefetch coseno.
- [x] **IT-03** — Implementar la rama BM25: envolver `query` original en `Document`
  Construir `Document(text=query, model="Qdrant/bm25")`. El argumento `query` es siempre el texto original, sin modificar, incluso cuando HyDE está activo.
- [x] **IT-04** — Lanzar ambos prefetch en paralelo y fusionar con RRF
  Usar `AsyncQdrantClient.query_points()` con dos objetos `Prefetch`: uno con el vector denso (coseno, límite `top_k * 2`) y otro con el objeto Document BM25 (límite `top_k * 2`). Solicitar fusión RRF nativa de Qdrant. Devolver los `top_k` puntos fusionados como lista de `models.ScoredPoint`.
- [x] **IT-05** — Validar `1 ≤ top_k ≤ 10` al inicio de `search()`
  Lanzar `ValueError` con mensaje claro si `top_k` está fuera de rango; la capa MCP lo capturará y lo convertirá en `tool_error`.
- [x] **IT-06** — Añadir tipos completos y anotaciones mypy
  Asegurar que `domain/retrieval.py` pasa `mypy --strict` sin errores nuevos.

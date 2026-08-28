# Architecture Decision Records

Catálogo de las decisiones arquitectónicas del proyecto. Sirve para localizar rápidamente qué se decidió, por qué y con qué estado (`Draft`/`Proposed`/`Accepted`).

<!-- arch-manage añade aquí una línea por ADR creado: `- [ADR-XXX: Título](ADR-XXX-slug.md)`. No reordenar ni eliminar entradas manualmente. -->

- [ADR-001: FastMCP como framework del servidor MCP](ADR-001-fastmcp-servidor-mcp.md)
- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [ADR-003: Python 3.12, pip y entorno virtual como toolchain](ADR-003-python312-pip-venv-toolchain.md)
- [ADR-004: Compuerta de calidad: pytest, ruff, mypy estricto, coverage ≥ 80%](ADR-004-compuerta-calidad-pytest-mypy-ruff.md)
- [ADR-005: Unidad de indexación es la operación OpenAPI](ADR-005-unidad-indexacion-operacion-openapi.md)
- [ADR-006: Enriquecimiento LLM en tiempo de ingesta](ADR-006-enriquecimiento-llm-ingesta.md)
- [ADR-007: Consulta híbrida con ramas densa y BM25 fusionadas con RRF](ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- [ADR-008: Expansión de consulta con HyDE, desactivable](ADR-008-expansion-consulta-hyde.md)
- [ADR-009: Modelo de embedding único truncado a EMBED_DIM, fuente única en capa compartida](ADR-009-modelo-embedding-unico-embed-dim.md)
- [ADR-010: Inferencia de vectores dispersos delegada al motor](ADR-010-inferencia-vectores-dispersos-motor.md)
- [ADR-011: Campos de payload indexados al asegurar la colección](ADR-011-campos-payload-indexados-ensure-collection.md)
- [ADR-012: Idempotencia de ingesta con granularidad de fuente](ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- [ADR-013: Arranque del servidor MCP por referencia ASGI](ADR-013-arranque-servidor-mcp-asgi.md)
- [ADR-014: Proveedor de embeddings configurable — OpenAI y Watsonx](ADR-014-proveedor-embeddings-openai-watsonx.md)

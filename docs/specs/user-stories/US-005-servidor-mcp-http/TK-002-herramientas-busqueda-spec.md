# TK-002: Herramientas search_openapi y get_endpoint_spec

**Estado:** Ready
**Historia:** [US-005](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Registrar en el servidor FastMCP las dos herramientas MCP del sistema:

- **`search_openapi(query: str, top_k: int = 5)`**: invoca el pipeline de búsqueda híbrida (US-004 / `domain.retrieval.search`), compone los `SearchResult` (MD-03) y los devuelve como markdown compacto más contenido estructurado. NO incluye el JSON OpenAPI completo en la respuesta. Un `top_k` fuera del rango `[1, 10]` se reporta como `tool_error`, no como excepción del servidor.
- **`get_endpoint_spec(spec_ref: str)`**: recupera el punto de Qdrant por `spec_ref` usando `domain.result.get_by_spec_ref`, extrae el fragmento `raw_spec` (MD-02), construye la `call_url` (`server_url + path`) y el `deeplink`, y los devuelve como markdown más contenido estructurado. Un `spec_ref` inválido (formato ≠ 3 segmentos no vacíos) o no encontrado se reporta como `tool_error` mediante `raise McpError` (o equivalente FastMCP); NUNCA se propaga como excepción del servidor (BR-02 / AC-005).

## Dependencias

- `smart_api_search.server` (TK-001) — instancia `mcp` en la que se registran las herramientas con `@mcp.tool`
- `smart_api_search.domain.retrieval.search` (US-004 / TK-002) — pipeline de búsqueda híbrida HyDE + RRF
- `smart_api_search.domain.result.compose_result`, `get_by_spec_ref` (US-004 / TK-003) — composición de `SearchResult` y recuperación por `spec_ref`
- `smart_api_search.config.Settings` (MD-05) — parámetros de Qdrant y proveedor de embeddings
- `fastmcp` ≥ 2.0 — decorador `@mcp.tool` y mecanismo `McpError` / `tool_error`

## Referencias

- **Arquitectura:** [ADR-007 — Consulta híbrida con ramas densa y BM25 fusionadas con RRF](../../adr/ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- **Arquitectura:** [ADR-008 — Expansión de consulta con HyDE, desactivable](../../adr/ADR-008-expansion-consulta-hyde.md)
- **Documentación técnica:** [API-01: search_openapi](../../specs/technical-docs/smart-api-search.md#api-01)
- **Documentación técnica:** [API-02: get_endpoint_spec](../../specs/technical-docs/smart-api-search.md#api-02)
- **Documentación técnica:** [MD-02: RawSpec](../../specs/technical-docs/smart-api-search.md#md-02)
- **Documentación técnica:** [MD-03: SearchResult](../../specs/technical-docs/smart-api-search.md#md-03)
- **Documentación técnica:** [FL-02: Retrieval híbrido — pasos 1–8 y manejo de errores](../../specs/technical-docs/smart-api-search.md#fl-02)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ server.py    # Registrar @mcp.tool search_openapi y @mcp.tool get_endpoint_spec
```

## Plan de implementación

- [x] **IT-01** — Implementar `search_openapi` como herramienta MCP en `server.py`
  Decorar con `@mcp.tool`. Firma: `async def search_openapi(query: str, top_k: int = 5) -> str`. Validar `1 ≤ top_k ≤ 10`; si falla, lanzar `McpError` con mensaje claro (no `ValueError` ni excepción de servidor). Llamar a `domain.retrieval.search(query, top_k)` para obtener la lista de `ScoredPoint`; por cada punto llamar a `domain.result.compose_result(point, ranking)` para componer un `SearchResult` (MD-03). Formatear la lista como markdown compacto (campos: ranking, method, path, summary, call_url, spec_ref) seguido del contenido estructurado. NO incluir el JSON completo del spec.
- [x] **IT-02** — Implementar `get_endpoint_spec` como herramienta MCP en `server.py`
  Decorar con `@mcp.tool`. Firma: `async def get_endpoint_spec(spec_ref: str) -> str`. Llamar a `domain.result.get_by_spec_ref(spec_ref, client, settings.QDRANT_COLLECTION)`; si devuelve lista vacía o `spec_ref` es inválido, lanzar `McpError` con mensaje de error de herramienta (no propagar excepción). Cuando se encuentre el punto: extraer el fragmento `raw_spec` (MD-02), construir `call_url = server_url + path` (nunca el `deeplink`), y devolver markdown más contenido estructurado con los tres elementos: fragmento OpenAPI, `call_url` y `deeplink`.
- [x] **IT-03** — Inicializar el cliente Qdrant de forma reutilizable en el módulo
  Crear un `AsyncQdrantClient` único a nivel de módulo (o con patrón de factory cargado una sola vez al arrancar el servidor) usando `Settings`. Las herramientas lo referencian sin crear una conexión nueva por llamada.
- [x] **IT-04** — Añadir tipos completos y anotaciones mypy
  Asegurar que las dos herramientas y el cliente Qdrant en `server.py` pasan `mypy --strict` sin errores nuevos.

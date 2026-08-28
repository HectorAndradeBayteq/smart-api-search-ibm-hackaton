# TK-003: Composición y normalización del resultado de búsqueda

**Estado:** Ready
**Historia:** [US-004](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la lógica de composición y normalización del resultado de búsqueda en `smart_api_search.domain`: transforma cada `ScoredPoint` devuelto por Qdrant en un objeto `SearchResult` (MD-03) con los campos `ranking`, `category`, `method`, `path`, `summary`, `description`, `consolidated_definition`, `call_url`, `deeplink`, `spec_ref`, `tags`, `source`, `params` y `body`. Incluye la construcción de `call_url` como `server_url + path` (nunca el deeplink ni la URL del portal), el parseo estricto de `spec_ref` (formato `source_file|METHOD|/path`, exactamente tres segmentos no vacíos), la normalización de `params` (parámetros declarados en la operación + inferidos del template del path, omitiendo los sin nombre) y la recuperación segura por `spec_ref` que devuelve lista vacía sin lanzar excepción si el punto no existe.

## Dependencias

- TK-001 (`smart_api_search.shared` + `Settings`) — la capa de composición lee `Settings` para construir el cliente Qdrant en la recuperación segura por referencia
- `qdrant-client` — `AsyncQdrantClient.retrieve()` para la recuperación por `spec_ref`
- `smart_api_search.domain.retrieval` (TK-002) — el pipeline llama a la composición sobre cada `ScoredPoint` devuelto

## Referencias

- **Arquitectura:** [ADR-011 — Campos payload indexados y ensure_collection](../../adr/ADR-011-campos-payload-indexados-ensure-collection.md)
- **Documentación técnica:** [MD-01: QdrantPoint](../../specs/technical-docs/smart-api-search.md#md-01)
- **Documentación técnica:** [MD-03: SearchResult](../../specs/technical-docs/smart-api-search.md#md-03)
- **Documentación técnica:** [FL-02: Retrieval híbrido — paso 7 (composición)](../../specs/technical-docs/smart-api-search.md#fl-02)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── domain/
        ├── + result.py        # Dataclass SearchResult y función compose_result(scored_point, ranking) -> SearchResult
        ├── + params.py        # Función normalize_params(operation, path_template) -> list[dict] con inferencia de path params
        └── ~ __init__.py      # Reexportar SearchResult, compose_result desde domain
```

## Plan de implementación

- [ ] **IT-01** — Definir la dataclass `SearchResult` en `domain/result.py`
  Campos obligatorios y opcionales según MD-03. Usar `@dataclass` con `field(default=None)` para los opcionales. El tipo de `params` es `list[dict[str, Any]]` y el de `body` es `dict[str, Any] | None`.
- [ ] **IT-02** — Implementar parseo estricto de `spec_ref` en `compose_result()`
  Dividir por `|`; verificar exactamente 3 segmentos no vacíos. Si el formato es inválido, omitir el resultado del ranking y emitir `logging.warning` (comportamiento especificado en FL-02 manejo de errores).
- [ ] **IT-03** — Implementar construcción de `call_url`
  `call_url = server_url + path` donde `server_url` es el valor del campo `server_url` del payload (MD-01). Si `server_url` está vacío o ausente, `call_url` queda como cadena vacía. Nunca usar `deeplink` ni ninguna otra URL del portal.
- [ ] **IT-04** — Implementar normalización de `params` en `domain/params.py`
  Extraer los parámetros declarados en el objeto `operation` del payload (`raw_spec`). Inferir además los parámetros de path a partir del template (`{param}` en el path). Omitir los parámetros sin nombre. Devolver `list[dict]` con al menos `name`, `in` y `required` por entrada.
- [ ] **IT-05** — Implementar `get_by_spec_ref(spec_ref: str, client: AsyncQdrantClient, collection: str) -> list[SearchResult]`
  Llamar a `client.retrieve()` filtrando por el campo indexado `spec_ref`. Si no existen puntos, devolver `[]` sin lanzar excepción. Si `spec_ref` tiene formato inválido, devolver `[]` tras emitir `logging.warning`.
- [ ] **IT-06** — Añadir tipos completos y anotaciones mypy
  Asegurar que `domain/result.py` y `domain/params.py` pasan `mypy --strict` sin errores nuevos.

---
id: ADR-011
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [qdrant, payload-index, keyword, ensure-collection, persistence]
supersedes: null
superseded_by: null
emits: [persistence/CR-003]
---

# ADR-011: Campos de payload indexados al asegurar la colección

## Contexto

Los campos `source_file` y `spec_ref` del payload Qdrant se usan como criterio de filtro en las consultas de recuperación y en la lógica de idempotencia de ingesta. Qdrant requiere que los campos usados en filtros tengan un índice previo; sin él, la operación devuelve `400 Bad Request: Index required but not found for "source_file"`. En la implementación anterior, la ingesta abortaba con ese error (Anexo A-3) porque los índices no se creaban al inicializar la colección.

## Decisión

Los campos de payload `source_file` y `spec_ref` forman parte del **contrato de la colección** y se indexan como **`keyword`** de forma **idempotente** al asegurar o crear la colección (`ensure_collection()`). Si los índices ya existen, la operación no falla ni los duplica.

## Alternativas consideradas

- **Crear índices bajo demanda (lazy)**: requiere manejo de errores en cada operación de filtro; complica la lógica de recuperación e ingesta.
- **Sin índices (scan completo)**: funciona para colecciones pequeñas pero no escala; además, Qdrant requiere índice explícito para ciertos tipos de filtro.

## Consecuencias

### Positivas

- Elimina el error `400 Bad Request: Index required but not found` verificado en producción.
- La colección siempre tiene el contrato correcto desde el primer uso; no hay estado intermedio sin índices.
- La idempotencia de `ensure_collection()` permite ejecutarla en cada arranque sin efecto secundario.

### Negativas / trade-offs

- `ensure_collection()` debe actualizarse si se añaden nuevos campos de filtro al contrato de la colección.
- Los índices de tipo `keyword` consumen algo más de memoria en el motor.

## Referencias

- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [ADR-012: Idempotencia de ingesta con granularidad de fuente](ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- [Estándar Persistencia](../standards/persistence.md)

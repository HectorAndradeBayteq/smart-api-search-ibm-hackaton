---
id: ADR-012
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [ingestion, idempotency, source-file, force-reindex, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-008]
---

# ADR-012: Idempotencia de ingesta con granularidad de fuente

## Contexto

La lógica de idempotencia de ingesta debe evitar reindexar fuentes ya presentes en la colección, salvo que el usuario lo solicite explícitamente con `--force`. En la implementación anterior (Anexo A-4), la comprobación de "¿ya está indexada esta operación?" se reevaluaba por cada operación individual; esto hacía que, tras indexar el primer punto de una fuente nueva, la fuente apareciera como "ya indexada" y el resto de sus operaciones se omitían. La colección quedó con 6 puntos en vez de los 272 esperados.

## Decisión

La **decisión de omitir o indexar una fuente** se toma **una sola vez por fuente**, antes de procesar su primera operación, consultando si ya existen puntos con ese `source_file` en la colección. Esta decisión se **cachea en memoria** durante toda la ejecución y **no se reevalúa** operación a operación. El flag `--force` borra los puntos previos de esa fuente antes de reindexarla.

## Alternativas consideradas

- **Comprobación por operación individual**: error verificado en producción; descartado.
- **Sin idempotencia (siempre reindexar)**: duplicaría puntos en la colección en cada ingesta; obliga a usar `--force` siempre.

## Consecuencias

### Positivas

- Elimina el error de colección con puntos insuficientes verificado en producción (6 puntos en vez de 272).
- La ingesta incremental funciona correctamente: fuentes nuevas se indexan, fuentes existentes se omiten.
- `--force` permite reindexar una fuente específica cuando su contenido cambió.

### Negativas / trade-offs

- La decisión cacheada asume que el estado de la colección no cambia durante la ejecución; en ejecuciones concurrentes podría haber inconsistencias (no aplica al diseño actual de una sola ejecución).
- Si la primera operación de una fuente falla, la fuente queda marcada como "indexada" con puntos parciales; se necesitaría `--force` para reindexarla correctamente.

## Referencias

- [ADR-005: Unidad de indexación es la operación OpenAPI](ADR-005-unidad-indexacion-operacion-openapi.md)
- [ADR-011: Campos de payload indexados al asegurar la colección](ADR-011-campos-payload-indexados-ensure-collection.md)
- [Estándar Retrieval](../standards/retrieval.md)

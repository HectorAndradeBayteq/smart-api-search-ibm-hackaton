---
id: ADR-005
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [openapi, indexing, retrieval, operation, spec-ref]
supersedes: null
superseded_by: null
emits: [retrieval/CR-001]
---

# ADR-005: Unidad de indexación es la operación OpenAPI

## Contexto

Un catálogo de APIs OpenAPI puede contener decenas o cientos de endpoints con propósitos muy distintos. Indexar el documento completo como unidad produciría documentos demasiado grandes y heterogéneos para la búsqueda semántica, dificultando la recuperación precisa del endpoint que el desarrollador necesita.

## Decisión

La **unidad de indexación es la operación OpenAPI**: el par `(método HTTP, path)`. Cada operación se indexa como un documento independiente con su propio embedding y payload de metadatos. El identificador único de cada punto indexado (`spec_ref`) sigue el formato `source_file|METHOD|/path`.

## Alternativas consideradas

- **Indexar el documento completo**: produce un único vector por API; la búsqueda no puede discriminar entre endpoints de la misma API con propósitos distintos.
- **Indexar por tag/grupo**: agrupa operaciones relacionadas, pero las descripciones grupales son genéricas y pierden precisión en la recuperación.

## Consecuencias

### Positivas

- La recuperación devuelve el endpoint exacto relevante para la consulta, no el documento completo.
- El payload de cada punto contiene todos los metadatos de la operación individual (parámetros, respuestas, descripción).
- El `spec_ref` permite identificar de forma única cada punto y gestionar la idempotencia de ingesta por operación.

### Negativas / trade-offs

- Una API con 100 operaciones genera 100 puntos en la colección; el volumen de ingesta es proporcional al número de operaciones.
- El `spec_ref` debe parsearse para recuperar el archivo fuente, el método y el path.

## Referencias

- [ADR-012: Idempotencia de ingesta con granularidad de fuente](ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- [Estándar Retrieval](../standards/retrieval.md)

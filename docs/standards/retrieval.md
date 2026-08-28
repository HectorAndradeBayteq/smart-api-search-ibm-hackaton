---
name: Estándares de Retrieval
domain: retrieval
status: Active
last_update: 2025-07-14
source_adrs: [ADR-005, ADR-006, ADR-007, ADR-008, ADR-009, ADR-010, ADR-012, ADR-014]
tags: [retrieval, openapi, indexing, hybrid-search, bm25, dense, rrf, hyde, embedding, idempotency]
---

# Estándares de Retrieval

Este estándar cubre las normas del dominio de recuperación y búsqueda semántica del proyecto `smart-api-search`. Aplica a la unidad de indexación de operaciones OpenAPI, el enriquecimiento LLM en ingesta, el flujo de consulta híbrida (densa + BM25 + RRF), la expansión de consulta con HyDE, el modelo de embedding, el manejo de vectores dispersos, la idempotencia de ingesta y la configuración del proveedor de embeddings.

## Unidad de indexación: operación OpenAPI

**ID:** unidad-indexacion
**Estado:** Active

La unidad de indexación **DEBE** ser la **operación OpenAPI**: el par `(método HTTP, path)`. **NO DEBE** indexarse el documento OpenAPI completo ni la API como unidad. El identificador único de cada punto indexado (`spec_ref`) **DEBE** seguir el formato `source_file|METHOD|/path` (ejemplo: `petstore.yaml|GET|/pets`).

### Excepciones

Ninguna.

## Enriquecimiento LLM en ingesta

**ID:** enriquecimiento-llm
**Estado:** Active

Cada operación OpenAPI **DEBE** enriquecerse con un LLM en tiempo de ingesta, generando un texto de **250–400 palabras** en inglés que incluya propósito, casos de uso, keywords y preguntas de ejemplo. El flag `--no-enrich` **DEBE** permitir omitir el enriquecimiento LLM e indexar directamente los metadatos del spec.

### Excepciones

El modo `--no-enrich` es válido para pruebas o cuando no se dispone de API key de LLM. La calidad de recuperación será inferior sin enriquecimiento.

## Consulta híbrida: prefetch densa + BM25 con RRF

**ID:** consulta-hibrida
**Estado:** Active

Toda consulta de recuperación **DEBE** ejecutar un `prefetch` denso y un `prefetch` BM25 en **paralelo**, fusionados con **RRF (Reciprocal Rank Fusion)** nativa de Qdrant. La **rama BM25 DEBE** recibir siempre el **texto original de la consulta** sin ninguna reescritura (ni HyDE ni ningún otro mecanismo de expansión).

### Excepciones

Ninguna. La rama BM25 no puede recibir la consulta reescrita por HyDE bajo ninguna circunstancia.

## Expansión de consulta con HyDE

**ID:** expansion-hyde
**Estado:** Active

Antes del embedding de la consulta densa, **DEBE** generarse una descripción hipotética de endpoint (HyDE) usando el LLM, salvo que `HYDE_ENABLED=false` esté configurado en el entorno. Con HyDE desactivado, el embedding **DEBE** calcularse sobre la consulta original directamente.

### Excepciones

`HYDE_ENABLED=false` desactiva HyDE para toda la ejecución. Es la configuración recomendada para debugging y pruebas de rendimiento.

## Modelo de embedding único y capa compartida

**ID:** embedding-shared-layer
**Estado:** Active

La dimensión del modelo de embedding (`EMBED_DIM`) **DEBE** declararse **una sola vez** en el archivo `.env`. La capa `smart_api_search.shared` es la **única** que **PUEDE** invocar la API de embeddings (OpenAI o Watsonx); ninguna otra capa del sistema **DEBE** importar directamente los clientes de embeddings. `EMBED_DIM` **DEBE** coincidir con el proveedor activo (`EMBED_PROVIDER`); una inconsistencia produce vectores de dimensión incorrecta.

### Excepciones

Ninguna. Las pruebas que necesiten embeddings deben hacerlo a través de `smart_api_search.shared` o usando mocks.

## Vectores dispersos: objeto de documento del motor

**ID:** vectores-dispersos-documento
**Estado:** Active

> ⚠ Lección aprendida de fallo en producción (Anexo A-2).

El texto para la rama BM25 **DEBE** enviarse envuelto en el objeto de documento del motor Qdrant (`models.Document(text=...)`), tanto al **indexar** como al **consultar**. **NO DEBE** enviarse texto plano a la rama BM25 bajo ninguna circunstancia. Enviar texto plano genera el error `400 Bad Request: Expected some form of vector`.

### Excepciones

Ninguna.

## Idempotencia de ingesta por fuente

**ID:** idempotencia-ingesta
**Estado:** Active

> ⚠ Lección aprendida de fallo en producción (Anexo A-4).

La decisión de omitir o indexar una fuente **DEBE** tomarse **una sola vez por fuente**, antes de procesar su primera operación, y **NO DEBE** reevaluarse durante la ejecución. La decisión se cachea en memoria para toda la ejecución. El flag `--force` **DEBE** borrar los puntos previos de esa fuente antes de reindexarla.

### Excepciones

Ninguna. Reevaluar la decisión por operación individual produce el error verificado en producción (colección con puntos insuficientes).

## Proveedor de embeddings configurable

**ID:** proveedor-embeddings
**Estado:** Active

El proveedor de embeddings **DEBE** configurarse mediante la variable de entorno `EMBED_PROVIDER`, con los valores aceptados `openai` y `watsonx`:

- `EMBED_PROVIDER=openai`: modelo `text-embedding-3-large`, `EMBED_DIM=1024`.
- `EMBED_PROVIDER=watsonx`: modelo `ibm/granite-embedding-278m-multilingual`, `EMBED_DIM=768`.

`EMBED_DIM` **DEBE** coincidir con el proveedor activo. Cambiar de proveedor invalida la colección Qdrant existente y **REQUIERE** reindexar todo el catálogo.

### Excepciones

Ninguna. No es posible mezclar embeddings de proveedores distintos en la misma colección.

## Criterios de cumplimiento

| ID | Requisito | Descripción | Origen | Automatizable | Enfoque | Verificación |
|----|-----------|-------------|--------|---------------|---------|--------------|
| CR-001 | unidad-indexacion | La unidad de indexación **DEBE** ser la operación OpenAPI; `spec_ref` **DEBE** tener formato `source_file\|METHOD\|/path` | [ADR-005](../adr/ADR-005-unidad-indexacion-operacion-openapi.md) | yes | bloqueante | no |
| CR-002 | enriquecimiento-llm | Cada operación **DEBE** enriquecerse con LLM (250–400 palabras); `--no-enrich` **DEBE** estar disponible | [ADR-006](../adr/ADR-006-enriquecimiento-llm-ingesta.md) | yes | bloqueante | no |
| CR-003 | consulta-hibrida | La consulta **DEBE** ejecutar prefetch denso y BM25 en paralelo fusionados con RRF; la rama BM25 **DEBE** recibir la consulta original | [ADR-007](../adr/ADR-007-consulta-hibrida-densa-bm25-rrf.md) | yes | bloqueante | no |
| CR-004 | expansion-hyde | HyDE **DEBE** expandir la consulta antes del embedding denso; **DEBE** desactivarse con `HYDE_ENABLED=false` | [ADR-008](../adr/ADR-008-expansion-consulta-hyde.md) | yes | bloqueante | no |
| CR-005 | embedding-shared-layer | `EMBED_DIM` **DEBE** declararse una sola vez en `.env` | [ADR-009](../adr/ADR-009-modelo-embedding-unico-embed-dim.md) | yes | bloqueante | no |
| CR-006 | embedding-shared-layer | Solo `smart_api_search.shared` **PUEDE** invocar la API de embeddings | [ADR-009](../adr/ADR-009-modelo-embedding-unico-embed-dim.md) | yes | bloqueante | no |
| CR-007 | vectores-dispersos-documento | El texto para BM25 **DEBE** enviarse como `models.Document(text=...)`; nunca texto plano | [ADR-010](../adr/ADR-010-inferencia-vectores-dispersos-motor.md) | yes | bloqueante | no |
| CR-008 | idempotencia-ingesta | La decisión de omitir/indexar una fuente **DEBE** tomarse una vez y no reevaluarse | [ADR-012](../adr/ADR-012-idempotencia-ingesta-granularidad-fuente.md) | yes | bloqueante | no |
| CR-009 | proveedor-embeddings | `EMBED_PROVIDER` **DEBE** ser `openai` o `watsonx`; `EMBED_DIM` **DEBE** coincidir con el proveedor | [ADR-014](../adr/ADR-014-proveedor-embeddings-openai-watsonx.md) | yes | bloqueante | no |
| CR-010 | proveedor-embeddings | Cambiar de proveedor **REQUIERE** reindexar la colección | [ADR-014](../adr/ADR-014-proveedor-embeddings-openai-watsonx.md) | no | warning | no |

## Referencias

- [ADR-005: Unidad de indexación es la operación OpenAPI](../adr/ADR-005-unidad-indexacion-operacion-openapi.md)
- [ADR-006: Enriquecimiento LLM en tiempo de ingesta](../adr/ADR-006-enriquecimiento-llm-ingesta.md)
- [ADR-007: Consulta híbrida con ramas densa y BM25 fusionadas con RRF](../adr/ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- [ADR-008: Expansión de consulta con HyDE, desactivable](../adr/ADR-008-expansion-consulta-hyde.md)
- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](../adr/ADR-009-modelo-embedding-unico-embed-dim.md)
- [ADR-010: Inferencia de vectores dispersos delegada al motor](../adr/ADR-010-inferencia-vectores-dispersos-motor.md)
- [ADR-012: Idempotencia de ingesta con granularidad de fuente](../adr/ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- [ADR-014: Proveedor de embeddings configurable — OpenAI y Watsonx](../adr/ADR-014-proveedor-embeddings-openai-watsonx.md)

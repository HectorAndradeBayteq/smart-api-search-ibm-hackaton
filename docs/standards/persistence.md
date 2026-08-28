---
name: Estándares de Persistencia
domain: persistence
status: Active
last_update: 2025-07-14
source_adrs: [ADR-002, ADR-011]
tags: [qdrant, vector-db, hybrid, bm25, dense, payload-index]
---

# Estándares de Persistencia

Este estándar cubre las normas del dominio de persistencia y datos del proyecto `smart-api-search`. Aplica al acceso y configuración de la base vectorial Qdrant Cloud: estructura de la colección, tipos de vectores, contrato de payload e índices requeridos. Define las reglas que toda escritura, lectura e inicialización de la colección deben cumplir.

## Colección Qdrant híbrida

**ID:** coleccion-qdrant-hibrida
**Estado:** Active

La colección Qdrant **DEBE** estar configurada como colección híbrida con dos vectores nombrados:

- **Vector denso**: similitud coseno, dimensión `EMBED_DIM` (configurable en `.env`, coherente con el proveedor activo).
- **Vector disperso BM25**: con modificador IDF, gestionado por el motor Qdrant.

Toda operación de escritura **DEBE** incluir ambos vectores simultáneamente. Una escritura parcial (solo vector denso o solo vector disperso) **NO DEBE** realizarse, ya que generará errores del motor y dejará puntos incompletos en la colección.

### Excepciones

Ninguna. Si el proveedor de embeddings cambia (y con él `EMBED_DIM`), la colección debe ser recreada y reindexada completamente.

## Índices de payload de la colección

**ID:** indices-payload-coleccion
**Estado:** Active

Los campos de payload `source_file` y `spec_ref` forman parte del **contrato de la colección** y **DEBEN** indexarse como tipo `keyword` de forma **idempotente** al crear o asegurar la colección (`ensure_collection()`). La función `ensure_collection()` **DEBE** crear estos índices si no existen y **NO DEBE** fallar si ya existen.

Este requisito previene el error `400 Bad Request: Index required but not found for "source_file"` verificado en producción (Anexo A-3), que abortaba la ingesta al intentar filtrar por un campo sin índice previo.

### Excepciones

Ninguna. Si se añaden nuevos campos de filtro al contrato de la colección, deben incluirse en `ensure_collection()`.

## Criterios de cumplimiento

| ID | Requisito | Descripción | Origen | Automatizable | Enfoque | Verificación |
|----|-----------|-------------|--------|---------------|---------|--------------|
| CR-001 | coleccion-qdrant-hibrida | La colección **DEBE** tener vector denso (coseno, dimensión `EMBED_DIM`) y vector disperso BM25 | [ADR-002](../adr/ADR-002-qdrant-cloud-base-vectorial.md) | yes | bloqueante | no |
| CR-002 | coleccion-qdrant-hibrida | Toda escritura **DEBE** incluir ambos vectores simultáneamente | [ADR-002](../adr/ADR-002-qdrant-cloud-base-vectorial.md) | yes | bloqueante | no |
| CR-003 | indices-payload-coleccion | Los campos `source_file` y `spec_ref` **DEBEN** tener índice keyword creado de forma idempotente en `ensure_collection()` | [ADR-011](../adr/ADR-011-campos-payload-indexados-ensure-collection.md) | yes | bloqueante | no |

## Referencias

- [ADR-002: Qdrant Cloud como base vectorial](../adr/ADR-002-qdrant-cloud-base-vectorial.md)
- [ADR-011: Campos de payload indexados al asegurar la colección](../adr/ADR-011-campos-payload-indexados-ensure-collection.md)
- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](../adr/ADR-009-modelo-embedding-unico-embed-dim.md)

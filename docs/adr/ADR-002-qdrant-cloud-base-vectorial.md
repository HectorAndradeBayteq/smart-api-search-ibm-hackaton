---
id: ADR-002
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [qdrant, vector-db, hybrid-search, bm25, rrf, persistence]
supersedes: null
superseded_by: null
emits: [persistence/CR-001, persistence/CR-002]
---

# ADR-002: Qdrant Cloud como base vectorial

## Contexto

El sistema requiere búsqueda semántica híbrida sobre catálogos OpenAPI. La base vectorial debe soportar colecciones con múltiples tipos de vectores (denso y disperso), fusión de rankings de múltiples fuentes (Reciprocal Rank Fusion) y filtrado por campos de payload, todo sin postprocesado externo costoso.

## Decisión

Usar **Qdrant Cloud** como base vectorial con colección híbrida: **vector denso** (similitud coseno, dimensión configurable `EMBED_DIM`) y **vector disperso BM25** (con modificador IDF). La fusión de resultados usa **RRF (Reciprocal Rank Fusion)** nativa del motor. Toda escritura incluye ambos vectores simultáneamente.

## Alternativas consideradas

- **Pinecone**: sin soporte nativo para búsqueda híbrida BM25 + densa en el momento de la decisión; requeriría postprocesado externo.
- **Weaviate**: mayor complejidad operacional para este alcance; el módulo BM25 tiene configuración más compleja.
- **pgvector**: no soporta BM25 nativo; requeriría integración con un motor de búsqueda de texto completo externo (p. ej. tsvector de PostgreSQL), duplicando la infraestructura.

## Consecuencias

### Positivas

- Soporte nativo de colecciones con múltiples vectores nombrados.
- RRF integrada en el motor: no requiere postprocesado en la capa de aplicación.
- Qdrant Cloud elimina la operación de infraestructura propia.

### Negativas / trade-offs

- Dependencia de un servicio cloud externo (Qdrant Cloud); requiere credenciales (`QDRANT_URL`, `QDRANT_API_KEY`).
- Cambiar `EMBED_DIM` (o el proveedor de embeddings) invalida la colección existente y obliga a reindexar.
- Toda escritura debe incluir ambos vectores; una escritura parcial (solo denso o solo BM25) generará errores del motor.

## Referencias

- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](ADR-009-modelo-embedding-unico-embed-dim.md)
- [ADR-011: Campos de payload indexados al asegurar la colección](ADR-011-campos-payload-indexados-ensure-collection.md)
- [Estándar Persistencia](../standards/persistence.md)

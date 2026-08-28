---
id: ADR-007
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [hybrid-search, bm25, dense, rrf, retrieval, qdrant]
supersedes: null
superseded_by: null
emits: [retrieval/CR-003]
---

# ADR-007: Consulta híbrida con ramas densa y BM25 fusionadas con RRF

## Contexto

La búsqueda solo densa (embeddings) pierde términos técnicos exactos como nombres de endpoints, parámetros específicos o códigos de respuesta. La búsqueda solo BM25 no captura sinónimos semánticos ni consultas en lenguaje natural. La fusión de ambas ramas requiere un mecanismo que no dependa de calibrar pesos entre las dos distribuciones de puntuación.

## Decisión

La recuperación usa un **flujo híbrido**: `prefetch` denso + `prefetch` BM25 en **paralelo**, fusionados con **RRF (Reciprocal Rank Fusion)** nativa de Qdrant. La **rama BM25 recibe siempre el texto original de la consulta** (sin reescritura por HyDE ni por ningún otro mecanismo de expansión).

## Alternativas consideradas

- **Solo búsqueda densa**: falla en términos técnicos exactos; menor precisión para nombres de endpoints.
- **Solo BM25**: no captura semántica; falla en consultas coloquiales o en idiomas distintos al del spec.
- **Fusión con pesos ponderados manuales**: requiere calibración y es sensible al dominio; RRF es más robusta sin configuración.

## Consecuencias

### Positivas

- Mejor calidad de recuperación que cualquiera de las dos ramas por separado.
- RRF no requiere calibración de pesos: es una fórmula determinista basada en rangos.
- Los prefetch paralelos no añaden latencia en serie.

### Negativas / trade-offs

- La rama BM25 debe recibir la consulta original (no la reescrita por HyDE); la capa de recuperación debe mantener esa distinción explícitamente.
- Toda escritura debe incluir el vector BM25 (ver ADR-002); una colección sin vectores dispersos no soporta este flujo.

## Referencias

- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [ADR-008: Expansión de consulta con HyDE, desactivable](ADR-008-expansion-consulta-hyde.md)
- [ADR-010: Inferencia de vectores dispersos delegada al motor](ADR-010-inferencia-vectores-dispersos-motor.md)
- [Estándar Retrieval](../standards/retrieval.md)

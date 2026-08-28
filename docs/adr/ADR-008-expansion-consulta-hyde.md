---
id: ADR-008
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [hyde, query-expansion, llm, embedding, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-004]
---

# ADR-008: Expansión de consulta con HyDE, desactivable

## Contexto

Las consultas de usuario son cortas y coloquiales ("¿cómo creo un usuario?", "endpoint de autenticación"), mientras que los documentos indexados son enriquecimientos largos y técnicos de 250–400 palabras. Esta asimetría en la distribución hace que el embedding de la consulta corta caiga lejos del espacio de los documentos, reduciendo la calidad de la recuperación densa.

## Decisión

Antes de embeber la consulta, se genera una **descripción hipotética de endpoint (HyDE)** usando el LLM: el modelo produce un fragmento de descripción técnica que podría corresponder al endpoint buscado. Este texto expandido se usa como entrada del modelo de embedding en lugar de la consulta original. HyDE puede **desactivarse** con la variable de entorno `HYDE_ENABLED=false`; en ese caso se embebe la consulta original directamente.

## Alternativas consideradas

- **Sin expansión de consulta**: calidad de recuperación densa inferior para consultas cortas/coloquiales.
- **Expansión con múltiples consultas (Multi-Query)**: mayor coste en tokens y latencia; HyDE produce resultados similares con una sola llamada LLM.

## Consecuencias

### Positivas

- Acerca la distribución del embedding de la consulta a la de los documentos indexados (enriquecidos).
- Desactivable sin cambios de código: útil para debugging, pruebas de rendimiento o entornos sin API LLM.

### Negativas / trade-offs

- Con HyDE activo, cada consulta hace una llamada al LLM antes del embedding: añade latencia y coste.
- HyDE no aplica a la rama BM25 (ver ADR-007): la rama dispersa sigue usando la consulta original.

## Referencias

- [ADR-007: Consulta híbrida con ramas densa y BM25 fusionadas con RRF](ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](ADR-009-modelo-embedding-unico-embed-dim.md)
- [Estándar Retrieval](../standards/retrieval.md)

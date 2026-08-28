---
id: ADR-006
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [llm, openai, enrichment, ingestion, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-002]
---

# ADR-006: Enriquecimiento LLM en tiempo de ingesta

## Contexto

Los specs OpenAPI reales suelen tener descripciones pobres, ausentes o demasiado técnicas para la búsqueda semántica en lenguaje natural. Sin enriquecimiento, el embedding de una operación captura poco semántico útil para consultas coloquiales. El enriquecimiento en tiempo de búsqueda aumentaría la latencia de cada consulta.

## Decisión

Cada operación OpenAPI se enriquece con un **LLM (OpenAI Responses API)** en **tiempo de ingesta**, generando un texto de 250–400 palabras en inglés que incluye: propósito de la operación, casos de uso típicos, keywords técnicas y preguntas de ejemplo que un desarrollador podría hacer. Se provee un modo de ingesta rápida (`--no-enrich`) que omite la llamada al LLM e indexa los metadatos del spec directamente.

## Alternativas consideradas

- **Enriquecimiento en tiempo de consulta**: aumenta la latencia de búsqueda; inviable para un servidor de uso interactivo.
- **Sin enriquecimiento**: la calidad de recuperación semántica es significativamente inferior para consultas coloquiales.

## Consecuencias

### Positivas

- Mejora la calidad de recuperación semántica sin aumentar la latencia de búsqueda.
- Las consultas en lenguaje natural se alinean mejor con el texto enriquecido que con la descripción técnica del spec.
- `--no-enrich` permite indexar rápidamente para pruebas o cuando no se dispone de API key de LLM.

### Negativas / trade-offs

- La ingesta es más lenta: una llamada LLM por operación.
- Añade coste operacional (tokens LLM) proporcional al número de operaciones indexadas.
- El texto enriquecido depende del modelo LLM activo; cambiar el modelo puede producir distribuciones de embedding distintas.

## Referencias

- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](ADR-009-modelo-embedding-unico-embed-dim.md)
- [Estándar Retrieval](../standards/retrieval.md)

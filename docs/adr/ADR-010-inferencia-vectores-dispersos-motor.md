---
id: ADR-010
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [qdrant, bm25, sparse-vector, document-object, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-007]
---

# ADR-010: Inferencia de vectores dispersos delegada al motor

> ⚠ **Lección aprendida de fallo en producción (Anexo A-2):** enviar texto plano a la rama dispersa de Qdrant generó `400 Bad Request: Expected some form of vector`. El requisito anterior de "sin transformación" en la rama BM25 indujo este error. Esta decisión lo corrige explícitamente.

## Contexto

El motor Qdrant infiere el vector disperso BM25 en el servidor a partir de un objeto de documento con estructura específica (`models.Document(text=...)`). Cuando se envía texto plano directamente a la rama BM25, el motor devuelve un error `400 Bad Request: Expected some form of vector`, porque no puede inferir el vector sin el objeto de documento correcto.

## Decisión

El cliente **envuelve el texto en el objeto de documento que el motor Qdrant exige** para la inferencia del vector disperso en el servidor, tanto al **indexar** como al **consultar**:

- Al **indexar**: el texto de la operación se envuelve en `models.Document(text=texto_operacion)`.
- Al **consultar**: la consulta original (sin reescritura por HyDE) se envuelve en `models.Document(text=consulta_original)`.

No se envía texto plano a la rama BM25 en ningún caso.

## Alternativas consideradas

- **Texto plano a la rama BM25**: causa error `400 Bad Request` verificado en producción; descartado.
- **Calcular el vector disperso en el cliente**: requiere reimplementar BM25 en Python; añade complejidad y diverge del modelo IDF del servidor.

## Consecuencias

### Positivas

- Elimina el error `400 Bad Request: Expected some form of vector` verificado en producción.
- El servidor aplica el mismo modelo BM25 (con sus parámetros IDF) tanto al indexar como al consultar, garantizando consistencia.

### Negativas / trade-offs

- El cliente debe conocer el tipo `models.Document` de la librería cliente de Qdrant; no puede usar texto plano.
- Esta convención debe mantenerse en cualquier refactor que toque la capa de acceso a Qdrant.

## Referencias

- [ADR-007: Consulta híbrida con ramas densa y BM25 fusionadas con RRF](ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [Estándar Retrieval](../standards/retrieval.md)

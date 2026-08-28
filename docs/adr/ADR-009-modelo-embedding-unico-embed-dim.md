---
id: ADR-009
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [embedding, embed-dim, shared-layer, architecture, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-005, retrieval/CR-006]
---

# ADR-009: Modelo de embedding único truncado a EMBED_DIM, fuente única en capa compartida

## Contexto

En implementaciones anteriores coexistieron dos valores contradictorios de dimensión de embedding (3072 y 1024) en distintos módulos del proyecto. Cambiar la dimensión del modelo o del valor configurado invalida la colección Qdrant existente y obliga a reindexar todo el catálogo. Además, acceder directamente a la API de embeddings desde múltiples capas hace que cualquier cambio de proveedor o dimensión requiera modificaciones en varios lugares.

## Decisión

Se usa **un único modelo de embedding** (configurable vía `EMBED_PROVIDER`), con **dimensión configurable `EMBED_DIM`** declarada en un único lugar (`.env`). La **capa `smart_api_search.shared`** es la única que puede invocar la API de embeddings (OpenAI o Watsonx); ninguna otra capa puede importar directamente los clientes de embeddings.

## Alternativas consideradas

- **Múltiples capas accediendo a la API de embeddings**: mayor acoplamiento; un cambio de modelo o proveedor requiere modificar varios módulos.
- **EMBED_DIM hardcodeado**: error verificado en producción; cualquier inconsistencia entre el valor hardcodeado y el modelo activo corrompe los resultados de búsqueda.

## Consecuencias

### Positivas

- `EMBED_DIM` aparece **una sola vez** en la documentación y configuración, eliminando la posibilidad de inconsistencias.
- Cambiar de proveedor de embeddings solo requiere modificar `shared/`; el resto de las capas no se ven afectadas.
- La capa `shared` puede aplicar truncado, normalización y caché de embeddings de forma centralizada.

### Negativas / trade-offs

- Todas las capas que necesiten embeddings deben pasar por `shared/`; no pueden llamar directamente a la API.
- Si `EMBED_DIM` no coincide con el modelo activo, los vectores generados tendrán dimensión incorrecta y la escritura en Qdrant fallará.

## Referencias

- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [ADR-014: Proveedor de embeddings configurable — OpenAI y Watsonx](ADR-014-proveedor-embeddings-openai-watsonx.md)
- [Estándar Retrieval](../standards/retrieval.md)

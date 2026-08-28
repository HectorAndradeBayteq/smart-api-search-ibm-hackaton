---
id: ADR-014
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [embedding, openai, watsonx, ibm, granite, embed-provider, retrieval]
supersedes: null
superseded_by: null
emits: [retrieval/CR-009, retrieval/CR-010]
---

# ADR-014: Proveedor de embeddings configurable — OpenAI y Watsonx

## Contexto

El hackathon IBM requiere integración con IBM Watsonx como proveedor de embeddings. Al mismo tiempo, OpenAI sigue siendo la opción principal durante el desarrollo del equipo. Ambos proveedores tienen APIs distintas, modelos distintos y dimensiones de embedding distintas (1024 para OpenAI `text-embedding-3-large` truncado, 768 para IBM `granite-embedding-278m-multilingual`). Un cambio de proveedor invalida la colección Qdrant existente (distinto `EMBED_DIM`) y requiere reindexar.

## Decisión

El sistema soporta **dos proveedores de embeddings intercambiables**, seleccionados por la variable de entorno `EMBED_PROVIDER`:

- **OpenAI** (`EMBED_PROVIDER=openai`): modelo `text-embedding-3-large`, truncado a `EMBED_DIM=1024` dimensiones.
- **Watsonx IBM** (`EMBED_PROVIDER=watsonx`): modelo `ibm/granite-embedding-278m-multilingual`, 768 dimensiones, ventana de 512 tokens (`EMBED_DIM=768`).

Ambos proveedores son accesibles a través de la **capa compartida `smart_api_search.shared`**, que abstrae las diferencias de API. `EMBED_DIM` debe configurarse en `.env` de forma coherente con el proveedor activo.

## Alternativas consideradas

- **Solo OpenAI**: no cumple el requisito de integración con IBM Watsonx del hackathon.
- **Solo Watsonx**: limita las opciones del equipo durante desarrollo; la ventana de 512 tokens es más restrictiva.
- **Autodetección de EMBED_DIM**: podría silenciar errores de configuración; se prefiere la declaración explícita para que el operador sea consciente del valor.

## Consecuencias

### Positivas

- Cumple el requisito de integración IBM Watsonx del hackathon sin eliminar OpenAI como opción de desarrollo.
- La capa `shared` abstrae la diferencia de API; el resto del sistema es agnóstico al proveedor.
- Cambiar de proveedor es una operación de configuración (`.env`) sin cambios de código.

### Negativas / trade-offs

- `EMBED_DIM` debe coincidir con el proveedor activo; una inconsistencia produce vectores de dimensión incorrecta y falla en escritura de Qdrant.
- Cambiar de proveedor invalida la colección existente (distintas dimensiones); obliga a reindexar todo el catálogo.
- Watsonx tiene ventana de 512 tokens; textos enriquecidos más largos se truncarán.

## Referencias

- [ADR-009: Modelo de embedding único truncado a EMBED_DIM](ADR-009-modelo-embedding-unico-embed-dim.md)
- [ADR-002: Qdrant Cloud como base vectorial](ADR-002-qdrant-cloud-base-vectorial.md)
- [Estándar Retrieval](../standards/retrieval.md)
- [IBM Watsonx — granite-embedding-278m-multilingual](https://www.ibm.com/products/watsonx-ai)

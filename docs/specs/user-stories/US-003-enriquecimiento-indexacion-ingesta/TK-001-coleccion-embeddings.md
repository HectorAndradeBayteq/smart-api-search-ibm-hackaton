# TK-001: Colección Qdrant híbrida y cliente de embeddings configurable

**Estado:** Ready
**Historia:** [US-003](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la función `ensure_collection()` que crea o verifica de forma idempotente la colección Qdrant con configuración híbrida: vector denso con métrica coseno y dimensión `EMBED_DIM` leído desde configuración, y vector disperso BM25 con modificador IDF. Al asegurar la colección crear también de forma idempotente los índices `keyword` para `source_file` y `spec_ref`. Implementar además el cliente de embeddings configurable en `smart_api_search.shared` que selecciona el proveedor según `EMBED_PROVIDER` y usa `EMBED_DIM` exclusivamente desde `.env`; ninguna otra capa puede invocar las APIs de embeddings directamente.

## Dependencias

- `qdrant-client` — creación de colección, configuración de vectores nombrados e índices de payload
- `python-dotenv` — lectura de `QDRANT_URL`, `QDRANT_API_KEY`, `EMBED_PROVIDER` y `EMBED_DIM` desde `.env`
- `openai` SDK — embeddings `text-embedding-3-large` cuando `EMBED_PROVIDER=openai`
- `ibm-watsonx-ai` SDK — embeddings `ibm/granite-embedding-278m-multilingual` cuando `EMBED_PROVIDER=watsonx`
- `smart_api_search.config.EmbedProvider` — enumeración de proveedores ya disponible

## Referencias

- **Arquitectura:** [ADR-002: Qdrant Cloud como base vectorial](../../../adr/ADR-002-qdrant-cloud-base-vectorial.md)
- **Arquitectura:** [ADR-009: Modelo de embedding único truncado a EMBED_DIM](../../../adr/ADR-009-modelo-embedding-unico-embed-dim.md)
- **Arquitectura:** [ADR-011: Campos de payload indexados al asegurar la colección](../../../adr/ADR-011-campos-payload-indexados-ensure-collection.md)
- **Arquitectura:** [ADR-014: Proveedor de embeddings configurable — OpenAI y Watsonx](../../../adr/ADR-014-proveedor-embeddings-openai-watsonx.md)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
├── src/smart_api_search/
│   ├── ~ config.py                                    # añadir lectura de QDRANT_URL, QDRANT_API_KEY, EMBED_DIM, EMBED_PROVIDER y COLLECTION_NAME
│   ├── shared/
│   │   ├── ~ __init__.py                              # exportar get_embedding()
│   │   └── + embeddings.py                            # cliente de embeddings configurable (openai / watsonx)
│   └── domain/
│       └── + collection.py                            # ensure_collection(): crea colección híbrida + índices keyword idempotentes
└── tests/
    └── + test_collection_and_embeddings.py            # pruebas unitarias de ensure_collection y del cliente de embeddings con mock
```

## Plan de implementación

- [ ] **IT-01** — Ampliar `config.py` con las variables de entorno de Qdrant y embeddings
  Añadir `QDRANT_URL: str`, `QDRANT_API_KEY: str`, `COLLECTION_NAME: str` (por defecto `"api-operations"`), `EMBED_DIM: int` y `EMBED_PROVIDER: EmbedProvider` como constantes cargadas desde `.env`; `EMBED_DIM` nunca como literal en código.
- [ ] **IT-02** — Implementar `shared/embeddings.py` con `get_embedding(text: str) -> list[float]`
  Seleccionar proveedor según `config.EMBED_PROVIDER`: si `openai`, llamar a `openai.embeddings.create(model="text-embedding-3-large", input=text, dimensions=config.EMBED_DIM)`; si `watsonx`, usar `ibm-watsonx-ai` con `ibm/granite-embedding-278m-multilingual` y `EMBED_DIM=768`. Ninguna otra capa importa los SDKs de embeddings directamente.
- [ ] **IT-03** — Exportar `get_embedding` desde `shared/__init__.py`
  Mantener `shared` como único punto de acceso a embeddings en todo el paquete.
- [ ] **IT-04** — Implementar `domain/collection.py` con `ensure_collection(client: QdrantClient) -> None`
  Comprobar si la colección existe; si no, crearla con `VectorsConfig` usando `NamedVector` denso (coseno, `EMBED_DIM`) y `SparseVectorConfig` BM25 (modificador IDF). Crear después los índices keyword para `source_file` y `spec_ref` usando `create_payload_index` con `PayloadSchemaType.KEYWORD`; si ya existen, ignorar la excepción (idempotencia).
- [ ] **IT-05** — Escribir pruebas unitarias en `tests/test_collection_and_embeddings.py`
  Verificar con mock de `QdrantClient` que `ensure_collection` llama a `create_collection` solo cuando la colección no existe, y que llama a `create_payload_index` para `source_file` y `spec_ref`. Verificar que `get_embedding` delega al SDK correcto según `EMBED_PROVIDER` (mock de ambos SDKs) y que nunca usa `EMBED_DIM` como literal.

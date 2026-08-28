# TK-002: Pipeline de enriquecimiento LLM e indexación híbrida

**Estado:** Ready
**Historia:** [US-003](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el pipeline central que toma una operación OpenAPI extraída y realiza dos fases en secuencia: (1) **enriquecimiento LLM** — llamar a la OpenAI Responses API para generar un texto en inglés de 250–400 palabras con la estructura requerida (propósito, capacidades, casos de uso, línea `Keywords:` y sección `Example questions users might ask:`); (2) **indexación híbrida** — componer el texto indexable como `[categoría | API | formato | método path | tags | base]` + texto enriquecido (el deeplink no forma parte del texto embebido), generar el vector denso via `shared.get_embedding()`, construir el objeto `Document(text=texto, model="Qdrant/bm25")` para el vector disperso, y escribir el punto en Qdrant con el payload completo requerido. El flag `--no-enrich` omite la llamada al LLM e indexa los metadatos del spec directamente.

## Dependencias

- TK-001 — `ensure_collection()`, `shared.get_embedding()` y variables de configuración disponibles
- `openai` SDK — OpenAI Responses API para generación del texto enriquecido
- `qdrant-client` — escritura de puntos con vectores nombrados denso y disperso
- Operación extraída (US-002 / TK-001 de US-002) — estructura de `OperationRecord` con los campos de payload

## Referencias

- **Arquitectura:** [ADR-005: Unidad de indexación es la operación OpenAPI](../../../adr/ADR-005-unidad-indexacion-operacion-openapi.md)
- **Arquitectura:** [ADR-006: Enriquecimiento LLM en tiempo de ingesta](../../../adr/ADR-006-enriquecimiento-llm-ingesta.md)
- **Arquitectura:** [ADR-009: Modelo de embedding único truncado a EMBED_DIM](../../../adr/ADR-009-modelo-embedding-unico-embed-dim.md)
- **Arquitectura:** [ADR-010: Inferencia de vectores dispersos delegada al motor](../../../adr/ADR-010-inferencia-vectores-dispersos-motor.md)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
├── src/smart_api_search/
│   └── domain/
│       ├── + enricher.py       # enrich_operation(op, no_enrich=False) -> str: llama al LLM o devuelve texto plano
│       └── + indexer.py        # index_operation(client, op, enriched_text): compone texto, genera vectores y escribe punto
└── tests/
    └── + test_pipeline.py      # pruebas unitarias con mock del LLM y del cliente Qdrant
```

## Plan de implementación

- [x] **IT-01** — Implementar `domain/enricher.py` con `enrich_operation(op: OperationRecord, no_enrich: bool = False) -> str`
  Si `no_enrich=True`, devolver el texto compuesto de los metadatos disponibles sin llamar al LLM. Si `no_enrich=False`, construir el prompt con los metadatos de la operación y llamar a la OpenAI Responses API; el texto devuelto debe tener 250–400 palabras, estar en inglés y contener propósito, capacidades, casos de uso, línea `Keywords:` y sección `Example questions users might ask:`.
- [x] **IT-02** — Implementar `domain/indexer.py` con `index_operation(client: QdrantClient, op: OperationRecord, enriched_text: str) -> None`
  Componer el texto indexable: `[{categoría} | {api_title} | {spec_format} | {method} {path} | {tags} | {base}]` + `"\n\n"` + `enriched_text`; el `deeplink` no forma parte del texto embebido. Generar el vector denso con `shared.get_embedding(texto_indexable)`. Construir el objeto disperso como `models.Document(text=texto_indexable, model="Qdrant/bm25")`. Construir el payload con todos los campos requeridos: `api_title`, `api_version`, `api_description`, `category`, `method`, `path`, `summary`, `description`, `tags`, `operationId`, `environment`, `server_url`, `spec_format`, `source_file`, `enriched_text`, `raw_spec` y `deeplink`. Escribir el punto en Qdrant con los dos vectores nombrados de forma simultánea; nunca escribir un punto con un solo vector.
- [x] **IT-03** — Derivar `spec_ref` como `{source_file}|{METHOD}|{/path}` y añadirlo al payload
  Seguir el formato definido en ADR-005: `source_file|METHOD|/path`. Incluirlo en el payload para que el índice keyword de `spec_ref` (creado en TK-001) sea utilizable en filtros.
- [x] **IT-04** — Escribir pruebas unitarias en `tests/test_pipeline.py`
  Prueba de `enrich_operation` con LLM mockeado: verificar que con `no_enrich=False` se llama a la API y que con `no_enrich=True` no se llama. Prueba de `index_operation` con cliente Qdrant mockeado: capturar el argumento del punto escrito y verificar (a) que el objeto en la rama dispersa es instancia de `models.Document`, (b) que los dos vectores están presentes simultáneamente en el punto, (c) que el payload contiene todos los campos obligatorios.

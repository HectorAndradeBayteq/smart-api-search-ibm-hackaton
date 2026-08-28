# TK-004: Pruebas y verificabilidad del flujo de búsqueda híbrida

**Estado:** Ready
**Historia:** [US-004](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Escribir la suite de pruebas unitarias e integración ligera que verifica el flujo completo de búsqueda híbrida. Los tests usan mocks de LLM (para HyDE) y un cliente Qdrant simulado o fixture in-memory para evitar dependencias externas. La suite debe cubrir: flujo nominal con HyDE activo e inactivo, separación estricta de ramas densa y BM25 (la rama BM25 siempre recibe la consulta original), correcta composición del objeto `SearchResult` con todos sus campos, construcción de `call_url` como `server_url+path`, parseo estricto y rechazo de `spec_ref` inválidos, omisión de params sin nombre, recuperación segura ante punto inexistente (devuelve vacío sin excepción) y coherencia de `Settings`: mismo proveedor y dimensión en toda la cadena.

## Dependencias

- TK-001 (`smart_api_search.shared.embed`, `warn_if_mismatch`) — los tests verifican el contrato de la capa compartida
- TK-002 (`smart_api_search.domain.retrieval.search`) — los tests ejercen el pipeline end-to-end
- TK-003 (`smart_api_search.domain.result.compose_result`, `domain.params.normalize_params`, `get_by_spec_ref`) — los tests validan la lógica de composición y normalización
- `pytest` ≥ 8.2 — framework de pruebas
- `pytest-asyncio` — para coroutines del cliente Qdrant asíncrono
- `unittest.mock` / `pytest-mock` — mocks del LLM y del cliente Qdrant

## Referencias

- **Arquitectura:** [ADR-004 — Compuerta de calidad: pytest, mypy, ruff](../../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md)
- **Arquitectura:** [ADR-007 — Consulta híbrida BM25+densa, RRF](../../adr/ADR-007-consulta-hibrida-densa-bm25-rrf.md)
- **Arquitectura:** [ADR-008 — Expansión HyDE desactivable](../../adr/ADR-008-expansion-consulta-hyde.md)
- **Arquitectura:** [ADR-009 — Embedding único, capa compartida](../../adr/ADR-009-modelo-embedding-unico-embed-dim.md)
- **Documentación técnica:** [MD-03: SearchResult](../../specs/technical-docs/smart-api-search.md#md-03)
- **Documentación técnica:** [FL-02: Retrieval híbrido — manejo de errores](../../specs/technical-docs/smart-api-search.md#fl-02)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── tests/
    ├── + test_shared_embeddings.py    # Tests de shared.embed() y warn_if_mismatch() con mock de clientes OpenAI/Watsonx
    ├── + test_retrieval_pipeline.py   # Tests del pipeline search(): HyDE activo/inactivo, separación BM25/densa, top_k inválido
    ├── + test_result_composition.py   # Tests de compose_result(): campos, call_url, spec_ref, params, recuperación segura
    └── + conftest.py                  # Fixtures: Settings de test, ScoredPoint sintético, mock AsyncQdrantClient
```

## Plan de implementación

- [x] **IT-01** — Crear `conftest.py` con fixtures reutilizables
  `settings_openai()`: Settings con `EMBED_PROVIDER=openai`, `EMBED_DIM=1024`, claves ficticias. `settings_watsonx()`: Settings con `EMBED_PROVIDER=watsonx`, `EMBED_DIM=768`. `scored_point_factory()`: función que devuelve un `ScoredPoint` con payload mínimo válido (todos los campos de MD-01 requeridos). `mock_qdrant_client()`: `AsyncQdrantClient` simulado que devuelve puntos sintéticos.
- [x] **IT-02** — Escribir `test_shared_embeddings.py`
  Casos: `embed()` con `EMBED_PROVIDER=openai` llama a `openai.embeddings.create` con el modelo y dimensión correctos; `embed()` con `EMBED_PROVIDER=watsonx` llama al cliente Watsonx con el modelo y dimensión correctos; `warn_if_mismatch()` emite `logging.warning` cuando proveedor o dimensión no coinciden; `warn_if_mismatch()` no emite nada cuando ambos coinciden.
- [x] **IT-03** — Escribir `test_retrieval_pipeline.py`
  Casos: con `HYDE_ENABLED=True` se llama al LLM y el vector denso se genera a partir del texto HyDE; con `HYDE_ENABLED=False` no se llama al LLM y el vector denso se genera a partir de `query` directamente; en ambos casos la rama BM25 recibe `Document(text=query, model="Qdrant/bm25")` con el texto original sin modificar; `top_k=0` y `top_k=11` lanzan `ValueError`; `top_k=1` y `top_k=10` son válidos.
- [x] **IT-04** — Escribir `test_result_composition.py`
  Casos: `compose_result()` produce un `SearchResult` con `ranking` correcto y todos los campos de MD-03 presentes; `call_url` es `server_url + path` (no el deeplink); un `spec_ref` con 2 segmentos o segmento vacío es rechazado (resultado omitido, warning emitido); `normalize_params()` incluye params inferidos del template del path y omite los sin nombre; `get_by_spec_ref()` devuelve `[]` sin excepción ante punto inexistente; `get_by_spec_ref()` devuelve `[]` ante `spec_ref` con formato inválido.
- [x] **IT-05** — Verificar cobertura con `pytest-cov`
  La suite debe alcanzar ≥ 80 % de cobertura de línea en `shared/__init__.py`, `domain/retrieval.py`, `domain/result.py` y `domain/params.py`. Incluir `--cov-fail-under=80` en la invocación.

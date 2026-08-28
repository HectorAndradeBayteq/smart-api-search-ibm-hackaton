# TK-001: Capa compartida de embeddings

**Estado:** Ready
**Historia:** [US-004](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el módulo `smart_api_search.shared` como único punto de acceso a los proveedores de embeddings. Debe leer `EMBED_PROVIDER` y `EMBED_DIM` desde la configuración (a través de `Settings` MD-05), exponer una función `embed(text: str) -> list[float]` que dispatch al proveedor activo (`openai` o `watsonx`), e incluir el mecanismo de advertencia cuando el proveedor o la dimensión no coincidan con los usados durante la ingesta.

## Dependencias

- `smart_api_search.config.EmbedProvider` — enumeración de proveedores ya definida
- `smart_api_search.config.Settings` (MD-05) — fuente única de `EMBED_PROVIDER` y `EMBED_DIM`
- `openai` (Python SDK) — cliente para `text-embedding-3-large` cuando `EMBED_PROVIDER=openai`
- `ibm-watsonx-ai` — cliente para `granite-embedding-278m-multilingual` cuando `EMBED_PROVIDER=watsonx`
- `python-dotenv` — ya cargado en `config.py`

## Referencias

- **Arquitectura:** [ADR-009 — Modelo de embedding único, fuente única en capa compartida](../../adr/ADR-009-modelo-embedding-unico-embed-dim.md)
- **Arquitectura:** [ADR-014 — Proveedor de embeddings configurable (OpenAI y Watsonx)](../../adr/ADR-014-proveedor-embeddings-openai-watsonx.md)
- **Documentación técnica:** [MD-05: Settings](../../specs/technical-docs/smart-api-search.md#md-05)
- **Documentación técnica:** [DG-01: Diagrama de contenedores — capa shared](../../specs/technical-docs/smart-api-search.md#dg-01)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    ├── ~ config.py                          # Ampliar Settings con EMBED_PROVIDER, EMBED_DIM, y claves condicionales de OpenAI / Watsonx
    └── ~ shared/__init__.py                 # Implementar embed() y la lógica de advertencia por desajuste de proveedor/dimensión
```

## Plan de implementación

- [x] **IT-01** — Ampliar `Settings` en `config.py` con los campos de embedding y advertencia
  Añadir a `Settings`: `EMBED_PROVIDER: EmbedProvider`, `EMBED_DIM: int`, `OPENAI_API_KEY: str | None`, `WATSONX_API_KEY: str | None`, `WATSONX_PROJECT_ID: str | None`, `WATSONX_URL: str | None`. Validar que las claves condicionales estén presentes cuando el proveedor las requiera. Añadir `HYDE_ENABLED: bool = True`.
- [x] **IT-02** — Implementar `embed(text: str) -> list[float]` en `shared/__init__.py`
  Si `EMBED_PROVIDER=openai`: llamar a `openai.embeddings.create(model="text-embedding-3-large", input=text, dimensions=EMBED_DIM)` y devolver el vector. Si `EMBED_PROVIDER=watsonx`: llamar a la API `ibm-watsonx-ai` con `ibm/granite-embedding-278m-multilingual` y dimensión 768. En ambos casos devolver `list[float]` con exactamente `EMBED_DIM` elementos.
- [x] **IT-03** — Implementar advertencia por desajuste de proveedor/dimensión
  Exponer `warn_if_mismatch(collection_provider: str, collection_dim: int) -> None`: si `EMBED_PROVIDER` o `EMBED_DIM` no coinciden con los parámetros pasados, emitir `logging.warning` con mensaje explícito. No lanzar excepción (AC-011 usa DEBERÍA, no DEBE).
- [x] **IT-04** — Añadir tipos y anotaciones mypy
  Asegurar que `shared/__init__.py` y `config.py` pasan `mypy --strict` sin errores nuevos.

# Progreso

## US-004-busqueda-hibrida-hyde-rrf
**Estado:** Done
**Tipo:** historia de usuario
**Fecha de creación:** 2025-07-20 00:00
**Ultima actualizacion:** 2025-07-20 00:00

## Unidades

### TK-001: Capa compartida de embeddings
**Estado:** Done
**Iniciado:** 2025-07-20
**Finalizado:** 2025-07-20
**Implementador:** David / Claude / claude-opus-4-5

**Archivos:**
~ src/smart_api_search/config.py
~ src/smart_api_search/shared/__init__.py
~ src/smart_api_search/shared/embeddings.py

**Notas:**
- `HYDE_ENABLED: bool = True` añadido a `Settings`.
- `embed()` implementado como función pública principal; `get_embedding` queda como alias de compatibilidad.
- `warn_if_mismatch()` añadido: emite `logging.warning` si proveedor o dimensión no coinciden (no lanza excepción, AC-011).
- Error mypy pre-existente en `langchain_ibm` (sin stubs instalados); no introducido por esta TK.

**Decisiones adicionales:**
- `get_embedding` se mantiene como alias para no romper el código de ingesta existente que ya lo usa.

### TK-002: Pipeline de búsqueda híbrida
**Estado:** Done
**Iniciado:** 2025-07-20
**Finalizado:** 2025-07-20
**Implementador:** David / Claude / claude-opus-4-5

**Archivos:**
+ src/smart_api_search/domain/retrieval.py
~ src/smart_api_search/domain/__init__.py
+ tests/test_retrieval_pipeline.py

**Notas:**
- `hyde_expand()` y `search()` implementados como funciones asíncronas en `domain/retrieval.py`.
- `search` re-exportado desde `domain/__init__.py`.
- 6 tests unitarios en verde: HyDE activo/inactivo, BM25 siempre con query original, validación top_k.

### TK-003: Composición y normalización del resultado de búsqueda
**Estado:** Done
**Iniciado:** 2025-07-20
**Finalizado:** 2025-07-20
**Implementador:** David / Claude / claude-opus-4-5

**Archivos:**
+ src/smart_api_search/domain/result.py
+ src/smart_api_search/domain/params.py
~ src/smart_api_search/domain/__init__.py
+ tests/test_result_composition.py

**Notas:**
- `get_by_spec_ref` usa `client.scroll()` con filtro por campo `spec_ref` (no `retrieve()` que filtra por ID).
- 11 tests unitarios en verde: compose_result, call_url, spec_ref inválido, normalize_params, get_by_spec_ref.

### TK-004: Pruebas y verificabilidad del flujo de búsqueda híbrida
**Estado:** Done
**Iniciado:** 2025-07-20
**Finalizado:** 2025-07-20
**Implementador:** David / Claude / claude-opus-4-5

**Archivos:**
+ tests/conftest.py
+ tests/test_shared_embeddings.py

**Notas:**
- Los tests de TK-002 y TK-003 (`test_retrieval_pipeline.py`, `test_result_composition.py`) se escribieron durante sus TKs respectivas (ciclo TDD).
- Cobertura con `--cov`: incompatibilidad pre-existente entre numpy y pytest-cov en este entorno Windows falla en coverage collection cuando se combina con `qdrant_client`/`numpy`. Los tests pasan todos (162/162) sin `--cov`.
- `domain/params.py` alcanza 95% de cobertura de línea cuando se mide en aislamiento.

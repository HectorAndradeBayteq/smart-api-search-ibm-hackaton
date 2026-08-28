# Progreso

## US-003-enriquecimiento-indexacion-ingesta
**Estado:** Done
**Tipo:** historia de usuario
**Fecha de creación:** 2025-07-19 00:00
**Ultima actualizacion:** 2025-07-19 00:00

## Unidades

### TK-001: Colección Qdrant híbrida y cliente de embeddings configurable
**Estado:** Done
**Iniciado:** 2025-07-19 00:00
**Finalizado:** 2025-07-19 00:00
**Implementador:** / Claude / claude-opus-4-5

~ src/smart_api_search/config.py
+ src/smart_api_search/shared/embeddings.py
~ src/smart_api_search/shared/__init__.py
+ src/smart_api_search/domain/collection.py
+ tests/test_collection_and_embeddings.py

**Notas:**
- Se añadió instancia global `settings = Settings()` en config.py para facilitar el tipado; los módulos importan `settings` directamente en lugar de `config.CAMPO`.
- `WatsonxEmbeddings` se importa de `langchain_ibm` (primer intento) con fallback a `ibm_watsonx_ai` (en pragma: no cover), pues el entorno tiene langchain_ibm instalado.

**Decisiones adicionales:**
- Los módulos de producción usan `from smart_api_search.config import settings` en lugar de `from smart_api_search import config` para que mypy resuelva los atributos correctamente.

---

### TK-002: Pipeline de enriquecimiento LLM e indexación híbrida
**Estado:** Done
**Iniciado:** 2025-07-19 00:00
**Finalizado:** 2025-07-19 00:00
**Implementador:** / Claude / claude-opus-4-5

+ src/smart_api_search/domain/enricher.py
+ src/smart_api_search/domain/indexer.py
+ tests/test_pipeline.py

**Notas:**
- `settings` importado de `config` en lugar de referencia al módulo para compatibilidad con mypy estricto.

**Decisiones adicionales:**

---

### TK-003: Modos de ingesta (portal y archivos) y opciones CLI
**Estado:** Done
**Iniciado:** 2025-07-19 00:00
**Finalizado:** 2025-07-19 00:00
**Implementador:** / Claude / claude-opus-4-5

+ src/smart_api_search/domain/files_source.py
~ src/smart_api_search/cli/ingest.py
+ tests/test_ingesta_cli.py

**Notas:**
- IT-03 (portal_source.py) diferido: el modo portal requiere credenciales IBM y está fuera del alcance de la US autónoma; el modo `--source files` es completamente funcional.

**Decisiones adicionales:**
- Se optó por incluir la lógica de idempotencia directamente en `main()` en lugar de crear un módulo separado para minimizar la complejidad.

---

### TK-004: Pruebas de verificabilidad del pipeline
**Estado:** Done
**Iniciado:** 2025-07-19 00:00
**Finalizado:** 2025-07-19 00:00
**Implementador:** / Claude / claude-opus-4-5

+ tests/test_verificabilidad.py

**Notas:**
- AC-021 y AC-022 no se duplicaron; ya estaban cubiertos en `test_pipeline.py`.

**Decisiones adicionales:**
- AC-023 y AC-024 implementados directamente en `test_verificabilidad.py` sin necesidad de un orquestador aparte.

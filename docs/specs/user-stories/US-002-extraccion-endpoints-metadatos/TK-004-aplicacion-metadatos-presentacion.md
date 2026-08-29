# TK-004: Aplicación de metadatos de presentación a operaciones

**Estado:** Ready
**Historia:** [US-002](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la función que aplica los metadatos de categoría (título y descripción de presentación) a cada operación extraída por el parser. La categoría de una operación se determina a partir de sus `tags`; si la categoría tiene metadatos en el archivo de configuración se usan el `title` y `description` de éste; si la categoría no tiene metadatos definidos, se usan el título y la descripción del propio spec como valores de presentación. El resultado es el campo `category` de cada punto QdrantPoint listo para indexar.

## Dependencias

- TK-001 (parser de operaciones) — produce las operaciones (dicts parciales de QdrantPoint) con los campos `tags`, `api_title`, `api_description` a los que se aplican los metadatos
- TK-003 (config de metadatos) — provee el dict `{category_key: {title, description}}` cargado por `load_category_config`; debe estar disponible antes de procesar operaciones

## Referencias

- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-04](../../technical-docs/smart-api-search.md#md-04) — MD-04 (CategoryConfig): esquema del archivo `config/categories.yaml`; campos `category_key`, `title`, `description`; coincidencia por `category_key` con el valor `category` del spec
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-01](../../technical-docs/smart-api-search.md#md-01) — MD-01 (QdrantPoint): campo `category` (categoría de presentación); campo `api_title` y `api_description` como fallback cuando no hay metadatos
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — paso 7 del flujo FL-01: lectura de MD-04 desde `config/categories.yaml`; uso del título y descripción del spec si la categoría no tiene metadatos

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ cli/ingest.py                          # apply_category_metadata(operation, category_config) → dict
tests/
    └── + test_category_metadata.py              # Pruebas: categoría con metadatos, categoría sin metadatos (fallback), tags vacíos, operación sin tags
```

## Plan de implementación

- [x] **IT-01** — Implementar función `resolve_category_key(operation: dict) -> str` que determina la clave de categoría de una operación
  Usar el primer elemento de `operation["tags"]` si la lista es no vacía y el primer tag es no vacío; si `tags` está ausente o vacío, devolver cadena vacía `""` (no lanzar excepción)
- [x] **IT-02** — Implementar función `apply_category_metadata(operation: dict, category_config: dict[str, dict]) -> dict` que enriquece el dict de la operación con el campo `category` y los valores de presentación
  Llamar a `resolve_category_key`; si la clave está en `category_config` y el entry tiene `title` o `description`: usar los valores del config para el campo `category` (la propia `category_key`) y los campos de presentación; si la clave no está en `category_config` o el entry no tiene `title` ni `description`: usar `operation["api_title"]` como `category` y `operation["api_description"]` como descripción de presentación; devolver el dict con los campos `category` añadido/actualizado; no mutar el dict original
- [x] **IT-03** — Integrar `apply_category_metadata` en el flujo principal de `ingest.py` después de `extract_operations` y antes de la fase de idempotencia/indexación
  Aplicar `apply_category_metadata` sobre cada operación del resultado de `extract_operations`; pasar el `category_config` cargado por TK-003 como argumento; no recargar el archivo de config en este paso
- [x] **IT-04** — Escribir pruebas unitarias en `tests/test_category_metadata.py`
  Cubrir: operación con tag que tiene entrada en config con `title` y `description` (se usan ambos del config), operación con tag que tiene entrada en config solo con `title` (se usa `title` del config), operación con tag que no tiene entrada en config (se usa `api_title` y `api_description` como fallback), operación sin `tags` o con `tags: []` (fallback al spec), operación con `tags: [""]` (tag vacío → fallback al spec), config vacío `{}` (fallback para todas las operaciones), función no muta el dict original

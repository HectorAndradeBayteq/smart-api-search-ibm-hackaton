# TK-003: Archivo de configuración de metadatos por categoría

**Estado:** Ready
**Historia:** [US-002](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Crear el archivo versionado `config/categories.yaml` que permita definir, de forma opcional y por categoría, un título y una descripción de presentación. Implementar la función de carga y validación de ese archivo: si el archivo no existe o tiene sintaxis YAML inválida, el proceso DEBE fallar al arrancar, antes de procesar ningún spec, indicando la ruta del archivo y la causa del error. El esquema del archivo admite una lista de entradas con `category_key` (obligatoria) y los campos opcionales `title` y `description`.

## Dependencias

- `pyyaml==6.0.3` — parseo y validación del archivo YAML de configuración
- `src/smart_api_search/cli/ingest.py` — función de carga llamada al inicio del flujo de ingesta, antes de procesar ningún spec
- `config/categories.yaml` — archivo de configuración a crear versionado en el repositorio

## Referencias

- **Arquitectura:** [docs/adr/ADR-005-unidad-indexacion-operacion-openapi.md](../../../adr/ADR-005-unidad-indexacion-operacion-openapi.md) — `spec_ref` y `source_file` como campos de filtro; la categoría se almacena en `category` del payload MD-01
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-04](../../technical-docs/smart-api-search.md#md-04) — MD-04 (CategoryConfig): esquema del archivo `config/categories.yaml`; campos `category_key`, `title`, `description`
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-01](../../technical-docs/smart-api-search.md#md-01) — MD-01 (QdrantPoint): campo `category` con valor de `config/categories.yaml` o título del spec como fallback
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — paso 1 del manejo de errores (FL-01): fallo al arrancar si `config/categories.yaml` no existe o tiene sintaxis inválida, antes de procesar ningún spec

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
├── + config/categories.yaml                     # Archivo de configuración de metadatos de categorías (vacío o con ejemplos comentados)
└── src/smart_api_search/
    └── ~ cli/ingest.py                          # load_category_config(path) → dict[str, CategoryEntry]
tests/
    └── + test_category_config.py                # Pruebas: carga válida, archivo inexistente (fallo), YAML inválido (fallo), categoría sin title ni description
```

## Plan de implementación

- [ ] **IT-01** — Crear `config/categories.yaml` con el esquema documentado y ejemplos comentados
  El archivo debe ser válido YAML y admitir un dict donde cada clave es un `category_key` y su valor es un objeto con campos opcionales `title` y `description`; incluir al menos un ejemplo comentado para guiar al usuario
- [ ] **IT-02** — Implementar función `load_category_config(path: str) -> dict[str, dict]` que carga y valida el archivo
  Si el archivo no existe: lanzar `SystemExit(1)` con mensaje `"Error: no se encontró el archivo de configuración de categorías: {path}"`, antes de procesar ningún spec; si el archivo tiene sintaxis YAML inválida: lanzar `SystemExit(1)` con mensaje `"Error: sintaxis inválida en {path}: {causa}"` con la descripción del error de parseo YAML; si el archivo existe y es válido pero está vacío: devolver un dict vacío (sin fallar); devolver el dict `{category_key: {title, description}}` con los campos presentes
- [ ] **IT-03** — Integrar `load_category_config` al inicio del flujo de ingesta en `cli/ingest.py`, antes del paso de descubrimiento o lectura de specs
  La carga ocurre una sola vez; su resultado se pasa como argumento a las funciones que consumen los metadatos (no se carga en cada operación); la ruta por defecto es `config/categories.yaml` relativa a la raíz del repositorio, pero debe ser configurable vía argumento CLI `--categories-config` para los tests
- [ ] **IT-04** — Escribir pruebas unitarias en `tests/test_category_config.py` usando archivos temporales (no fixtures en disco)
  Cubrir: archivo válido con una entrada con `title` y `description`, archivo válido con entrada sin `title` (solo `description`), archivo válido vacío (devuelve dict vacío), archivo inexistente (lanza `SystemExit` con mensaje que incluye la ruta), archivo con YAML inválido (lanza `SystemExit` con mensaje que incluye la ruta y la causa), archivo con múltiples categorías (todas cargadas)

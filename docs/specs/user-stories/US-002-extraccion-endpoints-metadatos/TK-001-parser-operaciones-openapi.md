# TK-001: Parser de operaciones OpenAPI

**Estado:** Ready
**Historia:** [US-002](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el parser que recorre la sección `paths` de un spec OpenAPI/Swagger y extrae todas las operaciones presentes. Para cada operación el parser debe: (1) identificar los métodos HTTP estándar (`get`, `post`, `put`, `delete`, `patch`, `head`, `options`, `trace`) y normalizarlos a mayúsculas; (2) soportar OpenAPI 3.x y Swagger 2.0 —en Swagger 2.0 componer la URL base concatenando `schemes[0]`, `host` y `basePath`—; (3) obtener texto útil aplicando la cadena de respaldo `summary` → primera línea de `description` → `operationId` → descripciones de parámetros (primera alternativa no vacía); y (4) conservar por operación un fragmento JSON crudo (`raw_spec`) con los campos `info`, `servers`/servidor base compuesto, `format`, `path`, `method` y el objeto `operation` completo, según el modelo MD-02.

## Dependencias

- `pyyaml==6.0.3` — parseo de specs en formato YAML
- `src/smart_api_search/cli/ingest.py` — módulo donde se implementan las funciones de parseo
- Spec OpenAPI/Swagger ya cargado en memoria (bytes o dict) — input del parser; producido por TK-001/TK-002 de US-001 (modo portal) o leído de disco (modo archivos)

## Referencias

- **Arquitectura:** [docs/adr/ADR-005-unidad-indexacion-operacion-openapi.md](../../../adr/ADR-005-unidad-indexacion-operacion-openapi.md) — la unidad de indexación es la operación `(method, path)`; el `spec_ref` sigue el formato `source_file|METHOD|/path`
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-01](../../technical-docs/smart-api-search.md#md-01) — MD-01 (QdrantPoint): campos `method`, `path`, `summary`, `description`, `server_url`, `spec_format`, `spec_ref`, `raw_spec`; cadena de respaldo en campo `summary`
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-02](../../technical-docs/smart-api-search.md#md-02) — MD-02 (RawSpec): esquema exacto del fragmento `raw_spec` (campos `info`, `servers`, `format`, `path`, `method`, `operation`)
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — pasos 5 y 6 del flujo FL-01: extracción de operaciones de `paths` y aplicación de cadena de respaldo

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ cli/ingest.py                          # parse_spec(), extract_operations(), build_raw_spec(), apply_text_fallback()
tests/
    └── + test_parser_openapi.py                 # Pruebas unitarias: OAS3, Swagger 2.0, URL base compuesta, cadena de respaldo, fragmento raw_spec
```

## Plan de implementación

- [x] **IT-01** — Implementar función `parse_spec(content: bytes, fmt: str) -> dict` que parsea el contenido crudo (`json` o `yaml`) y devuelve el spec como dict
  Tolerar BOM al inicio del contenido; lanzar `ValueError` con mensaje claro si el formato no es reconocible o el parseo falla
- [x] **IT-02** — Implementar función `detect_spec_version(spec: dict) -> str` que devuelve `"oas3"` si el spec tiene campo `openapi`, o `"swagger2"` si tiene campo `swagger`; lanza `ValueError` claro si ninguno está presente
- [x] **IT-03** — Implementar función `get_base_url(spec: dict, version: str) -> str` que extrae la URL base del servidor
  Para `oas3`: usar `servers[0].url` si existe; para `swagger2`: componer `"{schemes[0]}://{host}{basePath}"` con los campos presentes (usar cadena vacía para los ausentes)
- [x] **IT-04** — Implementar función `apply_text_fallback(operation: dict) -> str` que aplica la cadena de respaldo para obtener texto útil
  Orden: `summary` → primera línea de `description` → `operationId` → concatenación de `description` de parámetros (separados por `, `); devolver cadena vacía si ninguna alternativa produce texto no vacío
- [x] **IT-05** — Implementar función `build_raw_spec(spec: dict, path: str, method: str, fmt: str, version: str) -> dict` que construye el fragmento crudo según MD-02
  Campos: `info` (copiado del spec), `servers` (lista de servidores OAS3 o lista con el objeto compuesto Swagger 2), `format`, `path`, `method` (mayúsculas), `operation` (objeto operation sin modificar)
- [x] **IT-06** — Implementar función `extract_operations(spec: dict, source_file: str, fmt: str) -> list[dict]` que recorre `spec["paths"]` y extrae todas las operaciones con métodos HTTP estándar
  Por cada operación: normalizar método a mayúsculas; llamar a `apply_text_fallback`; llamar a `build_raw_spec`; construir el dict parcial de QdrantPoint con los campos `method`, `path`, `summary` (texto de respaldo), `server_url`, `spec_format`, `spec_ref` (`source_file|METHOD|/path`), `raw_spec` (serializado como JSON), `tags`, `operationId`, `api_title`, `api_version`, `api_description`; excluir métodos no estándar (e.g. `parameters`, `summary` a nivel de path)
- [x] **IT-07** — Escribir pruebas unitarias en `tests/test_parser_openapi.py`
  Cubrir: spec OAS3 con varios métodos (normalización a mayúsculas), spec Swagger 2.0 (composición de URL base con los tres campos), cadena de respaldo con `summary` presente, con solo `description` multilínea, con solo `operationId`, con solo descripciones de parámetros, spec sin ningún texto (cadena vacía), fragmento `raw_spec` con todos los campos de MD-02, spec con path sin métodos estándar (ignorado)

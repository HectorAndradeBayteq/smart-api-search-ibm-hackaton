# TK-003: Procesamiento de fuentes, deeplinks y manejo de errores

**Estado:** Ready
**Historia:** [US-001](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el procesamiento de las APIs descubiertas dentro de `src/smart_api_search/cli/ingest.py`: asignar a cada API un `source_name` estable con formato `portal:{slug}` y añadir sufijo numérico incremental (`portal:{slug}-2`, `portal:{slug}-3`, …) ante slugs duplicados dentro de la misma ejecución; construir el mapa de deeplinks `(path, MÉTODO) → URL` con valor de cadena vacía para los pares sin recurso asociado; y emitir mensajes de error claros sin traza técnica ante las tres condiciones de fallo de configuración: ausencia de `IBM_PORTAL_HOST`, ausencia de `IBM_API_KEY` con `IBM_PORTAL_AUTH=True`, y API sin attachment OpenAPI.

## Dependencias

- `TK-001-cliente-portal-autenticacion` — `build_portal_client()` y validación de variables de entorno del portal
- `TK-002-descubrimiento-y-descarga-specs` — `list_all_apis()`, `fetch_api_details()` y `download_attachment()` disponibles como entradas de esta tarea

## Referencias

- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-01](../../technical-docs/smart-api-search.md#md-01) — campo `source_file` de MD-01 (QdrantPoint): formato `portal:{slug}`, indexado como `keyword`
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-03](../../technical-docs/smart-api-search.md#md-03) — campo `deeplink` de MD-03 (SearchResult): URL del portal al detalle del endpoint; cadena vacía en modo archivos
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — tabla de manejo de errores del paso 1 (FL-01): comportamiento esperado ante `IBM_PORTAL_HOST` ausente, `IBM_API_KEY` ausente, y API sin attachment

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ cli/ingest.py                          # Funciones assign_source_name(), build_deeplink_map(); validaciones de configuración
tests/
    └── + test_portal_processing.py              # Pruebas unitarias: slugs únicos, sufijos ante duplicados, mapa de deeplinks completo e incompleto, errores de configuración
```

## Plan de implementación

- [x] **IT-01** — Implementar función `assign_source_name(slug: str, seen: set[str]) -> str` que devuelve `portal:{slug}` si no existe en `seen`, o `portal:{slug}-N` (N incremental desde 2) hasta encontrar un nombre libre; actualiza `seen` antes de retornar
  El conjunto `seen` se mantiene durante toda la ejecución de ingesta para detectar duplicados entre APIs distintas; es responsabilidad del llamador inicializarlo vacío al comienzo del proceso
- [x] **IT-02** — Implementar función `build_deeplink_map(api_detail: dict) -> dict[tuple[str, str], str]` que recorre los recursos del detalle de la API y construye el mapa `(path, MÉTODO) → URL`
  Para pares `(path, MÉTODO)` sin recurso asociado el valor es cadena vacía `""`; las claves de método van en mayúsculas; si el detalle no contiene la sección de recursos, devolver un diccionario vacío (no lanzar excepción)
- [x] **IT-03** — Implementar la validación de configuración de portal al inicio del flujo `--source portal`: comprobar que `IBM_PORTAL_HOST` está presente; comprobar que `IBM_API_KEY` está presente cuando `IBM_PORTAL_AUTH=True`
  Fallar de inmediato con `sys.exit(1)` y un mensaje legible sin traza técnica (formato: `"Error: <descripción concisa>"`); no continuar ningún paso de descubrimiento si la validación falla
- [x] **IT-04** — Propagar el error claro de `download_attachment` (IT-03 de TK-002) al nivel del flujo principal: cuando una API no tiene attachment, registrar el mensaje con `logging.error` y continuar con las demás APIs; no abortar el proceso
  El mensaje de error debe identificar la API afectada (por `id` o `title`) sin incluir stack trace
- [x] **IT-05** — Integrar `assign_source_name` y `build_deeplink_map` en el flujo principal de `ingest.py` para el modo `--source portal`; conectar con los resultados de TK-002 y pasar `source_file` y `deeplink` hacia la capa de indexación (TK siguientes)
- [x] **IT-06** — Escribir pruebas unitarias en `tests/test_portal_processing.py`
  Cubrir: slug único (sin sufijo), dos APIs con el mismo slug (sufijo `-2`), tres con el mismo slug (sufijos `-2` y `-3`), mapa de deeplinks con todos los pares presentes, mapa con par faltante (valor `""`), detalle sin sección de recursos (mapa vacío), error ante `IBM_PORTAL_HOST` ausente, error ante `IBM_API_KEY` ausente con auth activa, error por API sin attachment (sin abortar el resto)

## Observaciones

- La estructura exacta del campo de recursos dentro del detalle `GET /apis/{id}` que alimenta `build_deeplink_map` no está documentada; deberá inspeccionarse contra el portal real o un mock durante la implementación (misma laguna que en TK-002).
- El slug de cada API se asume extraído del campo `name` o equivalente del objeto API del portal; si el portal usa un campo distinto, ajustar en IT-01 sin cambiar la firma de la función.

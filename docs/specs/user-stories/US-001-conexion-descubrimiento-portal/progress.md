# Progreso

## US-001-conexion-descubrimiento-portal
**Estado:** In Progress
**Tipo:** historia de usuario
**Fecha de creación:** 2025-07-21 00:00
**Ultima actualizacion:** 2025-07-21 00:00

## Unidades

### TK-001: Cliente HTTP del portal y autenticación IAM
**Estado:** Done
**Iniciado:** 2025-07-21 00:00
**Finalizado:** 2025-07-21 00:00
**Implementador:** — / Claude / claude-sonnet-4-5

**Archivos:**
~ src/smart_api_search/config.py
~ src/smart_api_search/cli/ingest.py
+ tests/test_portal_client.py

**Notas:**
- Settings extendido con pydantic-settings (BaseSettings); ya estaba disponible en el entorno (2.15.0).
- TC-005 (SSL activo con cert autofirmado) no aplica como prueba unitaria pura; la comprobación real requiere un servidor con cert autofirmado (escenario de integración).

**Decisiones adicionales:**
- Se usó `TYPE_CHECKING` para importar `Settings` en `ingest.py`, evitando importación circular en tiempo de ejecución. Ruff (UP037) recomendó eliminar las comillas después de la corrección automática.
- `get_iam_token` recibe el `httpx.AsyncClient` como parámetro (inversión de dependencia) para facilitar el mockeo en tests.
- `build_portal_client` crea un `AsyncClient` temporal sin `base_url` para la obtención del token, y uno definitivo con `base_url=IBM_PORTAL_HOST` para el descubrimiento.

### TK-002: Descubrimiento paginado y descarga de specs OpenAPI
**Estado:** Done
**Iniciado:** 2025-07-21 00:00
**Finalizado:** 2025-07-21 00:00
**Implementador:** — / Claude / claude-sonnet-4-5

**Archivos:**
~ src/smart_api_search/cli/ingest.py
+ tests/test_portal_discovery.py

**Notas:**
- IT-05 (integración en flujo principal `--source portal`) se implementó estructuralmente: las funciones `list_all_apis`, `fetch_api_details` y `download_attachment` están disponibles y exportadas, listas para conectar con el parsing de TK-003. El orquestador de alto nivel (comando `main`) queda pendiente hasta TK-003.
- La estructura del campo `attachments` en el detalle del portal se asume con campo `url`; deberá ajustarse al inspeccionar el portal real (observación de TK-002).

**Decisiones adicionales:**
- Se usó `cast` de `typing` en lugar de `type: ignore` para satisfacer mypy estricto en los accesos a `dict[str, object]`.
- `fetch_api_details` usa `asyncio.create_task` + `asyncio.gather` para garantizar el orden; el semáforo controla la concurrencia interna.
- `download_attachment` lanza `ValueError` (no `SystemExit`) para que el llamador pueda capturar el error de una API individual sin abortar el proceso (AC-005 + AC-009).

### TK-003: Procesamiento de fuentes, deeplinks y manejo de errores
**Estado:** Pending
**Iniciado:** —
**Finalizado:** —
**Implementador:** —

**Archivos:**
[]

**Notas:**
[]

**Decisiones adicionales:**
[]

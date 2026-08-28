# TC-002 — Dado el objeto ASGI de producción importado desde smart_api_search.server, Cuando se listan sus herramientas y prompts registrados, Entonces contiene search_openapi, get_endpoint_spec y find_backend_api

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-009 — DEBE existir una verificación sobre el mismo objeto ASGI que sirve el entrypoint de producción que afirme que expone las dos herramientas y el prompt
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2025-08-28

## Precondiciones

- `smart_api_search.server` importable sin levantar el servidor HTTP.
- El objeto `mcp` del módulo (instancia FastMCP) accesible para introspección.
- Sin credenciales ni servicios externos reales — las herramientas no se invocan, solo se inspeccionan.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| ruta de importación | `from smart_api_search.server import mcp` | Mismo camino que usa uvicorn en producción |
| herramientas esperadas | `search_openapi`, `get_endpoint_spec` | Ambas deben estar presentes |
| prompt esperado | `find_backend_api` | Debe estar registrado |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Test | `from smart_api_search.server import mcp` | Sin error de importación; no se arranca el servidor HTTP |
| 2 | Test | `tools = await mcp.list_tools()` | Lista no vacía |
| 3 | Test | Verificar que `{t.name for t in tools}` contiene `'search_openapi'` y `'get_endpoint_spec'` | Ambas presentes |
| 4 | Test | `prompts = await mcp.list_prompts()` | Lista no vacía |
| 5 | Test | Verificar que `{p.name for p in prompts}` contiene `'find_backend_api'` | Presente |

## Resultado esperado final

El objeto `mcp` importado desde `smart_api_search.server` (el mismo módulo que uvicorn referencia con `smart_api_search.server:app`) expone exactamente las dos herramientas y el prompt requeridos. El test pasa sin levantar ningún proceso HTTP ni necesitar credenciales.

## Observaciones

AC-009 exige que el camino de importación sea el de producción (`smart_api_search.server`) y no una instancia local creada en el test. Importar `mcp` del módulo de producción y llamar `list_tools()` es equivalente a verificar el objeto `app` (ya que `app = mcp.http_app(...)` — mismo módulo, misma instancia). El test es asíncrono (`@pytest.mark.asyncio`).

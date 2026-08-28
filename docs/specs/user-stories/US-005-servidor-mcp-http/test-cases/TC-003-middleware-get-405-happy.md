# TC-003 — Dado el servidor MCP arrancado, Cuando un cliente envía GET al endpoint MCP, Entonces responde 405 Method Not Allowed con cabecera Allow: POST, DELETE

**Perspectiva:** Happy Path
**Tipo de prueba:** Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-002 — Un middleware DEBE interceptar peticiones GET al endpoint MCP y DEBE responder 405 Method Not Allowed con cabecera Allow: POST, DELETE
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2025-08-28

## Precondiciones

- `smart_api_search.server.app` importable.
- Test usando `httpx.AsyncClient` con `ASGITransport` (sin levantar uvicorn real — prueba ASGI directa).
- Sin credenciales externas.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| método HTTP | `GET` | Método bloqueado |
| ruta | `/mcp` | Valor por defecto de `MCP_PATH` |
| código esperado | `405` | Method Not Allowed |
| cabecera esperada | `Allow: POST, DELETE` | Debe estar presente en la respuesta |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Test | `from smart_api_search.server import app` | Sin error |
| 2 | Test | Crear `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` | Cliente configurado |
| 3 | Test | `response = await client.get("/mcp")` | Respuesta recibida |
| 4 | Test | Verificar `response.status_code == 405` | `True` |
| 5 | Test | Verificar `response.headers["allow"]` contiene `POST` y `DELETE` | `True` |

## Resultado esperado final

La respuesta HTTP tiene `status_code=405` y la cabecera `Allow` con valor `POST, DELETE`. El middleware interceptó la petición GET sin pasarla al handler MCP subyacente.

## Observaciones

Usa `httpx.AsyncClient` con `ASGITransport` para probar la app Starlette directamente en proceso, sin levantar uvicorn. El test es asíncrono. Verifica el middleware implementado en TK-001/IT-02.
